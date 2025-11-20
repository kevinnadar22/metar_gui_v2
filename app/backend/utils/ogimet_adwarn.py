"""
OGIMET API for Aerodrome Warning - Special version with timestamp prefixes

This module is specifically for AD Warning verification which requires
YYYYMMDDHHMM timestamp prefix on each METAR line.
"""

import requests
import csv
import io
import re
from datetime import datetime
from typing import List, Dict, Optional, Union, Any
import random
import string
import os
from app.backend.config import AD_WARN_DIR

class OgimetAPIAdWarn:
    """
    Client for accessing OGIMET meteorological data for Aerodrome Warning verification.
    
    This version adds YYYYMMDDHHMM timestamp prefix to each METAR line for compatibility
    with AD Warning validation and extraction code.
    """
    
    BASE_URL = "http://www.ogimet.com/cgi-bin"
    
    def __init__(self):
        """Initialize the OGIMET API client."""
        pass
    
    def get_metar(self, 
                 begin: Union[str, datetime],
                 end: Optional[Union[str, datetime]] = None,
                 icao: Optional[str] = None,
                 state: Optional[str] = None,
                 lang: str = "eng",
                 header: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve METAR (Meteorological Aerodrome Report) data from OGIMET.
        
        Args:
            begin: Start date/time in format YYYYMMDDHHmm or datetime object
            end: End date/time in format YYYYMMDDHHmm or datetime object (default: current time)
            icao: Filter by ICAO airport code prefix (e.g., "SPZO")
            state: Filter by country name prefix (e.g., "Per" for Peru)
            lang: Language for results ("eng" for English)
            header: Whether to include header in results
            
        Returns:
            List of dictionaries containing METAR data with keys:
            ICAOIND, YEAR, MONTH, DAY, HOUR, MIN, REPORT
        """
        # Format datetime objects if provided
        if isinstance(begin, datetime):
            begin = begin.strftime("%Y%m%d%H%M")
        if end and isinstance(end, datetime):
            end = end.strftime("%Y%m%d%H%M")
            
        # Build request parameters
        params = {
            "begin": begin,
            "lang": lang,
        }
        
        if end:
            params["end"] = end
        if icao:
            params["icao"] = icao
        if state:
            params["state"] = state
        if header:
            params["header"] = "yes"
            
        # Make the request
        response = requests.get(f"{self.BASE_URL}/getmetar", params=params)
        response.raise_for_status()
        
        # Parse CSV response
        csv_data = csv.reader(io.StringIO(response.text))
        
        # Convert to list of dictionaries
        result = []
        headers = next(csv_data) if header else ["ICAOIND", "YEAR", "MONTH", "DAY", "HOUR", "MIN", "REPORT"]
        
        for row in csv_data:
            if len(row) >= len(headers):
                result.append(dict(zip(headers, row)))
                
        return result
    
    def save_metar_to_file(self, begin: Union[str, datetime], end: Optional[Union[str, datetime]] = None, 
                          icao: Optional[str] = None) -> str:
        """
        Retrieve METAR data and save it to a text file with YYYYMMDDHHMM timestamp prefix.
        
        This method is specifically designed for AD Warning verification which requires
        each METAR line to start with a 12-digit timestamp in YYYYMMDDHHMM format.
        
        Args:
            begin: Start date/time in format YYYYMMDDHHmm or datetime object
            end: End date/time in format YYYYMMDDHHmm or datetime object
            icao: ICAO airport code
            
        Returns:
            The filename where the METAR data was saved
        """
        
        res = self.get_metar(
            begin=begin,
            end=end,
            icao=icao
        )

        # Generate random filename
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        random_filename = f"metar_adwarn_{random_string}.txt"
        
        # Save METAR data to a text file in METAR_DATA_DIR
        file_path = os.path.join(AD_WARN_DIR, random_filename)

        if res and len(res) > 0:
            with open(file_path, 'w') as txtfile:
                for item in res:
                    # Check for either REPORT or PARTE column
                    metar_report = item.get('REPORT') or item.get('PARTE')
                    if metar_report:
                        # Parse from the begin datetime to get year and month
                        begin_str = begin if isinstance(begin, str) else begin.strftime("%Y%m%d%H%M")
                        year = begin_str[:4]
                        month = begin_str[4:6]
                        
                        # Extract day/hour/minute from METAR report (format: DDHHMM)
                        # Look for pattern like "010000Z" in "METAR VABB 010000Z"
                        match = re.search(r'\s(\d{6})Z', metar_report)
                        if match:
                            ddhhmmz = match.group(1)
                            day = ddhhmmz[:2]
                            hour = ddhhmmz[2:4]
                            minute = ddhhmmz[4:6]
                        else:
                            # Fallback: use begin datetime
                            print(f"[WARNING] Could not parse timestamp from METAR: {metar_report[:50]}")
                            day = begin_str[6:8]
                            hour = begin_str[8:10]
                            minute = begin_str[10:12]
                        
                        # Validate all components are numeric
                        if not (year.isdigit() and month.isdigit() and day.isdigit() and 
                               hour.isdigit() and minute.isdigit()):
                            print(f"[ERROR] Invalid timestamp components: year={year}, month={month}, day={day}, hour={hour}, minute={minute}")
                            continue
                        
                        # Format timestamp as YYYYMMDDHHMM
                        timestamp = f"{year}{month}{day}{hour}{minute}"
                        
                        # Write timestamp followed by METAR report
                        txtfile.write(f"{timestamp} {metar_report}\n")
                print(f"AD Warning METAR data for station {icao} saved to {file_path}")
        else:
            print(f"No METAR data found for station {icao}")
            
        return file_path

if __name__ == "__main__":
    # example usage
    def main():
        ins = OgimetAPIAdWarn()
        ins.save_metar_to_file(
            begin="202507010000",
            end="202507020000",
            icao="VABB"
        )

    # main()
