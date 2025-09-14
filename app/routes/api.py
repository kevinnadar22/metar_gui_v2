from flask import Blueprint, request, jsonify, send_file, render_template
import os
import uuid
import base64
from datetime import datetime
import re
from werkzeug.utils import secure_filename
from app.utils import decode_metar_to_csv, extract_data_from_file_with_day_and_wind, compare_weather_data, OgimetAPI, extract_day_month_year_from_filename,extract_month_year_from_date,fetch_upper_air_data,circular_difference,process_weather_accuracy_helper,interpolate_temperature_only,generate_upper_air_verification_xlsx
from app.utils.AD_warn import parse_warning_file
from app.utils.generate_warning_report import generate_warning_report, generate_aerodrome_warnings_table
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
import math
import base64, io
from PIL import Image
 

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

def parse_validity_to_month_year(validity_str):
    """Parse validity string like '202506010000' to month and year format"""
    try:
        # Remove 'Z' suffix if present
        validity_str = validity_str.rstrip('Z')
        
        # Check if it's a 12-digit format (YYYYMMDDHHMM)
        if len(validity_str) == 12:
            year = int(validity_str[:4])
            month = int(validity_str[4:6])
            day = int(validity_str[6:8])
            hour = int(validity_str[8:10])
            minute = int(validity_str[10:12])
            
            from datetime import datetime
            date_obj = datetime(year, month, day, hour, minute)
            
        # Check if it's a 6-digit format (DDHHMM) - legacy format
        elif len(validity_str) == 6:
            day = int(validity_str[:2])
            hour = int(validity_str[2:4])
            minute = int(validity_str[4:6])
            
            # For 6-digit format, we need to determine the month and year
            from datetime import datetime
            year = 2024  # Based on the data context
            month = 1  # January
            
            try:
                date_obj = datetime(year, month, day, hour, minute)
            except ValueError:
                # If day is invalid for January, try February
                month = 2
                date_obj = datetime(year, month, day, hour, minute)
            
        # Check if it's an 8-digit format (DDHHMMYY)
        elif len(validity_str) == 8:
            day = int(validity_str[:2])
            hour = int(validity_str[2:4])
            minute = int(validity_str[4:6])
            year = int(validity_str[6:8])
            
            # Convert 2-digit year to 4-digit year
            if year < 50:  # Assume 20xx for years 00-49
                year += 2000
            else:  # Assume 19xx for years 50-99
                year += 1900
            
            # Use current month as default, adjust if needed
            from datetime import datetime
            current_date = datetime.now()
            date_obj = datetime(year, current_date.month, day, hour, minute)
            
        # Check if it's a 10-digit format (DDHHMMYYYY)
        elif len(validity_str) == 10:
            day = int(validity_str[:2])
            hour = int(validity_str[2:4])
            minute = int(validity_str[4:6])
            year = int(validity_str[6:10])
            
            from datetime import datetime
            current_date = datetime.now()
            date_obj = datetime(year, current_date.month, day, hour, minute)
            
        else:
            # If format is not recognized, return the original string
            return validity_str
        
        # Format as "Month Year"
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        month_name = month_names[date_obj.month - 1]
        year = date_obj.year
        
        return f"{month_name} {year}"
        
    except Exception as e:
        print(f"Error parsing validity string '{validity_str}': {e}")
        return validity_str

