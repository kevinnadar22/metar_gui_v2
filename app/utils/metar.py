import metar.Metar as mt
import pandas as pd
import re
from datetime import datetime

def clean_metar_inplace(file_path):
    """
    Cleans METAR data by removing trailing '=' characters and newlines.

    Args:
        file_path (str): Path to the METAR file to clean.
    """
    with open(file_path, "r") as infile:
        lines = infile.readlines()

    with open(file_path, "w") as outfile:
        for line in lines:
            outfile.write(line.rstrip("=\n") + "\n")

    print("METAR data cleaned in place.")


def decode_metar_to_csv(input_file, output_file):
    try:
        with open(input_file, "r") as file:
            metar_text = file.read().strip()

        metar_reports = re.split(r"\nMETAR ", metar_text)
        data_list = []

        for metar_code in metar_reports:
            metar_code = metar_code.strip()
            if not metar_code:
                continue

            if not metar_code.startswith("METAR"):
                metar_code = "METAR " + metar_code

            nosig_present = "NOSIG" in metar_code
            metar_code = metar_code.replace("NOSIG", "")

            try:
                report = mt.Metar(metar_code, month=9)
                # Adjust the observation date safely
                # corrected_time = adjust_metar_date(report.time.day)
                # print("corrected_time = ", corrected_time)

                data = {
                    # "Station": getattr(report, "station", "Mumbai/Chhatrapati Shivaji Intl"),
                    # "Location": getattr(report, "name", "India 19.07N 072.51E"),
                    "DAY": report.time.strftime("%d"),
                    "TIME": f"{report.time.hour:02}{report.time.minute:02}Z",
                    # "Wind Speed (m/s)": report.wind_speed.value("MPS") if report.wind_speed else "N/A",
                    "WIND_DIR": report.wind_dir.value() if report.wind_dir else "N/A",
                    "WIND_SPEED": (
                        report.wind_speed.value("KT") if report.wind_speed else "N/A"
                    ),
                    # "Visibility (m)": report.vis.value() if report.vis else "N/A",
                    # "Present Weather": report.present_weather() if report.present_weather() else "None",
                    # "Clouds": report.sky_conditions() if report.sky_conditions() else "No Significant Cloud",
                    "TEMP": report.temp.value("C") if report.temp else "N/A",
                    # "Dew-Point Temperature (°C)": report.dewpt.value("C") if report.dewpt else "N/A",
                    "QNH": report.press.value("hPa") if report.press else "N/A",
                    # "Significant Change": "No significant change" if nosig_present else metar_code.split()[-1],
                }

                data_list.append(data)

            except Exception as e:
                pass
                # print(f"Error decoding METAR: {e}\nProblematic METAR: {metar_code}")

        df = pd.DataFrame(data_list)
        df.to_csv(output_file, index=False)
        # print(df)
        print(f"Decoded METAR data saved to {output_file}")
        return df
    except Exception as e:
        print(f"Error processing METAR file: {e}")


