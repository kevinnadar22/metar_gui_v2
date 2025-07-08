import os
from PyPDF2 import PdfReader
import re
from datetime import datetime, timedelta
from app.utils.ogimet import OgimetAPI


def get_pdf_text(pdf_path):
    """
    Extract text content from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Concatenated text content from all pages of the PDF.
    """
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() for page in reader.pages)
    return text


def parse_weather_section(text):
    """
    Parse the WEATHER section from forecast text.

    Args:
        text (str): The complete forecast text.

    Returns:
        str: Extracted weather section text.

    Raises:
        ValueError: If weather section is not found in the text.
    """

    match = re.search(r"WEATHER\s+(.*?)=", text, re.DOTALL)
    if not match:
        raise ValueError("Weather section not found")
    weather_text = match.group(1).strip().replace("\n", " ")

    return weather_text


def format_weather_text(weather_text: str):
    """
    Format weather text by replacing intensity indicators and extracting primary conditions.

    Args:
        weather_text (str): Raw weather text to format.

    Returns:
        list: List of formatted weather conditions.

    Notes:
        - Replaces "FBL" with "-" (light)
        - Replaces "MOD" with "" (moderate)
        - Replaces "HVY" with "+" (heavy)
        - Extracts conditions up to BECMG or TEMPO indicators
    """
    data_to_replace = {"FBL": "-", "MOD": "", "HVY": "+"}

    for key, value in data_to_replace.items():
        weather_text = weather_text.replace(key, value)
    match = re.search(r"BECMG|TEMPO", weather_text)

    if match:
        weather_text = weather_text[: match.start()]

    weather_text = weather_text.strip().split()
    weather_text = [x.strip() for x in weather_text]
    return weather_text


def get_date_range(pdf_text):
    """
    Extract date range from PDF text using regex.

    Args:
        pdf_text (str): Complete text content from the PDF.

    Returns:
        tuple: A pair of datetime objects (start_date, end_date).

    Raises:
        ValueError: If date range is not found in the text.
    """
    pattern = (
        r"FROM (\d{4}/\d{2}/\d{2} \d{2}:\d{2}UTC) TO (\d{4}/\d{2}/\d{2} \d{2}:\d{2}UTC)"
    )
    match = re.search(pattern, pdf_text)
    if not match:
        raise ValueError("Date range not found")

    start_date = datetime.strptime(match.group(1), "%Y/%m/%d %H:%MUTC")
    end_date = datetime.strptime(match.group(2), "%Y/%m/%d %H:%MUTC")

    return start_date, end_date


def parse_and_format_weather_text(text):
    """
    Combine parsing and formatting of weather text into a single operation.

    Args:
        text (str): Raw text containing weather information.

    Returns:
        list: Formatted list of weather conditions.
    """
    weather_text = parse_weather_section(text)
    weather_data = format_weather_text(weather_text)
    return weather_data


def get_bcmg_temp_data(weather_text):
    """
    Extract BECMG and TEMPO data from weather text.

    Args:
        weather_text (str): Weather text containing BECMG/TEMPO data

    Returns:
        list[dict]: List of dictionaries containing:
            - change_type (str): "BECMG" or "TEMPO"
            - start_time (str): Start time in format "HHMM"
            - end_time (str): End time in format "HHMM"
            - weather_data (list): List of weather conditions
    """
    changes = []

    pattern = r"(BECMG|TEMPO)\s+(\d{4}/\d{4})\s+(.*?)(?=BECMG|TEMPO|=|$)"
    matches = re.finditer(pattern, weather_text)

    for match in matches:
        change_type = match.group(1)
        time_range = match.group(2)
        weather = match.group(3).strip()

        start_time = time_range.split("/")[0]
        end_time = time_range.split("/")[1]

        weather_data = [x.strip() for x in weather.split()]

        changes.append(
            {
                "change_type": change_type,
                "start_time": start_time,
                "end_time": end_time,
                "weather_data": weather_data,
            }
        )

    return changes


def check_if_date_is_in_range(
    start_time, end_time, total_start_time: datetime, total_end_time: datetime
):
    """
    Check if the given time range overlaps with more than half of the total time range.

    Args:
        start_time (str): Start time in DDHH format
        end_time (str): End time in DDHH format
        total_start_time (datetime): Total range start time
        total_end_time (datetime): Total range end time

    Returns:
        bool: True if time range overlaps with more than half of total range
    """
    # Convert DDHH strings to datetime objects
    start_day = int(start_time[:2])
    start_hour = int(start_time[2:])
    end_day = int(end_time[:2])
    end_hour = int(end_time[2:])

    # Create datetime objects using the base date from total_start_time
    base_date = total_start_time.replace(hour=0, minute=0, second=0, microsecond=0)

    # Calculate the actual datetime by adding days and hours to base date
    range_start = base_date + timedelta(days=start_day - 1, hours=start_hour)
    range_end = base_date + timedelta(days=end_day - 1, hours=end_hour)

    # Handle case where end time is before start time (crosses month boundary)
    if range_end <= range_start:
        range_end += timedelta(days=30)  # Assume next month

    # Calculate the duration of the given time range in seconds
    range_duration = (range_end - range_start).total_seconds()

    # Calculate the duration of the total time range in seconds
    total_duration = (total_end_time - total_start_time).total_seconds()
    print(range_duration, total_duration, total_start_time, total_end_time)
    # Check if the given range duration is more than half of the total duration
    return range_duration > total_duration / 2


