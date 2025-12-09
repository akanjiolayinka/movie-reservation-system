# Movie Reservation System - Backend Architecture

## Overview
Production-grade backend system for a movie reservation service built with Python/FastAPI, PostgreSQL, and SQLAlchemy ORM. The system implements complex business logic for seat reservation with concurrency control, user authentication with role-based access control, and comprehensive movie/showtime management.

## Technology Stack

### Backend Framework
- **FastAPI 0.115+**: High-performance async web framework with automatic OpenAPI documentation
- **Python 3.11+**: Modern Python with type hints and performance improvements
- **Uvicorn**: ASGI server for production deployment

### Database & ORM
- **PostgreSQL 15+**: Relational database with row-level locking support (local installation)
- **SQLAlchemy 2.0+**: ORM with async support and advanced query capabilities
- **Alembic**: Database migration management tool
- **psycopg2-binary**: PostgreSQL adapter for Python

### Authentication & Security
- **python-jose[cryptography]**: JWT token generation and verification
- **passlib[bcrypt]**: Password hashing with bcrypt algorithm
- **python-multipart**: Form data and file upload handling

### Task Scheduling
- **APScheduler**: Background task scheduler for seat lock cleanup

### Testing
- **pytest**: Testing framework with fixtures and async support
- **pytest-asyncio**: Async test support
- **httpx**: Async HTTP client for API testing

### Development Tools
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation and settings management
- **pydantic-settings**: Configuration management

## Project Structure

```
backend/
├── src/
│   ├── api/                    # API layer (controllers/routes)
│   │   ├── __init__.py
│   │   ├── auth/              # Authentication endpoints
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── movies/            # Movie management endpoints
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── showtimes/         # Showtime management endpoints
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── reservations/      # Reservation endpoints
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   └── admin/             # Admin reporting endpoints
│   │       ├── __init__.py
│   │       └── routes.py
│   │
│   ├── models/                # Database models (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── movie.py
│   │   ├── theater.py
│   │   ├── seat.py
│   │   ├── showtime.py
│   │   ├── reservation.py
│   │   └── seat_lock.py
│   │
│   ├── schemas/               # Pydantic schemas (DTOs)
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── movie.py
│   │   ├── showtime.py
│   │   ├── reservation.py
│   │   └── admin.py
│   │
│   ├── services/              # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── movie_service.py
│   │   ├── showtime_service.py
│   │   ├── reservation_service.py
│   │   └── admin_service.py
│   │
│   ├── middleware/            # Custom middleware
│   │   ├── __init__.py
│   │   ├── auth.py           # JWT authentication & RBAC
│   │   └── error_handler.py  # Centralized error handling
│   │
│   ├── config/                # Configuration
│   │   ├── __init__.py
│   │   ├── database.py       # Database connection & session
│   │   └── settings.py       # Application settings
│   │
│   ├── utils/                 # Utility functions
│   │   ├── __init__.py
│   │   ├── dependencies.py   # FastAPI dependencies
│   │   └── exceptions.py     # Custom exceptions
│   │
│   └── main.py               # Application entry point
│
├── alembic/                   # Database migrations
│   ├── versions/
│   └── env.py
│
├── scripts/                   # Utility scripts
│   └── seed_data.py          # Database seeding script
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_auth.py
│   ├── test_movies.py
│   ├── test_reservations.py
│   └── test_concurrency.py
│
├── uploads/                   # Static file storage (movie posters)
│
├── .env.example              # Environment variables template
├── .gitignore
├── requirements.txt          # Python dependencies
├── alembic.ini              # Alembic configuration
└── README.md                # Setup and usage instructions
```

## Architectural Principles

### 1. Separation of Concerns
- **API Layer**: Request/response handling, validation, and routing
- **Service Layer**: Business logic, transaction management, and data orchestration
- **Data Layer**: Database models and relationships
- **Schema Layer**: Data transfer objects (DTOs) for API contracts

### 2. Dependency Injection
- FastAPI's dependency injection system for database sessions, authentication, and authorization
- Reusable dependencies in `utils/dependencies.py`

