import pandas as pd
import re
import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows

def generate_warning_report(ad_warn_output_path, metar_features_path):
    # Read warnings
    ad_warn_df = pd.read_csv(ad_warn_output_path, dtype={'Issue date/time': str})

    # Read extracted METAR features
    with open(metar_features_path, 'r') as f:
        metar_blocks = f.read().split('\nRow ')[1:]  # Split by each row block
        metar_blocks = ['Row ' + block for block in metar_blocks]

    # Compile regex for TS/TSRA variants
    TSRA_REGEX = re.compile(r'(TSRA|TS|FBL TSRA|MOD TSRA|HVY TSRA|MOD TS|FBL TS|HVY TS)', re.IGNORECASE)

    results = []

    for idx, row in ad_warn_df.iterrows():
        sl_no = idx + 1
        sig_wx = str(row.get('Significant Wx', ''))
        gust_val = str(row.get('Gust', ''))
        wind_dir_fcst = row.get('Wind dir (deg)', None)
        issue_time = str(row.get('Issue date/time', '')).zfill(6)
        station = str(row.get('Station', ''))
        validity_from = str(row.get('Validity from', ''))
        validity_to = str(row.get('Validity To', ''))
        true_false = 0
        remark = ''

        # Check for TS/TSRA and gust in warning
        has_tsra = bool(TSRA_REGEX.search(sig_wx))
        has_gust = bool(re.match(r'\d{2,3}KT', gust_val))

        # Find corresponding METAR block
        metar_block = next((b for b in metar_blocks if f'Row {sl_no}:' in b), None)
        metar_lines = metar_block.split('\n') if metar_block else []

        # If the block says FCST/OBS is OBS, skipping extraction
        if metar_block and 'FCST/OBS is OBS, skipping extraction.' in metar_block:
            true_false = 1
            # Elements logic for OBS rows (just reflect the warning forecast)
            if has_gust and has_tsra:
                elements = 'Gust & Thunderstorm warning'
            elif has_gust:
                elements = 'Gust warning'
            elif has_tsra:
                elements = 'Thunderstorm warning'
            else:
                elements = ''
            remark = 'OBS'
            results.append([sl_no, elements, issue_time, true_false, remark, station, validity_from, validity_to])
            continue

        found_gust = False
        found_dir = False
        found_cb = False
        gust_reported = ''
        dir_reported = ''
        cb_reported = ''
        tsra_reported = ''
        cb_cloud_group = ''

        for line in metar_lines:
            # Gust
            gust_match = re.search(r'Gust: (\d+)', line)
            if gust_match:
                metar_gust = int(gust_match.group(1))
                # Wind Dir
                dir_match = re.search(r'Wind Dir: (\d+)', line)
                if dir_match and wind_dir_fcst:
                    metar_dir = int(dir_match.group(1))
                    try:
                        fcst_dir = int(wind_dir_fcst)
                        if abs(metar_dir - fcst_dir) <= 30:
                            found_gust = True
                            found_dir = True
                            gust_reported = f'{metar_gust}KT'
                            dir_reported = f'{metar_dir}'
                    except Exception:
                        pass
            # CB cloud detection from Clouds list
            clouds_match = re.search(r"Clouds: \[(.*?)\]", line)
            if clouds_match:
                clouds_list = [c.strip().strip("'") for c in clouds_match.group(1).split(',')]
                cb_groups = [c for c in clouds_list if 'CB' in c]
                if cb_groups:
                    found_cb = True
                    cb_reported = 'CB'
                    cb_cloud_group = cb_groups[0]  # Take the first CB group found
            # TSRA
            if re.search(r'TSRA', line):
                tsra_reported = 'TSRA'

        # Elements logic for FCST rows (based on METAR evidence)
        elements = ''
        if found_gust and found_cb:
            elements = 'Gust & Thunderstorm warning'
        elif found_gust:
            elements = 'Gust warning'
        elif found_cb:
            elements = 'Thunderstorm warning'

        # Logic for true/false and remarks (unchanged)
        if has_gust and not has_tsra:
            if found_gust and found_dir:
                true_false = 1
                remark = f'Gust {gust_reported} Dir {dir_reported} matched'
                if cb_cloud_group:
                    remark += f' {cb_cloud_group} found'
            else:
                remark = 'No gust/direction mismatch'
        elif has_gust and has_tsra:
            if found_gust and found_dir:
                true_false = 1
                remark = f'Gust {gust_reported} Dir {dir_reported} matched'
                if cb_cloud_group:
                    remark += f' {cb_cloud_group} found'
            elif found_cb:
                true_false = 1
                remark = ''
                if cb_cloud_group:
                    remark += f' {cb_cloud_group} found'
            else:
                remark = 'Missing CB or direction mismatch'
        elif has_tsra:
            if found_cb:
                true_false = 1
                remark = ''
                if cb_cloud_group:
                    remark += f' {cb_cloud_group} found'
            else:
                remark = 'Missing CB or direction mismatch'
        else:
            remark = 'No significant weather matched'
        
        if not elements:
            if has_gust and has_tsra:
                elements = 'Gust & Thunderstorm warning'
            elif has_gust:
                elements = 'Gust warning'
            elif has_tsra:
                elements = 'Thunderstorm warning'

        results.append([sl_no, elements, issue_time, true_false, remark, station, validity_from, validity_to])

    # Output report
    final_df = pd.DataFrame(results, columns=[
        'Sl. No.',
        'Elements (Thunderstorm/Surface wind & Gust)',
        'Warning issue Time',
        'true-1 / false-0',
        'Remarks',
        'Station',
        'Validity From',
        'Validity To'
    ])
    
    # Add additional columns for better parsing
    final_df['Accuracy_Percentage'] = final_df['true-1 / false-0'].apply(lambda x: f"{x*100}%" if x == 1 else "0%")
    final_df['Warning_Type'] = final_df['Elements (Thunderstorm/Surface wind & Gust)'].apply(
        lambda x: 'Thunderstorm' if 'thunderstorm' in x.lower() else 
                  'Wind' if 'wind' in x.lower() or 'gust' in x.lower() else 'Other'
    )
    
    # Save to a file in the same directory as the input file
    output_path = os.path.join(os.path.dirname(ad_warn_output_path), 'final_warning_report.csv')
    final_df.to_csv(output_path, index=False)
    print('Report saved as final_warning_report.csv')

    # Calculate percentage correct
    total = len(final_df)
    correct = final_df['true-1 / false-0'].sum()
    
    try:
        df_gust = final_df[final_df['Elements (Thunderstorm/Surface wind & Gust)'] == 'Gust warning']
        gust = df_gust['true-1 / false-0'].sum()
        total_gust = len(df_gust)
        df_tsra = final_df[final_df['Elements (Thunderstorm/Surface wind & Gust)'] == 'Thunderstorm warning']
        tsra = df_tsra['true-1 / false-0'].sum()
        total_tsra = len(df_tsra)

        if total > 0:
            percent = (correct / total) * 100
            print(f'Aerodrome Warning : {percent:.0f} % accurate')
        if total_gust > 0:
            percent_gust = (gust / total_gust) * 100
            print(f'Gust warning : {percent_gust:.0f} % accurate')
        if total_tsra > 0:
            percent_tsra = (tsra / total_tsra) * 100
            print(f'Thunderstorm warning : {percent_tsra:.0f} % accurate')
        else:
            print('No warnings to evaluate.')
    except Exception as e:
        print('Could not calculate accuracy:', e)

    # Return the overall accuracy for the API
    accuracy = (correct / total) * 100 if total > 0 else 0
    return final_df, accuracy