def extract_wind_data(wind_str):
    """
    Extracts wind direction and speed from a wind string, handling various formats.
    """
    # Format with slash and KT (e.g., "310/05KT")
    match = re.match(r"(\d{3})/(\d{2})KT", wind_str)
    if match:
        return int(match.group(1)), int(match.group(2))

    # Format with digits and KT (e.g., "35005KT")
    match = re.match(r"(\d{3})(\d{2})KT", wind_str)
    if match:
        return int(match.group(1)), int(match.group(2))

    # Format with gust and KT (e.g., "28007G17KT")
    match = re.match(r"(\d{3})\d{2}G(\d{2})KT", wind_str)
    if match:
        return int(match.group(1)), int(match.group(2))

    # Variable wind with KT (e.g., "VRB02KT")
    match_vrb_kt = re.match(r"(VRB)(\d{2})KT", wind_str)
    if match_vrb_kt:
        return "N/A", int(match_vrb_kt.group(2))

    # Variable wind without KT, but with speed (e.g., "VRB05")
    match_vrb_no_kt = re.match(r"(VRB)(\d{2})", wind_str)
    if match_vrb_no_kt:
        return "N/A", int(match_vrb_no_kt.group(2))

    # Variable wind with slash and KT (e.g., "VRB/02KT") - might exist in some formats
    match_vrb_slash_kt = re.match(r"(VRB)/(\d{2})KT", wind_str)
    if match_vrb_slash_kt:
        return "N/A", int(match_vrb_slash_kt.group(2))

    # Variable wind with slash and no KT (e.g., "VRB/02") - might exist
    match_vrb_slash_no_kt = re.match(r"(VRB)/(\d{2})", wind_str)
    if match_vrb_slash_no_kt:
        return "N/A", int(match_vrb_slash_no_kt.group(2))

    # Handle just "VRB" with no speed information
    if "VRB" == wind_str:
        return "N/A", None

    # New format with slash and no KT (e.g., "320/07") - Keep this for numeric directions
    match_numeric_slash = re.match(r"(\d{3})/(\d{2})", wind_str)
    if match_numeric_slash:
        return int(match_numeric_slash.group(1)), int(match_numeric_slash.group(2))

    return None, None  # Return None, None if no match


# def extract_data_from_file_with_day_and_wind(file_path):
#     """
#     Extracts data from a file, including day, time, and separated wind direction/speed.

#     Args:
#         file_path (str): The path to the file.

#     Returns:
#         pandas.DataFrame: DataFrame with extracted data.
#     """

#     data = []
#     day = 1
#     try:
#         with open(file_path, "r") as file:
#             next(file)
#             for line in file:
#                 line = line.strip()
#                 if line:
#                     if re.match(r"^\d+$", line) and len(line) <= 2:
#                         day = int(line)
#                         continue
#                     match = re.match(r"(\d{4}Z)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)", line)
#                     if match:
#                         time, wind_str, temp, qfe, qnh = match.groups()
#                         wind_dir, wind_speed = extract_wind_data(wind_str)
#                         data.append(
#                             {
#                                 "DAY": day,
#                                 "TIME": time,
#                                 "WIND_DIR": wind_dir,
#                                 "WIND_SPEED": wind_speed,
#                                 "TEMP": int(temp),
#                                 "QFE": int(qfe),
#                                 "QNH": int(qnh),
#                             }
#                         )
#         return pd.DataFrame(data)
#     except FileNotFoundError:
#         print(f"Error: File not found at {file_path}")
#         return pd.DataFrame()
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return pd.DataFrame()

import os

def extract_data_from_file_with_day_and_wind(file_path):
    """
    Extracts data from a file, including day (from filename or file content), time,
    and separated wind direction/speed.

    Supports both daily and monthly forecast files.
    """
    data = []

    print(f"Processing file: {file_path}")

    filename = os.path.basename(file_path)
    print(f"Processing file: {filename}")
    day_from_name, month_from_name, year_from_name, _ = extract_day_month_year_from_filename(filename)
    print(f"Extracted from filename: Day={day_from_name}, Month={month_from_name}, Year={year_from_name}")

    # Decide strategy:
    # - daily files: use the day from filename
    # - monthly files: detect days inside file
    use_day_from_filename = bool(day_from_name and month_from_name and year_from_name and day_from_name != "01")
    current_day = int(day_from_name) if use_day_from_filename else None

    try:
        with open(file_path, "r") as file:
            lines = file.readlines()

            # Skip first line only if day is not from filename (monthly format often has headers)
            if not use_day_from_filename and lines:
                lines = lines[1:]

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # For monthly files, update current_day whenever we see a day marker (1, 2, … 31)
                if not use_day_from_filename and re.match(r"^\d{1,2}$", line):
                    current_day = int(line)
                    continue

                # Extract data rows like: 0000Z 09010KT 25 1009 1012
                match = re.match(r"(\d{4}Z)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)", line)
                if match:
                    time, wind_str, temp, qfe, qnh = match.groups()
                    wind_dir, wind_speed = extract_wind_data(wind_str)
                    data.append({
                        "DAY": current_day if current_day else 1,
                        "MONTH": month_from_name,
                        "YEAR": year_from_name,
                        "TIME": time,
                        "WIND_DIR": wind_dir,
                        "WIND_SPEED": wind_speed,
                        "TEMP": int(temp),
                        "QFE": int(qfe),
                        "QNH": int(qnh),
                    })

        return pd.DataFrame(data)

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()