### 3. Transaction Management
- Database transactions managed at the service layer
- Pessimistic locking for critical operations (seat reservations)
- Automatic rollback on errors

### 4. Error Handling
- Custom exception hierarchy
- Centralized error handler middleware
- Structured JSON error responses with proper HTTP status codes

## Database Schema

### Core Entities

#### Users
```sql
users (
    id: UUID PRIMARY KEY,
    email: VARCHAR(255) UNIQUE NOT NULL,
    password_hash: VARCHAR(255) NOT NULL,
    first_name: VARCHAR(100),
    last_name: VARCHAR(100),
    role: ENUM('admin', 'user') DEFAULT 'user',
    created_at: TIMESTAMP DEFAULT NOW(),
    updated_at: TIMESTAMP DEFAULT NOW()
)
```

#### Movies
```sql
movies (
    id: UUID PRIMARY KEY,
    title: VARCHAR(255) NOT NULL,
    description: TEXT,
    poster_url: VARCHAR(500),
    genre: VARCHAR(100) NOT NULL,
    duration_minutes: INTEGER NOT NULL,
    release_date: DATE,
    created_at: TIMESTAMP DEFAULT NOW(),
    updated_at: TIMESTAMP DEFAULT NOW()
)
INDEX idx_movies_genre ON movies(genre)
```

#### Theaters
```sql
theaters (
    id: UUID PRIMARY KEY,
    name: VARCHAR(255) NOT NULL,
    total_seats: INTEGER NOT NULL,
    created_at: TIMESTAMP DEFAULT NOW()
)
```

#### Seats
```sql
seats (
    id: UUID PRIMARY KEY,
    theater_id: UUID REFERENCES theaters(id),
    row_label: VARCHAR(10) NOT NULL,
    seat_number: INTEGER NOT NULL,
    seat_type: ENUM('regular', 'premium', 'vip') DEFAULT 'regular',
    created_at: TIMESTAMP DEFAULT NOW(),
    UNIQUE(theater_id, row_label, seat_number)
)
INDEX idx_seats_theater ON seats(theater_id)
```

#### Showtimes
```sql
showtimes (
    id: UUID PRIMARY KEY,
    movie_id: UUID REFERENCES movies(id),
    theater_id: UUID REFERENCES theaters(id),
    start_time: TIMESTAMP NOT NULL,
    end_time: TIMESTAMP NOT NULL,
    price: DECIMAL(10, 2) NOT NULL,
    created_at: TIMESTAMP DEFAULT NOW(),
    CHECK (end_time > start_time)
)
INDEX idx_showtimes_movie ON showtimes(movie_id)
INDEX idx_showtimes_theater_time ON showtimes(theater_id, start_time)
```

#### Reservations
```sql
reservations (
    id: UUID PRIMARY KEY,
    user_id: UUID REFERENCES users(id),
    showtime_id: UUID REFERENCES showtimes(id),
    status: ENUM('pending', 'confirmed', 'cancelled') DEFAULT 'confirmed',
    total_price: DECIMAL(10, 2) NOT NULL,
    created_at: TIMESTAMP DEFAULT NOW(),
    updated_at: TIMESTAMP DEFAULT NOW()
)
INDEX idx_reservations_user ON reservations(user_id)
INDEX idx_reservations_showtime ON reservations(showtime_id)
```

#### ReservationSeats (Many-to-Many)
```sql
reservation_seats (
    reservation_id: UUID REFERENCES reservations(id) ON DELETE CASCADE,
    seat_id: UUID REFERENCES seats(id),
    PRIMARY KEY (reservation_id, seat_id)
)
INDEX idx_reservation_seats_showtime ON reservation_seats(seat_id)
```

#### SeatLocks (Temporary Seat Holding)
```sql
seat_locks (
    id: UUID PRIMARY KEY,
    seat_id: UUID REFERENCES seats(id),
    showtime_id: UUID REFERENCES showtimes(id),
    user_id: UUID REFERENCES users(id),
    expires_at: TIMESTAMP NOT NULL,
    created_at: TIMESTAMP DEFAULT NOW(),
    UNIQUE(seat_id, showtime_id)
)
INDEX idx_seat_locks_expires ON seat_locks(expires_at)
INDEX idx_seat_locks_user ON seat_locks(user_id)
```

