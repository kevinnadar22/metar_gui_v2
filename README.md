# METAR Data Analysis API

A Flask-based API for retrieving, processing, and comparing METAR (Meteorological Aerodrome Report) data with forecast data.

## Overview

This API provides endpoints to:
- Retrieve METAR observation data from OGIMET
- Process and compare METAR observations with forecast data
- Generate and download comparison CSV files for analysis

The API integrates with the OGIMET service to fetch actual meteorological observations and compares them with forecast data to determine forecast accuracy.

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd metar_api
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

The API will be available at `http://localhost:5000`.

## API Endpoints

### Health Check

```
GET /health
```

Returns the status of the API.

#### Response

```json
{
  "status": "ok",
  "message": "METAR API is running"
}
```

### Process METAR Data

```
POST /api/process_metar
```

Process METAR data by fetching observations and comparing them with forecast data.

#### Request

Content-Type: `multipart/form-data`

Form fields:
- `start_date`: Start date for METAR data in format YYYYMMDDHHMM
- `end_date`: End date for METAR data in format YYYYMMDDHHMM
- `icao`: ICAO code for the airport (e.g., "VABB" for Mumbai)
- `forecast_file`: Text file containing forecast data

#### Response

```json
{
  "status": "success",
  "message": "METAR data processed successfully",
  "metrics": {
    "total_comparisons": 24,
    "accurate_predictions": 18,
    "accuracy_percentage": 75.0
  },
  "file_paths": {
    "metar_file": "downloads/metar_data_abc123.txt",
    "metar_csv": "downloads/decoded_metar_VABB_202404091512.csv",
    "comparison_csv": "downloads/comparison_VABB_202404091512.csv"
  },
  "comparison_data": [
    {
      "DATETIME": "09 0000Z",
      "DAY_actual": "09",
      "TIME_actual": "0000Z",
      "WIND_DIR_actual": 330,
      "WIND_SPEED_actual": 9,
      "TEMP_actual": 26,
      "QNH_actual": 1009,
      "DAY_forecast": "09",
      "TIME_forecast": "0000Z",
      "WIND_DIR_forecast": 320,
      "WIND_SPEED_forecast": 8,
      "TEMP_forecast": 26,
      "QNH_forecast": 1009,
      "Accuracy": "Accurate"
    },
    ...
  ]
}
```

### Get Raw METAR Data

```
GET /api/metar
```

Retrieve raw METAR data for a specific airport and date range.

#### Parameters

- `start_date`: Start date in format YYYYMMDDHHMM
- `end_date`: End date in format YYYYMMDDHHMM
- `icao`: ICAO code for the airport

#### Response

```json
{
  "status": "success",
  "message": "METAR data retrieved for VABB",
  "data": [
    {
      "ICAOIND": "VABB",
      "YEAR": "2024",
      "MONTH": "04",
      "DAY": "09",
      "HOUR": "00",
      "MIN": "00",
      "REPORT": "METAR VABB 090000Z 33009KT 5000 HZ NSC 26/21 Q1009 NOSIG="
    },
    ...
  ]
}
```

### Download Files

```
GET /api/download/<file_type>
```

Download generated files.

#### Parameters

- `file_type`: Type of file to download ('metar', 'metar_csv', 'comparison_csv')
- `file_path`: Path to the file (from the process_metar response)

#### Response

The API returns the requested file as an attachment.

### Create Comparison CSV

```
POST /api/comparison_csv
```

Create a comparison CSV file from METAR and forecast data and return it directly.

#### Request

Content-Type: `multipart/form-data`

Form fields:
- `start_date`: Start date for METAR data in format YYYYMMDDHHMM
- `end_date`: End date for METAR data in format YYYYMMDDHHMM
- `icao`: ICAO code for the airport
- `forecast_file`: Text file containing forecast data

#### Response

Returns a CSV file as an attachment.

## Usage Examples

### Python Example

```python
import requests

# Process METAR data
def process_metar_data(start_date, end_date, icao, forecast_file_path):
    url = "http://localhost:5000/api/process_metar"
    
    # Prepare form data
    form_data = {
        "start_date": start_date,
        "end_date": end_date,
        "icao": icao
    }
    
    # Prepare files
    files = {
        "forecast_file": open(forecast_file_path, "rb")
    }
    
    # Make POST request
    response = requests.post(url, data=form_data, files=files)
    
    # Close file
    files["forecast_file"].close()
    
    # Check if request was successful
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.json()['error']}")
        return None

# Example usage
result = process_metar_data(
    start_date="202404090000",
    end_date="202404100000",
    icao="VABB",
    forecast_file_path="forecast.txt"
)

if result:
    # Download comparison CSV
    download_url = f"http://localhost:5000/api/download/comparison_csv?file_path={result['file_paths']['comparison_csv']}"
    download_response = requests.get(download_url)
    
    # Save the CSV file
    if download_response.status_code == 200:
        with open("metar_comparison.csv", "wb") as f:
            f.write(download_response.content)
        print("Comparison CSV downloaded successfully!")
    else:
        print(f"Error downloading CSV: {download_response.json()['error']}")
```

### cURL Example

```bash
# Process METAR data
curl -X POST \
  -F "start_date=202404090000" \
  -F "end_date=202404100000" \
  -F "icao=VABB" \
  -F "forecast_file=@/path/to/forecast.txt" \
  http://localhost:5000/api/process_metar

# Get raw METAR data
curl -X GET \
  "http://localhost:5000/api/metar?start_date=202404090000&end_date=202404100000&icao=VABB"

# Download comparison CSV directly
curl -X POST \
  -F "start_date=202404090000" \
  -F "end_date=202404100000" \
  -F "icao=VABB" \
  -F "forecast_file=@/path/to/forecast.txt" \
  -o comparison.csv \
  http://localhost:5000/api/comparison_csv
```

## Error Handling

The API returns appropriate HTTP status codes and error messages for different error scenarios:

- `400 Bad Request`: Missing or invalid parameters
- `404 Not Found`: Requested resource not found
- `500 Internal Server Error`: Server-side errors

Example error response:

```json
{
  "error": "Missing required parameters. Please provide start_date, end_date, and icao."
}
```

## Dependencies

- Flask: Web framework
- Pandas: Data manipulation and analysis
- Requests: HTTP library for API calls
- metar: Library for parsing METAR reports

## License

[Specify license information here] 