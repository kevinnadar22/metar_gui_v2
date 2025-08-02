import re
from datetime import datetime, timedelta
import os

def extract_icao_from_metar(metar_file_path):
    """
    Extract ICAO station code from METAR file.
    METAR format: ICAO YYYYMMDDHHMMZ AUTO or similar
    """
    try:
        with open(metar_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if line:
                # METAR format typically starts with 4-letter ICAO code
                # Look for pattern: 4 uppercase letters followed by space or timestamp
                match = re.match(r'^([A-Z]{4})\s+', line)
                if match:
                    return match.group(1)
                
                # Also check for ICAO code in the middle of the line (some formats)
                match_middle = re.search(r'\b([A-Z]{4})\s+\d{6}Z', line)
                if match_middle:
                    return match_middle.group(1)
                
                # Check for ICAO code followed by any timestamp format
                match_any = re.search(r'\b([A-Z]{4})\s+\d{8,12}', line)
                if match_any:
                    return match_any.group(1)
        
        return None
    except Exception as e:
        print(f"Error extracting ICAO from METAR file: {e}")
        return None

def extract_icao_from_warning(warning_file_path):
    """
    Extract ICAO station code from aerodrome warning file.
    Warning format typically has ICAO code in the first few lines
    """
    try:
        with open(warning_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if line:
                # Look for 4-letter ICAO code pattern
                # Common patterns: "VABB" or "VABB 231105Z" etc.
                match = re.search(r'\b([A-Z]{4})\b', line)
                if match:
                    return match.group(1)
                
                # Also check for ICAO code followed by date/time
                match_with_time = re.search(r'\b([A-Z]{4})\s+\d{6}Z', line)
                if match_with_time:
                    return match_with_time.group(1)
        
        return None
    except Exception as e:
        print(f"Error extracting ICAO from warning file: {e}")
        return None

def extract_issue_date_from_warning(warning_file_path):
    """
    Extract issue date from the first line of aerodrome warning file.
    Expected format: YYYYMMDD in the first line
    """
    try:
        with open(warning_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check first few lines for date patterns
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line:
                # Look for YYYYMMDD pattern
                match = re.search(r'(\d{8})', line)
                if match:
                    return match.group(1)
                
                # Also check for DDMMYYYY format and convert
                ddmm_match = re.search(r'(\d{2})(\d{2})(\d{4})', line)
                if ddmm_match:
                    day, month, year = ddmm_match.groups()
                    return f"{year}{month}{day}"
        
        return None
    except Exception as e:
        print(f"Error extracting issue date from warning file: {e}")
        return None

def extract_metar_timestamps(metar_file_path):
    """
    Extract timestamps from METAR file.
    Look for YYYYMMDDHHMM format in the first 12 digits of each METAR record.
    """
    timestamps = []
    try:
        with open(metar_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if line:
                # Look for YYYYMMDDHHMM pattern (12 digits)
                match = re.search(r'(\d{12})', line)
                if match:
                    timestamp = match.group(1)
                    timestamps.append(timestamp)
                
                # Also check for DDHHMMZ format and convert to YYYYMMDDHHMM
                # This is common in METAR files where date is in a different format
                ddhmm_match = re.search(r'(\d{6})Z', line)
                if ddhmm_match:
                    ddhmm = ddhmm_match.group(1)
                    # Try to extract year from the line or use current year
                    year_match = re.search(r'(\d{4})', line)
                    if year_match:
                        year = year_match.group(1)
                        # Construct full timestamp
                        timestamp = f"{year}{ddhmm}"
                        timestamps.append(timestamp)
        
        return timestamps
    except Exception as e:
        print(f"Error extracting METAR timestamps: {e}")
        return []

def validate_station_code_match(metar_file_path, warning_file_path):
    """
    Validate that the ICAO station codes match between METAR and warning files.
    
    Returns:
        tuple: (is_valid, metar_code, warning_code, error_message)
    """
    metar_code = extract_icao_from_metar(metar_file_path)
    warning_code = extract_icao_from_warning(warning_file_path)
    

    
    if not metar_code:
        return False, None, None, "Could not extract ICAO code from METAR file"
    
    if not warning_code:
        return False, None, None, "Could not extract ICAO code from warning file"
    
    if metar_code != warning_code:
        return False, metar_code, warning_code, f"Station code mismatch: METAR = {metar_code}, Warning = {warning_code}"
    
    return True, metar_code, warning_code, None

def validate_date_range_match(metar_file_path, warning_file_path):
    """
    Validate that METAR timestamps fall within the 30-day range from warning issue date.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Extract issue date from warning file
    issue_date_str = extract_issue_date_from_warning(warning_file_path)
    if not issue_date_str:
        return False, "Could not extract issue date from warning file"
    
    try:
        # Parse issue date (YYYYMMDD format)
        issue_date = datetime.strptime(issue_date_str, "%Y%m%d")
        
        # Calculate 30-day range
        range_start = issue_date
        range_end = issue_date + timedelta(days=30)
        
        # Extract METAR timestamps
        metar_timestamps = extract_metar_timestamps(metar_file_path)
        if not metar_timestamps:
            return False, "Could not extract timestamps from METAR file"
        
        # Check if any METAR timestamp falls within the range
        valid_timestamps = []
        for timestamp in metar_timestamps:
            try:
                # Parse timestamp (YYYYMMDDHHMM format)
                metar_datetime = datetime.strptime(timestamp, "%Y%m%d%H%M")
                if range_start <= metar_datetime <= range_end:
                    valid_timestamps.append(metar_datetime)
            except ValueError:
                # Skip invalid timestamps
                continue
        
        if not valid_timestamps:
            return False, "No METAR data falls within the valid warning period (within 30 days)"
        
        return True, None
        
    except ValueError as e:
        return False, f"Error parsing dates: {str(e)}"
    except Exception as e:
        return False, f"Error during date validation: {str(e)}"

def validate_files(metar_file_path, warning_file_path):
    """
    Perform complete validation of METAR and warning files.
    
    Returns:
        dict: Validation results with success status and error messages
    """
    # Check if files exist
    if not os.path.exists(metar_file_path):
        return {
            'success': False,
            'error': 'METAR file not found'
        }
    
    if not os.path.exists(warning_file_path):
        return {
            'success': False,
            'error': 'Warning file not found'
        }
    
    # Validate station code match
    station_valid, metar_code, warning_code, station_error = validate_station_code_match(
        metar_file_path, warning_file_path
    )
    
    if not station_valid:
        return {
            'success': False,
            'error': station_error,
            'metar_code': metar_code,
            'warning_code': warning_code
        }
    
    # Validate date range match
    date_valid, date_error = validate_date_range_match(metar_file_path, warning_file_path)
    
    if not date_valid:
        return {
            'success': False,
            'error': date_error,
            'metar_code': metar_code,
            'warning_code': warning_code
        }
    
    return {
        'success': True,
        'metar_code': metar_code,
        'warning_code': warning_code,
        'message': 'Validation successful'
    } 