# Movie Reservation System - Backend

A production-grade backend API for a movie reservation service built with FastAPI, PostgreSQL, and SQLAlchemy.

## Features

- 🔐 **JWT Authentication** with role-based access control (Admin/User)
- 🎬 **Movie Management** with genre categorization and poster uploads
- 🎫 **Seat Reservation** with concurrency control and temporary seat locking
- 📊 **Admin Reporting** with capacity and revenue analytics
- 🔒 **Pessimistic Locking** to prevent double-booking
- 📝 **Automatic API Documentation** with Swagger UI
- ✅ **Comprehensive Testing** with pytest

## Tech Stack

- **Framework**: FastAPI 0.115+
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **Authentication**: JWT (python-jose)
- **Password Hashing**: Bcrypt (passlib)
- **Migrations**: Alembic
- **Task Scheduler**: APScheduler
- **Testing**: Pytest

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+ (installed locally)
- pgAdmin (optional, for database management)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "movie reservation system/backend"
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Create Database in PostgreSQL

Open pgAdmin or use psql command:

```sql
CREATE DATABASE movie_reservation;
```

Or via command line:

```bash
psql -U postgres
CREATE DATABASE movie_reservation;
\q
```

### 5. Environment Configuration

Copy the example environment file and configure:

```bash
copy .env.example .env  # Windows
# or
cp .env.example .env    # Linux/Mac
```

Edit `.env` file with your PostgreSQL credentials:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/movie_reservation
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
```

### 6. Run Database Migrations

```bash
alembic upgrade head
```

### 7. Seed Initial Data

```bash
python scripts/seed_data.py
```

This will create:
- An admin user (email: `admin@example.com`, password: `admin123`)
- Sample theaters with seat layouts
- Sample movies and showtimes

### 8. Run the Application

```bash
uvicorn src.main:app --reload
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Project Structure

```
backend/
├── src/
│   ├── api/              # API routes/controllers
│   ├── models/           # SQLAlchemy database models
│   ├── schemas/          # Pydantic schemas (DTOs)
│   ├── services/         # Business logic layer
│   ├── middleware/       # Authentication & error handling
│   ├── config/           # Configuration and database
│   ├── utils/            # Utility functions
│   └── main.py           # Application entry point
├── alembic/              # Database migrations
├── scripts/              # Utility scripts
├── tests/                # Test suite
├── uploads/              # Movie poster uploads
└── requirements.txt      # Python dependencies
```

## Default Admin Credentials

After running the seed script:

- **Email**: `admin@example.com`
- **Password**: `admin123`

⚠️ **Change these credentials in production!**

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user profile

### Movies (Public)
- `GET /api/v1/movies` - List all movies
- `GET /api/v1/movies/{id}` - Get movie details
- `GET /api/v1/movies/{id}/showtimes` - Get movie showtimes

### Movies (Admin Only)
- `POST /api/v1/movies` - Create movie
- `PUT /api/v1/movies/{id}` - Update movie
- `DELETE /api/v1/movies/{id}` - Delete movie
- `POST /api/v1/movies/{id}/poster` - Upload poster

### Showtimes (Admin Only)
- `POST /api/v1/showtimes` - Create showtime
- `PUT /api/v1/showtimes/{id}` - Update showtime
- `DELETE /api/v1/showtimes/{id}` - Delete showtime

### Reservations
- `GET /api/v1/showtimes/{id}/seats` - Get available seats
- `POST /api/v1/showtimes/{id}/lock-seats` - Lock seats temporarily
- `POST /api/v1/reservations` - Create reservation
- `GET /api/v1/reservations` - Get user reservations
- `DELETE /api/v1/reservations/{id}` - Cancel reservation

### Admin Reports
- `GET /api/v1/admin/reports/capacity` - Capacity analytics
- `GET /api/v1/admin/reports/revenue` - Revenue analytics
- `GET /api/v1/admin/reports/popular-movies` - Popular movies
- `POST /api/v1/admin/users/{id}/promote` - Promote user to admin

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_reservations.py

# Run with verbose output
pytest -v
```

## Development

### Code Formatting

```bash
black src/
```

### Linting

```bash
flake8 src/
```

### Type Checking

```bash
mypy src/
```

## Database Migrations

### Create a new migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations

```bash
alembic upgrade head
```

### Rollback migration

```bash
alembic downgrade -1
```

## Troubleshooting

### Database Connection Issues

1. Verify PostgreSQL is running
2. Check credentials in `.env` file
3. Ensure database exists: `movie_reservation`
4. Test connection with pgAdmin

### Port Already in Use

If port 8000 is taken, specify a different port:

```bash
uvicorn src.main:app --reload --port 8001
```

### Migration Errors

Reset database and migrations:

```bash
# Drop and recreate database
psql -U postgres -c "DROP DATABASE IF EXISTS movie_reservation;"
psql -U postgres -c "CREATE DATABASE movie_reservation;"

# Run migrations
alembic upgrade head
python scripts/seed_data.py
```

## Architecture

See [ARCHITECTURE.md](../ARCHITECTURE.md) for detailed architectural documentation.

## Security Notes

- Always use HTTPS in production
- Change default JWT secret key
- Use strong passwords
- Implement rate limiting for production
- Regular security audits
- Keep dependencies updated

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Ensure all tests pass
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions, please create an issue in the repository.
