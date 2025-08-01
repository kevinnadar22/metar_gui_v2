import requests
from datetime import datetime
import re
import sys
import os

def fetch_all_metar(icao, start_dt, end_dt, output_file="metar.txt"):
    # Ensure output file is saved in ad_warn_data directory
    ad_warn_dir = os.path.join(os.getcwd(), 'ad_warn_data')
    os.makedirs(ad_warn_dir, exist_ok=True)
    
    # If output_file doesn't have a path, save it in ad_warn_data directory
    if not os.path.dirname(output_file):
        output_file = os.path.join(ad_warn_dir, output_file)
    
    url = (
        f"https://www.ogimet.com/display_metars2.php?lang=en&lugar={icao}&tipo=ALL&ord=DIR&nil=NO&fmt=txt"
        f"&ano={start_dt.year}&mes={start_dt.month:02}&day={start_dt.day:02}&hora={start_dt.hour:02}"
        f"&anof={end_dt.year}&mesf={end_dt.month:02}&dayf={end_dt.day:02}&horaf={end_dt.hour:02}&min=00&minf=59"
    )

    print(f"[+] Fetching from: {url}")
    response = requests.get(url, timeout=60)
    if response.status_code == 200:
        lines = response.text.strip().split("\n")
        metar_lines = []
        
        for line in lines:
            line = line.strip()
            # Exclude comment lines starting with '#'
            if line.startswith('#'):
                continue
            # Keep ALL lines that contain METAR data
            if line and ('METAR' in line or line.startswith(icao)):
                metar_lines.append(line)

        with open(output_file, "w", encoding="utf-8") as f:
            for line in metar_lines:
                f.write(line + "\n")

        print(f"[✔] Saved {len(metar_lines)} METAR lines to {output_file}")
        print(f"[✔] Total lines processed: {len(lines)}")
    else:
        print(f"[✘] Failed to fetch METAR data (status code: {response.status_code})")

icao = sys.argv[1] if len(sys.argv) > 1 else "VABB"

# # Set the date range
# start_dt = datetime(2025, 6, 1, 0)   # June 1, 2025 at 00:00
# end_dt = datetime(2025, 7, 1, 3)   # June 30, 2025 at 23:00

# # Call the function
# fetch_all_metar("VABB", start_dt, end_dt)




