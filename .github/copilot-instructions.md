# METAR GUI v2 - AI Coding Agent Instructions

## Project Overview
**METAR GUI v2** is a Flask-based web application for analyzing Meteorological Aerodrome Report (METAR) data. It fetches actual meteorological observations from OGIMET service, compares them with forecast data, and generates verification reports for forecast accuracy analysis. The system includes role-based authentication (user/admin/super_admin) and multi-airport support.

## Architecture & Data Flow

### Component Structure
```
app/
├── backend/           # Flask API + processing logic
│   ├── app.py        # App factory & initialization
│   ├── auth.py       # JWT-based authentication system
│   ├── models.py     # SQLAlchemy User model (SQLite)
│   ├── config.py     # Data directories + environment detection
│   └── routes/       # API/web blueprints
│       ├── api.py    # 1430-line core processing endpoint (/api/*)
│       └── web.py    # Page routing + METAR fetching
│   └── utils/        # Data processing utilities
│       ├── metar.py  # METAR parsing & CSV decoding
│       ├── ogimet*.py # External API calls to OGIMET service
│       ├── validation.py # ICAO/date range validation
│       └── upper_data_fetch.py # Upper air sounding data
└── frontend/         # HTML/JS served as static files
    ├── index.html    # Main dashboard
    ├── js/
    │   ├── app.js    # Core UI logic (2081 lines)
    │   ├── auth.js   # Auth flow
    │   └── admin.js/superadmin.js
    └── css/style.css # Tailwind-based styling
```

### Data Directory Structure
**Configured via `config.py`** - auto-detects Docker vs local:
- `app/data/metar_data/` - METAR observations (uploads/downloads subdirs)
- `app/data/upper_air_data/` - Upper air sounding data
- `app/data/ad_warn_data/` - Aerodrome warning processing workspace

Files flow: **OGIMET API → local file → CSV processing → downloads**

## Critical Patterns & Workflows

