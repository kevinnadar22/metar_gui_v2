# Windows Installation Guide

This guide helps resolve common installation issues on Windows, particularly with `psycopg2-binary`.

## Issue: psycopg2-binary Installation Error

### Error Message
```
Error: pg_config executable not found.
pg_config is required to build psycopg2 from source.
```

### Solution Options

#### Option 1: Install Pre-built Wheel (Recommended)

```powershell
# Update pip first
python -m pip install --upgrade pip

# Install psycopg2-binary directly
python -m pip install psycopg2-binary==2.9.9 --only-binary :all:

# Then install other requirements
python -m pip install -r app/backend/requirements.txt
```

#### Option 2: Use Alternative PostgreSQL Driver

If `psycopg2-binary` continues to fail, you can temporarily use `psycopg` (the newer version):

```powershell
# Edit requirements.txt and replace:
# psycopg2-binary==2.9.9
# with:
# psycopg[binary]==3.1.18

# Then install
python -m pip install -r app/backend/requirements.txt
```

#### Option 3: Install PostgreSQL Development Tools (For psycopg2 source build)

If you need to build from source:

1. **Download PostgreSQL for Windows**
   - Visit: https://www.postgresql.org/download/windows/
   - Download and install PostgreSQL (includes pg_config)

2. **Add to PATH**
   ```powershell
   # Add PostgreSQL bin directory to PATH
   # Usually: C:\Program Files\PostgreSQL\15\bin
   $env:PATH += ";C:\Program Files\PostgreSQL\15\bin"
   ```

3. **Install psycopg2**
   ```powershell
   python -m pip install psycopg2-binary==2.9.9
   ```

#### Option 4: Use Docker (Easiest - Recommended)

Instead of installing locally, use Docker which handles all dependencies:

```powershell
# Install Docker Desktop for Windows
# Then simply run:
docker-compose up -d --build
```

This avoids all Windows-specific installation issues!

## Complete Windows Setup Steps

### Method 1: Docker (Recommended - No Local Installation)

1. **Install Docker Desktop**
   - Download: https://www.docker.com/products/docker-desktop
   - Install and restart computer
   - Ensure WSL 2 is enabled

2. **Clone and Setup**
   ```powershell
   cd metar_gui_v2
   
   # Create .env file
   Copy-Item ENV_FILE_TEMPLATE.md .env
   # Edit .env with your values
   
   # Start services
   docker-compose up -d --build
   ```

3. **Access Application**
   - Open: http://localhost:8080

### Method 2: Local Python Installation

1. **Install Python 3.11+**
   - Download: https://www.python.org/downloads/
   - Check "Add Python to PATH" during installation

2. **Install PostgreSQL** (if not using Docker)
   - Download: https://www.postgresql.org/download/windows/
   - Remember the password you set

3. **Install Dependencies**
   ```powershell
   # Navigate to project
   cd metar_gui_v2
   
   # Create virtual environment (recommended)
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # Update pip
   python -m pip install --upgrade pip setuptools wheel
   
   # Install psycopg2-binary first (with workaround)
   python -m pip install psycopg2-binary==2.9.9 --only-binary :all:
   
   # Install other requirements
   python -m pip install -r app/backend/requirements.txt
   ```

4. **Create .env File**
   ```powershell
   # Copy template
   Copy-Item ENV_FILE_TEMPLATE.md .env
   
   # Edit .env - set DB_HOST=localhost for local PostgreSQL
   ```

5. **Run Application**
   ```powershell
   # Set environment variables
   $env:FLASK_APP="app.backend.app"
   $env:FLASK_ENV="development"
   
   # Run
   python -m flask run
   ```

## Troubleshooting psycopg2-binary on Windows

### Error: "Microsoft Visual C++ 14.0 or greater is required"

**Solution:**
```powershell
# Install Visual C++ Build Tools
# Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Or install pre-built wheel
python -m pip install psycopg2-binary==2.9.9 --only-binary :all: --no-cache-dir
```

### Error: "Failed building wheel for psycopg2-binary"

**Solution:**
```powershell
# Force use of binary wheel
python -m pip install psycopg2-binary==2.9.9 --only-binary psycopg2-binary

# If still fails, try older version
python -m pip install psycopg2-binary==2.9.5
```

### Error: "No module named 'psycopg2'"

**Solution:**
```powershell
# Verify installation
python -c "import psycopg2; print(psycopg2.__version__)"

# If fails, reinstall
python -m pip uninstall psycopg2-binary
python -m pip install psycopg2-binary==2.9.9 --no-cache-dir
```

## Alternative: Use SQLite for Development (No PostgreSQL Needed)

If you just want to test locally without PostgreSQL:

1. **Modify config.py temporarily:**
   ```python
   # Change SQLALCHEMY_DATABASE_URI to:
   SQLALCHEMY_DATABASE_URI = 'sqlite:///metar_dev.db'
   ```

2. **Remove psycopg2-binary from requirements.txt temporarily**

3. **Run application**

**Note:** SQLite has limitations and is not recommended for production.

## Recommended Approach for Windows

**Best Option: Use Docker**

Docker handles all dependencies and avoids Windows-specific issues:

```powershell
# 1. Install Docker Desktop
# 2. Enable WSL 2 backend
# 3. Run:
docker-compose up -d --build
```

This is the easiest and most reliable method on Windows!

## Quick Fix Script

Create a file `install-windows.ps1`:

```powershell
# install-windows.ps1
Write-Host "Installing dependencies for Windows..." -ForegroundColor Green

# Update pip
python -m pip install --upgrade pip setuptools wheel

# Install psycopg2-binary with workaround
Write-Host "Installing psycopg2-binary..." -ForegroundColor Yellow
python -m pip install psycopg2-binary==2.9.9 --only-binary :all: --no-cache-dir

# Install other requirements
Write-Host "Installing other requirements..." -ForegroundColor Yellow
python -m pip install -r app/backend/requirements.txt

Write-Host "Installation complete!" -ForegroundColor Green
```

Run with:
```powershell
.\install-windows.ps1
```

## Verification

After installation, verify:

```powershell
# Check psycopg2
python -c "import psycopg2; print('psycopg2:', psycopg2.__version__)"

# Check Flask
python -c "import flask; print('Flask:', flask.__version__)"

# Check SQLAlchemy
python -c "import flask_sqlalchemy; print('Flask-SQLAlchemy installed')"
```

## Still Having Issues?

1. **Use Docker** - Simplest solution
2. **Check Python version** - Need 3.11+
3. **Use virtual environment** - Avoids conflicts
4. **Check PATH** - Ensure Python is in PATH
5. **Run as Administrator** - Sometimes needed for system packages

