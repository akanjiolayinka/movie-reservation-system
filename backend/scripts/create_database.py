"""
Database setup script - Creates the movie_reservation database if it doesn't exist.
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    """Create the movie_reservation database if it doesn't exist."""
    # Connection parameters
    conn_params = {
        'host': 'localhost',
        'user': 'postgres',
        'password': '123456789',
        'port': 5432
    }
    
    try:
        # Connect to postgres database (default)
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(**conn_params, database='postgres')
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            ('movie_reservation',)
        )
        exists = cursor.fetchone()
        
        if exists:
            print("✓ Database 'movie_reservation' already exists")
        else:
            # Create database
            print("Creating database 'movie_reservation'...")
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier('movie_reservation')
                )
            )
            print("✓ Database 'movie_reservation' created successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Movie Reservation System - Database Setup")
    print("=" * 60)
    success = create_database()
    print("=" * 60)
    if success:
        print("✓ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run migrations: alembic upgrade head")
        print("2. Seed database: python scripts\\seed_data.py")
        print("3. Start server: uvicorn src.main:app --reload")
    else:
        print("✗ Setup failed. Please check your PostgreSQL configuration.")
    print("=" * 60)