def is_accurate_weather_data(weather_data, metar_data):
    """
    Check if weather data matches any line in the METAR data.

    Args:
        weather_data (list): List of weather conditions to check.
        metar_data (str): Raw METAR data as multiline string.

    Returns:
        bool: True if any weather condition is found in METAR data, False otherwise.
    """
    for line in metar_data.split("\n"):
        for item in weather_data:
            # Special case: if item is RA or SHRA, check for both
            if item == "RA" or item == "SHRA":
                if "RA" in line or "SHRA" in line:
                    print(line)
                    print(item)
                    return True
            elif item in line:
                print(line)
                print(item)
                return True
    return False

def process_weather_accuracy_helper(weather_text, start_datetime, end_datetime, icao):
    accuracy_point = 0


    ins = OgimetAPI()
    file = ins.save_metar_to_file(begin=start_datetime, end=end_datetime, icao=icao)
    with open(file, "r") as f:
        metar_data = f.read()

    weather_data = format_weather_text(weather_text)

    print(weather_text + " " + str(weather_data))
    print(
        f"From {start_datetime} to {end_datetime}"
    )

    if is_accurate_weather_data(weather_data, metar_data):
        accuracy_point = 100

    if accuracy_point == 0:
        print("Not accurate in 1st attempt")

        temp_data = get_bcmg_temp_data(weather_text=weather_text)

        for item in temp_data:

            if check_if_date_is_in_range(
                item["start_time"], item["end_time"], start_datetime, end_datetime
            ):
                print(item)
                weather_data = item["weather_data"]

                if is_accurate_weather_data(weather_data, metar_data):
                    accuracy_point = 50
                    break

    return accuracy_point

def process_single_file(forecast_file_path, icao="VABB"):
    accuracy_point = 0
    text = get_pdf_text(forecast_file_path)

    weather_text = parse_weather_section(text)
    # weather_text = "FY BECMG 1100/1102 HZ FU TEMPO 1101/1103 HZ FU BECMG 1104/1109 FU"
    weather_data = format_weather_text(weather_text)
    start_date, end_date = get_date_range(text)

    begin = start_date.strftime("%Y%m%d%H%M")
    end = end_date.strftime("%Y%m%d%H%M")

    ins = OgimetAPI()
    file = ins.save_metar_to_file(begin=begin, end=end, icao=icao)

    with open(file, "r") as f:
        metar_data = f.read()

    print(weather_data)
    print(
        f"From {start_date.strftime('%Y/%m/%d %H:%MUTC')} to {end_date.strftime('%Y/%m/%d %H:%MUTC')}"
    )

    if is_accurate_weather_data(weather_data, metar_data):
        accuracy_point = 100

    if accuracy_point == 0:
        print("Not accurate in 1st attempt")

        temp_data = get_bcmg_temp_data(weather_text=weather_text)

        for item in temp_data:

            if check_if_date_is_in_range(
                item["start_time"], item["end_time"], start_date, end_date
            ):
                print(item)
                weather_data = item["weather_data"]

                if is_accurate_weather_data(weather_data, metar_data):
                    accuracy_point = 50
                    break

    return accuracy_point


if __name__ == "__main__":
    def main():
        """
        Main function to process weather forecasts and compare with METAR data.

        The function:
        1. Reads PDF files from 'pdf' directory
        2. Extracts weather data and date ranges
        3. Fetches corresponding METAR data
        4. Compares forecast accuracy
        5. Handles BECMG/TEMPO conditions if initial comparison fails

        Prints accuracy scores (0, 50, or 100) for each processed file.
        """
        for file in os.listdir("pdf"):
            accuracy_point = 0
            text = get_pdf_text(f"pdf/{file}")

            weather_text = parse_weather_section(text)
            weather_text = (
                "FY BECMG 1100/1102 HZ FU TEMPO 1101/1103 HZ FU BECMG 1104/1109 FU"
            )
            weather_data = format_weather_text(weather_text)
            start_date, end_date = get_date_range(text)

            begin = start_date.strftime("%Y%m%d%H%M")
            end = end_date.strftime("%Y%m%d%H%M")

            ins = OgimetAPI()
            file = ins.save_metar_to_file(begin=begin, end=end, icao="VABB")

            with open(file, "r") as f:
                metar_data = f.read()

            print(weather_data)
            print(
                f"From {start_date.strftime('%Y/%m/%d %H:%MUTC')} to {end_date.strftime('%Y/%m/%d %H:%MUTC')}"
            )

            if is_accurate_weather_data(weather_data, metar_data):
                accuracy_point = 100

            if accuracy_point == 0:
                print("Not accurate in 1st attempt")

                temp_data = get_bcmg_temp_data(weather_text=weather_text)

                for item in temp_data:

                    if check_if_date_is_in_range(
                        item["start_time"], item["end_time"], start_date, end_date
                    ):
                        print(item)
                        weather_data = item["weather_data"]

                        if is_accurate_weather_data(weather_data, metar_data):
                            accuracy_point = 50
                            break

            print(f"Accurare point:", accuracy_point)
            print("--------------------------------")


    main()
