# 🎬 Movie Reservation System - Quick Start Guide

## Prerequisites Checklist

Before starting, ensure you have:
- ✅ Python 3.11 or higher installed
- ✅ PostgreSQL 15+ installed and running locally
- ✅ pgAdmin (optional, for database management)
- ✅ Git (for version control)

## Step-by-Step Setup Instructions

### 1. Database Setup

#### Option A: Using pgAdmin
1. Open pgAdmin
2. Connect to your local PostgreSQL server
3. Right-click on "Databases" → "Create" → "Database"
4. Database name: `movie_reservation`
5. Click "Save"

#### Option B: Using Command Line
```bash
# Open PowerShell or CMD
psql -U postgres
CREATE DATABASE movie_reservation;
\q
```

### 2. Environment Configuration

1. Navigate to the backend directory:
```powershell
cd "c:\Users\User\OneDrive\Desktop\movie reservation system\backend"
```

2. Copy the example environment file:
```powershell
copy .env.example .env
```

3. Edit `.env` file and update your PostgreSQL credentials:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/movie_reservation
JWT_SECRET_KEY=your-super-secret-key-here-change-this
```

**Important**: Replace `YOUR_PASSWORD` with your PostgreSQL password!

### 3. Python Virtual Environment

Create and activate a virtual environment:

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### 4. Install Dependencies

```powershell
# Make sure you're in the backend directory and venv is activated
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- SQLAlchemy (database ORM)
- Alembic (database migrations)
- JWT libraries (authentication)
- Pytest (testing)
- And many more...

### 5. Database Migrations

Initialize the database schema:

```powershell
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations to database
alembic upgrade head
```

You should see output confirming tables were created.

### 6. Seed Initial Data

Populate the database with sample data:

```powershell
python scripts\seed_data.py
```

This creates:
- **Admin user**: `admin@example.com` / `admin123`
- **2 regular users** for testing
- **3 theaters** with seat layouts
- **6 movies** with various genres
- **Showtimes** for the next 7 days

### 7. Run the Application

Start the FastAPI server:

```powershell
uvicorn src.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### 8. Test the API

Open your browser and visit:
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🧪 Testing Your Setup

### Test Authentication

1. Go to http://localhost:8000/docs
2. Find the `POST /api/v1/auth/login` endpoint
3. Click "Try it out"
4. Enter:
   ```json
   {
     "email": "admin@example.com",
     "password": "admin123"
   }
   ```
5. Click "Execute"
6. You should receive an `access_token`

### Authorize API Requests

1. Copy the `access_token` from the login response
2. Click the "Authorize" button at the top of the Swagger UI
3. Enter: `Bearer YOUR_TOKEN_HERE`
4. Click "Authorize"
5. Now you can test protected endpoints!

### Test Movie Listing

1. Find `GET /api/v1/movies`
2. Click "Try it out" → "Execute"
3. You should see a list of movies

### Test Seat Availability

1. Find `GET /api/v1/showtimes/{showtime_id}/seats`
2. Get a showtime_id from the movies list
3. Execute the request
4. You'll see all available seats with their status

## 🔧 Troubleshooting

### Problem: "Cannot connect to database"
**Solution**:
- Check PostgreSQL is running
- Verify DATABASE_URL in `.env` file
- Ensure database `movie_reservation` exists
- Test connection with pgAdmin

### Problem: "Module not found" errors
**Solution**:
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Problem: "Port 8000 already in use"
**Solution**:
```powershell
# Use a different port
uvicorn src.main:app --reload --port 8001
```

### Problem: Alembic migration errors
**Solution**:
```powershell
# Drop and recreate database
psql -U postgres -c "DROP DATABASE IF EXISTS movie_reservation;"
psql -U postgres -c "CREATE DATABASE movie_reservation;"

# Run migrations again
alembic upgrade head
python scripts\seed_data.py
```

## 📝 Running Tests

Run the test suite:

```powershell
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests\test_auth.py

# Run with coverage report
pytest --cov=src --cov-report=html
```

## 🎯 Next Steps

Now that your backend is running:

1. **Explore the API**: Use the Swagger UI to test all endpoints
2. **Create a Reservation**: 
   - Login as a user
   - Browse movies
   - Lock seats for a showtime
   - Create a reservation
3. **Admin Features**:
   - Login as admin
   - Create new movies
   - View analytics reports
4. **Build a Frontend**: Connect a React/Vue/Angular frontend to this API

## 📚 Key API Endpoints

### Public Endpoints
- `GET /api/v1/movies` - List movies
- `GET /api/v1/movies/{id}` - Get movie details
- `GET /api/v1/movies/{id}/showtimes` - Get showtimes

### User Endpoints (Requires Authentication)
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get profile
- `GET /api/v1/showtimes/{id}/seats` - View seat availability
- `POST /api/v1/showtimes/{id}/lock-seats` - Lock seats
- `POST /api/v1/reservations` - Create reservation
- `GET /api/v1/reservations` - View my reservations
- `DELETE /api/v1/reservations/{id}` - Cancel reservation

### Admin Endpoints (Requires Admin Role)
- `POST /api/v1/movies` - Create movie
- `PUT /api/v1/movies/{id}` - Update movie
- `DELETE /api/v1/movies/{id}` - Delete movie
- `POST /api/v1/showtimes` - Create showtime
- `GET /api/v1/admin/reports/capacity` - Capacity report
- `GET /api/v1/admin/reports/revenue` - Revenue report
- `POST /api/v1/admin/users/{id}/promote` - Promote user to admin

## 🔐 Security Notes

- **Change default passwords** before deploying to production
- **Use strong JWT_SECRET_KEY** in production
- **Enable HTTPS** for production deployment
- **Implement rate limiting** for authentication endpoints
- **Regular security audits** and dependency updates

## 📖 Documentation

- **Architecture**: See `ARCHITECTURE.md` for detailed system design
- **API Docs**: Available at `/docs` when server is running
- **Code Comments**: All code is thoroughly documented

## 🆘 Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Review error messages in the terminal
3. Check PostgreSQL logs
4. Verify environment variables in `.env`
5. Ensure all dependencies are installed

## 🎉 Success!

If you can:
- ✅ Access http://localhost:8000/docs
- ✅ Login with admin credentials
- ✅ View movies and showtimes
- ✅ Create a test reservation

**Congratulations! Your movie reservation system is ready!** 🍿

---

**Happy Coding! 🚀**
