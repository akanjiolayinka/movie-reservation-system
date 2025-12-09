"""
Database seeding script.
Run this script to populate the database with initial data.
"""
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timedelta
from decimal import Decimal

from src.config.database import SessionLocal
from src.models import (
    User,
    UserRole,
    Movie,
    Theater,
    Seat,
    SeatType,
    Showtime,
)
from src.services.auth_service import auth_service


def seed_database():
    """Seed database with initial data."""
    db = SessionLocal()
    
    try:
        print("🌱 Starting database seeding...")
        
        # Check if data already exists
        if db.query(User).first():
            print("⚠️  Database already contains data. Skipping seeding.")
            return
        
        # 1. Create admin user
        print("\\n👤 Creating admin user...")
        admin = User(
            email="admin@example.com",
            password_hash=auth_service.hash_password("admin123"),
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN
        )
        db.add(admin)
        db.flush()
        print(f"   ✅ Admin created: {admin.email} (password: admin123)")
        
        # 2. Create regular users
        print("\\n👥 Creating regular users...")
        users = [
            User(
                email="john.doe@example.com",
                password_hash=auth_service.hash_password("password123"),
                first_name="John",
                last_name="Doe",
                role=UserRole.USER
            ),
            User(
                email="jane.smith@example.com",
                password_hash=auth_service.hash_password("password123"),
                first_name="Jane",
                last_name="Smith",
                role=UserRole.USER
            ),
        ]
        for user in users:
            db.add(user)
            print(f"   ✅ User created: {user.email}")
        db.flush()
        
        # 3. Create theaters
        print("\\n🎭 Creating theaters...")
        theaters = [
            Theater(name="Theater 1 - IMAX", total_seats=100),
            Theater(name="Theater 2 - Standard", total_seats=80),
            Theater(name="Theater 3 - Premium", total_seats=60),
        ]
        for theater in theaters:
            db.add(theater)
        db.flush()
        print(f"   ✅ Created {len(theaters)} theaters")
        
        # 4. Create seats for each theater
        print("\\n💺 Creating seats...")
        seat_configs = {
            0: {"rows": 10, "seats_per_row": 10, "vip_rows": [0, 1]},  # Theater 1
            1: {"rows": 8, "seats_per_row": 10, "vip_rows": [0, 1]},   # Theater 2
            2: {"rows": 6, "seats_per_row": 10, "vip_rows": [0, 1, 2]}, # Theater 3
        }
        
        total_seats = 0
        for idx, theater in enumerate(theaters):
            config = seat_configs[idx]
            for row in range(config["rows"]):
                row_label = chr(65 + row)  # A, B, C, etc.
                for seat_num in range(1, config["seats_per_row"] + 1):
                    if row in config["vip_rows"]:
                        seat_type = SeatType.VIP
                    elif row < config["rows"] // 2:
                        seat_type = SeatType.PREMIUM
                    else:
                        seat_type = SeatType.REGULAR
                    
                    seat = Seat(
                        theater_id=theater.id,
                        row_label=row_label,
                        seat_number=seat_num,
                        seat_type=seat_type
                    )
                    db.add(seat)
                    total_seats += 1
        
        db.flush()
        print(f"   ✅ Created {total_seats} seats across all theaters")
        
        # 5. Create movies
        print("\\n🎬 Creating movies...")
        movies = [
            Movie(
                title="The Matrix",
                description="A computer hacker learns about the true nature of reality and his role in the war against its controllers.",
                genre="Sci-Fi",
                duration_minutes=136,
                release_date=datetime(1999, 3, 31).date(),
                poster_url="/static/posters/matrix.jpg"
            ),
            Movie(
                title="Inception",
                description="A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.",
                genre="Sci-Fi",
                duration_minutes=148,
                release_date=datetime(2010, 7, 16).date(),
                poster_url="/static/posters/inception.jpg"
            ),
            Movie(
                title="The Dark Knight",
                description="When the menace known as the Joker wreaks havoc on Gotham, Batman must accept one of the greatest tests.",
                genre="Action",
                duration_minutes=152,
                release_date=datetime(2008, 7, 18).date(),
                poster_url="/static/posters/dark-knight.jpg"
            ),
            Movie(
                title="Interstellar",
                description="A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
                genre="Sci-Fi",
                duration_minutes=169,
                release_date=datetime(2014, 11, 7).date(),
                poster_url="/static/posters/interstellar.jpg"
            ),
            Movie(
                title="Parasite",
                description="Greed and class discrimination threaten the newly formed symbiotic relationship between two families.",
                genre="Thriller",
                duration_minutes=132,
                release_date=datetime(2019, 5, 30).date(),
                poster_url="/static/posters/parasite.jpg"
            ),
            Movie(
                title="The Shawshank Redemption",
                description="Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
                genre="Drama",
                duration_minutes=142,
                release_date=datetime(1994, 9, 23).date(),
                poster_url="/static/posters/shawshank.jpg"
            ),
        ]
        for movie in movies:
            db.add(movie)
        db.flush()
        print(f"   ✅ Created {len(movies)} movies")
        
        # 6. Create showtimes for next 7 days
        print("\\n🎫 Creating showtimes...")
        base_date = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
        showtime_count = 0
        
        # Prices based on theater and time
        prices = {
            "Theater 1 - IMAX": Decimal("15.00"),
            "Theater 2 - Standard": Decimal("12.00"),
            "Theater 3 - Premium": Decimal("18.00"),
        }
        
        for day in range(7):  # Next 7 days
            date = base_date + timedelta(days=day)
            
            # 3 showtimes per day per theater
            for theater in theaters:
                # Assign different movies to each showtime
                for slot, hour_offset in enumerate([0, 4, 8]):  # 2PM, 6PM, 10PM
                    movie = movies[(day * 3 + slot) % len(movies)]
                    start_time = date + timedelta(hours=hour_offset)
                    end_time = start_time + timedelta(minutes=movie.duration_minutes)
                    
                    # Add 20 minute buffer
                    end_time = end_time + timedelta(minutes=20)
                    
                    showtime = Showtime(
                        movie_id=movie.id,
                        theater_id=theater.id,
                        start_time=start_time,
                        end_time=end_time,
                        price=prices[theater.name]
                    )
                    db.add(showtime)
                    showtime_count += 1
        
        db.flush()
        print(f"   ✅ Created {showtime_count} showtimes")
        
        # Commit all changes
        db.commit()
        
        print("\\n✨ Database seeding completed successfully!")
        print("\\n📋 Summary:")
        print(f"   • Admin user: admin@example.com (password: admin123)")
        print(f"   • Regular users: {len(users)}")
        print(f"   • Theaters: {len(theaters)}")
        print(f"   • Seats: {total_seats}")
        print(f"   • Movies: {len(movies)}")
        print(f"   • Showtimes: {showtime_count}")
        print("\\n⚠️  IMPORTANT: Change the admin password in production!")
        
    except Exception as e:
        print(f"\\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("  Movie Reservation System - Database Seeding")
    print("=" * 60)
    seed_database()
