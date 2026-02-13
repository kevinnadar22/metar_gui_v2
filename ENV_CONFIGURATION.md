# Environment Configuration Guide

This guide explains how to configure the `.env` file for different environments.

## Quick Start

1. **Copy the appropriate example file:**
   ```bash
   # For Docker deployment (recommended)
   cp .env.example .env
   
   # For local development
   cp .env.development.example .env
   
   # For production
   cp .env.production.example .env
   ```

2. **Edit `.env` file** with your values
3. **Generate secret key** (see below)
4. **Set strong passwords** for database and admin

## Required Variables

### Minimum Required Configuration

```env
# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=metar_db
DB_USER=metar_user
DB_PASSWORD=your_secure_password

# Security
SECRET_KEY=your_generated_secret_key

# Admin
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_EMAIL=admin@metar.local
SUPER_ADMIN_PASSWORD=your_secure_admin_password
```

## Generating Secret Key

### Method 1: Python (Recommended)
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Method 2: OpenSSL (Linux/Mac)
```bash
openssl rand -hex 32
```

### Method 3: PowerShell (Windows)
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
```

## Environment-Specific Configurations

### Development (Local, No Docker)

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=metar_db_dev
DB_USER=metar_user
DB_PASSWORD=dev_password_123
SECRET_KEY=dev-secret-key-not-for-production
FLASK_ENV=development
DEBUG=True
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_EMAIL=admin@localhost
SUPER_ADMIN_PASSWORD=Admin@123
```

### Development (Docker)

```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=metar_db
DB_USER=metar_user
DB_PASSWORD=dev_password_123
SECRET_KEY=dev-secret-key-not-for-production
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_EMAIL=admin@metar.local
SUPER_ADMIN_PASSWORD=Admin@123
```

### Production (Docker)

```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=metar_db_prod
DB_USER=metar_prod_user
DB_PASSWORD=STRONG_PRODUCTION_PASSWORD
SECRET_KEY=GENERATED_STRONG_SECRET_KEY
FLASK_ENV=production
DEBUG=False
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_EMAIL=admin@yourdomain.com
SUPER_ADMIN_PASSWORD=STRONG_ADMIN_PASSWORD
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120
```

## Variable Descriptions

### Database Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DB_HOST` | PostgreSQL hostname | `postgres` | Yes |
| `DB_PORT` | PostgreSQL port | `5432` | Yes |
| `DB_NAME` | Database name | `metar_db` | Yes |
| `DB_USER` | Database username | `metar_user` | Yes |
| `DB_PASSWORD` | Database password | `metar_password` | Yes |

**Notes:**
- For Docker: Use `postgres` (service name)
- For Local: Use `localhost` or `127.0.0.1`

### Security Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Flask secret key for sessions | - | **Yes** |
| `SESSION_LIFETIME` | Session timeout in seconds | `86400` (24h) | No |

**Important:** Always generate a unique, strong `SECRET_KEY` for production!

### Super Admin Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SUPER_ADMIN_USERNAME` | Admin username | `admin` | Yes |
| `SUPER_ADMIN_EMAIL` | Admin email | `admin@metar.local` | Yes |
| `SUPER_ADMIN_PASSWORD` | Admin password | `Admin@123` | Yes |

**Important:** Change these before production deployment!

### Application Variables (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `production` |
| `DEBUG` | Enable debug mode | `False` |
| `APP_HOST` | Application host | `0.0.0.0` |
| `APP_PORT` | Application port | `5000` |

### Gunicorn Variables (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `GUNICORN_WORKERS` | Number of worker processes | `4` |
| `GUNICORN_TIMEOUT` | Worker timeout (seconds) | `120` |

### Logging Variables (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | `INFO` |
| `ENABLE_FILE_LOGGING` | Enable file logging | `True` |
| `LOG_FILE_PATH` | Log file path | `logs/metar_dashboard.log` |

## Password Requirements

### Database Password
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- Example: `MetarDB2024!Secure`

### Admin Password
- Minimum 12 characters
- Strong password for admin account
- Example: `Admin@Metar2024!Secure`

### Secret Key
- Minimum 32 characters (64 hex characters recommended)
- Random and unpredictable
- Never reuse across environments

## Security Best Practices

1. ✅ **Never commit `.env` to Git** (already in `.gitignore`)
2. ✅ **Use different values for each environment**
3. ✅ **Generate strong, unique secret keys**
4. ✅ **Use strong passwords** (12+ characters, mixed case, numbers, symbols)
5. ✅ **Change default admin credentials** before production
6. ✅ **Rotate secrets periodically** in production
7. ✅ **Use environment-specific files** (`.env.development`, `.env.production`)
8. ✅ **Restrict file permissions** (chmod 600 on Linux/Mac)

## Validation

After creating your `.env` file, validate it:

```bash
# Check if all required variables are set
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
required = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'SECRET_KEY']
missing = [v for v in required if not os.getenv(v)]
if missing:
    print(f'Missing: {missing}')
else:
    print('✅ All required variables present')
"
```

## Troubleshooting

### Issue: "Environment variable not found"
- Check `.env` file exists in project root
- Verify variable name spelling (case-sensitive)
- Ensure no extra spaces around `=`

### Issue: "Database connection failed"
- Verify `DB_HOST` is correct (`postgres` for Docker, `localhost` for local)
- Check `DB_PASSWORD` matches PostgreSQL password
- Ensure PostgreSQL is running

### Issue: "Invalid secret key"
- Generate new key using methods above
- Ensure key is at least 32 characters
- Check for special characters that might need escaping

## Example .env Files

### Minimal Working Example
```env
DB_HOST=postgres
DB_NAME=metar_db
DB_USER=metar_user
DB_PASSWORD=SecurePass123!
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_EMAIL=admin@metar.local
SUPER_ADMIN_PASSWORD=AdminSecure123!
```

### Full Production Example
```env
# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=metar_db_prod
DB_USER=metar_prod_user
DB_PASSWORD=Str0ng!Pr0d@DB#P@ss2024

# Security
SECRET_KEY=7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2

# Admin
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_EMAIL=admin@yourdomain.com
SUPER_ADMIN_PASSWORD=Str0ng!Adm1n@P@ss2024

# Application
FLASK_ENV=production
DEBUG=False

# Gunicorn
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120

# Logging
LOG_LEVEL=INFO
ENABLE_FILE_LOGGING=True
```

## Next Steps

1. ✅ Copy appropriate `.env.example` file to `.env`
2. ✅ Generate strong `SECRET_KEY`
3. ✅ Set strong passwords
4. ✅ Update admin credentials
5. ✅ Test configuration with `docker-compose up`
6. ✅ Verify database connection
7. ✅ Test login with admin credentials

