# Setup Guide - Environment Variables and PostgreSQL

This guide explains how to set up the `.env` file and PostgreSQL for local development.

## Part 1: Setting Up .env File

### Step 1: Create .env File

1. **Navigate to project root directory**
   ```bash
   cd metar_gui_v2
   ```

2. **Copy the example file**
   ```bash
   # On Windows (PowerShell)
   Copy-Item .env.example .env
   
   # On Windows (CMD)
   copy .env.example .env
   
   # On Linux/Mac
   cp .env.example .env
   ```

3. **Open .env file in a text editor**
   - Windows: Notepad, VS Code, or any text editor
   - Linux/Mac: nano, vim, or VS Code

### Step 2: Configure Environment Variables

Edit the `.env` file with your desired values:

```env
# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=metar_db
DB_USER=metar_user
DB_PASSWORD=your_secure_password_here

# Flask Secret Key (IMPORTANT: Generate a strong random key!)
SECRET_KEY=your-secret-key-change-in-production-12345

# Super Admin Default Credentials
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_EMAIL=admin@metar.local
SUPER_ADMIN_PASSWORD=YourSecureAdminPassword123!
```

### Step 3: Generate a Strong Secret Key

**Option A: Using Python**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Option B: Using OpenSSL (Linux/Mac)**
```bash
openssl rand -hex 32
```

**Option C: Online Generator**
- Visit: https://randomkeygen.com/
- Use "CodeIgniter Encryption Keys" or "Fort Knox Password"

Copy the generated key and paste it as `SECRET_KEY` in your `.env` file.

### Step 4: Set Strong Passwords

**For DB_PASSWORD:**
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, and symbols
- Example: `MetarDB2024!Secure`

**For SUPER_ADMIN_PASSWORD:**
- Minimum 12 characters
- Strong password for admin account
- Example: `Admin@Metar2024!Secure`

### Step 5: Verify .env File

Your final `.env` file should look like:
```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=metar_db
DB_USER=metar_user
DB_PASSWORD=MetarDB2024!Secure
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_EMAIL=admin@metar.local
SUPER_ADMIN_PASSWORD=Admin@Metar2024!Secure
```

### Important Notes:
- ✅ **Never commit .env to Git** (already in .gitignore)
- ✅ **Use different passwords** for production
- ✅ **Keep .env file secure** - don't share it
- ✅ **Change default admin password** before production

---

## Part 2: PostgreSQL Setup (For Local Development)

### Option A: Using Docker (Recommended - No Installation Needed)

If you're using Docker Compose, PostgreSQL runs automatically in a container. **No local installation needed!**

The `docker-compose.yml` already includes PostgreSQL:
```yaml
postgres:
  image: postgres:15-alpine
  # Automatically sets up database
```

**Just run:**
```bash
docker-compose up -d
```

PostgreSQL will be available at `localhost:5432` (if you expose the port).

---

### Option B: Install PostgreSQL Locally (For Development Without Docker)

#### Windows Installation:

1. **Download PostgreSQL**
   - Visit: https://www.postgresql.org/download/windows/
   - Or use installer: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
   - Download version 15 or newer

2. **Run Installer**
   - Run the downloaded `.exe` file
   - Follow installation wizard
   - **Remember the password** you set for `postgres` user
   - Default port: `5432` (keep this)
   - Default locale: `English, United States`

3. **Verify Installation**
   - Open "pgAdmin 4" (installed with PostgreSQL)
   - Or use Command Prompt:
     ```cmd
     psql --version
     ```

4. **Create Database and User**
   ```sql
   -- Connect to PostgreSQL (as postgres user)
   psql -U postgres
   
   -- Enter your postgres password when prompted
   
   -- Create database
   CREATE DATABASE metar_db;
   
   -- Create user
   CREATE USER metar_user WITH PASSWORD 'your_secure_password_here';
   
   -- Grant privileges
   GRANT ALL PRIVILEGES ON DATABASE metar_db TO metar_user;
   
   -- Exit
   \q
   ```

5. **Update .env File for Local Development**
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=metar_db
   DB_USER=metar_user
   DB_PASSWORD=your_secure_password_here
   ```

#### Linux Installation (Ubuntu/Debian):

1. **Install PostgreSQL**
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```

2. **Start PostgreSQL Service**
   ```bash
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   ```

