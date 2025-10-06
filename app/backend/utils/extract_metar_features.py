import pandas as pd
import re
import os

def get_metar_time_group(metar):
    # Extract the 6-digit time group (DDHHMM) from METAR (e.g., 231105 from 231105Z)
    match = re.search(r'\b(\d{6})Z\b', metar)
    if match:
        return match.group(1)
    # If not found, try to extract from full timestamp (e.g., 202309231105)
    match_full = re.match(r'(\d{8})(\d{4})', metar)
    if match_full:
        # Use DDHHMM from the timestamp
        date_part = match_full.group(1)  # YYYYMMDD
        time_part = match_full.group(2)  # HHMM
        dd = date_part[-2:]
        hhmm = time_part
        return f"{dd}/{hhmm}"
    return None

def extract_metar_features(ad_warn_output_path, metar_file_path, output_path):
    """
    Extract METAR features from the METAR file based on warning validity periods.
    
    Args:
        ad_warn_output_path (str): Path to the AD warning output CSV file
        metar_file_path (str): Path to the METAR text file
        output_path (str): Path where to save the extracted features
    """
    # Read warnings
    ad_warn_df = pd.read_csv(ad_warn_output_path)

    # Read METAR lines
    with open(metar_file_path, 'r') as f:
        metar_lines = [line.strip() for line in f if line.strip()]

    with open(output_path, 'w') as out:
        for idx, row in enumerate(ad_warn_df.iterrows()):
            fcst_obs = str(row[1].get('FCST/OBS', '')).strip().upper()
            if fcst_obs != 'FCST':
                out.write(f'\nRow {idx+1}: FCST/OBS is {fcst_obs}, skipping extraction.\n')
                continue
            validity_from = str(row[1].get('Validity from', '')).replace('Z', '')[-6:]  # always last 6 digits
            validity_to = str(row[1].get('Validity To', '')).replace('Z', '')[-6:]      # always last 6 digits
            out.write(f'\nRow {idx+1}: Validity {validity_from} to {validity_to}\n')
            extracting = False
            wrapped = False
            if int(validity_to) < int(validity_from):
                wrapped = True
            for i, metar in enumerate(metar_lines):
                metar_time = get_metar_time_group(metar)
                if not metar_time:
                    continue
                # WRAP-AROUND: extract from validity_from to end, then from start to validity_to
                if wrapped:
                    if not extracting and int(metar_time) >= int(validity_from):
                        extracting = True
                    if extracting:
                        wind_match = re.search(r' (\d{3})(\d{2})(G(\d{2,3}))?KT', metar)
                        wind_dir = int(wind_match.group(1)) if wind_match else None
                        wind_gust = int(wind_match.group(4)) if wind_match and wind_match.group(4) else None
                        clouds = re.findall(r'(FEW\d{3}(?:CB|TCU)?|SCT\d{3}(?:CB|TCU)?|BKN\d{3}(?:CB|TCU)?|OVC\d{3}(?:CB|TCU)?)', metar)
                        out.write(f'  METAR: {metar}\n')
                        out.write(f'    Wind Dir: {wind_dir}, Gust: {wind_gust}, Clouds: {clouds}\n')
                    # If we reach the end, continue from the start
                    if extracting and i == len(metar_lines) - 1:
                        for j, metar2 in enumerate(metar_lines):
                            metar_time2 = get_metar_time_group(metar2)
                            if not metar_time2:
                                continue
                            if int(metar_time2) <= int(validity_to):
                                wind_match = re.search(r' (\d{3})(\d{2})(G(\d{2,3}))?KT', metar2)
                                wind_dir = int(wind_match.group(1)) if wind_match else None
                                wind_gust = int(wind_match.group(4)) if wind_match and wind_match.group(4) else None
                                clouds = re.findall(r'(FEW\d{3}(?:CB|TCU)?|SCT\d{3}(?:CB|TCU)?|BKN\d{3}(?:CB|TCU)?|OVC\d{3}(?:CB|TCU)?)', metar2)
                                out.write(f'  METAR: {metar2}\n')
                                out.write(f'    Wind Dir: {wind_dir}, Gust: {wind_gust}, Clouds: {clouds}\n')
                            if int(metar_time2) == int(validity_to):
                                break
                        break
                # NORMAL: extract from >= validity_from to <= validity_to
                else:
                    if not extracting and int(metar_time) >= int(validity_from):
                        extracting = True
                    if extracting:
                        wind_match = re.search(r' (\d{3})(\d{2})(G(\d{2,3}))?KT', metar)
                        wind_dir = int(wind_match.group(1)) if wind_match else None
                        wind_gust = int(wind_match.group(4)) if wind_match and wind_match.group(4) else None
                        clouds = re.findall(r'(FEW\d{3}(?:CB|TCU)?|SCT\d{3}(?:CB|TCU)?|BKN\d{3}(?:CB|TCU)?|OVC\d{3}(?:CB|TCU)?)', metar)
                        out.write(f'  METAR: {metar}\n')
                        out.write(f'    Wind Dir: {wind_dir}, Gust: {wind_gust}, Clouds: {clouds}\n')
                    if extracting and int(metar_time) > int(validity_to):
                        break
    
    return output_path 