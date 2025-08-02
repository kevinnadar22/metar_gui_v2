from flask import Blueprint, request, jsonify, send_file
import os
import uuid
import base64
from datetime import datetime
import re
from werkzeug.utils import secure_filename
from app.utils import decode_metar_to_csv, extract_data_from_file_with_day_and_wind, compare_weather_data, OgimetAPI, extract_day_month_year_from_filename,extract_month_year_from_date,fetch_upper_air_data,circular_difference,process_weather_accuracy_helper,interpolate_temperature_only
from app.utils.AD_warn import parse_warning_file
from app.utils.generate_warning_report import generate_warning_report
from app.utils.extract_metar_features import extract_metar_features
from app.utils.validation import validate_files
from app.config import METAR_DATA_DIR, UPPER_AIR_DATA_DIR
import tempfile
import pandas as pd
import numpy as np
import re
from PyPDF2 import PdfReader
import requests
from urllib.parse import quote
import sys  
import subprocess

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Create uploads and downloads subdirectories in METAR_DATA_DIR
METAR_UPLOADS_DIR = os.path.join(METAR_DATA_DIR, 'uploads')
METAR_DOWNLOADS_DIR = os.path.join(METAR_DATA_DIR, 'downloads')

UPPER_AIR_UPLOADS_DIR = os.path.join(UPPER_AIR_DATA_DIR, 'uploads')
UPPER_AIR_DOWNLOADS_DIR = os.path.join(UPPER_AIR_DATA_DIR, 'downloads')

os.makedirs(METAR_UPLOADS_DIR, exist_ok=True)
os.makedirs(METAR_DOWNLOADS_DIR, exist_ok=True)
os.makedirs(UPPER_AIR_UPLOADS_DIR, exist_ok=True)
os.makedirs(UPPER_AIR_DOWNLOADS_DIR, exist_ok=True)

def encode_file_path(file_path):
    """Encode a file path to a secure token"""
    # Combine with a random UUID to prevent guessing
    token = f"{uuid.uuid4()}:{file_path}"
    # Encode to base64
    encoded = base64.urlsafe_b64encode(token.encode()).decode()
    return encoded

def decode_file_path(encoded_path):
    """Decode a secure token back to a file path"""
    try:
        # Decode from base64
        decoded = base64.urlsafe_b64decode(encoded_path.encode()).decode()
        # Extract the file path (remove the UUID part)
        _, file_path = decoded.split(':', 1)
        return file_path
    except Exception:
        return None

@api_bp.route('/get_metar', methods=['GET'])
def get_metar():
    """
    Fetch METAR data from Ogimet and return the raw text file.
    
    Query parameters:
        start_date: Start date for METAR data in format YYYYMMDDHHMM
        end_date: End date for METAR data in format YYYYMMDDHHMM
        icao: ICAO code for the airport
        
    Returns:
        Raw METAR text file or JSON error response
    """
    try:
        # Extract parameters from query string
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        icao = request.args.get('icao')
        
        # Validate required parameters
        if not all([start_date, end_date, icao]):
            return jsonify({
                "error": "Missing required parameters. Please provide start_date, end_date, and icao."
            }), 400
        
        # Sanitize ICAO code (allow only alphanumeric characters)
        icao = re.sub(r'[^a-zA-Z0-9]', '', icao)
        
        # Validate date formats
        try:
            datetime.strptime(start_date, "%Y%m%d%H%M")
            datetime.strptime(end_date, "%Y%m%d%H%M")
        except ValueError:
            return jsonify({
                "error": "Invalid date format. Please use the format YYYYMMDDHHMM."
            }), 400
        
        # Get METAR data using OgimetAPI
        api = OgimetAPI()
        metar_path = api.save_metar_to_file(
            begin=start_date,
            end=end_date,
            icao=icao
        )
        
        # Return the raw METAR file
        if os.path.exists(metar_path):
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            download_name = secure_filename(f"metar_{icao}_{timestamp}.txt")
            return send_file(
                metar_path,
                mimetype='text/plain',
                as_attachment=True,
                download_name=download_name
            )
        else:
            return jsonify({
                "error": "Failed to retrieve METAR data."
            }), 500
            
    except Exception as e:
        print(f"Error in get_metar: {str(e)}")
        return jsonify({
            "error": f"An error occurred while retrieving METAR data: {str(e)}"
        }), 500

