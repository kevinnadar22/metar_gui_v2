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
   git clone https://github.com/kevinnadar22/metar_gui_v2
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

### Get Raw METAR Data

```
GET /api/get_metar
```

Retrieve raw METAR data for a specific airport and date range.

#### Parameters

- `start_date`: Start date in format YYYYMMDDHHMM
- `end_date`: End date in format YYYYMMDDHHMM
- `icao`: ICAO code for the airport

#### Response

Returns a text file containing the raw METAR data.

### Process METAR Data

```
POST /api/process_metar
```

Process METAR data by fetching observations and comparing them with forecast data.

#### Request

Content-Type: `multipart/form-data`

Form fields:
- `start_date`: Start date for METAR data in format YYYYMMDDHHMM (optional if observation_file is provided)
- `end_date`: End date for METAR data in format YYYYMMDDHHMM (optional if observation_file is provided)
- `icao`: ICAO code for the airport (e.g., "VABB" for Mumbai)
- `forecast_file`: Text file containing forecast data
- `observation_file`: Text file containing METAR observations (optional if start_date and end_date are provided)

#### Forecast File Format

The forecast file should be a text file named in the format MMYYYY.txt (e.g., 012023.txt for January 2023) with the following format:
- Each line should contain space-separated values in the format: `YYYYMMDDHHMM WIND TEMP QFE QNH`
- Example:
```
TIME 	WIND	TEMP	QFE 	QNH
0000Z 000/00KT	28	1008	1009
0100Z	070/04KT	28	1008	1009
0200Z	090/04KT        29	1009	1010
0300Z	110/05KT	29	1009	1010
0400Z   130/05KT	29	1010	1011
0500Z	030/05KT	30	1010	1011
0600Z	270/10KT 	31	1009	1010
0700Z	290/08KT	32	1008	1009
0800Z	300/10KT	33	1007	1008
0900Z	290/12KT	33	1007	1008
1000Z   280/12KT	32	1006	1007
```

#### Response

```json
{
  "status": "success",
  "message": "METAR data processed successfully",
  "metrics": {
    "total_comparisons": 24,
    "accurate_predictions": 0,
    "accuracy_percentage": 0.0
  },
  "file_paths": {
    "metar_file": "<encoded_path>",
    "metar_csv": "<encoded_path>",
    "comparison_csv": "<encoded_path>"
  }
}
```

### Download Files

```
GET /api/download/<file_type>
```

Download generated files.

#### Parameters

- `file_type`: Type of file to download ('metar', 'metar_csv', 'comparison_csv')
- `file_path`: Encoded path to the file (from the process_metar response)

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


### cURL Example

```bash
# Get raw METAR data
curl -X GET \
  "http://localhost:5000/api/get_metar?start_date=202404090000&end_date=202404100000&icao=VABB" \
  -o metar_data.txt

# Process METAR data with forecast file
curl -X POST \
  -F "start_date=202404090000" \
  -F "end_date=202404100000" \
  -F "icao=VABB" \
  -F "forecast_file=@/path/to/forecast.txt" \
  http://localhost:5000/api/process_metar

# Process METAR data with observation file
curl -X POST \
  -F "icao=VABB" \
  -F "forecast_file=@/path/to/forecast.txt" \
  -F "observation_file=@/path/to/metar_data.txt" \
  http://localhost:5000/api/process_metar
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