3. **Create Database and User**
   ```bash
   # Switch to postgres user
   sudo -u postgres psql
   
   -- In PostgreSQL prompt:
   CREATE DATABASE metar_db;
   CREATE USER metar_user WITH PASSWORD 'your_secure_password_here';
   GRANT ALL PRIVILEGES ON DATABASE metar_db TO metar_user;
   \q
   ```

4. **Update .env File**
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=metar_db
   DB_USER=metar_user
   DB_PASSWORD=your_secure_password_here
   ```

#### Mac Installation:

1. **Using Homebrew**
   ```bash
   brew install postgresql@15
   brew services start postgresql@15
   ```

2. **Create Database and User**
   ```bash
   # Connect to PostgreSQL
   psql postgres
   
   -- In PostgreSQL prompt:
   CREATE DATABASE metar_db;
   CREATE USER metar_user WITH PASSWORD 'your_secure_password_here';
   GRANT ALL PRIVILEGES ON DATABASE metar_db TO metar_user;
   \q
   ```

3. **Update .env File**
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=metar_db
   DB_USER=metar_user
   DB_PASSWORD=your_secure_password_here
   ```

---

## Part 3: Testing the Setup

### Test Database Connection (Local PostgreSQL)

1. **Test connection**
   ```bash
   psql -h localhost -U metar_user -d metar_db
   # Enter password when prompted
   ```

2. **If connection successful**, you'll see:
   ```
   metar_db=>
   ```

3. **Exit**
   ```sql
   \q
   ```

### Test with Docker

1. **Start services**
   ```bash
   docker-compose up -d
   ```

2. **Check PostgreSQL logs**
   ```bash
   docker logs metar_postgres
   ```

3. **Check if database was created**
   ```bash
   docker exec -it metar_postgres psql -U metar_user -d metar_db -c "\dt"
   ```

---

## Part 4: Troubleshooting

### Issue: "Connection refused" or "Cannot connect to database"

**Solution:**
1. Check if PostgreSQL is running:
   ```bash
   # Windows
   services.msc (look for PostgreSQL service)
   
   # Linux
   sudo systemctl status postgresql
   
   # Mac
   brew services list
   ```

2. Check if port 5432 is available:
   ```bash
   # Windows
   netstat -an | findstr 5432
   
   # Linux/Mac
   netstat -an | grep 5432
   ```

3. Verify .env file has correct values

### Issue: "Authentication failed"

**Solution:**
1. Verify username and password in .env match PostgreSQL
2. Check PostgreSQL authentication settings:
   ```bash
   # Edit pg_hba.conf (location varies by OS)
   # Ensure: host all all 127.0.0.1/32 md5
   ```

### Issue: "Database does not exist"

**Solution:**
1. Create database manually:
   ```sql
   CREATE DATABASE metar_db;
   ```

2. Grant privileges:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE metar_db TO metar_user;
   ```

### Issue: Docker PostgreSQL not starting

**Solution:**
1. Check logs:
   ```bash
   docker logs metar_postgres
   ```

2. Remove old volume and restart:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

---

## Part 5: Development vs Production

### Development (Local)
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=metar_db
DB_USER=metar_user
DB_PASSWORD=dev_password_123
SECRET_KEY=dev-secret-key-not-for-production
```

### Production (Docker)
```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=metar_db
DB_USER=metar_user
DB_PASSWORD=STRONG_PRODUCTION_PASSWORD
SECRET_KEY=STRONG_RANDOM_SECRET_KEY
SUPER_ADMIN_PASSWORD=STRONG_ADMIN_PASSWORD
```

**Important:** Use environment variables or secrets management in production, not .env files!

---

## Quick Reference

### Common PostgreSQL Commands

```sql
-- List all databases
\l

-- Connect to database
\c metar_db

-- List all tables
\dt

-- List all users
\du

-- Exit
\q
```

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker logs metar_postgres
docker logs metar_backend

# Access PostgreSQL shell
docker exec -it metar_postgres psql -U metar_user -d metar_db
```

---

## Next Steps

1. ✅ Create `.env` file with your values
2. ✅ Install PostgreSQL (if not using Docker)
3. ✅ Create database and user
4. ✅ Test connection
5. ✅ Start application: `docker-compose up -d`
6. ✅ Access: http://localhost:8080
7. ✅ Login with super admin credentials

You're all set! 🚀

