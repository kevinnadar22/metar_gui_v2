# Validation Features for Aerodrome Warning Verification

## Overview

The aerodrome warning verification system now includes comprehensive validation features that ensure data integrity before processing. These validations help prevent errors and provide clear feedback to users when issues are detected.

## Validation Features

### 1. Station Code Match Validation

**Purpose**: Ensures that the METAR data and aerodrome warning files are for the same station.

**Process**:
- Extracts ICAO station codes from both the uploaded `metar.txt` file and `ad_warn.txt` file
- Compares the extracted codes for exact match
- If codes don't match, shows an alert with both codes

**Error Message**: `"Station code mismatch: METAR = <code1>, Warning = <code2>"`

**Supported Formats**:
- METAR files: `VABB 202312011200Z ...` or similar formats
- Warning files: `VABB 20231201` or similar formats

### 2. Date Range Validation

**Purpose**: Ensures that METAR data falls within a valid 30-day period from the warning issue date.

**Process**:
- Extracts the issue date from the first line of the warning file (YYYYMMDD format)
- Calculates a 30-day range starting from the issue date
- Extracts timestamps from METAR records (YYYYMMDDHHMM format)
- Validates that at least one METAR timestamp falls within the 30-day range

**Error Message**: `"No METAR data falls within the valid warning period (within 30 days)"`

**Supported Date Formats**:
- Warning issue date: YYYYMMDD, DDMMYYYY
- METAR timestamps: YYYYMMDDHHMM, DDHHMMZ (with year extraction)

## Implementation Details

### Backend Validation

The validation is implemented in `app/utils/validation.py` with the following key functions:

- `validate_files()`: Main validation function that performs both checks
- `validate_station_code_match()`: Validates station code matching
- `validate_date_range_match()`: Validates date range compatibility
- `extract_icao_from_metar()`: Extracts ICAO codes from METAR files
- `extract_icao_from_warning()`: Extracts ICAO codes from warning files
- `extract_issue_date_from_warning()`: Extracts issue dates from warning files
- `extract_metar_timestamps()`: Extracts timestamps from METAR files

### API Integration

The validation is integrated into the `/api/adwrn_verify` endpoint:

1. **Pre-processing Validation**: Validation occurs before any file processing
2. **Error Response**: Returns detailed error messages with validation context
3. **Success Response**: Includes validation information in successful responses

### Frontend Integration

The frontend JavaScript (`app/static/js/app.js`) handles validation errors:

1. **Enhanced Error Messages**: Provides context-specific error messages
2. **User-Friendly Alerts**: Uses the existing `showCustomAlert()` function
3. **Detailed Feedback**: Explains what needs to be corrected

## Error Handling

### Station Code Mismatch
```
Error: Station code mismatch: METAR = VABB, Warning = VAPO

Please ensure both files are for the same station.
```

### Date Range Issues
```
Error: No METAR data falls within the valid warning period (within 30 days)

Please check that the METAR data covers the warning period and that the warning file contains a valid issue date.
```

## File Format Requirements

### METAR File Format
- Must contain ICAO station codes (4 uppercase letters)
- Must contain timestamps in YYYYMMDDHHMM or DDHHMMZ format
- Example: `VABB 202312011200Z 12015G25KT 9999 FEW020 SCT100 25/18 Q1013`

### Warning File Format
- Must contain ICAO station codes (4 uppercase letters)
- Must contain issue date in YYYYMMDD or DDMMYYYY format in the first few lines
- Example: `VABB 20231201` or `VABB 01122023`

## Benefits

1. **Prevents Processing Errors**: Catches issues before expensive processing
2. **Clear User Feedback**: Provides specific error messages explaining the problem
3. **Data Integrity**: Ensures files are compatible before verification
4. **User Experience**: Helps users understand what needs to be corrected
5. **Robust Parsing**: Handles multiple file formats and date formats

## Testing

The validation system has been tested with various file formats and edge cases:

- ✅ Matching station codes
- ✅ Non-matching station codes
- ✅ Valid date ranges
- ✅ Invalid date ranges
- ✅ Different timestamp formats
- ✅ Different date formats

## Future Enhancements

Potential improvements for future versions:

1. **Additional File Format Support**: Support for more METAR and warning file formats
2. **Configurable Validation Rules**: Allow users to adjust validation parameters
3. **Batch Validation**: Validate multiple file pairs at once
4. **Validation History**: Track validation results for quality assurance
5. **Advanced Date Parsing**: Support for more complex date/time formats 