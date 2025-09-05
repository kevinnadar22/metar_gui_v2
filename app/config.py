import os
import shutil

# Base directory of the application
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directory for storing all METAR related files
METAR_DATA_DIR = os.path.join(BASE_DIR, 'app', 'static', 'metar_data')
UPPER_AIR_DATA_DIR = os.path.join(BASE_DIR,'app','static','upper_air_data')
# clean the directory
if os.path.exists(METAR_DATA_DIR):
    shutil.rmtree(METAR_DATA_DIR, ignore_errors=True), 

if os.path.exists(UPPER_AIR_DATA_DIR):
    shutil.rmtree(UPPER_AIR_DATA_DIR, ignore_errors=True)
# Create the directory if it doesn't exist
os.makedirs(METAR_DATA_DIR, exist_ok=True)
os.makedirs(UPPER_AIR_DATA_DIR, exist_ok=True) 