def generate_excel_warning_report(ad_warn_output_path, metar_features_path):
    """
    Generate Excel file with the specific format requested:
    1. Tropical cyclone
    2. Thunderstorms
    3. Hail
    4. Snow
    5. Freezing precipitation
    6. Hoar Frost or rime
    7. Dust storm
    8. Sandstorm
    9. Rising sand or dust
    10. Strong surface wind and gusts / Speed
    11. Direction change
    12. Squall
    13. Volcanic ash
    14. Tsunami
    """
    # Read warnings
    ad_warn_df = pd.read_csv(ad_warn_output_path, dtype={'Issue date/time': str})

    # Read extracted METAR features
    with open(metar_features_path, 'r') as f:
        metar_blocks = f.read().split('\nRow ')[1:]  # Split by each row block
        metar_blocks = ['Row ' + block for block in metar_blocks]

    # Compile regex for TS/TSRA variants
    TSRA_REGEX = re.compile(r'(TSRA|TS|FBL TSRA|MOD TSRA|HVY TSRA|MOD TS|FBL TS|HVY TS)', re.IGNORECASE)

    # Predefined warning types
    warning_types = [
        "Tropical cyclone",
        "Thunderstorms", 
        "Hail",
        "Snow",
        "Freezing precipitation",
        "Hoar Frost or rime",
        "Dust storm",
        "Sandstorm",
        "Rising sand or dust",
        "Strong surface wind and gusts / Speed",
        "Direction change",
        "Squall",
        "Volcanic ash",
        "Tsunami"
    ]

    # Create workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Aerodrome Warning Report"

    # Define styles
    header_font = Font(bold=True, size=12)
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Add headers
    headers = ["Sl. No.", "Warning Type", "Issue Time", "Status", "Remarks"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True, color="FFFFFF", size=12)
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border

    # Set column widths
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 35
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 10
    ws.column_dimensions['E'].width = 50

    # Analyze the warning data to extract gust and TSRA information
    thunderstorm_data = []
    gust_data = []
    direction_data = []
    
    for idx, row in ad_warn_df.iterrows():
        sl_no = idx + 1
        sig_wx = str(row.get('Significant Wx', ''))
        gust_val = str(row.get('Gust', ''))
        wind_dir_fcst = row.get('Wind dir (deg)', None)
        issue_time = str(row.get('Issue date/time', '')).zfill(6)
        
        # Check for TS/TSRA in warning
        has_tsra = bool(TSRA_REGEX.search(sig_wx))
        has_gust = bool(re.match(r'\d{2,3}KT', gust_val))
        
        if has_tsra:
            thunderstorm_data.append({
                'sl_no': sl_no,
                'issue_time': issue_time,
                'sig_wx': sig_wx
            })
        
        if has_gust:
            gust_data.append({
                'sl_no': sl_no,
                'issue_time': issue_time,
                'gust': gust_val
            })
        
        if wind_dir_fcst is not None:
            direction_data.append({
                'sl_no': sl_no,
                'issue_time': issue_time,
                'direction': wind_dir_fcst
            })

    row_num = 2
    for idx, warning_type in enumerate(warning_types, 1):
        # Initialize default values
        issue_time = ""
        status = "Not Applicable"
        remarks = ""
        
        # Check if this warning type is relevant based on the data
        if warning_type == "Thunderstorms":
            if thunderstorm_data:
                issue_time = thunderstorm_data[0]['issue_time']
                status = "Active"
                remarks = f"Thunderstorm warnings detected: {len(thunderstorm_data)} instances"
                if len(thunderstorm_data) > 1:
                    remarks += f" (First at {thunderstorm_data[0]['issue_time']}, Last at {thunderstorm_data[-1]['issue_time']})"
            else:
                status = "Not Active"
                remarks = "No thunderstorm warnings found in data"
                
        elif warning_type == "Strong surface wind and gusts / Speed":
            if gust_data:
                issue_time = gust_data[0]['issue_time']
                status = "Active"
                remarks = f"Gust warnings detected: {len(gust_data)} instances"
                if len(gust_data) > 1:
                    remarks += f" (First at {gust_data[0]['issue_time']}, Last at {gust_data[-1]['issue_time']})"
                # Add specific gust values
                gust_values = [item['gust'] for item in gust_data]
                remarks += f" - Gust values: {', '.join(gust_values)}"
            else:
                status = "Not Active"
                remarks = "No gust warnings found in data"
                
        elif warning_type == "Direction change":
            if direction_data:
                issue_time = direction_data[0]['issue_time']
                status = "Active"
                remarks = f"Wind direction warnings detected: {len(direction_data)} instances"
                if len(direction_data) > 1:
                    remarks += f" (First at {direction_data[0]['issue_time']}, Last at {direction_data[-1]['issue_time']})"
                # Add specific direction values
                direction_values = [str(item['direction']) for item in direction_data]
                remarks += f" - Directions: {', '.join(direction_values)}"
            else:
                status = "Not Active"
                remarks = "No wind direction warnings found in data"
        
        # Add row to worksheet
        ws.cell(row=row_num, column=1, value=idx).border = border
        ws.cell(row=row_num, column=2, value=warning_type).border = border
        ws.cell(row=row_num, column=3, value=issue_time).border = border
        ws.cell(row=row_num, column=4, value=status).border = border
        ws.cell(row=row_num, column=5, value=remarks).border = border
        
        # Apply conditional formatting for status
        status_cell = ws.cell(row=row_num, column=4)
        if status == "Active":
            status_cell.fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
            status_cell.font = Font(color="FFFFFF", bold=True)
        elif status == "Not Active":
            status_cell.fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")
            status_cell.font = Font(color="000000", bold=True)
        else:
            status_cell.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
            status_cell.font = Font(color="000000", bold=True)
        
        row_num += 1

    # Save the Excel file
    output_path = os.path.join(os.path.dirname(ad_warn_output_path), 'aerodrome_warning_report.xlsx')
    wb.save(output_path)
    print(f'Excel report saved as {output_path}')
    
    return output_path 