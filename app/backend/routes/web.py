from flask import Blueprint, render_template, request, jsonify, send_file,make_response
from app.backend.utils.ogimet_adwarn import OgimetAPIAdWarn
from datetime import datetime
import os
import shutil
from app.backend.config import METAR_DATA_DIR, AD_WARN_DIR


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
                
                # Use OgimetAPIAdWarn to fetch METAR data with timestamp prefix
                api = OgimetAPIAdWarn()
                metar_result_path = api.save_metar_to_file(
                    begin=start_dt.strftime("%Y%m%d%H%M"),
                    end=end_dt.strftime("%Y%m%d%H%M"),
                    icao=icao
                )

                # Determine candidate METAR file: prefer metar_result_path if present,
                # otherwise pick the most recently modified file in configured METAR_DATA_DIR.
                chosen_file = None
                if metar_result_path and os.path.exists(metar_result_path):
                    chosen_file = metar_result_path
                else:
                    try:
                        # Prefer files in AD_WARN_DIR (aerodrome warning workspace)
                        files = [
                            os.path.join(AD_WARN_DIR, f) for f in os.listdir(AD_WARN_DIR)
                            if os.path.isfile(os.path.join(AD_WARN_DIR, f))
                        ]
                        if files:
                            chosen_file = max(files, key=os.path.getmtime)
                        else:
                            # fallback to METAR_DATA_DIR if AD_WARN_DIR empty
                            files = [
                                os.path.join(METAR_DATA_DIR, f) for f in os.listdir(METAR_DATA_DIR)
                                if os.path.isfile(os.path.join(METAR_DATA_DIR, f))
                            ]
                            if files:
                                chosen_file = max(files, key=os.path.getmtime)
                    except Exception:
                        chosen_file = None

                # Fallback: if nothing found in METAR_DATA_DIR, try current working dir
                if not chosen_file:
                    try:
                        cwd_files = [os.path.join(os.getcwd(), f) for f in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), f))]
                        if cwd_files:
                            chosen_file = max(cwd_files, key=os.path.getmtime)
                    except Exception:
                        chosen_file = None

                # Copy the chosen file into AD_WARN_DIR as 'metar.txt' so downstream APIs can find it
                if chosen_file and os.path.exists(chosen_file):
                    os.makedirs(AD_WARN_DIR, exist_ok=True)
                    dest = os.path.join(AD_WARN_DIR, 'metar.txt')
                    shutil.copy2(chosen_file, dest)
                    file_path = dest
                else:
                    file_path = None
                
                # Read the generated file to show preview
                try:
                    if file_path and os.path.exists(file_path):
                        print(f"[DEBUG] Chosen METAR file for preview: {file_path}")
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                            metar_preview = file_content
                    else:
                        metar_preview = "METAR data fetched (no file available for preview)"
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
        
        # Use OgimetAPIAdWarn to fetch METAR data with timestamp prefix
        api = OgimetAPIAdWarn()
        metar_result_path = api.save_metar_to_file(
            begin=start_dt.strftime("%Y%m%d%H%M"),
            end=end_dt.strftime("%Y%m%d%H%M"),
            icao=icao
        )

        # Determine candidate METAR file: prefer metar_result_path if present,
        # otherwise pick the most recently modified file in configured METAR_DATA_DIR.
        chosen_file = None
        if metar_result_path and os.path.exists(metar_result_path):
            chosen_file = metar_result_path
        else:
            try:
                files = [
                    os.path.join(METAR_DATA_DIR, f) for f in os.listdir(METAR_DATA_DIR)
                    if os.path.isfile(os.path.join(METAR_DATA_DIR, f))
                ]
                if files:
                    chosen_file = max(files, key=os.path.getmtime)
            except Exception:
                chosen_file = None

        # Fallback to cwd
        if not chosen_file:
            try:
                cwd_files = [os.path.join(os.getcwd(), f) for f in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), f))]
                if cwd_files:
                    chosen_file = max(cwd_files, key=os.path.getmtime)
            except Exception:
                chosen_file = None

        # Copy chosen file into METAR_DATA_DIR with requested output_file name
        if chosen_file and os.path.exists(chosen_file):
            os.makedirs(METAR_DATA_DIR, exist_ok=True)
            dest_path = os.path.join(METAR_DATA_DIR, output_file)
            shutil.copy2(chosen_file, dest_path)
            print(f"[DEBUG] Copied chosen METAR file {chosen_file} -> {dest_path}")
        
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
    """Run combined_graph.py and serve the generated chart"""
    try:
        import subprocess
        import sys

        # script path in the same folder as this web.py
        script_path = os.path.join(os.path.dirname(__file__), 'combined_graph.py')

        if not os.path.exists(script_path):
            return jsonify({'error': 'combined_graph.py script not found'}), 404

        # Run the combined_graph.py script with cwd = script dir so output lands next to script
        result = subprocess.run([sys.executable, script_path],
                                capture_output=True, text=True,
                                cwd=os.path.dirname(script_path))

        if result.returncode == 0:
            # Chart file expected in the same folder as script
            chart_file = os.path.join(os.path.dirname(script_path), 'combined_accuracy_chart.html')

            if os.path.exists(chart_file):
                # Serve file without conditional caching and set no-cache headers
                resp = make_response(send_file(chart_file, mimetype='text/html', conditional=False))
                resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
                resp.headers['Pragma'] = 'no-cache'
                resp.headers['Expires'] = '0'
                return resp
            else:
                return jsonify({'error': 'Chart file not generated'}), 500
        else:
            error_msg = result.stderr if result.stderr else 'Unknown script error'
            return jsonify({'error': f'Script execution failed: {error_msg}'}), 500

    except Exception as e:
        return jsonify({'error': f'Error generating chart: {str(e)}'}), 500
