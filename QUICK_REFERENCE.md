# 🚀 Quick Reference - Movie Reservation System

## Essential Commands

### Starting the Server
```powershell
cd "c:\Users\User\OneDrive\Desktop\movie reservation system\backend"
.\venv\Scripts\activate
uvicorn src.main:app --reload
```

### Database Operations
```powershell
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Reset and reseed database
psql -U postgres -c "DROP DATABASE IF EXISTS movie_reservation;"
psql -U postgres -c "CREATE DATABASE movie_reservation;"
alembic upgrade head
python scripts\seed_data.py
```

### Testing
```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests\test_auth.py -v
```

---

## Default Credentials

**Admin Account:**
- Email: `admin@example.com`
- Password: `admin123`

**Test Users:**
- Email: `john.doe@example.com` / Password: `password123`
- Email: `jane.smith@example.com` / Password: `password123`

---

## API Endpoint Quick Reference

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | None | Register new user |
| POST | `/api/v1/auth/login` | None | Login and get token |
| GET | `/api/v1/auth/me` | User | Get current user profile |

### Movies
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/movies` | None | List all movies |
| GET | `/api/v1/movies/{id}` | None | Get movie details |
| GET | `/api/v1/movies/{id}/showtimes` | None | Get movie showtimes |
| POST | `/api/v1/movies` | Admin | Create movie |
| PUT | `/api/v1/movies/{id}` | Admin | Update movie |
| DELETE | `/api/v1/movies/{id}` | Admin | Delete movie |

### Showtimes
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/showtimes/{id}` | None | Get showtime details |
| POST | `/api/v1/showtimes` | Admin | Create showtime |
| PUT | `/api/v1/showtimes/{id}` | Admin | Update showtime |
| DELETE | `/api/v1/showtimes/{id}` | Admin | Delete showtime |

### Reservations
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/showtimes/{id}/seats` | None | View seat availability |
| POST | `/api/v1/showtimes/{id}/lock-seats` | User | Lock seats (10 min) |
| POST | `/api/v1/reservations` | User | Create reservation |
| GET | `/api/v1/reservations` | User | View my reservations |
| DELETE | `/api/v1/reservations/{id}` | User | Cancel reservation |

### Admin Reports
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/admin/reports/capacity` | Admin | Capacity utilization |
| GET | `/api/v1/admin/reports/revenue` | Admin | Revenue analytics |
| GET | `/api/v1/admin/reports/popular-movies` | Admin | Popular movies |
| POST | `/api/v1/admin/users/{id}/promote` | Admin | Promote/demote user |

---

## cURL Examples

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

### Create Movie (Admin)
```bash
curl -X POST "http://localhost:8000/api/v1/movies" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"New Movie",
    "description":"Description here",
    "genre":"Action",
    "duration_minutes":120,
    "release_date":"2025-12-31"
  }'
```

### Get Seat Availability
```bash
curl -X GET "http://localhost:8000/api/v1/showtimes/SHOWTIME_ID/seats"
```

### Lock Seats
```bash
curl -X POST "http://localhost:8000/api/v1/showtimes/SHOWTIME_ID/lock-seats" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"seat_ids":["SEAT_ID_1","SEAT_ID_2"]}'
```

### Create Reservation
```bash
curl -X POST "http://localhost:8000/api/v1/reservations" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "showtime_id":"SHOWTIME_ID",
    "seat_ids":["SEAT_ID_1","SEAT_ID_2"]
  }'
```

---

## Common Workflows

### As a User - Making a Reservation

1. **Register/Login**
   - POST `/api/v1/auth/register` or `/api/v1/auth/login`
   - Save the `access_token`

2. **Browse Movies**
   - GET `/api/v1/movies`
   - Select a movie

3. **View Showtimes**
   - GET `/api/v1/movies/{movie_id}/showtimes`
   - Select a showtime

4. **Check Seat Availability**
   - GET `/api/v1/showtimes/{showtime_id}/seats`
   - Choose available seats

5. **Lock Seats**
   - POST `/api/v1/showtimes/{showtime_id}/lock-seats`
   - Provide `seat_ids` array
   - You have 10 minutes

6. **Create Reservation**
   - POST `/api/v1/reservations`
   - Provide `showtime_id` and `seat_ids`
   - Receive confirmation

7. **View Reservations**
   - GET `/api/v1/reservations`
   - See all your bookings

8. **Cancel if Needed**
   - DELETE `/api/v1/reservations/{reservation_id}`
   - Only before showtime starts

### As an Admin - Adding a Movie

1. **Login as Admin**
   - POST `/api/v1/auth/login`
   - Use admin credentials

2. **Create Movie**
   - POST `/api/v1/movies`
   - Provide movie details

3. **Create Showtimes**
   - POST `/api/v1/showtimes`
   - Set movie, theater, time, price

4. **View Analytics**
   - GET `/api/v1/admin/reports/capacity`
   - GET `/api/v1/admin/reports/revenue`
   - GET `/api/v1/admin/reports/popular-movies`

---

## Environment Variables Reference

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/movie_reservation

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application
DEBUG=True
ENVIRONMENT=development
APP_NAME=Movie Reservation System
APP_VERSION=1.0.0

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# File Upload
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE_MB=5
ALLOWED_IMAGE_EXTENSIONS=jpg,jpeg,png,webp

# Seat Lock
SEAT_LOCK_TTL_MINUTES=10
SEAT_LOCK_CLEANUP_INTERVAL_SECONDS=60

# API
API_V1_PREFIX=/api/v1
```

---

## Troubleshooting Quick Fixes

### "Database connection failed"
```powershell
# Check PostgreSQL is running
# Verify credentials in .env
# Test connection:
psql -U postgres -d movie_reservation
```

### "Module not found"
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

### "Alembic migration failed"
```powershell
# Reset database
psql -U postgres -c "DROP DATABASE movie_reservation;"
psql -U postgres -c "CREATE DATABASE movie_reservation;"
alembic upgrade head
```

### "Port already in use"
```powershell
uvicorn src.main:app --reload --port 8001
```

---

## File Locations

```
Project Root: c:\Users\User\OneDrive\Desktop\movie reservation system\

Key Files:
├── ARCHITECTURE.md       → System design
├── SETUP_GUIDE.md       → Setup instructions
├── PROJECT_STATUS.md    → Implementation status
├── QUICK_REFERENCE.md   → This file
│
└── backend/
    ├── src\main.py                    → Application entry
    ├── src\config\settings.py         → Configuration
    ├── src\models\*.py                → Database models
    ├── src\services\*.py              → Business logic
    ├── src\api\*\routes.py            → API endpoints
    ├── scripts\seed_data.py           → Database seeding
    ├── tests\*.py                     → Test files
    ├── requirements.txt               → Dependencies
    ├── .env                           → Environment (create from .env.example)
    └── alembic\                       → Database migrations
```

---

## Useful URLs

- **API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health
- **Root**: http://localhost:8000/

---

## Database Schema Summary

**Tables:** 8
- `users` → User accounts
- `movies` → Movie catalog
- `theaters` → Cinema halls
- `seats` → Seat inventory
- `showtimes` → Screening schedule
- `reservations` → Bookings
- `reservation_seats` → Seat-reservation link
- `seat_locks` → Temporary holds

---

## Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": { ... }
  }
}
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (Deleted) |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict (e.g., seat taken) |
| 422 | Validation Error |
| 500 | Server Error |

---

**Need more help? Check:**
- SETUP_GUIDE.md for detailed setup
- ARCHITECTURE.md for system design
- PROJECT_STATUS.md for implementation details
- http://localhost:8000/docs for interactive API testing
