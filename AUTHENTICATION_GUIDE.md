# Authentication Guide

This guide explains the authentication system for the Local Buyer Intelligence Platform.

## Overview

The platform uses **JWT (JSON Web Tokens)** for authentication with role-based access control.

## User Roles

Three roles are supported:

1. **admin** - Full access, can create users, access all clients (if client_id is null)
2. **analyst** - Can analyze data, generate reports
3. **client** - Standard user, scoped to their client

## Authentication Flow

### 1. Login

**Endpoint**: `POST /api/v1/auth/login`

**Request** (OAuth2 compatible):
```
Content-Type: application/x-www-form-urlencoded

username=user@example.com
password=yourpassword
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Using the Token

Include the token in the Authorization header for all authenticated requests:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Get Current User

**Endpoint**: `GET /api/v1/auth/me`

**Response**:
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "role": "admin",
  "client_id": "uuid-here",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Creating Users

### Create Admin User (First Time Setup)

You need to create the first admin user programmatically. See `QUICK_START.md` for a Python script.

### Create Additional Users

**Endpoint**: `POST /api/v1/auth/register` (admin only)

**Request**:
```json
{
  "email": "newuser@example.com",
  "password": "securepassword",
  "role": "analyst",
  "client_id": "uuid-here"  // optional, null for global admin
}
```

## Frontend Authentication

The frontend handles authentication automatically:

1. **Login Page**: `/login` - Users enter credentials
2. **Token Storage**: Token stored in `localStorage` as `access_token`
3. **Auto-redirect**: Unauthenticated users redirected to `/login`
4. **Token Refresh**: Token included in all API requests via axios interceptor

### Logout

Call `authService.logout()` or click logout button - clears token and redirects to login.

## API Authentication

All API endpoints (except login) require authentication:

```bash
# Without token - will fail
curl http://localhost:8000/api/v1/geography/

# With token - will succeed
curl http://localhost:8000/api/v1/geography/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Multi-Tenancy

All data is scoped by `client_id`:

- Users belong to a client (or are global admins)
- All queries filter by `client_id` automatically
- Users cannot access other clients' data
- Global admins (client_id=null) can access all data

## Security Best Practices

1. **Change Default Passwords**: Always change default passwords
2. **Strong Passwords**: Use strong, unique passwords
3. **Token Expiration**: Tokens expire after 30 minutes (configurable)
4. **HTTPS in Production**: Always use HTTPS in production
5. **SECRET_KEY**: Use a strong, random SECRET_KEY in production

## Environment Variables

**Backend `.env`**:
```
SECRET_KEY=your-very-secure-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Generate a secure SECRET_KEY:
```python
import secrets
print(secrets.token_urlsafe(32))
```

## Troubleshooting

### "Could not validate credentials"

- Token expired - login again
- Token missing - include Authorization header
- Invalid token - clear localStorage and login again

### "User account is inactive"

- User account has been deactivated
- Contact admin to reactivate

### "Operation requires one of these roles: admin"

- User doesn't have required role
- Use admin account or request role change

### Frontend redirects to login immediately

- Token missing from localStorage
- Token expired
- Backend not running

## Example: Creating Users via API

```python
import requests

# Login as admin
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={
        "username": "admin@example.com",
        "password": "adminpassword"
    }
)
token = login_response.json()["access_token"]

# Create new user
headers = {"Authorization": f"Bearer {token}"}
create_user_response = requests.post(
    "http://localhost:8000/api/v1/auth/register",
    headers=headers,
    json={
        "email": "analyst@example.com",
        "password": "analystpassword",
        "role": "analyst",
        "client_id": "client-uuid-here"
    }
)
```

## Example: Using API with Authentication

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={"username": "user@example.com", "password": "password"}
)
token = response.json()["access_token"]

# Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}
geographies = requests.get(
    "http://localhost:8000/api/v1/geography/",
    headers=headers
)
print(geographies.json())
```

## See Also

- [QUICK_START.md](QUICK_START.md) - Initial setup including creating admin user
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup instructions
- API Documentation: http://localhost:8000/docs

