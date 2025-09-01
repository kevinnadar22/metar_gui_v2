from flask import Blueprint, render_template, request, jsonify, send_file
from app.utils.fetch_metar import fetch_all_metar
from datetime import datetime
import os

web = Blueprint('web', __name__)

@web.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            # Handle form data from aerodrome warning section
            icao = request.form.get('icao', 'VABB')
            start_date = request.form.get('start_date')
            start_hour = request.form.get('start_hour', '0')
            start_min = request.form.get('start_min', '0')
            end_date = request.form.get('end_date')
            end_hour = request.form.get('end_hour', '23')
            end_min = request.form.get('end_min', '59')
            
            # Parse dates
            if start_date and end_date:
                start_dt = datetime.strptime(f"{start_date} {start_hour}:{start_min}", "%Y-%m-%d %H:%M")
                end_dt = datetime.strptime(f"{end_date} {end_hour}:{end_min}", "%Y-%m-%d %H:%M")
                
                # Call the fetch_all_metar function
                output_file = "metar.txt"
                fetch_all_metar(icao, start_dt, end_dt, output_file)
                
                # Read the generated file to show preview
                try:
                    # The file should now be in ad_warn_data directory
                    ad_warn_dir = os.path.join(os.getcwd(), 'ad_warn_data')
                    file_path = os.path.join(ad_warn_dir, output_file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        metar_preview = file_content
                except FileNotFoundError:
                    metar_preview = "METAR data fetched successfully"
                
                return jsonify({
                    'success': True,
                    'message': f'METAR data fetched successfully for {icao}',
                    'metar_preview': metar_preview
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Start and end dates are required'
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
    
    return render_template('index.html')

@web.route('/fetch_metar', methods=['POST'])
def fetch_metar():
    try:
        data = request.get_json()
        icao = data.get('icao', 'VABB')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        output_file = data.get('output_file', 'metar.txt')
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else datetime.now()
        end_dt = datetime.fromisoformat(end_date) if end_date else datetime.now()
        
        # Call the fetch_all_metar function
        fetch_all_metar(icao, start_dt, end_dt, output_file)
        
        return jsonify({
            'success': True,
            'message': f'METAR data fetched successfully for {icao}',
            'output_file': output_file
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@web.route('/bar_chart')
def bar_chart():
    """Serve the bar chart HTML file"""
    try:
        return send_file('bar_chart.html', mimetype='text/html')
    except FileNotFoundError:
        return jsonify({'error': 'Bar chart file not found'}), 404

