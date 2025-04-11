import os

# Base directory of the application
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directory for storing all METAR related files
METAR_DATA_DIR = os.path.join(BASE_DIR, 'app', 'static', 'metar_data')

# Create the directory if it doesn't exist
os.makedirs(METAR_DATA_DIR, exist_ok=True) 