## Key Features & Implementation Details

### 1. Authentication & Authorization

#### JWT Token Authentication
- Access tokens with 24-hour expiration
- Token payload includes: `user_id`, `email`, `role`
- HS256 algorithm for signing
- Tokens passed in `Authorization: Bearer <token>` header

#### Role-Based Access Control (RBAC)
- Two roles: `admin` and `user`
- Middleware dependencies:
  - `get_current_user`: Extract and validate JWT token
  - `require_admin`: Ensure current user has admin role
- Admin-only operations:
  - Movie CRUD
  - Showtime management
  - Reporting and analytics
  - User promotion to admin

#### Password Security
- Bcrypt hashing with automatic salt generation
- Password validation: minimum 8 characters
- No plaintext password storage

### 2. Movie & Showtime Management

#### Movie CRUD (Admin Only)
- Create movie with title, description, genre, duration, poster image
- Update movie details
- Delete movie (cascade to showtimes)
- Filter by genre, search by title

#### Showtime Scheduling
- Validation: No overlapping showtimes in same theater
- Automatic end_time calculation: `start_time + movie.duration_minutes`
- Price configuration per showtime
- Theater availability check before scheduling

#### Public Browsing
- Get movies by genre
- Get movies showing on specific date
- Get showtimes for a movie
- Filter showtimes by date range

### 3. Seat Reservation System

#### Concurrency Control Strategy
**Pessimistic Locking with Temporary Seat Holds**

1. **Seat Selection Phase**:
   - User requests available seats for a showtime
   - System returns seat map with availability status
   - User selects desired seats

2. **Temporary Lock Phase** (Prevents double-booking during selection):
   - Create `seat_lock` entries with 10-minute TTL
   - Use database transaction with `SELECT ... FOR UPDATE`
   - Check for existing locks or reservations
   - Lock acquired only if seats are available

3. **Reservation Creation Phase**:
   - Within database transaction:
     - Verify seat locks belong to requesting user
     - Check locks haven't expired
     - Create reservation record
     - Link seats to reservation via `reservation_seats`
     - Delete seat locks (no longer needed)
   - Atomic operation: All or nothing

4. **Lock Cleanup**:
   - APScheduler background job runs every minute
   - Deletes expired seat locks (`expires_at < NOW()`)
   - Frees seats if user abandons reservation

#### Preventing Overbooking
- Database constraints: `UNIQUE(seat_id, showtime_id)` on `seat_locks`
- Row-level locking: `with_for_update(nowait=False)` in SQLAlchemy
- Transaction isolation: `READ COMMITTED` level
- Validation checks at multiple layers

#### Seat Availability Query
```python
# Returns seats that are NOT:
# 1. Already reserved (in reservation_seats for this showtime)
# 2. Currently locked by another user (in seat_locks)
available_seats = (
    SELECT seats 
    WHERE theater_id = showtime.theater_id
    AND seat_id NOT IN (
        SELECT seat_id FROM reservation_seats 
        WHERE reservation.showtime_id = ? AND reservation.status != 'cancelled'
    )
    AND seat_id NOT IN (
        SELECT seat_id FROM seat_locks 
        WHERE showtime_id = ? AND expires_at > NOW()
    )
)
```

#### User Reservation Management
- View all reservations (upcoming and past)
- Cancel upcoming reservations (before showtime)
- Cannot cancel past or already-started showtimes

### 4. Admin Reporting

#### Analytics Endpoints
- **Capacity Report**: Seats sold vs. total seats per showtime/date/movie
- **Revenue Report**: Total revenue by movie, date, theater
- **Popular Movies**: Most reserved movies by time period
- **Occupancy Rate**: Average theater occupancy percentage

