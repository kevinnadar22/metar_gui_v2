"""
OGIMET API Documentation

This module provides access to meteorological data from OGIMET.
"""

import requests
import csv
import io
from datetime import datetime
from typing import List, Dict, Optional, Union, Any
import random
import string
import os
from app.config import METAR_DATA_DIR

class OgimetAPI:
    """
    Client for accessing OGIMET meteorological data.
    
    OGIMET provides professional information about meteorological conditions worldwide.
    This class allows retrieving METAR reports and other meteorological data.
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
            
        Examples:
            >>> api = OgimetAPI()
            >>> # Get METAR data for Peru for January 1, 2023
            >>> peru_data = api.get_metar(
            ...     begin="202301010000", 
            ...     end="202301012359", 
            ...     state="Per"
            ... )
            >>> 
            >>> # Get METAR data for a specific airport (SPZO) for a date range
            >>> airport_data = api.get_metar(
            ...     begin="202301010000",
            ...     end="202301050000",
            ...     icao="SPZO"
            ... )
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
        Retrieve METAR data and save it to a text file with a random filename.
        
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
        random_filename = f"metar_data_{random_string}.txt"
        
        # Save PARTE column values to a text file in METAR_DATA_DIR
        file_path = os.path.join(METAR_DATA_DIR, random_filename)

        if res and len(res) > 0:
            with open(file_path, 'w') as txtfile:
                for item in res:
                    if 'PARTE' in item:
                        txtfile.write(f"{item['PARTE']}\n")
                print(f"METAR data for station {icao} saved to {file_path}")
        else:
            print(f"No METAR data found for station {icao}")
            
        return file_path

if __name__ == "__main__":
    # example usage
    def main():
        import os
        
        ins = OgimetAPI()
        ins.save_metar_to_file(
            begin="202504090000",
            end="202504100000",
            icao="VABB"
        )

    # main()