def extract_date_from_metar_file(metar_file_path):
    """Extract date information from METAR file to determine month and year"""
    try:
        if not os.path.exists(metar_file_path):
            return None
            
        with open(metar_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if not lines:
            return None
            
        # Look for the first line with date information
        for line in lines:
            line = line.strip()
            if line and len(line) >= 12:
                # Check if the line starts with a date format (YYYYMMDDHHMM)
                if line[:12].isdigit():
                    date_str = line[:12]
                    return parse_validity_to_month_year(date_str)
                    
        # If no date found in first 12 characters, try to find date in the line
        for line in lines:
            line = line.strip()
            if line and 'METAR' in line:
                # Look for date patterns in the METAR line
                import re
                # Look for patterns like YYYYMMDDHHMM
                date_match = re.search(r'(\d{12})', line)
                if date_match:
                    date_str = date_match.group(1)
                    return parse_validity_to_month_year(date_str)
                    
        return None
        
    except Exception as e:
        print(f"Error extracting date from METAR file: {e}")
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
        global start_dt
        start_dt = start_date
        end_date = form_data.get('end_date')
        global end_dt
        end_dt = end_date
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
        
        # Store last comparison results globally (so /accuracy_chart can access it)
        global last_comparison_df
        last_comparison_df = comparison_df.copy()


        # chart_base64 = plot_accuracy_chart(comparison_df, metric="Overall")

        # img_bytes = base64.b64decode(chart_base64)
        # img = Image.open(io.BytesIO(img_bytes))
        # img.save("accuracy_chart.png")

        
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
        
from flask import Response
import plotly.express as px

# Global storage
last_comparison_df = None
        
@api_bp.route("/accuracy_chart", methods=["GET"])
def accuracy_chart():
    global last_comparison_df,start_dt,end_dt
    metric = request.args.get("metric", "Overall")

    format_date = lambda x: datetime.strptime(x, "%Y%m%d%H%M").strftime("%d/%m/%Y %H:%M UTC") if x else ""
    start_dt = format_date(start_dt)
    end_dt = format_date(end_dt)

    if last_comparison_df is None:
        return jsonify({"error": "No comparison data available. Run /process_metar first."}), 400

    # Prepare DataFrame for chart
    df = last_comparison_df.copy()
    df[metric] = df[metric].str.extract(r'(\d+\.?\d*)').astype(float)
    df = df[~df["DAY"].isin(["Whole Month", "ICAO Requirement"])]

    # Build interactive chart
    fig = px.bar(
        df,
        x="DAY",
        y=metric,
        text=metric,
        labels={"DAY": "Day", metric: f"{metric} Accuracy (%)"},
        color=metric,
        color_continuous_scale="Blues"
    )

    # Apply custom layout
    fig.update_traces(
        texttemplate="%{y:.1f}%",
        textposition="outside",
        hovertemplate="Day %{x}<br>Accuracy: %{y:.1f}%<extra></extra>"
    )
    fig.update_layout(
        title={
            'text': f"Daily {metric} Accuracy from {start_dt} to {end_dt}",
            'x': 0.5,  # Center the title
            'xanchor': 'center',
            'font': {'size': 18, 'color': 'black'}
        },
        xaxis_title_text="Day",
        yaxis_title_text="Accuracy (%)",
        barmode='group',
        yaxis_range=[0, 115],  # Allow a bit of headroom above 100%
        legend_title_text='Accuracy Level',
        legend=dict(x=0.01, y=0.98),  # Position legend inside plot
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        plot_bgcolor='rgba(128, 128, 128, 0.3)',  # Light gray plot area
        paper_bgcolor='white'  # White background
    )

    return Response(fig.to_html(full_html=False), mimetype="text/html")


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
        start_hour = dt.strftime("%H")
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
        end_hour = dt.strftime("%H")
    except ValueError:
    # Try another format if needed, or raise error
        raise ValueError(f"Could not parse date/time: '{endDateTimeRaw}'")
    
    validity_code = f"{start_hour}-{end_hour}"


    # Extract WEATHER section (from 'WEATHER' to end or next section)
    weather_match = re.search(r"WEATHER(.*?)(?==)", text, re.DOTALL)
    weather_text = weather_match.group(1).strip() if weather_match else ""

    # Extract wind data
    pattern = re.findall(r"(\d+)[Mm]\s+(\d{3})/(\d{2})\s+([+-]?\d{2})", upper_winds_text)
    data = [(int(alt), dir, speed, temp) for alt, dir, speed, temp in pattern]
    data.sort(reverse=True)

    df = pd.DataFrame(data, columns=["Altitude (m)", "Wind Direction", "Wind Speed (kt)", "Temperature (°C)"])
    return df, weather_text,startDateTime, endDateTime,icao,validity_code

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
            forecast_df,weather,startTime,endTime,icao,validity_code = parse_forecast_pdf(forecast_path)
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

        weather_check_result = validate_forecast_weather_with_metar(forecast_path)
        weather_accuracy_point = weather_check_result["status"]
        weather_accuracy_percentage= weather_check_result["match_percentage"]

        start_dt = datetime.strptime(startTime, "%Y%m%d%H%M")
        formatted_start = start_dt.strftime("%d/%m/%Y %H:%M UTC")
        end_dt = datetime.strptime(endTime, "%Y%m%d%H%M")
        formatted_end = end_dt.strftime("%d/%m/%Y %H:%M UTC")

        result_xlsx = os.path.join(UPPER_AIR_DOWNLOADS_DIR, f"upper_air_verification_{station_id}.xlsx")


        data_rows = []
        altitude_to_fl = {
        3000: "FL 100 (3000 M)",
        2100: "FL 070 (2100 M)",
        1500: "FL 050 (1500 M)",
        900:  "FL 030 (900 M)",
        600:  "FL 020 (600 M)",
        300:  "FL 010 (300 M)"
        }
         
        for _, row in min_pairs.iterrows():
            raw_altitude = row.get("Altitude (m)", None)

            if pd.isnull(raw_altitude) or not isinstance(raw_altitude, (int, float)) or math.isnan(raw_altitude):
                continue  # Skip rows with invalid or missing altitude

            altitude_m = int(raw_altitude)
 # Skip higher altitudes
            closest_alt = min(altitude_to_fl.keys(), key=lambda x: abs(x - altitude_m))
            fl_label = altitude_to_fl[closest_alt] if altitude_m <= 3000 else None

            data_rows.append({
                "date": formatted_start.split()[0],
                "validity": validity_code,
                "fl": fl_label,
                'weather_forecast': weather_check_result.get("forecast_text", ""),   # string
                'weather_matched': weather_check_result["matched_keywords"],
                "forecast_wind_dir": row.get("Wind Direction", ""),
                "forecast_speed": row.get("Wind Speed (kt)", ""),
                "forecast_temp": row.get("Temperature (°C)", ""),
                "actual_wind_dir": row.get("actual_wind_direction", ""),
                "actual_speed": round(row.get("wind speed_kt_actual", 0), 2),
                "actual_temp": row.get("interp_temperature_C", ""),
                "wind_dir_acc": "CORRECT" if row.get("wind_dir_correct") else "INCORRECT",
                "speed_acc": "CORRECT" if row.get("wind_correct") else "INCORRECT",
                "temp_acc": "CORRECT" if row.get("temp_correct") else "INCORRECT",
                "weather_acc": weather_accuracy_point,
                'temp_accuracy': temp_accuracy,
                'wind_accuracy': wind_accuracy,
                'wind_dir_accuracy': wind_dir_accuracy,
                # 'fl_accuracy_summary': fl_accuracy_summary,
            })

        metadata = {"icao": icao, "month_year": start_dt.strftime("%B %Y")}
        # Build weather_info dict to pass to Excel writer
        weather_info = {
            f"{formatted_start.split()[0]}_{validity_code}": {
                'weather_forecast': weather_check_result.get("forecast_text", ""),
                "matched": weather_check_result.get("matched_keywords", []),
                "accuracy": weather_accuracy_point
            }
        }

        generate_upper_air_verification_xlsx(data_rows, metadata, result_xlsx, weather_info=weather_info)

        return jsonify({
            'file_path': result_xlsx,
            'temp_accuracy': temp_accuracy,
            'wind_accuracy': wind_accuracy,
            'wind_dir_accuracy': wind_dir_accuracy,
            'weather_accuracy': weather_accuracy_percentage,
            'weather_forecast': weather_check_result.get("forecast_text", ""),   # string
            'weather_matched': weather_check_result["matched_keywords"],
            'data': data_rows,
            # 'fl_accuracy_summary': fl_accuracy_summary,
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
    elif file_path.endswith('.xlsx'):
        return send_file(file_path, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True)

    return jsonify({'error': 'File not found'}), 400

def validate_forecast_weather_with_metar(forecast_pdf_path):
    """
    Validates forecast weather condition against actual METARs for the same time range.
    """
    try:
        forecast_df, forecast_weather, start_time, end_time, icao, _ = parse_forecast_pdf(forecast_pdf_path)
        print(f"[INFO] Forecast weather: {forecast_weather}")
        print(f"[INFO] ICAO: {icao}, Time: {start_time} to {end_time}")

        # Fetch METAR using Ogimet
        api = OgimetAPI()
        metar_file_path = api.save_metar_to_file(begin=start_time, end=end_time, icao=icao)

        if not os.path.exists(metar_file_path):
            raise FileNotFoundError(f"METAR file not found: {metar_file_path}")

        with open(metar_file_path, 'r', encoding='utf-8') as f:
            metar_lines = f.readlines()

        forecast_keywords = re.findall(r'\b[A-Z]{2,}\b', forecast_weather)
        forecast_keywords = [w.strip() for w in forecast_keywords if w.isalpha()]
        print(f"[DEBUG] Forecast weather keywords: {forecast_keywords}")

        found_keywords = []
        for line in metar_lines:
            for keyword in forecast_keywords:
                if keyword in line:
                    found_keywords.append(keyword)

        match_status = "CORRECT" if found_keywords else "INCORRECT"
        match_percentage = 100 if found_keywords else 0

        return {
            "status": match_status,
            "metar_lines": metar_lines,
            "match_percentage": match_percentage,
            "matched_keywords": list(set(found_keywords)),
            "forecast_text": forecast_weather,
            # "found_keywords": list(set(found_keywords))
        }

    except Exception as e:
        print(f"[ERROR] Weather verification failed: {e}")
        return {
            "status": "ERROR",
            "match_percentage": 0,
            "error": str(e),
            "metar_lines": [],
            "matched_keywords": []
        }



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
        # Extract station code from the warning file using the validation function
        from app.utils.validation import extract_icao_from_warning
        station_code = extract_icao_from_warning(warning_file)
        if not station_code:
            station_code = "VABB"  # Default fallback
            print(f"[DEBUG] Could not extract station code from warning file, using default: {station_code}")
        else:
            print(f"[DEBUG] Extracted station code from warning file: {station_code}")
        
        df = parse_warning_file(warning_file, station_code=station_code)
        
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
        
        # Debug accuracy value
        print(f"[DEBUG] Accuracy type: {type(accuracy)}, value: {accuracy}")
        
        # Read the report content
        report_file = os.path.join(ad_warn_dir, 'final_warning_report.csv')
        print(f"[DEBUG] Report file: {report_file} (exists: {os.path.exists(report_file)})")
        
        if not os.path.exists(report_file):
            return jsonify({'success': False, 'error': 'Failed to generate report file'}), 500
            
        with open(report_file, 'r', encoding='utf-8') as f:
            report_content = f.read()
            
        # Calculate detailed accuracy percentages
        thunderstorm_accuracy = 0
        wind_accuracy = 0
        overall_accuracy = 0
        
        try:
            # Parse the CSV to get detailed accuracy
            import csv
            from io import StringIO
            
            csv_data = StringIO(report_content)
            csv_reader = csv.DictReader(csv_data)
            
            thunderstorm_count = 0
            thunderstorm_correct = 0
            wind_count = 0
            wind_correct = 0
            total_count = 0
            total_correct = 0
            
            for row in csv_reader:
                element = row.get('Elements (Thunderstorm/Surface wind & Gust)', '').lower()
                accuracy = row.get('true-1 / false-0', '0')
                
                if 'thunderstorm' in element or 'गर्जन' in element:
                    thunderstorm_count += 1
                    total_count += 1
                    if accuracy == '1':
                        thunderstorm_correct += 1
                        total_correct += 1
                elif 'wind' in element or 'gust' in element or 'पवन' in element:
                    wind_count += 1
                    total_count += 1
                    if accuracy == '1':
                        wind_correct += 1
                        total_correct += 1
            
            if thunderstorm_count > 0:
                thunderstorm_accuracy = round((thunderstorm_correct / thunderstorm_count) * 100)
            
            if wind_count > 0:
                wind_accuracy = round((wind_correct / wind_count) * 100)
            
            if total_count > 0:
                overall_accuracy = round((total_correct / total_count) * 100)
                
            print(f"[DEBUG] Detailed accuracy calculation:")
            print(f"  Thunderstorm: {thunderstorm_correct}/{thunderstorm_count} = {thunderstorm_accuracy}%")
            print(f"  Wind: {wind_correct}/{wind_count} = {wind_accuracy}%")
            print(f"  Overall: {total_correct}/{total_count} = {overall_accuracy}%")
                
        except Exception as e:
            print(f"Error calculating detailed accuracy: {e}")
        
        # Ensure accuracy is properly formatted
        try:
            if isinstance(accuracy, (int, float)):
                accuracy_str = f"{accuracy:.0f}"
            else:
                accuracy_str = str(accuracy)
        except Exception as e:
            print(f"[DEBUG] Error formatting accuracy: {e}")
            accuracy_str = str(accuracy)
        
        # Extract station and date information from METAR file
        station_info = ""
        validity_info = ""
        try:
            # Get station code from validation result
            station = validation_result.get('metar_code', 'VABB')
            
            # Extract date information from METAR file
            month_year = extract_date_from_metar_file(metar_file)
            
            if station and month_year:
                station_info = f"Aerodrome warning for station {station} for {month_year}"
            elif station:
                station_info = f"Aerodrome warning for station {station}"
                
            print(f"[DEBUG] Extracted station info: {station_info}")
            
        except Exception as e:
            print(f"[DEBUG] Error extracting station info: {e}")
        
        response_data = {
            'success': True, 
            'report': report_content, 
            'accuracy': f"{overall_accuracy}",
            'detailed_accuracy': {
                'thunderstorm': thunderstorm_accuracy,
                'wind': wind_accuracy,
                'overall': overall_accuracy
            },
            'validation': {
                'metar_code': validation_result['metar_code'],
                'warning_code': validation_result['warning_code']
            },
            'station_info': station_info,
            'validity_info': validity_info
        }
        
        print(f"[DEBUG] Sending response with detailed accuracy: {response_data['detailed_accuracy']}")
        
        # After generating the report and extracting station_info, prepend the heading to the CSV file
        if station_info:
            with open(report_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(station_info + '\n')
                f.write(original_content)
        
        return jsonify(response_data)
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

@api_bp.route('/download/adwrn_report', methods=['GET'])
def download_adwrn_report():
    """Download the aerodrome warning report CSV file"""
    try:
        # Look for the generated report file - check both possible locations
        report_file = os.path.join(METAR_DATA_DIR, 'ad_warn_data', 'final_warning_report.csv')
        print(f"[DEBUG] Looking for report file in METAR_DATA_DIR: {report_file}")
        print(f"[DEBUG] File exists: {os.path.exists(report_file)}")
        
        # If not found in METAR_DATA_DIR, check in the root ad_warn_data directory
        if not os.path.exists(report_file):
            # Check in the root directory
            root_ad_warn_dir = os.path.join(os.getcwd(), 'ad_warn_data')
            report_file = os.path.join(root_ad_warn_dir, 'final_warning_report.csv')
            print(f"[DEBUG] Looking for report file in root: {report_file}")
            print(f"[DEBUG] File exists: {os.path.exists(report_file)}")
            
            if not os.path.exists(report_file):
                # Check for any CSV file in the root ad_warn_data directory
                print(f"[DEBUG] Checking root ad_warn_dir: {root_ad_warn_dir}")
                print(f"[DEBUG] Directory exists: {os.path.exists(root_ad_warn_dir)}")
                
                if os.path.exists(root_ad_warn_dir):
                    csv_files = [f for f in os.listdir(root_ad_warn_dir) if f.endswith('.csv')]
                    print(f"[DEBUG] Found CSV files in root: {csv_files}")
                    if csv_files:
                        # Use the most recent CSV file
                        csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(root_ad_warn_dir, x)), reverse=True)
                        report_file = os.path.join(root_ad_warn_dir, csv_files[0])
                        print(f"[DEBUG] Using most recent file from root: {report_file}")
                    else:
                        return jsonify({"error": "No aerodrome warning report found"}), 404
                else:
                    return jsonify({"error": "Aerodrome warning data directory not found"}), 404
            
            # This code is now handled above in the root directory check
        
        if not os.path.exists(report_file):
            return jsonify({"error": "Aerodrome warning report not found"}), 404
        
        print(f"[DEBUG] Sending file: {report_file}")
        return send_file(
            report_file,
            mimetype='text/csv',
            as_attachment=True,
            download_name='aerodrome_warning_report.csv'
        )
    except Exception as e:
        print(f"Error downloading aerodrome warning report: {str(e)}")
        return jsonify({"error": f"An error occurred while downloading the report: {str(e)}"}), 500

 

 

@api_bp.route('/download/adwrn_table', methods=['GET'])
def download_adwrn_table():
    """Download the aerodrome warnings table in the exact format requested"""
    try:
        # Define base directory and ensure it exists
        ad_warn_dir = os.path.join(os.getcwd(), 'ad_warn_data')
        
        # Define input and output paths
        ad_warn_output = os.path.join(ad_warn_dir, 'AD_warn_output.csv')
        metar_features = os.path.join(ad_warn_dir, 'metar_extracted_features.txt')
        
        # Check if required files exist
        if not os.path.exists(ad_warn_output):
            return jsonify({"error": "Aerodrome warning output file not found. Please run verification first."}), 404
            
        if not os.path.exists(metar_features):
            return jsonify({"error": "METAR features file not found. Please run verification first."}), 404
        
        # Generate the specific table format
        table_file_path = generate_aerodrome_warnings_table(ad_warn_output, metar_features)
        
        if not os.path.exists(table_file_path):
            return jsonify({"error": "Failed to generate aerodrome warnings table"}), 500
        
        print(f"[DEBUG] Sending aerodrome warnings table: {table_file_path}")
        return send_file(
            table_file_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='Aerodrome_Warnings_Table.xlsx'
        )
    except Exception as e:
        print(f"Error downloading aerodrome warnings table: {str(e)}")
        return jsonify({"error": f"An error occurred while downloading the table: {str(e)}"}), 500