#### Data Aggregation
- SQLAlchemy aggregation functions: `func.count()`, `func.sum()`, `func.avg()`
- GROUP BY queries for time-series data
- JOIN operations across multiple tables

### 5. API Design

#### Versioning
- Base path: `/api/v1/`
- Future versions: `/api/v2/` (backward compatibility)

#### Endpoints Structure

**Authentication**
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user profile

**Movies (Public)**
- `GET /api/v1/movies` - List movies (filter by genre, date)
- `GET /api/v1/movies/{movie_id}` - Get movie details
- `GET /api/v1/movies/{movie_id}/showtimes` - Get showtimes for movie

**Movies (Admin)**
- `POST /api/v1/movies` - Create movie
- `PUT /api/v1/movies/{movie_id}` - Update movie
- `DELETE /api/v1/movies/{movie_id}` - Delete movie
- `POST /api/v1/movies/{movie_id}/poster` - Upload poster image

**Showtimes (Admin)**
- `POST /api/v1/showtimes` - Create showtime
- `PUT /api/v1/showtimes/{showtime_id}` - Update showtime
- `DELETE /api/v1/showtimes/{showtime_id}` - Delete showtime

**Reservations**
- `GET /api/v1/showtimes/{showtime_id}/seats` - Get seat availability
- `POST /api/v1/showtimes/{showtime_id}/lock-seats` - Lock seats temporarily
- `POST /api/v1/reservations` - Create reservation
- `GET /api/v1/reservations` - Get user's reservations
- `DELETE /api/v1/reservations/{reservation_id}` - Cancel reservation

**Admin Reports**
- `GET /api/v1/admin/reports/capacity` - Capacity analytics
- `GET /api/v1/admin/reports/revenue` - Revenue analytics
- `GET /api/v1/admin/reports/popular-movies` - Popular movies report
- `POST /api/v1/admin/users/{user_id}/promote` - Promote user to admin

#### Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

#### Error Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": { ... }
  }
}
```

## Configuration Management

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/movie_reservation

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application
DEBUG=True
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# File Upload
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE_MB=5

# Seat Lock
SEAT_LOCK_TTL_MINUTES=10
```

### Settings Management
- Pydantic Settings for type-safe configuration
- Environment-specific overrides
- Validation on startup

## Testing Strategy

### Unit Tests
- Service layer functions
- Utility functions
- Authentication logic
- Price calculation

### Integration Tests
- API endpoint testing
- Database operations
- Authentication flows
- File uploads

### Concurrency Tests
- Parallel seat reservation attempts
- Race condition scenarios
- Lock expiration edge cases
- Stress testing with multiple users

### Test Coverage Goals
- Minimum 80% code coverage
- 100% coverage for critical paths (reservations, auth)

## Security Considerations

### Input Validation
- Pydantic models for all request bodies
- Query parameter validation
- File upload validation (type, size)

### SQL Injection Prevention
- SQLAlchemy parameterized queries
- No raw SQL strings with user input

### Authentication Security
- JWT token expiration
- Password strength requirements
- Rate limiting on auth endpoints (future)

### Authorization
- Role-based access control
- Resource ownership validation
- Middleware-enforced permissions

### Data Protection
- Password hashing with bcrypt
- Sensitive data exclusion from logs
- HTTPS enforcement in production

## Performance Optimization

### Database Optimization
- Appropriate indexes on foreign keys and query columns
- Connection pooling
- Query result pagination
- Eager loading for relationships (avoid N+1)

### Caching Strategy (Future Enhancement)
- Redis for session management
- Cache seat availability for popular showtimes
- Cache movie list with short TTL

### Background Tasks
- APScheduler for cleanup jobs
- Async operations for non-blocking I/O
- Batch operations for bulk updates

## Deployment Considerations

### Local Development Setup
1. Install PostgreSQL 15+ locally
2. Create database: `CREATE DATABASE movie_reservation;`
3. Clone repository
4. Create virtual environment: `python -m venv venv`
5. Install dependencies: `pip install -r requirements.txt`
6. Copy `.env.example` to `.env` and configure
7. Run migrations: `alembic upgrade head`
8. Seed database: `python scripts/seed_data.py`
9. Start server: `uvicorn src.main:app --reload`