def compare_wind_by_time(df1, df2):
    """
    Compares wind data from two DataFrames based on matching *first* 'TIME' values.
    Handles potential duplicates by keeping only the first occurrence of each time.

    Args:
        df1 (pd.DataFrame): Actual (METAR) data with 'TIME', 'WIND_DIR', 'WIND_SPEED'.
        df2 (pd.DataFrame): Forecast data with 'TIME', 'WIND_DIR', 'WIND_SPEED'.

    Returns:
        pd.DataFrame: Merged DataFrame with 'Accuracy' column.
    """

    if not isinstance(df1, pd.DataFrame) or not isinstance(df2, pd.DataFrame):
        print("Error: Input arguments must be Pandas DataFrames.")
        return pd.DataFrame()

    if "TIME" not in df1.columns or "TIME" not in df2.columns:
        print("Error: Both DataFrames must contain a 'TIME' column.")
        return pd.DataFrame()

    # Remove duplicate times, keeping the first occurrence
    df1_unique = df1.drop_duplicates(subset="TIME", keep="first")
    df2_unique = df2.drop_duplicates(subset="TIME", keep="first")

    merged_df = pd.merge(
        df1_unique,
        df2_unique,
        on="TIME",
        suffixes=("_actual", "_forecast"),
        how="inner",
    )

    if merged_df.empty:
        print("No matching times found between the DataFrames.")
        return pd.DataFrame()

    accuracy = []
    # save the merged_df to a csv file
    merged_df.to_csv("merged_df.csv", index=False)
    for _, row in merged_df.iterrows():
        actual_dir = row["WIND_DIR_actual"]
        actual_speed = row["WIND_SPEED_actual"]
        forecast_dir = row["WIND_DIR_forecast"]
        forecast_speed = row["WIND_SPEED_forecast"]

        dir_accurate = False
        speed_accurate = False

        if (
            actual_dir == "VRB"
            or forecast_dir == "VRB"
            or actual_dir is None
            or forecast_dir is None
        ):
            dir_accurate = True
        else:
            try:
                dir_diff = abs(int(forecast_dir) - int(actual_dir))
                dir_accurate = dir_diff <= 30 or dir_diff >= 330
            except (ValueError, TypeError):
                print("Invalid wind direction: ", forecast_dir, actual_dir)

        if actual_speed is not None and forecast_speed is not None:
            try:
                speed_accurate = abs(int(forecast_speed) - int(actual_speed)) <= 1
            except (ValueError, TypeError):
                print("Invalid wind speed: ", forecast_speed, actual_speed)
        else:
            print(f"Warning: Missing wind speed for TIME {row['TIME']}.")

        accuracy.append(
            "Accurate" if dir_accurate and speed_accurate else "Not Accurate"
        )

    merged_df["Accuracy"] = accuracy
    return merged_df


def circular_difference(dir1, dir2):
    """
    Calculates the minimum angular difference between two directions, considering circular wrap-around.
    """
    if (
        dir1 is None
        or dir2 is None
        or not isinstance(dir1, (int, float))
        or not isinstance(dir2, (int, float))
    ):
        return None  # Or raise an exception, depending on your error handling

    return min(abs(dir1 - dir2), 360 - (abs(dir1 - dir2)))


# def extract_day_month_year_from_filename(filename):
#     """
#     Extract day, month, and year from a filename following pattern like 'TAKEOFF_Forecast_12092023.txt'
#     or 'TAKEOFF_Forecast_092023' then return day as 01
    
