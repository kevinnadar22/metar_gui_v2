import pandas as pd
import re
import os

def parse_warning_file(filepath, station_code=None):
    pd.set_option('display.max_rows', None)

    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    data = []
    i = 0
    while i < len(lines):
        if re.search(r"\bWRNG\b", lines[i]) or re.search(r"\bWARNING\b", lines[i]):
            # Move to next non-header line
            while i + 1 < len(lines) and not re.search(r"\bAD WRNG\b", lines[i + 1]):
                i += 1
            i += 1
            if i >= len(lines):
                break

            main_line = lines[i]
            main_parts = main_line.split()
            print(main_parts)
            if len(main_parts) < 2:
                i += 1
                continue
            station = main_parts[0]
            issue_time = main_parts[1]
            validity_from, validity_to = "", ""
            valid_match = re.search(r"VALID\s*(\d{6,8})/(\d{6,8})", main_line)
            if valid_match:
                validity_from = f"{valid_match.group(1)}Z"
                validity_to = f"{valid_match.group(2)}Z"

            i += 1
            if i >= len(lines): break
            wx_line = lines[i]

            wind_dir_dict = {
                "N": 0, "NNE": 20, "NE": 50, "ENE": 70,
                "E": 90, "ESE": 110, "SE": 140, "SSE": 160,
                "S": 180, "SSW": 200, "SW": 230, "WSW": 250,
                "W": 270, "WNW": 290, "NW": 320, "NNW": 340,
                "WEST": 270, "EAST": 90, "SOUTH": 180, "NORTH": 0
            }

            wind_speed_match = re.search(r"SFC WSPD (\d+KT)", wx_line)
            wind_speed = wind_speed_match.group(1) if wind_speed_match else ""

            gust_match = re.search(r"MAX(\d+)", wx_line)
            gust = f"{gust_match.group(1)}KT" if gust_match else ""

            wind_dir_match = re.search(r"FROM\s+([A-Z]+)", wx_line)
            wind_dir_str = wind_dir_match.group(1) if wind_dir_match else ""
            wind_dir = wind_dir_str
            wind_dir_num = wind_dir_dict.get(wind_dir_str, "")

            sig_wx = ""
            wx_patterns = {
                "HVY TSRA": "+TSRA", "FBL TSRA": "-TSRA", "MOD TSRA": "TSRA", "TSRA": "TSRA",
                "HVY TS": "+TS", "FBL TS": "-TS", "MOD TS": "TS", "TS": "TS"
            }
            for pattern, code in wx_patterns.items():
                if pattern in wx_line:
                    sig_wx = code
                    break

            fcst_obs = "FCST" if "FCST" in wx_line else "OBS" if "OBS" in wx_line or "OBSD" in wx_line else ""

            data.append({
                "Station": station,
                "Issue date/time": issue_time,
                "Validity from": validity_from,
                "Validity To": validity_to,
                "Wind dir (deg)": wind_dir_num,
                "Wind Speed": wind_speed,
                "Gust": gust,
                "Significant Wx": sig_wx,
                "FCST/OBS": fcst_obs
            })
        i += 1

    df = pd.DataFrame(data)

    def round_down_to_half_hour(timestr):
        z = 'Z' if timestr.endswith('Z') else ''
        timestr = timestr.rstrip('Z')
        if len(timestr) < 4: return timestr + z
        prefix, hhmm = timestr[:-4], timestr[-4:]
        hour, minute = int(hhmm[:2]), int(hhmm[2:])
        minute = 0 if minute < 30 else 30
        return f"{prefix}{hour:02d}{minute:02d}{z}"

    def round_up_to_next_half_hour(timestr):
        z = 'Z' if timestr.endswith('Z') else ''
        timestr = timestr.rstrip('Z')
        if len(timestr) < 4: return timestr + z
        
        # Handle case where prefix contains day information (e.g., "13" from "132345")
        if len(timestr) >= 6:  # Format like "132345" or "132345Z"
            day = int(timestr[:2])
            hour, minute = int(timestr[2:4]), int(timestr[4:6])
        else:  # Format like "2345" or "2345Z"
            day = 1  # Default day
            hour, minute = int(timestr[-4:-2]), int(timestr[-2:])
        
        if minute == 0 or minute == 30:
            return timestr + z
        elif minute < 30:
            minute = 30
        else:
            hour = (hour + 1) % 24
            minute = 0
            # If hour rolled over to 00, increment the day
            if hour == 0:
                day = (day % 30) + 1  # Assuming 30 days max, adjust if needed
        
        # Format the result based on original format
        if len(timestr) >= 6:
            return f"{day:02d}{hour:02d}{minute:02d}{z}"
        else:
            return f"{hour:02d}{minute:02d}{z}"

    def fix_2400(timestr):
        z = 'Z' if timestr.endswith('Z') else ''
        timestr = timestr.rstrip('Z')
        
        # Handle case where time is "2400" (should become "0000" of next day)
        if timestr.endswith('2400'):
            if len(timestr) >= 6:  # Format like "132400"
                day = int(timestr[:2])
                # Extract prefix (everything before the day)
                prefix = timestr[:-6]
                new_day = (day % 30) + 1  # Increment day, assuming 30 days max
                return f"{prefix}{new_day:02d}0000{z}"
            else:  # Format like "2400"
                return f"0000{z}"
        
        return timestr + z

    df["Validity from"] = df["Validity from"].astype(str).apply(round_down_to_half_hour).apply(fix_2400)
    df["Validity To"] = df["Validity To"].astype(str).apply(round_up_to_next_half_hour).apply(fix_2400)
    df["Issue date/time"] = df["Issue date/time"].apply(
    lambda val: f"{val[:2]}/{val[2:-1]}" if isinstance(val, str) and val.endswith('Z') else (
        f"{val[:2]}/{val[2:]}" if isinstance(val, str) else val
    )
)
    # Only filter by station code if it's provided
    if station_code:
        df = df[df["Station"] == station_code].reset_index(drop=True)
    df["Wind dir (deg)"] = pd.to_numeric(df["Wind dir (deg)"], errors="coerce").astype("Int64")

    # Save to a file in the same directory as the input file
    output_path = os.path.join(os.path.dirname(filepath), 'AD_warn_output.csv')
    df.to_csv(output_path, index=True)
    return df