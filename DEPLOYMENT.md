# Deployment Guide

This guide explains how to deploy the METAR Dashboard with authentication system.

## Prerequisites

- Docker and Docker Compose installed
- At least 2GB of available RAM
- Port 8080 available (or modify in docker-compose.yml)

## Quick Start

1. **Clone the repository** (if not already done)
   ```bash
   git clone <repository-url>
   cd metar_gui_v2
   ```

2. **Create environment file** (optional, uses defaults if not created)
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and change the following:
   - `SECRET_KEY`: Generate a strong random secret key
   - `DB_PASSWORD`: Change the database password
   - `SUPER_ADMIN_PASSWORD`: Change the default admin password

3. **Build and start services**
   ```bash
   docker-compose up -d --build
   ```

4. **Access the application**
   - Open browser: `http://localhost:8080`
   - Default admin credentials (if using defaults):
     - Username: `admin`
     - Password: `Admin@123`

## Default Credentials

**IMPORTANT**: Change these in production!

- **Super Admin**:
  - Username: `admin` (or set via `SUPER_ADMIN_USERNAME`)
  - Email: `admin@metar.local` (or set via `SUPER_ADMIN_EMAIL`)
  - Password: `Admin@123` (or set via `SUPER_ADMIN_PASSWORD`)

## User Roles

1. **Super Admin**: Full access, can manage all users and their roles
2. **Admin**: Can delete users (except super admins)
3. **User**: Standard user with access to dashboard features

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=metar_db
DB_USER=metar_user
DB_PASSWORD=metar_password

# Flask Secret Key (REQUIRED in production!)
SECRET_KEY=your-secret-key-change-in-production-12345

# Super Admin Default Credentials
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_EMAIL=admin@metar.local
SUPER_ADMIN_PASSWORD=Admin@123
```

## Database

The application uses PostgreSQL. Data is persisted in a Docker volume `postgres_data`.

To backup the database:
```bash
docker exec metar_postgres pg_dump -U metar_user metar_db > backup.sql
```

To restore:
```bash
docker exec -i metar_postgres psql -U metar_user metar_db < backup.sql
```

## Stopping the Application

```bash
docker-compose down
```

To remove all data (including database):
```bash
docker-compose down -v
```

## Troubleshooting

### Database connection errors
- Ensure PostgreSQL container is healthy: `docker ps`
- Check logs: `docker logs metar_postgres`
- Verify environment variables are set correctly

### Authentication not working
- Clear browser cookies/session storage
- Check backend logs: `docker logs metar_backend`
- Verify SECRET_KEY is set in environment

### Port conflicts
- Change port in docker-compose.yml: `"0.0.0.0:8080:80"` to your desired port

## Production Considerations

1. **Change default passwords** in `.env` file
2. **Use strong SECRET_KEY** (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
3. **Enable HTTPS** by adding SSL certificates to nginx
4. **Set up regular database backups**
5. **Monitor logs**: `docker logs -f metar_backend`
6. **Resource limits**: Add resource limits in docker-compose.yml for production

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user info
- `GET /api/auth/users` - List all users (admin only)
- `DELETE /api/auth/users/<id>` - Delete user (admin only)
- `PUT /api/auth/users/<id>/role` - Update user role (super admin only)
- `PUT /api/auth/users/<id>/status` - Update user status (admin only)

## Security Notes

- All API routes (except auth) require authentication
- Passwords are hashed using Werkzeug's password hashing
- Sessions are stored server-side
- SQL injection protection via SQLAlchemy ORM
- CSRF protection recommended for production (add Flask-WTF)