#     Args:
#         filename (str): The filename to parse
        
#     Returns:
#         tuple: (day, month, year, day_month_year_str) where day_month_year_str is formatted as "DDMMYYYY"
#                Returns (None, None, None, None) if pattern not found
#     """
#     # Pattern: DDMMYYYY without separators
#     print(f"filename = {filename}")
#     match = re.search(r'(\d{2})(\d{2})(\d{4})\.txt$', filename)
#     if match:
#         day = match.group(1)
#         month = match.group(2)
#         year = match.group(3)
#         return day, month, year, f"{day}{month}{year}"
    
#     # Pattern: DD_MM_YYYY with underscores
#     match = re.search(r'(\d{2})_(\d{2})_(\d{4})\.txt$', filename)
#     if match:
#         day = match.group(1)
#         month = match.group(2)
#         year = match.group(3)
#         return day, month, year, f"{day}{month}{year}"
    
#     # No pattern matched
#     return None, None, None, None

def extract_day_month_year_from_filename(filename):
    """
    Accepts names like:
      - TAKEOFF_Forecast_12092023.txt  (DDMMYYYY)
      - TAKEOFF_Forecast_12_09_2023.txt (DD_MM_YYYY)
      - TAKEOFF_Forecast_092023.txt     (MMYYYY) -> day defaults to "01"
      - 12092023.txt / 12_09_2023.txt / 092023.txt, etc.

    Returns (day, month, year, "DDMMYYYY") or (None, None, None, None) if no date found.
    """
    import os, re
    name = os.path.basename(filename or "")
    print(f"filename = {name}")

    # 1) DDMMYYYY anywhere
    m = re.search(r'(?<!\d)(\d{2})(\d{2})(\d{4})(?=\.txt$|$)', name)
    if m:
        day, month, year = m.group(1), m.group(2), m.group(3)
        return day, month, year, f"{day}{month}{year}"

    # 2) DD_MM_YYYY anywhere
    m = re.search(r'(?<!\d)(\d{2})_(\d{2})_(\d{4})(?=\.txt$|$)', name)
    if m:
        day, month, year = m.group(1), m.group(2), m.group(3)
        return day, month, year, f"{day}{month}{year}"

    # 3) Monthly: MMYYYY anywhere (default day "01")
    m = re.search(r'(?<!\d)(\d{2})(\d{4})(?=\.txt$|$)', name)
    if m:
        month, year = m.group(1), m.group(2)
        day = "01"
        return day, month, year, f"{day}{month}{year}"

    return None, None, None, None



def extract_month_year_from_date(date_str, format_str="%Y%m%d%H%M"):
    """ 
    Extract month and year from a date string
    
    Args:
        date_str (str): Date string to parse
        format_str (str): Format of the date string
        
    Returns:
        tuple: (month, year, month_year_str) where month_year_str is formatted as "MMYYYY"
              Returns (None, None, None) if parsing fails
    """
    try:
        date_obj = datetime.strptime(date_str, format_str)
        print(f"date_obj = {date_obj}")
        day = f"{date_obj.day:02d}"
        print(f"day = {day}")
        month = f"{date_obj.month:02d}"
        year = f"{date_obj.year}"
        return day,month,year,f"{day}{month}{year}"
    except ValueError:
        return None, None, None,None

