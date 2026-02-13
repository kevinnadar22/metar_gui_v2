# .env File Template and Configuration

This document provides the complete `.env` file template with all available options.

## Create Your .env File

Create a file named `.env` in the project root directory with the following content:

```env
# =============================================================================
# METAR Dashboard - Environment Configuration
# =============================================================================
# Copy this template to .env and update the values
# NEVER commit .env file to version control
# =============================================================================

# -----------------------------------------------------------------------------
# DATABASE CONFIGURATION (REQUIRED)
# -----------------------------------------------------------------------------
# For Docker: Use 'postgres' as DB_HOST (service name)
# For Local: Use 'localhost' as DB_HOST

DB_HOST=postgres
DB_PORT=5432
DB_NAME=metar_db
DB_USER=metar_user
DB_PASSWORD=metar_password

# -----------------------------------------------------------------------------
# FLASK SECURITY CONFIGURATION (REQUIRED)
# -----------------------------------------------------------------------------
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
# Or: openssl rand -hex 32

SECRET_KEY=change-this-secret-key-in-production-generate-with-secrets-token-hex-32

# Session lifetime in seconds (default: 86400 = 24 hours)
SESSION_LIFETIME=86400

# -----------------------------------------------------------------------------
# SUPER ADMIN ACCOUNT CONFIGURATION (REQUIRED)
# -----------------------------------------------------------------------------
# Default super admin account created on first startup
# IMPORTANT: Change these values before production!

SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_EMAIL=admin@metar.local
SUPER_ADMIN_PASSWORD=Admin@123

# -----------------------------------------------------------------------------
# APPLICATION SETTINGS (OPTIONAL)
# -----------------------------------------------------------------------------
# Flask environment: 'development' or 'production'
FLASK_ENV=production

# Debug mode: Set to 'False' in production
DEBUG=False

# Application host (for local development)
APP_HOST=0.0.0.0

# Application port (for local development)
APP_PORT=5000

# -----------------------------------------------------------------------------
# GUNICORN CONFIGURATION (OPTIONAL - Production)
# -----------------------------------------------------------------------------
# Number of worker processes (default: 4)
GUNICORN_WORKERS=4

# Worker timeout in seconds (default: 120)
GUNICORN_TIMEOUT=120

# -----------------------------------------------------------------------------
# NGINX CONFIGURATION (OPTIONAL)
# -----------------------------------------------------------------------------
# Port for nginx to listen on (default: 8080)
NGINX_PORT=8080

# -----------------------------------------------------------------------------
# LOGGING CONFIGURATION (OPTIONAL)
# -----------------------------------------------------------------------------
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Enable file logging (default: True)
ENABLE_FILE_LOGGING=True

# Log file path (relative to app directory)
LOG_FILE_PATH=logs/metar_dashboard.log

# -----------------------------------------------------------------------------
# SECURITY SETTINGS (OPTIONAL)
# -----------------------------------------------------------------------------
# Maximum login attempts before account lockout
MAX_LOGIN_ATTEMPTS=5

# Lockout duration in minutes
LOCKOUT_DURATION=15

# Password reset token expiration in hours
PASSWORD_RESET_EXPIRY=24
```

## Quick Setup Commands

### 1. Create .env file (Windows PowerShell)
```powershell
@"
DB_HOST=postgres
DB_PORT=5432
DB_NAME=metar_db
DB_USER=metar_user
DB_PASSWORD=MetarDB2024!Secure
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_EMAIL=admin@metar.local
SUPER_ADMIN_PASSWORD=Admin@Metar2024!Secure
"@ | Out-File -FilePath .env -Encoding utf8
```

### 2. Create .env file (Linux/Mac)
```bash
cat > .env << 'EOF'
DB_HOST=postgres
DB_PORT=5432
DB_NAME=metar_db
DB_USER=metar_user
DB_PASSWORD=MetarDB2024!Secure
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_EMAIL=admin@metar.local
SUPER_ADMIN_PASSWORD=Admin@Metar2024!Secure
EOF
```

### 3. Generate Secret Key Separately
```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL (Linux/Mac)
openssl rand -hex 32

# PowerShell (Windows)
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
```

## Environment-Specific Templates

### Development Template
```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=metar_db_dev
DB_USER=metar_user
DB_PASSWORD=dev_password_123
SECRET_KEY=dev-secret-key-not-for-production-12345
FLASK_ENV=development
DEBUG=True
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_EMAIL=admin@metar.local
SUPER_ADMIN_PASSWORD=Admin@123
LOG_LEVEL=DEBUG
```

### Production Template
```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=metar_db_prod
DB_USER=metar_prod_user
DB_PASSWORD=STRONG_PRODUCTION_DB_PASSWORD
SECRET_KEY=GENERATED_STRONG_SECRET_KEY_64_CHARS
FLASK_ENV=production
DEBUG=False
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_EMAIL=admin@yourdomain.com
SUPER_ADMIN_PASSWORD=STRONG_ADMIN_PASSWORD
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120
LOG_LEVEL=INFO
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=15
```

## Variable Reference

### Required Variables

| Variable | Example | Description |
|----------|---------|-------------|
| `DB_HOST` | `postgres` or `localhost` | PostgreSQL hostname |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `metar_db` | Database name |
| `DB_USER` | `metar_user` | Database username |
| `DB_PASSWORD` | `SecurePass123!` | Database password |
| `SECRET_KEY` | `64-char-hex-string` | Flask secret key |
| `SUPER_ADMIN_USERNAME` | `admin` | Admin username |
| `SUPER_ADMIN_EMAIL` | `admin@metar.local` | Admin email |
| `SUPER_ADMIN_PASSWORD` | `Admin@123` | Admin password |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SESSION_LIFETIME` | `86400` | Session timeout (seconds) |
| `FLASK_ENV` | `production` | Flask environment |
| `DEBUG` | `False` | Debug mode |
| `GUNICORN_WORKERS` | `4` | Worker processes |
| `GUNICORN_TIMEOUT` | `120` | Worker timeout |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_LOGIN_ATTEMPTS` | `5` | Login attempt limit |
| `LOCKOUT_DURATION` | `15` | Lockout duration (minutes) |

## Validation Checklist

Before deploying, verify:

- [ ] `SECRET_KEY` is generated (not default value)
- [ ] `DB_PASSWORD` is strong (12+ characters)
- [ ] `SUPER_ADMIN_PASSWORD` is strong (12+ characters)
- [ ] `SUPER_ADMIN_EMAIL` is valid email
- [ ] `DEBUG=False` for production
- [ ] `FLASK_ENV=production` for production
- [ ] All default passwords changed
- [ ] `.env` file is NOT in Git (check `.gitignore`)

## Security Notes

1. **Never commit `.env`** - It's in `.gitignore` but double-check
2. **Use different values** for dev/staging/production
3. **Rotate secrets** periodically in production
4. **Restrict file permissions** (chmod 600 on Linux/Mac)
5. **Use secrets management** in cloud deployments (AWS Secrets Manager, etc.)