@api_bp.route('/process_metar', methods=['POST'])
def process_metar():
    """
    Process METAR data by fetching observations and comparing with forecast.
    
    Expected JSON body:
    {
        "start_date": "YYYYMMDDHHMM", // Start date for METAR data
        "end_date": "YYYYMMDDHHMM",   // End date for METAR data
        "icao": "VABB",               // ICAO code for the airport
    }
    
    The forecast file should be uploaded as 'forecast_file' in the multipart/form-data.
    
    Returns:
        JSON response with analysis results and paths to generated files
    """
    try:
        # Parse multipart/form-data
        form_data = request.form.to_dict()
        
        # Extract parameters from form data
        start_date = form_data.get('start_date')
        end_date = form_data.get('end_date') 
        icao = form_data.get('icao')
        verification_type = request.form.get('verification_type', 'daily')  # default to daily

        is_date_time_provided = start_date and end_date
        is_observation_file_provided = 'observation_file' in request.files

        # Validate required parameters
        if not ((start_date and end_date) or is_observation_file_provided) or not icao:
            return jsonify({
                "error": "Missing required parameters. Please provide either (start_date and end_date) or observation file, and icao."
            }), 400
        
        # Sanitize ICAO code (allow only alphanumeric characters)
        icao = re.sub(r'[^a-zA-Z0-9]', '', icao)
        
        # Validate date formats and extract month/year
        metar_month_year = None
        if is_date_time_provided:
            try:
                # Use helper function to extract month and year from start date
                _,_, _, metar_month_year = extract_month_year_from_date(start_date)
                print(f"Extracted METAR month/year: {metar_month_year}")
                # Also validate end date format
                datetime.strptime(end_date, "%Y%m%d%H%M")
                if not metar_month_year:
                    return jsonify({
                        "error": "Could not extract month and year from start date."
                    }), 400
            except ValueError:
                return jsonify({
                    "error": "Invalid date format. Please use the format YYYYMMDDHHMM."
                }), 400
            
        # Check if forecast file is provided
        if 'forecast_file' not in request.files:
            return jsonify({
                "error": "No forecast file provided. Please upload a forecast file."
            }), 400
            
        forecast_file = request.files['forecast_file']
        print(f"Forecast file: {forecast_file.filename}")

        if forecast_file.filename == '':
            return jsonify({
                "error": "Empty forecast file. Please upload a valid forecast file."
            }), 400
        
        # Extract month and year from forecast filename using helper function
        _,_, _, forecast_month_year = extract_day_month_year_from_filename(forecast_file.filename)

        if is_observation_file_provided:
            observation_file = request.files['observation_file']
            if observation_file.filename == '':
                return jsonify({
                    "error": "Empty observation file. Please upload a valid observation file."
                }), 400
            
            print(f"Observation file: {observation_file.filename}")
            # If using observation file, extract month/year from its filename if possible
            if not metar_month_year:
                _,_, _, metar_month_year = extract_day_month_year_from_filename(observation_file.filename)
        
        # Validate month/year match if both are available
        if metar_month_year and forecast_month_year and metar_month_year != forecast_month_year:
            return jsonify({
                "error": f"Month/year mismatch between METAR data ({metar_month_year}) and forecast file ({forecast_month_year}). Please ensure both files are for the same month and year."
            }), 200
            
        # Save forecast file with secure filename
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        forecast_filename = secure_filename(f"{forecast_month_year}.txt")
        forecast_path = os.path.join(METAR_UPLOADS_DIR, forecast_filename)
        forecast_file.save(forecast_path)
        
        if is_date_time_provided:   
            # Get METAR data using OgimetAPI
            api = OgimetAPI()
            metar_path = api.save_metar_to_file(
                begin=start_date,
                end=end_date,
                icao=icao
            )
        else:
            # get observation file
            # save observation file
            observation_filename = secure_filename(f"observation_{icao}_{timestamp}.txt")
            observation_path = os.path.join(METAR_UPLOADS_DIR, observation_filename)
            observation_file.save(observation_path)
            metar_path = observation_path
        
        # Decode METAR data to CSV with secure filename
        metar_csv_filename = secure_filename(f"decoded_metar_{icao}_{timestamp}.csv")
        metar_csv_path = os.path.join(METAR_DOWNLOADS_DIR, metar_csv_filename)
        df_metar = decode_metar_to_csv(metar_path, metar_csv_path)
        
        # Extract forecast data
        df_forecast = extract_data_from_file_with_day_and_wind(forecast_path)
        
        # Compare weather data
        comparison_df, merged_df = compare_weather_data(df_metar, df_forecast)
        
        # Save comparison results to CSV with secure filename
        comparison_csv_filename = secure_filename(f"comparison_{icao}_{timestamp}.csv")
        comparison_csv_path = os.path.join(METAR_DOWNLOADS_DIR, comparison_csv_filename)

        # Create header information with period and station details
        with open(comparison_csv_path, 'w', newline='', encoding='utf-8') as f:
            f.write(f"REPORT,")
            f.write(f"{icao},")
            if start_date and end_date:
                format_date = lambda x: datetime.strptime(x, "%Y%m%d%H%M").strftime("%d/%m/%Y %H:%M UTC") if x else ""
                f.write(f"{format_date(start_date)} to {format_date(end_date)},")
            else:
                f.write(f"Observation,")
            f.write("\n")  # Empty line separator

        comparison_df.to_csv(comparison_csv_path, index=False, mode='a')

        # Save merged data to CSV with secure filename
        merged_csv_filename = secure_filename(f"merged_{icao}_{timestamp}.csv")
        merged_csv_path = os.path.join(METAR_DOWNLOADS_DIR, merged_csv_filename)
        merged_df.to_csv(merged_csv_path, index=False)
        
        # Calculate metrics
        total_comparisons = len(comparison_df)
        #accurate_predictions = len(comparison_df[comparison_df['Accuracy'] == 'Accurate'])
        accurate_predictions = 0
        accuracy_percentage = (accurate_predictions / total_comparisons) * 100 if total_comparisons > 0 else 0
        
        # Encode file paths for security
        encoded_metar_path = encode_file_path(metar_path)
        encoded_metar_csv_path = encode_file_path(metar_csv_path)
        encoded_comparison_csv_path = encode_file_path(comparison_csv_path)
        encoded_merged_csv_path = encode_file_path(merged_csv_path)

        # Prepare response
        response_data = {
            "status": "success",
            "message": "METAR data processed successfully",
            "metrics": {
                "total_comparisons": total_comparisons,
                "accurate_predictions": accurate_predictions,
                "accuracy_percentage": round(accuracy_percentage, 2)
            },
            "file_paths": {
                "metar_file": encoded_metar_path,
                "metar_csv": encoded_metar_csv_path,
                "comparison_csv": encoded_comparison_csv_path,
                "merged_csv": encoded_merged_csv_path
            },
            "metadata": {
                "start_time": datetime.strptime(start_date, "%Y%m%d%H%M").strftime("%d/%m/%Y %H:%M UTC") if start_date else None,
                "end_time": datetime.strptime(end_date, "%Y%m%d%H%M").strftime("%d/%m/%Y %H:%M UTC") if end_date else None,
                "icao": icao,
            },
            # "comparison_data": comparison_df.to_dict(orient='records')
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        # Log the error (in a production environment, you'd use a proper logger)
        print(f"Error in process_metar: {str(e)}")
        return jsonify({
            "error": f"An error occurred while processing the METAR data: {str(e)}"
        }), 500
    

@api_bp.route('/download/<file_type>', methods=['GET'])
def download_file(file_type):
    """
    Download generated files.
    
    Parameters:
        file_type: Type of file to download ('metar', 'metar_csv', 'comparison_csv')
        file_path: Path to the file (from the process_metar response)
    """
    try:
        encoded_path = request.args.get('file_path')
        if not encoded_path:
            return jsonify({
                "error": "No file path provided. Please provide the file_path parameter."
            }), 400
        
        # Decode the file path
        file_path = decode_file_path(encoded_path)
        if not file_path:
            return jsonify({
                "error": "Invalid file path token."
            }), 400
        
        print(f"File path: {file_path}, normalized: {os.path.normpath(file_path)}")
            
        # Validate file path to prevent directory traversal
        normalized_path = os.path.normpath(file_path)
        valid_prefixes = ['uploads', 'downloads', 'app/static/metar_data/downloads']
        
        if not any(normalized_path.startswith(prefix) for prefix in valid_prefixes):
            # Also check for absolute paths that might contain our valid directories
            if not any(os.sep + prefix in normalized_path for prefix in valid_prefixes):
                return jsonify({
                    "error": "Invalid file path. Access denied."
                }), 403
            
        if not os.path.exists(file_path):
            return jsonify({
                "error": f"File not found at path: {file_path}"
            }), 404
        
        if file_type == 'metar':
            mime_type = 'text/plain'
            filename = secure_filename(os.path.basename(file_path))
        elif file_type in ['metar_csv', 'comparison_csv', 'merged_csv']:
            mime_type = 'text/csv'
            filename = secure_filename(os.path.basename(file_path))
        else:
            return jsonify({
                "error": f"Invalid file type: {file_type}. Valid types are 'metar', 'metar_csv', 'comparison_csv', and 'merged_csv'."
            }), 400
        
        return send_file(
            file_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Error in download_file: {str(e)}")
        return jsonify({
            "error": f"An error occurred while downloading the file: {str(e)}"
        }), 500

def parse_forecast_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() for page in reader.pages)

    # Extract UPPER WINDS section
    match = re.search(r"UPPER WINDS(.*?)WEATHER", text, re.DOTALL)
    if not match:
        raise ValueError("Upper Winds section not found in PDF.")
    upper_winds_text = match.group(1)

    icaoM = re.search(r"LOCAL FORECAST FOR(.*?)AND", text)
    if not icaoM:
        raise ValueError("ICAO code not found in PDF.")
    icao = icaoM.group(1).strip()
    print(f"ICAO code extracted: {icao}")

    startDateTimeM = re.search(r"FROM(.*?)UTC", text,re.DOTALL)
    if not startDateTimeM:
        raise ValueError("Start date and time not found in PDF.")
    
    startDateTimeRaw = startDateTimeM.group(1).strip()
    try:
    # Example: if the PDF gives "01 Jan 2023 00:00"
        dt = datetime.strptime(startDateTimeRaw, "%Y/%m/%d %H:%M")
        startDateTime = dt.strftime("%Y%m%d%H%M")
    except ValueError:
    # Try another format if needed, or raise error
        raise ValueError(f"Could not parse date/time: '{startDateTimeRaw}'")

    endDateTimeM = re.search(r"TO(.*?)UTC", text,re.DOTALL)
    if not endDateTimeM:
        raise ValueError("Start date and time not found in PDF.")
    
    endDateTimeRaw = endDateTimeM.group(1).strip()
    try:
    # Example: if the PDF gives "01 Jan 2023 00:00"
        dt = datetime.strptime(endDateTimeRaw, "%Y/%m/%d %H:%M")
        endDateTime = dt.strftime("%Y%m%d%H%M")
    except ValueError:
    # Try another format if needed, or raise error
        raise ValueError(f"Could not parse date/time: '{endDateTimeRaw}'")


    # Extract WEATHER section (from 'WEATHER' to end or next section)
    weather_match = re.search(r"WEATHER(.*?)(?==)", text, re.DOTALL)
    weather_text = weather_match.group(1).strip() if weather_match else ""

    # Extract wind data
    pattern = re.findall(r"(\d+)[Mm]\s+(\d{3})/(\d{2})\s+([+-]?\d{2})", upper_winds_text)
    data = [(int(alt), dir, speed, temp) for alt, dir, speed, temp in pattern]
    data.sort(reverse=True)

    df = pd.DataFrame(data, columns=["Altitude (m)", "Wind Direction", "Wind Speed (kt)", "Temperature (°C)"])
    return df, weather_text,startDateTime, endDateTime,icao

@api_bp.route('/get_upper_air', methods=['GET'])
def get_upper_air():
    datetime_str = request.args.get('datetime')
    print(f"[INFO] Fetching upper air data for datetime: {datetime_str}")
    station_id = request.args.get('station_id')
    print(f"[INFO] Station ID: {station_id}")
    try:
        file_path = fetch_upper_air_data(datetime_str, station_id)
        print(f"file_path: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        if os.path.exists(file_path):
            return send_file(
                file_path,
                mimetype='text/csv',
                as_attachment=True,
                download_name=os.path.basename(file_path)
            )
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@api_bp.route('/process_upper_air', methods=['POST'])
def process_upper_air():
    try:
        station_id = request.form['station_id']
        datetime_str = request.form.get('datetime')
        # reference_temp = request.form.get('reference_temp', None)
        # print(reference_temp)
        # try:
        #     reference_temp = float(reference_temp)
        # except (TypeError, ValueError):
        #     reference_temp = 2.0  # Default value

        observation_file = request.files.get('observation_file')
        forecast_file = request.files.get('forecast_file')

        # --- Handle Forecast File ---
        forecast_df = None
        if forecast_file:
            forecast_filename = secure_filename(forecast_file.filename)
            forecast_path = os.path.join(UPPER_AIR_DATA_DIR, 'uploads', forecast_filename)
            forecast_file.save(forecast_path)
            forecast_df,weather,startTime,endTime,icao = parse_forecast_pdf(forecast_path)
            if hasattr(forecast_df, 'columns'):
                forecast_df.columns = forecast_df.columns.str.strip()
                forecast_df = forecast_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        # --- Handle Observation File or Fetch ---
        if observation_file:
            obs_path = os.path.join(UPPER_AIR_DOWNLOADS_DIR, secure_filename(observation_file.filename))
            observation_file.save(obs_path)
            actual_df = pd.read_csv(obs_path, skipinitialspace=True)
            actual_df.columns = actual_df.columns.str.strip()
            actual_df = actual_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        else:
            file_path = fetch_upper_air_data(datetime_str, station_id)
            actual_df = pd.read_csv(file_path, skipinitialspace=True)
            actual_df.columns = actual_df.columns.str.strip()
            actual_df = actual_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        print(actual_df.head())

        # --- Debug: Print columns to verify ---
        print("actual_df columns:", actual_df.columns.tolist())
        if forecast_df is not None:
            print("forecast_df columns:", forecast_df.columns.tolist())

        # --- Convert columns to numeric as needed ---
        for col in ["geopotential height_m", "temperature_C", "wind speed_m/s"]:
            if col in actual_df.columns:
                actual_df[col] = pd.to_numeric(actual_df[col], errors="coerce")
            else:
                raise KeyError(f"Column '{col}' not found in observation data.")

        for col in ["Altitude (m)", "Temperature (°C)", "Wind Speed (kt)"]:
            if col in forecast_df.columns:
                forecast_df[col] = pd.to_numeric(forecast_df[col], errors="coerce")
            else:
                raise KeyError(f"Column '{col}' not found in forecast data.")

        # --- Merge and Calculate ---
        # actual_df["key"] = 1
        # forecast_df["key"] = 1

        # merged = pd.merge(actual_df, forecast_df, on="key").drop("key", axis=1)
        # merged["height_diff"] = (merged["geopotential height_m"] - merged["Altitude (m)"]).abs()
        # min_pairs = merged.loc[merged.groupby("Altitude (m)")["height_diff"].idxmin()]

        # min_pairs["wind speed_kt_actual"] = min_pairs["wind speed_m/s"] * 1.94384
        # min_pairs["temp_diff"] = (min_pairs["Temperature (°C)"] - min_pairs["temperature_C"]).abs()
        # min_pairs["wind_diff"] = (min_pairs["Wind Speed (kt)"] - min_pairs["wind speed_kt_actual"]).abs()
        # if "wind direction_degree" in min_pairs.columns and "Wind Direction" in min_pairs.columns:
        #     min_pairs["wind_dir_diff"] = min_pairs.apply(
        #         lambda row: circular_difference(
        #             float(row["wind direction_degree"]),
        #             float(row["Wind Direction"])
        #         ) if pd.notnull(row["wind direction_degree"]) and pd.notnull(row["Wind Direction"]) else np.nan,
        #         axis=1
        #     )

        #     wind_dir_threshold = 30
        #     min_pairs["wind_dir_correct"] = min_pairs["wind_dir_diff"].apply(
        #         lambda diff: not pd.isnull(diff) and diff <= wind_dir_threshold
        #     )       
        #     wind_dir_accuracy = round(min_pairs["wind_dir_correct"].mean() * 100, 2)
        # else:
        #     wind_dir_accuracy = None

        # Replaces merge + min_pairs logic

        min_pairs = interpolate_temperature_only(actual_df, forecast_df)

# Wind speed (converted)
        min_pairs["wind speed_kt_actual"] = min_pairs["actual_wind_speed_m/s"] * 1.94384

# Accuracy calculations
        min_pairs["temp_diff"] = (min_pairs["Temperature (°C)"] - min_pairs["interp_temperature_C"]).abs()
        min_pairs["wind_diff"] = (min_pairs["Wind Speed (kt)"] - min_pairs["wind speed_kt_actual"]).abs()

# Wind direction difference (if both columns present)
        if "Wind Direction" in min_pairs.columns and "actual_wind_direction" in min_pairs.columns:
            min_pairs["wind_dir_diff"] = min_pairs.apply(
                lambda row: circular_difference(
                    float(row["actual_wind_direction"]),
                    float(row["Wind Direction"])
                ) if pd.notnull(row["actual_wind_direction"]) and pd.notnull(row["Wind Direction"]) else np.nan,
                axis=1
            )
            min_pairs["wind_dir_correct"] = min_pairs["wind_dir_diff"] <= 30
            wind_dir_accuracy = round(min_pairs["wind_dir_correct"].mean() * 100, 2)
        else:
            wind_dir_accuracy = None



        min_pairs["temp_correct"] = min_pairs["temp_diff"] <= 2
        min_pairs["wind_correct"] = min_pairs["wind_diff"] <= 10

        temp_accuracy = round(min_pairs["temp_correct"].mean() * 100, 2)
        wind_accuracy = round(min_pairs["wind_correct"].mean() * 100, 2)


        result_csv = os.path.join(UPPER_AIR_DOWNLOADS_DIR, f"upper_air_verification_{station_id}.csv")
        weather_accuracy_point = process_weather_accuracy_helper(weather, startTime, endTime, icao)

        # Create header information with period and station details
        with open(result_csv, 'w', newline='', encoding='utf-8') as f:
            f.write(f"REPORT,")
            f.write(f"{station_id},")
            f.write(f"{icao},")
            # Convert startTime and endTime from YYYYMMDDHHMM to human readable format and merge
            start_dt = datetime.strptime(startTime, "%Y%m%d%H%M")
            formatted_start = start_dt.strftime("%d/%m/%Y %H:%M UTC")
            end_dt = datetime.strptime(endTime, "%Y%m%d%H%M")
            formatted_end = end_dt.strftime("%d/%m/%Y %H:%M UTC")
            f.write(f"{formatted_start} to {formatted_end},")
            f.write("\n")  # Empty line separator
            
            # Add accuracy details
            f.write("\n")  # Empty line
            f.write(f"Temperature Accuracy, Wind Speed Accuracy, Wind Direction Accuracy, Weather Accuracy\n")
            f.write(f"{temp_accuracy}, {wind_accuracy}, {wind_dir_accuracy}, {weather_accuracy_point}\n")
            f.write(",\n")  # Empty line before data
            f.write(",\n")
            
        # Append the actual data to the CSV
        min_pairs.to_csv(result_csv, mode='a', index=False)


        return jsonify({
            'file_path': result_csv,
            'temp_accuracy': temp_accuracy,
            'wind_accuracy': wind_accuracy,
            'wind_dir_accuracy': wind_dir_accuracy,
            'weather_accuracy': weather_accuracy_point,
            'metadata': {
                'station_id': station_id,
                'icao': icao,
                'start_time': formatted_start,
                'end_time': formatted_end
            }
        })

    except Exception as e:
        print(f"[ERROR] Exception in process_upper_air: {e}")
        return jsonify({'error': str(e)}), 500
    
@api_bp.route('download/upper_air_csv')
def download_upper_air_csv():
    file_path = request.args.get('file_path')
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


@api_bp.route('/upload_ad_warning', methods=['POST'])
def upload_ad_warning():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not file.filename.lower().endswith('.txt'):
        return jsonify({'error': 'Only .txt files are allowed'}), 400
    
    # Create a directory for AD warning files if it doesn't exist
    ad_warn_dir = os.path.join(os.getcwd(), 'ad_warn_data')
    os.makedirs(ad_warn_dir, exist_ok=True)
    
    # Save the warning file
    warning_file = os.path.join(ad_warn_dir, 'AD_warning.txt')
    file.save(warning_file)
    
    # Also copy metar.txt to ad_warn_data directory if it exists
    metar_source = os.path.join(os.getcwd(), 'metar.txt')
    if os.path.exists(metar_source):
        metar_dest = os.path.join(ad_warn_dir, 'metar.txt')
        import shutil
        shutil.copy2(metar_source, metar_dest)
        print(f"[DEBUG] Copied METAR file to: {metar_dest}")
    
    try:
        # Parse the warning file immediately to validate it
        df = parse_warning_file(warning_file, station_code="VABB")
        
        # Read the file for preview
        with open(warning_file, 'r', encoding='utf-8') as f:
            preview = f.read()
            
        return jsonify({
            'message': 'File uploaded and parsed successfully',
            'preview': preview
        })
    except Exception as e:
        print(f"[ERROR] Failed to process warning file: {str(e)}")
        return jsonify({'error': f'Failed to process file: {str(e)}'}), 500

@api_bp.route('/adwrn_verify', methods=['POST'])
def adwrn_verify():
    try:
        # Define base directory and ensure it exists
        ad_warn_dir = os.path.join(os.getcwd(), 'ad_warn_data')
        os.makedirs(ad_warn_dir, exist_ok=True)
        
        # Define input and output paths
        warning_file = os.path.join(ad_warn_dir, 'AD_warning.txt')
        metar_file = os.path.join(ad_warn_dir, 'metar.txt')
        ad_warn_output = os.path.join(ad_warn_dir, 'AD_warn_output.csv')
        metar_features = os.path.join(ad_warn_dir, 'metar_extracted_features.txt')
        
        print(f"[DEBUG] Checking paths:")
        print(f"Warning file: {warning_file} (exists: {os.path.exists(warning_file)})")
        print(f"METAR file: {metar_file} (exists: {os.path.exists(metar_file)})")
        
        # Check if required files exist
        if not os.path.exists(warning_file):
            return jsonify({'success': False, 'error': 'Warning file not found. Please upload it first.'}), 404
            
        if not os.path.exists(metar_file):
            return jsonify({'success': False, 'error': 'METAR file not found. Please ensure it exists.'}), 404
        
        # Perform validation before processing
        validation_result = validate_files(metar_file, warning_file)
        
        if not validation_result['success']:
            return jsonify({
                'success': False, 
                'error': validation_result['error'],
                'validation_failed': True,
                'metar_code': validation_result.get('metar_code'),
                'warning_code': validation_result.get('warning_code')
            }), 400
        
        # Parse warning file
        print("[DEBUG] Parsing warning file...")
        df = parse_warning_file(warning_file, station_code=validation_result['metar_code'])
        print(f"[DEBUG] AD warn output saved to: {ad_warn_output}")
        
        # Extract METAR features
        print("[DEBUG] Extracting METAR features...")
        try:
            extract_metar_features(ad_warn_output, metar_file, metar_features)
            print(f"[DEBUG] METAR features saved to: {metar_features}")
        except Exception as e:
            print(f"[ERROR] Failed to extract METAR features: {str(e)}")
            raise
        
        # Verify files exist after extraction
        print(f"[DEBUG] Checking if files were created:")
        print(f"AD warn output exists: {os.path.exists(ad_warn_output)}")
        print(f"METAR features exists: {os.path.exists(metar_features)}")
        
        # Generate warning report
        print("[DEBUG] Generating warning report...")
        final_df, accuracy = generate_warning_report(ad_warn_output, metar_features)
        
        # Read the report content
        report_file = os.path.join(ad_warn_dir, 'final_warning_report.csv')
        print(f"[DEBUG] Report file: {report_file} (exists: {os.path.exists(report_file)})")
        
        if not os.path.exists(report_file):
            return jsonify({'success': False, 'error': 'Failed to generate report file'}), 500
            
        with open(report_file, 'r', encoding='utf-8') as f:
            report_content = f.read()
            
        return jsonify({
            'success': True, 
            'report': report_content, 
            'accuracy': f"{accuracy:.0f}",
            'validation': {
                'metar_code': validation_result['metar_code'],
                'warning_code': validation_result['warning_code']
            }
        })
    except Exception as e:
        print(f"[ERROR] Error in adwrn_verify: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/download_metar', methods=['GET'])
def download_metar():
    """Download the METAR data file"""
    try:
        ad_warn_dir = os.path.join(os.getcwd(), 'ad_warn_data')
        metar_file = os.path.join(ad_warn_dir, 'metar.txt')
        
        if os.path.exists(metar_file):
            return send_file(metar_file, as_attachment=True, download_name='metar.txt')
        else:
            return jsonify({'error': 'METAR file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500