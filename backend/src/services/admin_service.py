"""
Admin service for analytics and reporting.
"""
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from decimal import Decimal
import uuid

from src.models.movie import Movie
from src.models.theater import Theater
from src.models.showtime import Showtime
from src.models.reservation import Reservation, ReservationSeat, ReservationStatus
from src.models.user import User, UserRole
from src.utils.exceptions import NotFoundException, AuthorizationException


class AdminService:
    """Service for admin operations and analytics."""
    
    @staticmethod
    def get_capacity_report(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        movie_id: Optional[uuid.UUID] = None,
        theater_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Generate capacity utilization report."""
        # Base query
        query = db.query(
            Showtime.id.label("showtime_id"),
            Movie.title.label("movie_title"),
            Theater.name.label("theater_name"),
            Showtime.start_time,
            Theater.total_seats,
            func.count(ReservationSeat.seat_id).label("reserved_seats")
        ).join(Movie).join(Theater).outerjoin(
            Reservation, and_(
                Reservation.showtime_id == Showtime.id,
                Reservation.status == ReservationStatus.CONFIRMED
            )
        ).outerjoin(ReservationSeat).group_by(
            Showtime.id,
            Movie.title,
            Theater.name,
            Showtime.start_time,
            Theater.total_seats
        )
        
        # Apply filters
        if start_date:
            query = query.filter(func.date(Showtime.start_time) >= start_date)
        if end_date:
            query = query.filter(func.date(Showtime.start_time) <= end_date)
        if movie_id:
            query = query.filter(Showtime.movie_id == movie_id)
        if theater_id:
            query = query.filter(Showtime.theater_id == theater_id)
        
        results = query.all()
        
        # Process results
        report_items = []
        total_capacity = 0
        total_reserved = 0
        
        for row in results:
            available = row.total_seats - row.reserved_seats
            occupancy_rate = row.reserved_seats / row.total_seats if row.total_seats > 0 else 0
            
            report_items.append({
                "showtime_id": row.showtime_id,
                "movie_title": row.movie_title,
                "theater_name": row.theater_name,
                "start_time": row.start_time,
                "total_seats": row.total_seats,
                "reserved_seats": row.reserved_seats,
                "available_seats": available,
                "occupancy_rate": round(occupancy_rate, 2)
            })
            
            total_capacity += row.total_seats
            total_reserved += row.reserved_seats
        
        avg_occupancy = total_reserved / total_capacity if total_capacity > 0 else 0
        
        return {
            "report_items": report_items,
            "summary": {
                "total_showtimes": len(results),
                "total_capacity": total_capacity,
                "total_reserved": total_reserved,
                "average_occupancy": round(avg_occupancy, 2)
            }
        }
    
    @staticmethod
    def get_revenue_report(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        movie_id: Optional[uuid.UUID] = None,
        theater_id: Optional[uuid.UUID] = None,
        group_by: str = "day"
    ) -> Dict[str, Any]:
        """Generate revenue report."""
        # Build query based on grouping
        if group_by == "movie":
            query = db.query(
                Movie.title.label("label"),
                func.count(Reservation.id).label("total_reservations"),
                func.count(ReservationSeat.seat_id).label("total_seats_sold"),
                func.sum(Reservation.total_price).label("total_revenue")
            ).join(
                Showtime, Showtime.movie_id == Movie.id
            ).join(
                Reservation, and_(
                    Reservation.showtime_id == Showtime.id,
                    Reservation.status == ReservationStatus.CONFIRMED
                )
            ).join(ReservationSeat).group_by(Movie.title)
            
        elif group_by == "theater":
            query = db.query(
                Theater.name.label("label"),
                func.count(Reservation.id).label("total_reservations"),
                func.count(ReservationSeat.seat_id).label("total_seats_sold"),
                func.sum(Reservation.total_price).label("total_revenue")
            ).join(
                Showtime, Showtime.theater_id == Theater.id
            ).join(
                Reservation, and_(
                    Reservation.showtime_id == Showtime.id,
                    Reservation.status == ReservationStatus.CONFIRMED
                )
            ).join(ReservationSeat).group_by(Theater.name)
            
        else:  # day, week, month
            date_format = {
                "day": func.date(Reservation.created_at),
                "week": func.date_trunc('week', Reservation.created_at),
                "month": func.date_trunc('month', Reservation.created_at)
            }[group_by]
            
            query = db.query(
                func.cast(date_format, type_=str).label("label"),
                func.count(Reservation.id).label("total_reservations"),
                func.count(ReservationSeat.seat_id).label("total_seats_sold"),
                func.sum(Reservation.total_price).label("total_revenue")
            ).join(
                ReservationSeat
            ).filter(
                Reservation.status == ReservationStatus.CONFIRMED
            ).group_by(date_format)
        
        # Apply filters
        if start_date and group_by not in ["movie", "theater"]:
            query = query.filter(func.date(Reservation.created_at) >= start_date)
        if end_date and group_by not in ["movie", "theater"]:
            query = query.filter(func.date(Reservation.created_at) <= end_date)
        
        # For movie/theater grouping, filter by showtime dates
        if group_by in ["movie", "theater"]:
            if start_date:
                query = query.filter(func.date(Showtime.start_time) >= start_date)
            if end_date:
                query = query.filter(func.date(Showtime.start_time) <= end_date)
        
        if movie_id and group_by != "movie":
            query = query.join(Showtime).filter(Showtime.movie_id == movie_id)
        if theater_id and group_by != "theater":
            query = query.join(Showtime).filter(Showtime.theater_id == theater_id)
        
        results = query.all()
        
        # Process results
        report_items = []
        total_revenue = Decimal("0")
        total_reservations = 0
        total_seats = 0
        
        for row in results:
            revenue = Decimal(str(row.total_revenue or 0))
            avg_price = revenue / row.total_seats_sold if row.total_seats_sold > 0 else Decimal("0")
            
            report_items.append({
                "label": row.label,
                "total_reservations": row.total_reservations,
                "total_seats_sold": row.total_seats_sold,
                "total_revenue": revenue,
                "average_ticket_price": round(avg_price, 2)
            })
            
            total_revenue += revenue
            total_reservations += row.total_reservations
            total_seats += row.total_seats_sold
        
        avg_ticket = total_revenue / total_seats if total_seats > 0 else Decimal("0")
        
        return {
            "report_items": report_items,
            "summary": {
                "total_revenue": total_revenue,
                "total_reservations": total_reservations,
                "total_seats_sold": total_seats,
                "average_ticket_price": round(avg_ticket, 2)
            }
        }
    
    @staticmethod
    def get_popular_movies(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get most popular movies by reservations."""
        query = db.query(
            Movie.id,
            Movie.title,
            Movie.genre,
            func.count(Reservation.id).label("total_reservations"),
            func.count(ReservationSeat.seat_id).label("total_seats_sold"),
            func.sum(Reservation.total_price).label("total_revenue"),
            (func.count(ReservationSeat.seat_id).cast(type_=Decimal) / 
             func.sum(Theater.total_seats).cast(type_=Decimal)).label("avg_occupancy")
        ).join(
            Showtime, Showtime.movie_id == Movie.id
        ).join(
            Theater, Theater.id == Showtime.theater_id
        ).join(
            Reservation, and_(
                Reservation.showtime_id == Showtime.id,
                Reservation.status == ReservationStatus.CONFIRMED
            )
        ).join(ReservationSeat).group_by(
            Movie.id, Movie.title, Movie.genre
        ).order_by(
            func.count(Reservation.id).desc()
        ).limit(limit)
        
        if start_date:
            query = query.filter(func.date(Showtime.start_time) >= start_date)
        if end_date:
            query = query.filter(func.date(Showtime.start_time) <= end_date)
        
        results = query.all()
        
        movies = []
        for row in results:
            movies.append({
                "movie_id": row.id,
                "movie_title": row.title,
                "genre": row.genre,
                "total_reservations": row.total_reservations,
                "total_seats_sold": row.total_seats_sold,
                "total_revenue": Decimal(str(row.total_revenue or 0)),
                "average_occupancy": round(float(row.avg_occupancy or 0), 2)
            })
        
        return {
            "movies": movies,
            "period_start": start_date,
            "period_end": end_date
        }
    
    @staticmethod
    def promote_user(
        db: Session,
        user_id: uuid.UUID,
        promote_to_admin: bool
    ) -> User:
        """Promote or demote user admin status."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException(
                message="User not found",
                resource="user"
            )
        
        new_role = UserRole.ADMIN if promote_to_admin else UserRole.USER
        user.role = new_role
        
        db.commit()
        db.refresh(user)
        return user


# Global instance
admin_service = AdminService()