### 1. METAR Data Processing Pipeline
**File: [app/backend/routes/api.py](app/backend/routes/api.py#L1)** (primary endpoint)

```python
# POST /api/process_metar - multipart form with observation + forecast files
# Flow: Upload → Parse timestamps → Extract METAR features → Compare with forecast → CSV output
```

**Key steps:**
- `decode_metar_to_csv()` ([utils/metar.py](app/backend/utils/metar.py)) - Uses `metar.Metar` library to parse ICAO codes
- `extract_metar_features()` - Extracts wind_dir, wind_speed, temp, QNH from observations
- `compare_weather_data()` - Matches forecast vs observation timestamps, calculates accuracy metrics
- Files saved to `METAR_DOWNLOADS_DIR` with encoded paths for secure file serving

### 2. External Data Fetching
**Classes: `OgimetAPI` (standard) and `OgimetAPIAdWarn` (deprecated wrapper)**

- Calls `https://www.ogimet.com/display_metars2.php` with ICAO/date range parameters
- Returns raw METAR text lines (filtered to exclude comments starting with '#')
- Automatically saves to `AD_WARN_DIR/metar.txt` or `METAR_DATA_DIR`
- **Timeout: 60 seconds** - may fail for slow networks or large date ranges

### 3. Authentication & Authorization
**JWT tokens stored in cookies** ([auth.py](app/backend/auth.py))

```python
# Token structure: {"id", "username", "role", "station", "exp": +8 hours}
# Role hierarchy: user(1) < admin(2) < super_admin(3)
# Decorator: @require_role("admin") - blocks by role order
```

**Routes:**
- `/auth/signup` - Register user (uppercase username validation)
- `/auth/login` - JWT token issued, expires in 8 hours
- `/auth/me` - Get current user info

### 4. Data Validation Layer
**File: [utils/validation.py](app/backend/utils/validation.py)**

Before processing:
- `validate_station_code_match()` - ICAO codes must match between METAR & warning files
- `extract_metar_timestamps()` - Validates METAR date format (12-digit YYYYMMDDHHMM)
- `validate_date_range_match()` - Observation timestamps must fall within warning validity window

## Development Workflows

### Running Locally
```bash
# Install dependencies
pip install -r app/backend/requirements.txt

# Run Flask server (auto-reloads on code changes)
python app/backend/app.py  # Runs on http://localhost:5000
```

### Docker Deployment
```bash
# Uses Gunicorn + Nginx reverse proxy
docker-compose up -d --build
# Backend: port 5000 (internal), Frontend: port 8080 (public)
```

**Key environment variables** (see `.env.example`):
- `JWT_SECRET` - Must change in production
- `SUPER_ADMIN_PASSWORD` - Initial admin account
- Database: SQLite (`auth_test.db`)

### Key Dependencies
- **Flask 3.1.0** - Web framework
- **metar 1.11.0** - METAR decoding library (uses `Metar.Metar` class)
- **Requests** - HTTP calls to OGIMET
- **Pandas** - CSV processing
- **Plotly** - Interactive charts
- **PyPDF2** - PDF upload handling
- **SQLAlchemy** - ORM for User model

## Common Code Patterns

### File Path Handling
**Always use `config.py` constants**, not hardcoded paths:
```python
from app.backend.config import METAR_DATA_DIR, AD_WARN_DIR, DOCKER_VOLUME_MOUNT_POINT
# Ensures Windows + Docker + Linux compatibility
```

### Error Handling
**Generic try/except with silent failures is common** - check console logs:
```python
# Example from metar.py: "except Exception as e: pass  # print(f"Error...)")"
# Pattern: Log errors to stdout, return None or default value
```

### File Encoding
**Always use UTF-8** when reading/writing METAR files:
```python
with open(file_path, "w", encoding="utf-8") as f:
```

### Timestamp Formats
- **METAR times**: 12-digit `YYYYMMDDHHMM` (e.g., "202501201530")
- **Display**: `DDHHMM` format in some legacy code paths
- **Parsing**: Use `datetime.strptime()` with careful format handling (see `api.py:parse_validity_to_month_year()`)

## Integration Points & Dependencies

### OGIMET Service
- **Endpoint**: `https://www.ogimet.com/display_metars2.php`
- **Required params**: `lang=en`, `lugar={icao}`, `tipo=ALL`, date/time filters
- **Returns**: Plain text METAR lines (line-by-line format)
- **Failure mode**: 60-second timeout, returns empty file

### Frontend-Backend Communication
- **API calls from [js/app.js](app/frontend/js/app.js)**: `/api/process_metar`, `/api/get_metar`
- **File download encoding**: Uses base64+UUID token to prevent directory traversal
- **CORS**: Enabled with credentials support

### Database
- **SQLite at `instance/auth_test.db`**
- **Schema**: Single `users` table with columns: id, username, station_code, password_hash, role, is_active, created_at
- **Initialization**: Auto-creates on first run via `db.create_all()`

## Debugging Tips

1. **Check data directory structure** - Verify `METAR_DATA_DIR` and `AD_WARN_DIR` exist
2. **METAR parsing fails silently** - Look at console for decoding errors (exceptions caught in metar.py)
3. **File not found** - Files may be in unexpected subdirs (`uploads/` or `downloads/`)
4. **Date range validation** - Ensure METAR timestamps fall within warning file validity (common source of failures)
5. **OGIMET timeouts** - Check network connectivity; large date ranges may exceed 60-second timeout
6. **Token expiry** - JWT tokens expire after 8 hours; check `exp` claim in console Network tab

## Code Standards
- **Python**: Flask conventions, SQLAlchemy ORM, try/except with logging to console
- **JavaScript**: Vanilla JS (no frameworks), event-driven form handling, custom alert system
- **Naming**: UPPERCASE for constants/dirs, snake_case for functions/files
- **Comments**: Sparse; existing code uses emoji markers (✔, ✘, ✅)
