# Environment Configuration - Suggested Changes Summary

## Overview

This document summarizes the recommended changes to your `.env` file configuration based on the current application setup.

## Key Changes Made

### 1. Updated `docker-compose.yml`
- ✅ Added `env_file: - .env` to backend service (loads all variables from .env)
- ✅ Made Gunicorn workers and timeout configurable via environment variables
- ✅ Made nginx port configurable via `NGINX_PORT`
- ✅ Added `FLASK_ENV` and `DEBUG` environment variables

### 2. Created Documentation Files
- ✅ `ENV_FILE_TEMPLATE.md` - Complete .env file template
- ✅ `ENV_CONFIGURATION.md` - Detailed configuration guide
- ✅ `ENV_CHANGES_SUMMARY.md` - This file

## Recommended .env File Structure

### Minimum Required Variables

```env
# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=metar_db
DB_USER=metar_user
DB_PASSWORD=your_secure_password_here

# Flask Security
SECRET_KEY=your_generated_secret_key_64_chars

# Super Admin
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_EMAIL=admin@metar.local
SUPER_ADMIN_PASSWORD=your_secure_admin_password
```

### Recommended Additional Variables

```env
# Application Settings
FLASK_ENV=production
DEBUG=False

# Gunicorn Configuration
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120

# Nginx Configuration
NGINX_PORT=8080

# Logging
LOG_LEVEL=INFO
ENABLE_FILE_LOGGING=True
```

## Step-by-Step Setup

### Step 1: Create .env File

**Windows (PowerShell):**
```powershell
# Navigate to project directory
cd metar_gui_v2

# Create .env file
New-Item -Path .env -ItemType File

# Or copy from template
Copy-Item ENV_FILE_TEMPLATE.md .env
```

**Linux/Mac:**
```bash
cd metar_gui_v2
touch .env
# Or
cp ENV_FILE_TEMPLATE.md .env
```

### Step 2: Generate Secret Key

```bash
# Python (recommended)
python -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL (Linux/Mac)
openssl rand -hex 32
```

### Step 3: Fill in .env File

Open `.env` in a text editor and add:

```env
# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=metar_db
DB_USER=metar_user
DB_PASSWORD=MetarDB2024!Secure

# Security (paste generated key)
SECRET_KEY=paste_your_generated_key_here

# Admin
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_EMAIL=admin@metar.local
SUPER_ADMIN_PASSWORD=Admin@Metar2024!Secure

# Application
FLASK_ENV=production
DEBUG=False
```

### Step 4: Verify Configuration

```bash
# Check if .env file exists
ls -la .env  # Linux/Mac
dir .env     # Windows

# Verify variables are loaded (if using docker-compose)
docker-compose config
```

## Environment-Specific Recommendations

### Development Environment

```env
DB_HOST=postgres
DB_NAME=metar_db_dev
DB_PASSWORD=dev_password_123
SECRET_KEY=dev-secret-key-not-for-production
FLASK_ENV=development
DEBUG=True
LOG_LEVEL=DEBUG
SUPER_ADMIN_PASSWORD=Admin@123
```

### Production Environment

```env
DB_HOST=postgres
DB_NAME=metar_db_prod
DB_USER=metar_prod_user
DB_PASSWORD=STRONG_PRODUCTION_PASSWORD_12+_CHARS
SECRET_KEY=GENERATED_STRONG_SECRET_KEY_64_CHARS
FLASK_ENV=production
DEBUG=False
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120
LOG_LEVEL=INFO
SUPER_ADMIN_PASSWORD=STRONG_ADMIN_PASSWORD_12+_CHARS
```

## Important Security Recommendations

### 1. Password Strength
- **Database Password**: Minimum 12 characters, mixed case, numbers, symbols
- **Admin Password**: Minimum 12 characters, strong and unique
- **Example**: `MetarDB2024!Secure` or `Admin@Metar2024!Secure`

### 2. Secret Key
- **Length**: Minimum 64 characters (32 bytes = 64 hex chars)
- **Generation**: Use cryptographically secure random generator
- **Storage**: Never commit to version control
- **Rotation**: Change periodically in production

### 3. Default Values
- ❌ **Never use default passwords** in production
- ❌ **Never use default secret keys** in production
- ✅ **Change all defaults** before deployment
- ✅ **Use different values** for each environment

## Docker Compose Integration

The updated `docker-compose.yml` now:

1. **Loads .env file automatically** via `env_file: - .env`
2. **Uses environment variables** with fallback defaults
3. **Makes ports configurable** via `NGINX_PORT`
4. **Makes Gunicorn configurable** via `GUNICORN_WORKERS` and `GUNICORN_TIMEOUT`

### Benefits:
- ✅ Single source of truth (`.env` file)
- ✅ Easy environment switching
- ✅ Secure (not in version control)
- ✅ Flexible configuration

## Validation Checklist

Before deploying, ensure:

- [ ] `.env` file exists in project root
- [ ] `SECRET_KEY` is generated (not default)
- [ ] `DB_PASSWORD` is strong (12+ chars)
- [ ] `SUPER_ADMIN_PASSWORD` is strong (12+ chars)
- [ ] `SUPER_ADMIN_EMAIL` is valid
- [ ] `DEBUG=False` for production
- [ ] `FLASK_ENV=production` for production
- [ ] All default values changed
- [ ] `.env` is in `.gitignore` (verify)
- [ ] File permissions set correctly (chmod 600 on Linux/Mac)

## Testing Your Configuration

### 1. Test Environment Variables Load
```bash
# Start services
docker-compose up -d

# Check backend logs
docker logs metar_backend | grep -i "database\|secret\|admin"

# Verify database connection
docker exec metar_backend python -c "from app.backend.config import Config; print('DB:', Config.DB_NAME)"
```

### 2. Test Database Connection
```bash
# Connect to PostgreSQL
docker exec -it metar_postgres psql -U metar_user -d metar_db

# If successful, you'll see:
# metar_db=>
```

### 3. Test Application Startup
```bash
# Check if app starts without errors
docker-compose logs backend | tail -20

# Should see:
# ✅ Created default super admin: admin
# ✅ Data directories created or verified.
```

## Troubleshooting

### Issue: Variables not loading
**Solution:**
- Ensure `.env` file is in project root (same directory as docker-compose.yml)
- Check file has no syntax errors (no spaces around `=`)
- Restart containers: `docker-compose down && docker-compose up -d`

### Issue: Database connection fails
**Solution:**
- Verify `DB_HOST=postgres` (for Docker) or `DB_HOST=localhost` (for local)
- Check `DB_PASSWORD` matches PostgreSQL password
- Ensure PostgreSQL container is healthy: `docker ps`

### Issue: Secret key errors
**Solution:**
- Generate new key: `python -c "import secrets; print(secrets.token_hex(32))"`
- Ensure key is at least 64 characters
- Check for special characters that might need escaping

## Quick Reference

### Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Create .env File
```bash
# Copy template
cp ENV_FILE_TEMPLATE.md .env

# Edit with your values
nano .env  # or use your preferred editor
```

### Validate Configuration
```bash
docker-compose config
```

### Test Connection
```bash
docker-compose up -d
docker logs metar_backend
```

## Next Steps

1. ✅ Create `.env` file using template
2. ✅ Generate and set `SECRET_KEY`
3. ✅ Set strong passwords
4. ✅ Update admin credentials
5. ✅ Test with `docker-compose up`
6. ✅ Verify login works
7. ✅ Deploy to production

---

**Remember**: Never commit `.env` file to version control! It's already in `.gitignore`, but always double-check.