### Production Deployment (Future)
- Containerization with Docker
- PostgreSQL hosted database (AWS RDS, etc.)
- Uvicorn with Gunicorn workers
- Nginx reverse proxy
- Environment variable management
- Logging to external service
- Monitoring and alerting

## API Documentation

### Automatic Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### Documentation Standards
- Detailed endpoint descriptions
- Request/response examples
- Error response documentation
- Authentication requirements

## Naming Conventions

### Python Code
- **Classes**: PascalCase (e.g., `MovieService`, `UserModel`)
- **Functions**: snake_case (e.g., `create_reservation`, `get_user_by_email`)
- **Variables**: snake_case (e.g., `user_id`, `total_price`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `JWT_SECRET_KEY`, `SEAT_LOCK_TTL`)
- **Private methods**: Leading underscore (e.g., `_validate_input`)

### Database
- **Tables**: Plural snake_case (e.g., `users`, `showtimes`, `reservation_seats`)
- **Columns**: snake_case (e.g., `created_at`, `user_id`, `total_price`)
- **Indexes**: Prefix `idx_` (e.g., `idx_users_email`, `idx_showtimes_theater_time`)
- **Foreign keys**: Suffix `_id` (e.g., `user_id`, `movie_id`)

### API Endpoints
- **REST conventions**: Plural resource names (e.g., `/movies`, `/reservations`)
- **Actions**: Hyphenated lowercase (e.g., `/lock-seats`, `/popular-movies`)
- **Versioning**: Prefix with version (e.g., `/api/v1/`)

### Files & Directories
- **Modules**: snake_case (e.g., `auth_service.py`, `movie_routes.py`)
- **Directories**: snake_case (e.g., `api/`, `middleware/`)
- **Test files**: Prefix `test_` (e.g., `test_auth.py`, `test_reservations.py`)

## Error Handling

### Exception Hierarchy
```python
APIException (Base)
├── AuthenticationException
├── AuthorizationException
├── ValidationException
├── NotFoundException
├── ConflictException (e.g., seat already booked)
└── BusinessLogicException
```

### HTTP Status Codes
- `200 OK`: Successful GET, PUT, DELETE
- `201 Created`: Successful POST
- `400 Bad Request`: Validation errors
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Business rule violation (e.g., double booking)
- `422 Unprocessable Entity`: Invalid entity state
- `500 Internal Server Error`: Unexpected errors

## Future Enhancements

### Phase 2 Features
- Payment gateway integration (Stripe, PayPal)
- Email notifications (reservation confirmation, reminders)
- SMS notifications via Twilio
- QR code ticket generation
- Mobile API optimizations

### Phase 3 Features
- Recommendation engine (based on viewing history)
- Loyalty program and discounts
- Group booking functionality
- Dynamic pricing based on demand
- Theater seat map visualization API

### Infrastructure Improvements
- Redis caching layer
- Message queue (Celery) for background jobs
- Elasticsearch for advanced search
- CDN for poster images
- Rate limiting and throttling
- API versioning strategy

## Maintenance & Monitoring

### Logging
- Structured logging with context
- Request/response logging
- Error tracking with stack traces
- Performance metrics logging

### Health Checks
- Database connection health
- Disk space monitoring
- API endpoint health check

### Backup Strategy
- Daily database backups
- Transaction log backups
- Poster image backups

## Contributing Guidelines

### Code Review Checklist
- [ ] Follows naming conventions
- [ ] Includes unit tests
- [ ] Updates API documentation
- [ ] No security vulnerabilities
- [ ] Handles errors appropriately
- [ ] Optimized database queries
- [ ] Follows separation of concerns

### Development Workflow
1. Create feature branch from `main`
2. Implement feature following architecture
3. Write tests (minimum 80% coverage)
4. Update documentation
5. Submit pull request
6. Code review and approval
7. Merge to `main`

---

**Document Version**: 1.0  
**Last Updated**: December 9, 2025  
**Authors**: Software Architecture Team
