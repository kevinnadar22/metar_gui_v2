# Fix psycopg2-binary Installation on Windows

## Quick Fix (PowerShell)

Run these commands in PowerShell:

```powershell
# Navigate to project directory (if not already there)
cd C:\Users\Aryan\Documents\GitHub\metar_gui_v2

# Update pip first
python -m pip install --upgrade pip setuptools wheel

# Install psycopg2-binary using pre-built wheel (avoids compilation)
python -m pip install psycopg2-binary==2.9.9 --only-binary :all: --no-cache-dir

# Verify installation
python -c "import psycopg2; print('Success! psycopg2 version:', psycopg2.__version__)"

# If successful, install other requirements
python -m pip install -r app/backend/requirements.txt
```

## Alternative Solutions

### Option 1: Use Docker (Easiest - Recommended)

Instead of installing locally, use Docker which handles all dependencies:

```powershell
# Install Docker Desktop for Windows first
# Then simply run:
docker-compose up -d --build
```

This completely avoids Windows installation issues!

### Option 2: Install Visual C++ Build Tools

If the above doesn't work, install build tools:

1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "C++ build tools" workload
3. Retry installation

### Option 3: Use Older Version

```powershell
python -m pip install psycopg2-binary==2.9.5 --no-cache-dir
```

### Option 4: Install PostgreSQL (Provides pg_config)

1. Download PostgreSQL: https://www.postgresql.org/download/windows/
2. Install (includes pg_config)
3. Add to PATH: `C:\Program Files\PostgreSQL\15\bin`
4. Retry installation

## Step-by-Step Fix

### Step 1: Open PowerShell as Administrator

Right-click PowerShell → "Run as Administrator"

### Step 2: Navigate to Project

```powershell
cd C:\Users\Aryan\Documents\GitHub\metar_gui_v2
```

### Step 3: Update pip

```powershell
python -m pip install --upgrade pip setuptools wheel
```

### Step 4: Install psycopg2-binary

```powershell
# Method 1: Force binary wheel
python -m pip install psycopg2-binary==2.9.9 --only-binary :all: --no-cache-dir

# If that fails, try Method 2:
python -m pip install psycopg2-binary==2.9.9 --no-cache-dir

# If still fails, try Method 3 (older version):
python -m pip install psycopg2-binary==2.9.5 --no-cache-dir
```

### Step 5: Verify

```powershell
python -c "import psycopg2; print('psycopg2 installed:', psycopg2.__version__)"
```

### Step 6: Install Other Requirements

```powershell
python -m pip install -r app/backend/requirements.txt
```

## Complete Installation Script

Copy and paste this entire block into PowerShell:

```powershell
# METAR Dashboard - Windows Installation Fix
Write-Host "Updating pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel

Write-Host "Installing psycopg2-binary..." -ForegroundColor Yellow
python -m pip install psycopg2-binary==2.9.9 --only-binary :all: --no-cache-dir

Write-Host "Verifying installation..." -ForegroundColor Yellow
python -c "import psycopg2; print('Success! psycopg2 version:', psycopg2.__version__)"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Installing other requirements..." -ForegroundColor Yellow
    python -m pip install -r app/backend/requirements.txt
    Write-Host "Installation complete!" -ForegroundColor Green
} else {
    Write-Host "psycopg2-binary installation failed. Try Docker instead!" -ForegroundColor Red
}
```

## Why This Error Occurs

The error "pg_config executable not found" happens because:
- `psycopg2-binary` sometimes tries to build from source on Windows
- Building requires PostgreSQL development tools (pg_config)
- The binary wheel should work without these tools

## Best Solution: Use Docker

**Recommended approach for Windows:**

1. Install Docker Desktop: https://www.docker.com/products/docker-desktop
2. Enable WSL 2 backend
3. Run: `docker-compose up -d --build`

This avoids all Windows-specific installation issues!

## Verification

After installation, test:

```powershell
# Test imports
python -c "import psycopg2; print('psycopg2: OK')"
python -c "import flask; print('Flask: OK')"
python -c "import flask_sqlalchemy; print('Flask-SQLAlchemy: OK')"
```

All should print "OK" without errors.

