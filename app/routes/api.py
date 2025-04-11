from flask import Blueprint, request, jsonify, send_file
import os
import uuid
import base64
from datetime import datetime
import re
from werkzeug.utils import secure_filename

from app.utils import decode_metar_to_csv, extract_data_from_file_with_day_and_wind, compare_weather_data, OgimetAPI
from app.config import METAR_DATA_DIR

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Create uploads and downloads subdirectories in METAR_DATA_DIR
UPLOADS_DIR = os.path.join(METAR_DATA_DIR, 'uploads')
DOWNLOADS_DIR = os.path.join(METAR_DATA_DIR, 'downloads')
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

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


        is_date_time_provided = start_date and end_date
        is_observation_file_provided = 'observation_file' in request.files

        # Validate required parameters
        if not ((start_date and end_date) or is_observation_file_provided) or not icao:
            return jsonify({
                "error": "Missing required parameters. Please provide either (start_date and end_date) or observation file, and icao."
            }), 400
        
        # Sanitize ICAO code (allow only alphanumeric characters)
        icao = re.sub(r'[^a-zA-Z0-9]', '', icao)
        
        # Validate date formats
        if is_date_time_provided:
            try:
                datetime.strptime(start_date, "%Y%m%d%H%M")
                datetime.strptime(end_date, "%Y%m%d%H%M")
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

        if forecast_file.filename == '':
            return jsonify({
                "error": "Empty forecast file. Please upload a valid forecast file."
            }), 400
        
        if is_observation_file_provided:
            observation_file = request.files['observation_file']
            if observation_file.filename == '':
                return jsonify({
                    "error": "Empty observation file. Please upload a valid observation file."
                }), 400
            
        # Save forecast file with secure filename
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        forecast_filename = secure_filename(f"forecast_{icao}_{timestamp}.txt")
        forecast_path = os.path.join(UPLOADS_DIR, forecast_filename)
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
            observation_path = os.path.join(UPLOADS_DIR, observation_filename)
            observation_file.save(observation_path)
            metar_path = observation_path
        
        # Decode METAR data to CSV with secure filename
        metar_csv_filename = secure_filename(f"decoded_metar_{icao}_{timestamp}.csv")
        metar_csv_path = os.path.join(DOWNLOADS_DIR, metar_csv_filename)
        df_metar = decode_metar_to_csv(metar_path, metar_csv_path)
        
        # Extract forecast data
        df_forecast = extract_data_from_file_with_day_and_wind(forecast_path)
        
        # Compare weather data
        comparison_df = compare_weather_data(df_metar, df_forecast)
        
        # Save comparison results to CSV with secure filename
        comparison_csv_filename = secure_filename(f"comparison_{icao}_{timestamp}.csv")
        comparison_csv_path = os.path.join(DOWNLOADS_DIR, comparison_csv_filename)
        comparison_df.to_csv(comparison_csv_path, index=False)
        
        # Calculate metrics
        total_comparisons = len(comparison_df)
        accurate_predictions = len(comparison_df[comparison_df['Accuracy'] == 'Accurate'])
        accuracy_percentage = (accurate_predictions / total_comparisons) * 100 if total_comparisons > 0 else 0
        
        # Encode file paths for security
        encoded_metar_path = encode_file_path(metar_path)
        encoded_metar_csv_path = encode_file_path(metar_csv_path)
        encoded_comparison_csv_path = encode_file_path(comparison_csv_path)
        
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
                "comparison_csv": encoded_comparison_csv_path
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
        elif file_type in ['metar_csv', 'comparison_csv']:
            mime_type = 'text/csv'
            filename = secure_filename(os.path.basename(file_path))
        else:
            return jsonify({
                "error": f"Invalid file type: {file_type}. Valid types are 'metar', 'metar_csv', and 'comparison_csv'."
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