def compare_weather_data(
    df1,
    df2,
    wind_dir_threshold=30,
    wind_speed_threshold=5,
    temp_threshold=1,
    qnh_threshold=1,
):
    """
    Compares weather data from two DataFrames based on matching 'DAY' and 'TIME'.

    Args:
        df1 (pd.DataFrame): Actual (METAR) data with 'TIME', 'WIND_DIR', 'WIND_SPEED', 'TEMP', 'QNH', and 'DAY'.
        df2 (pd.DataFrame): Forecast data with 'TIME', 'WIND_DIR', 'WIND_SPEED', 'TEMP', 'QNH', and 'DAY'.
        wind_dir_threshold (int): Threshold for wind direction accuracy in degrees.
        wind_speed_threshold (int): Threshold for wind speed accuracy in knots.
        temp_threshold (int): Threshold for temperature accuracy in °C.
        qnh_threshold (int): Threshold for QNH accuracy in hPa.

    Returns:
        pd.DataFrame: Daily accuracy summary with counts in parentheses.
    """

    if not isinstance(df1, pd.DataFrame) or not isinstance(df2, pd.DataFrame):
        print("Error: Input arguments must be Pandas DataFrames.")
        return pd.DataFrame()

    required_columns = ["TIME", "WIND_DIR", "WIND_SPEED", "TEMP", "QNH", "DAY"]

    # Check if all required columns are in df1
    if not all(col in df1.columns for col in required_columns):
        missing_cols = [col for col in required_columns if col not in df1.columns]
        print(f"Error: METAR DataFrame is missing columns: {missing_cols}")
        return pd.DataFrame()

    # Check if all required columns except QNH are in df2
    forecast_required = ["TIME", "WIND_DIR", "WIND_SPEED", "TEMP", "DAY"]
    if not all(col in df2.columns for col in forecast_required):
        missing_cols = [col for col in forecast_required if col not in df2.columns]
        print(f"Error: Forecast DataFrame is missing columns: {missing_cols}")
        return pd.DataFrame()

    # If QNH is not in df2 but QFE is, use QFE as QNH
    if "QNH" not in df2.columns and "QFE" in df2.columns:
        df2["QNH"] = df2["QFE"]
    elif "QNH" not in df2.columns:
        print(
            "Error: Forecast DataFrame is missing QNH column and no QFE column to substitute."
        )
        return pd.DataFrame()

    # Combine DAY and TIME for unique identification
    df1["DATETIME"] = (
        df1["DAY"].astype(str).str.zfill(2) + " " + df1["TIME"].astype(str)
    )
    df2["DATETIME"] = (
        df2["DAY"].astype(str).str.zfill(2) + " " + df2["TIME"].astype(str)
    )

    # Remove duplicate date-times, keeping the first occurrence
    df1_unique = df1.drop_duplicates(subset="DATETIME", keep="first")
    df2_unique = df2.drop_duplicates(subset="DATETIME", keep="first")

    merged_df = pd.merge(
        df1_unique,
        df2_unique,
        on="DATETIME",
        suffixes=("_actual", "_forecast"),
        how="inner",
    )

    if merged_df.empty:
        print("No matching day and times found between the DataFrames.")
        return pd.DataFrame()

    # Track parameter-wise individual accuracies
    dir_accuracy_flags = []
    speed_accuracy_flags = []
    temp_accuracy_flags = []
    qnh_accuracy_flags = []
    overall_accuracy = []
    inaccuracy_reasons = []

    for _, row in merged_df.iterrows():
        actual_dir = row["WIND_DIR_actual"]
        forecast_dir = row["WIND_DIR_forecast"]
        actual_speed = row["WIND_SPEED_actual"]
        forecast_speed = row["WIND_SPEED_forecast"]
        actual_temp = row["TEMP_actual"]
        forecast_temp = row["TEMP_forecast"]
        actual_qnh = row["QNH_actual"]
        forecast_qnh = row["QNH_forecast"]

        dir_accurate = False
        speed_accurate = False
        temp_accurate = False
        qnh_accurate = False
        reasons = []

        # Handle direction accuracy
        if (
            actual_dir == "VRB"
            or forecast_dir == "VRB"
            or actual_dir == "N/A"
            or forecast_dir == "N/A"
            or pd.isna(actual_dir)
            or pd.isna(forecast_dir)
        ):
            dir_accurate = True
        else:
            try:
                dir_diff = circular_difference(int(forecast_dir), int(actual_dir))
                dir_accurate = dir_diff is not None and dir_diff <= wind_dir_threshold
                if not dir_accurate and dir_diff is not None:
                    reasons.append(f"Wind Direction off by {dir_diff:.1f}°")
            except (ValueError, TypeError):
                print(
                    f"Warning: Invalid wind direction for DATETIME {row['DATETIME']}."
                )
                reasons.append("Wind Direction - Invalid data")

        # Handle speed accuracy
        if (
            pd.notna(actual_speed)
            and pd.notna(forecast_speed)
            and actual_speed != "N/A"
            and forecast_speed != "N/A"
        ):
            try:
                speed_diff = abs(int(forecast_speed) - int(actual_speed))
                speed_accurate = speed_diff <= wind_speed_threshold
                if not speed_accurate:
                    reasons.append(f"Wind Speed off by {speed_diff} knots")
            except (ValueError, TypeError):
                print(f"Warning: Invalid wind speed for DATETIME {row['DATETIME']}.")
                reasons.append("Wind Speed - Invalid data")
        else:
            print(f"Warning: Missing wind speed for DATETIME {row['DATETIME']}.")
            reasons.append("Wind Speed - Missing data")

        # Handle temperature accuracy
        if (
            pd.notna(actual_temp)
            and pd.notna(forecast_temp)
            and actual_temp != "N/A"
            and forecast_temp != "N/A"
        ):
            try:
                temp_diff = abs(float(forecast_temp) - float(actual_temp))
                temp_accurate = temp_diff <= temp_threshold
                if not temp_accurate:
                    reasons.append(f"Temperature off by {temp_diff:.1f}°C")
            except (ValueError, TypeError):
                print(f"Warning: Invalid temperature for DATETIME {row['DATETIME']}.")
                reasons.append("Temperature - Invalid data")
        else:
            print(f"Warning: Missing temperature for DATETIME {row['DATETIME']}.")
            reasons.append("Temperature - Missing data")

        # Handle QNH accuracy
        if (
            pd.notna(actual_qnh)
            and pd.notna(forecast_qnh)
            and actual_qnh != "N/A"
            and forecast_qnh != "N/A"
        ):
            try:
                qnh_diff = abs(float(forecast_qnh) - float(actual_qnh))
                qnh_accurate = qnh_diff <= qnh_threshold
                if not qnh_accurate:
                    reasons.append(f"QNH off by {qnh_diff:.1f} hPa")
            except (ValueError, TypeError):
                print(f"Warning: Invalid QNH for DATETIME {row['DATETIME']}.")
                reasons.append("QNH - Invalid data")
        else:
            print(f"Warning: Missing QNH for DATETIME {row['DATETIME']}.")
            reasons.append("QNH - Missing data")

        # Store individual accuracy flags
        dir_accuracy_flags.append(dir_accurate)
        speed_accuracy_flags.append(speed_accurate)
        temp_accuracy_flags.append(temp_accurate)
        qnh_accuracy_flags.append(qnh_accurate)

        # Overall accuracy
        overall_accuracy.append(
            "Accurate"
            if all([dir_accurate, speed_accurate, temp_accurate, qnh_accurate])
            else "Not Accurate"
        )
        
        # Store inaccuracy reasons
        inaccuracy_reasons.append(" | ".join(reasons) if reasons else "All Accurate")

    # Add accuracy flags to DataFrame
    merged_df["DIR_Accurate"] = dir_accuracy_flags
    merged_df["SPD_Accurate"] = speed_accuracy_flags
    merged_df["TEMP_Accurate"] = temp_accuracy_flags
    merged_df["QNH_Accurate"] = qnh_accuracy_flags
    merged_df["Accuracy"] = overall_accuracy
    merged_df["Inaccuracy_Reason"] = inaccuracy_reasons

    # Group-wise summary per DAY
    merged_df["DAY"] = merged_df["DATETIME"].str.split().str[0]  # Extract day again

    # Calculate daily accuracy percentages with counts
    daily_accuracy = (
        merged_df.groupby("DAY")
        .agg(
            {
                "DIR_Accurate": lambda x: f"{round(100 * x.sum() / len(x), 1)}% ({x.sum()})",
                "SPD_Accurate": lambda x: f"{round(100 * x.sum() / len(x), 1)}% ({x.sum()})",
                "TEMP_Accurate": lambda x: f"{round(100 * x.sum() / len(x), 1)}% ({x.sum()})",
                "QNH_Accurate": lambda x: f"{round(100 * x.sum() / len(x), 1)}% ({x.sum()})",
                "Accuracy": lambda x: f"{round(100 * (x == 'Accurate').sum() / len(x), 1)}% ({(x == 'Accurate').sum()})",
            }
        )
        .rename(
            columns={
                "DIR_Accurate": "Wind Direction",
                "SPD_Accurate": "Wind Speed",
                "TEMP_Accurate": "Temperature",
                "QNH_Accurate": "QNH",
                "Accuracy": "Overall",
            }
        )
        .reset_index()
    )

    # Calculate whole month accuracy
    total_records = len(merged_df)
    whole_month = {
        "DAY": "Whole Month",
        "Wind Direction": f"{round(100 * merged_df['DIR_Accurate'].sum() / total_records, 1)}% ({merged_df['DIR_Accurate'].sum()})",
        "Wind Speed": f"{round(100 * merged_df['SPD_Accurate'].sum() / total_records, 1)}% ({merged_df['SPD_Accurate'].sum()})",
        "Temperature": f"{round(100 * merged_df['TEMP_Accurate'].sum() / total_records, 1)}% ({merged_df['TEMP_Accurate'].sum()})",
        "QNH": f"{round(100 * merged_df['QNH_Accurate'].sum() / total_records, 1)}% ({merged_df['QNH_Accurate'].sum()})",
        "Overall": f"{round(100 * (merged_df['Accuracy'] == 'Accurate').sum() / total_records, 1)}% ({(merged_df['Accuracy'] == 'Accurate').sum()})",
    }

    # Add ICAO requirements row
    icao_requirements = {
        "DAY": "ICAO Requirement",
        "Wind Direction": "80%",
        "Wind Speed": "80%",
        "Temperature": "80%",
        "QNH": "80%",
        "Overall": "80%",
    }

    # Append whole month and ICAO requirements to daily accuracy
    daily_accuracy = pd.concat(
        [
            daily_accuracy,
            pd.DataFrame([whole_month]),
            pd.DataFrame([icao_requirements]),
        ],
        ignore_index=True,
    )

    return daily_accuracy, merged_df


