# ticknet Service

A Django REST Framework API for a comprehensive event management system with Swagger documentation and Uvicorn server.

## Features

- **Django REST Framework** for robust API development
- **Swagger/OpenAPI Documentation** with drf-spectacular
- **Uvicorn ASGI Server** for high-performance async support
- **CORS Support** for frontend integration
- **JWT Authentication** with SimpleJWT for secure API access
- **Custom User Model** with email authentication
- **Pagination** for large datasets
- **Custom Exception Handling** for better error responses
- **PostgreSQL Database** support
- **Poetry** for dependency management

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Poetry (for dependency management)
- PostgreSQL database

Install Poetry if you haven't already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Install PostgreSQL if you haven't already:
```bash
# macOS (using Homebrew)
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Windows
# Download from https://www.postgresql.org/download/windows/
```

### 1. Install Dependencies

```bash
poetry install
```

### 2. Environment Setup

Copy the environment example file and configure your settings:

```bash
cp env.example .env
```

Edit `.env` file with your configuration:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Server Settings
HOST=127.0.0.1
PORT=8000

# Database Settings (PostgreSQL)
DB_NAME=ticknet
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
```

### 3. Database Setup

First, create the PostgreSQL database:
```bash
# Connect to PostgreSQL
psql -U postgres

# Create the database
CREATE DATABASE ticknet;

# Exit psql
\q
```

Then run Django migrations:
```bash
poetry run python manage.py makemigrations
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
```

### 4. Run the Server

#### Option 1: Using the custom runner (Recommended)
```bash
poetry run python run.py
```

#### Option 2: Using Uvicorn directly
```bash
poetry run uvicorn config.asgi:application --host 127.0.0.1 --port 8000 --reload
```

#### Option 3: Using Django's development server
```bash
poetry run python manage.py runserver
```

### 5. Quick Setup Script

You can also use the automated setup script:

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

## API Endpoints

### Documentation
- **Swagger UI**: http://127.0.0.1:8000/api/docs/
- **OpenAPI Schema**: http://127.0.0.1:8000/api/schema/

### API Endpoints
- **Authentication**: `/api/auth/` (login, register, refresh, logout)
- **Users**: `/api/users/` (user management)

## Authentication

The API uses JWT (JSON Web Token) authentication with SimpleJWT. Here's how to authenticate:

### Register a new user:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your-password",
    "password_confirm": "your-password"
  }'
```

### Login to get tokens:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your-password"
  }'
```

### Use the access token in API requests:
```bash
curl -X GET http://127.0.0.1:8000/api/users/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Refresh your token:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

## Development

### Project Structure
```
service/
├── manage.py
├── pyproject.toml
├── run.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── urls.py
│   ├── migrations/
│   ├── auth/
│   │   ├── views.py
│   │   └── serializers.py
│   └── users/
│       ├── models.py
│       ├── views.py
│       └── serializers.py
├── core/
│   ├── exceptions.py
│   ├── pagination.py
│   └── permissions.py
└── scripts/
    └── setup.sh
```

### Key Features

1. **User Management**: User registration, authentication, and profile management
2. **JWT Authentication**: Secure token-based authentication with refresh tokens
3. **Custom User Model**: Email-based authentication instead of username
4. **API Documentation**: Auto-generated Swagger/OpenAPI documentation
5. **CORS Support**: Frontend integration support
6. **Custom Exception Handling**: Consistent error responses
7. **Pagination**: Handle large datasets efficiently
8. **Database Migrations**: Proper database schema management

### Poetry Scripts

The project includes convenient Poetry scripts:

```bash
# Start the server
poetry run start

# Run migrations
poetry run makemigrations
poetry run migrate
```

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in your environment
2. Configure proper `ALLOWED_HOSTS`
3. Use a production database (PostgreSQL recommended)
4. Set up proper logging and monitoring
5. Use a reverse proxy (nginx) with Uvicorn workers
6. Set up SSL/TLS certificates
7. Configure environment variables securely

## License

This project is licensed under the MIT License.
