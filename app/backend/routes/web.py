from flask import Blueprint, render_template, request, jsonify, send_file,make_response,redirect
from app.backend.utils.ogimet_adwarn import OgimetAPIAdWarn
from datetime import datetime
import os
import shutil
from app.backend.config import METAR_DATA_DIR, AD_WARN_DIR, DOCKER_VOLUME_MOUNT_POINT
from app.backend.auth import get_current_user, require_role

web = Blueprint('web', __name__)

@web.route('/login')
def login_page():
    return render_template('login.html')


@web.route('/signup')
def signup_page():
    return render_template('signup.html')

@web.route('/admin')
@require_role("admin")
def admin_dashboard(current_user):
    return render_template("admin.html")

@web.route('/superadmin')
@require_role("super_admin")
def superadmin_dashboard(current_user):
    return render_template("superadmin.html")

@web.route('/', methods=['GET', 'POST'])
def home():
    user = get_current_user()
    if not user:
        return redirect("/login")
    if request.method == 'POST':
        try:
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
                
                api = OgimetAPIAdWarn()
                metar_result_path = api.save_metar_to_file(
                    begin=start_dt.strftime("%Y%m%d%H%M"),
                    end=end_dt.strftime("%Y%m%d%H%M"),
                    icao=icao
                )

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
    """
    Generate the combined accuracy chart directly here (no external script).
    """
    try:
        import pandas as pd
        import plotly.graph_objects as go
        import re
        import os

        # Paths
        ad_warn_dir = os.path.join(DOCKER_VOLUME_MOUNT_POINT, 'ad_warn_data')
        report_csv = os.path.join(ad_warn_dir, 'final_warning_report.csv')
        output_chart = os.path.join(ad_warn_dir, 'combined_accuracy_chart.html')

        # Ensure report exists
        if not os.path.exists(report_csv):
            return jsonify({'error': 'Final warning report not found. Run ADWRN verify first.'}), 404

        # Read first line (station header)
        with open(report_csv, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()

        # Extract month name
        month_match = re.search(r'for (\w+) \d{4}', first_line)
        month_name = month_match.group(1) if month_match else "Unknown Month"

        # Load CSV skipping the first station_info line
        df = pd.read_csv(report_csv, skiprows=1)

        # Normalize column names
        df.columns = df.columns.str.strip()
        df.rename(columns={
            'Warning issue Time': 'Warning_issue_Time',
            'true-1 / false-0': 'Is_Correct',
        }, inplace=True)

        # Ensure required columns exist
        required = ['Warning_issue_Time', 'Warning_Type', 'Is_Correct']
        if not all(c in df.columns for c in required):
            return jsonify({'error': 'CSV missing required columns for graph generation.'}), 500

        # Extract day from warning time (e.g., "03/1200" → 3)
        df['Day'] = df['Warning_issue_Time'].astype(str).str.split('/').str[0].astype(int)

        # Filter valid warning types
        df = df[df['Warning_Type'].isin(['Thunderstorm', 'Wind'])]

        # Group by day + warning type
        grouped = df.groupby(['Day', 'Warning_Type'])['Is_Correct'].agg(
            correct='sum',
            total='count'
        ).reset_index()

        grouped['Accuracy'] = (grouped['correct'] / grouped['total']) * 100

        df_thunder = grouped[grouped['Warning_Type'] == 'Thunderstorm']
        df_wind = grouped[grouped['Warning_Type'] == 'Wind']

        # Create Plotly chart
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=df_thunder["Day"],
                y=df_thunder["Accuracy"],
                name="Thunderstorm",
                text=df_thunder["Accuracy"],
                texttemplate="%{y:.1f}%",
                textposition="outside",
                marker=dict(
                    color=df_thunder["Accuracy"],
                    colorscale="Blues",
                    showscale=True,
                    colorbar=dict(
                        title="TS Accuracy",
                        x=1.14,          # Position on far right
                        thickness=15,
                        len=0.75
                    )
                )
            )
        )


        fig.add_trace(
            go.Bar(
                x=df_wind["Day"],
                y=df_wind["Accuracy"],
                name="Wind",
                text=df_wind["Accuracy"],
                texttemplate="%{y:.1f}%",
                textposition="outside",
                marker=dict(
                    color=df_wind["Accuracy"],
                    colorscale="Reds",
                    showscale=True,
                    colorbar=dict(
                        title="Gust Accuracy",
                        x=1.02,          # Closer to the bars
                        thickness=15,
                        len=0.75
                    )
                )
            )
        )

        fig.update_layout(

            title=dict(
                text=(
                    f"Daily Accuracy of Thunderstorm and Gust Warning "
                    f"for the Month of {month_name}"
                ),
                x=0.5,
                xanchor="center",
                y=0.95,
                yanchor="top",
                font=dict(size=20, family="Arial Black")
            ),

        
            xaxis_title="Day",
            yaxis_title="Accuracy (%)",

            # Axis Limits
            yaxis=dict(range=[0, 110]),

            # Group bars side-by-side
            barmode="group",

            
            plot_bgcolor="#d9d9d9",   # Inner plot background
            # paper_bgcolor="#d9d9d9",  # Overall page background

            # Global font
            font=dict(size=14),

            legend=dict(
                title="Warning Type",
                x=0.02,
                y=0.98,
                bgcolor="rgba(255, 255, 255, 0.6)",
                bordercolor="black",
                borderwidth=1
            ),

            
            width=1500,
            height=675,

            margin=dict(l=50, r=200, t=120, b=50)
        )


        fig.write_html(output_chart)


        print(f"[DEBUG] Combined accuracy chart generated → {output_chart}")

        return send_file(output_chart, mimetype='text/html')

    except Exception as e:
        print("[ERROR] Error generating chart:", e)
        return jsonify({'error': str(e)}), 500

