import pandas as pd
import re
import os

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
            results.append([sl_no, elements, issue_time, true_false, remark])
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

        results.append([sl_no, elements, issue_time, true_false, remark])

    # Output report
    final_df = pd.DataFrame(results, columns=[
        'Sl. No.',
        'Elements (Thunderstorm/Surface wind & Gust)',
        'Warning issue Time',
        'true-1 / false-0',
        'Remarks'
    ])
    
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