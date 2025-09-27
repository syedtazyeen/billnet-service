# BillNet Service

Django REST API with JWT authentication.

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Configure environment:
```bash
cp env.example .env
# Edit .env with your settings
```

3. Setup database:
```bash
poetry run migrate
```

4. Run server:
```bash
poetry run start
```

## API

- **Docs**: http://127.0.0.1:8000/api/docs/
- **Auth**: `/api/auth/` (login, register, refresh)
- **Users**: `/api/users/`

## Authentication

Uses JWT tokens. Register/login to get access tokens for API requests.