import matplotlib.pyplot as plt
import io
import base64

# def plot_accuracy_chart(daily_accuracy, metric="Overall"):
#     """
#     Creates a bar chart for accuracy over days.
    
#     Args:
#         daily_accuracy (pd.DataFrame): DataFrame from compare_weather_data.
#         metric (str): Which metric to plot ("Overall", "Wind Direction", "Wind Speed", "Temperature", "QNH").
    
#     Returns:
#         str: Base64 encoded PNG image (can be sent to frontend).
#     """
#     df = daily_accuracy.copy()

#     # Extract only % number
#     df[metric] = df[metric].str.extract(r'(\d+\.?\d*)').astype(float)

#     # Filter out non-date rows (Whole Month, ICAO Requirement)
#     df = df[~df["DAY"].isin(["Whole Month", "ICAO Requirement"])]

#     # Plot
#     plt.figure(figsize=(10,5))
#     plt.bar(df["DAY"], df[metric], color="skyblue")
#     plt.xticks(rotation=45)
#     plt.ylim(0, 100)
#     plt.ylabel("Accuracy (%)")
#     plt.xlabel("Day")
#     plt.title(f"{metric} Accuracy per Day")

#     # Save to base64
#     buf = io.BytesIO()
#     plt.tight_layout()
#     plt.savefig(buf, format="png")
#     buf.seek(0)
#     img_base64 = base64.b64encode(buf.read()).decode("utf-8")
#     plt.close()
#     return img_base64
