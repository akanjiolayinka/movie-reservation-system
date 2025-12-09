# 🎬 Movie Reservation System - Testing Guide

## ✅ System Status: FULLY OPERATIONAL

### Backend Server
- **Status:** ✅ Running
- **URL:** http://127.0.0.1:8000
- **API Docs:** http://127.0.0.1:8000/docs
- **Features:** All endpoints working, seat lock cleanup running every 60 seconds

### Frontend Application
- **Location:** `frontend/index.html`
- **Status:** ✅ Created and configured
- **CORS:** ✅ Fixed (allow all origins for development)

---

## 🧪 Testing Instructions

### 1. Test with Frontend (Simple UI)

The frontend has been opened in your browser. If not, open: `C:\Users\User\OneDrive\Desktop\movie reservation system\frontend\index.html`

**Test Flow:**
1. **Login** - Use these credentials:
   - Admin: `admin@example.com` / `admin123`
   - User: `john.doe@example.com` / `password123`

2. **Browse Movies** - See all 6 seeded movies

3. **Select a Movie** - Click on any movie card

4. **Choose Showtime** - Pick from available showtimes

5. **Select Seats** - Click on available seats (green borders)
   - VIP seats have gold borders
   - Reserved seats are gray
   - Selected seats turn purple

6. **Book Seats** - Click "Book Seats" button

7. **View Reservations** - Go to "My Reservations" tab

8. **Admin Features** (admin account only):
   - View capacity reports
   - View revenue reports
   - Add new movies

### 2. Test with API Documentation (Swagger UI)

Visit: http://127.0.0.1:8000/docs

**Test Flow:**
1. **Expand `/api/v1/auth/login`**
   - Click "Try it out"
   - Enter credentials:
     ```json
     {
       "username": "admin@example.com",
       "password": "admin123"
     }
     ```
   - Click "Execute"
   - Copy the `access_token` from response

2. **Authorize:**
   - Click "Authorize" button (top right, green lock icon)
   - Enter: `Bearer <your_access_token>`
   - Click "Authorize"

3. **Test Endpoints:**
   - ✅ **GET `/api/v1/movies`** - List all movies
   - ✅ **GET `/api/v1/showtimes`** - List showtimes (filter by movie_id)
   - ✅ **GET `/api/v1/reservations/showtime/{showtime_id}/seats`** - Check seat availability
   - ✅ **POST `/api/v1/reservations`** - Create a reservation
   - ✅ **GET `/api/v1/reservations/my`** - View your reservations
   - ✅ **GET `/api/v1/admin/capacity-report`** - Admin analytics

---

## 🔍 What to Check For

### ✅ Features Working
1. **Authentication:**
   - Login with valid credentials
   - Receive JWT token
   - Access protected routes

2. **Movies:**
   - List all movies (6 seeded)
   - View movie details
   - Filter by genre (in code)

3. **Showtimes:**
   - List showtimes by movie
   - View theater information
   - See pricing

4. **Reservations:**
   - View seat availability with colors
   - Select multiple seats
   - Calculate correct pricing (VIP = 1.5x regular)
   - Create reservation
   - View personal reservations
   - Cancel reservations

5. **Concurrency Protection:**
   - Seats locked when selected
   - Seat locks expire after 10 minutes
   - Background cleanup running every 60 seconds

6. **Admin Features:**
   - Theater capacity reports
   - Revenue analytics by movie
   - Add new movies
   - View all data

### ⚠️ Known Behaviors
1. **Seat Locks:** Expire automatically after 10 minutes of inactivity
2. **Background Job:** Runs every 60 seconds to clean expired locks
3. **CORS:** Set to allow all origins for development (tighten for production)

---

## 🐛 Testing Errors & Edge Cases

### Test These Scenarios:

1. **Invalid Login:**
   - Wrong email/password → Should show error message

2. **Unauthorized Access:**
   - Try admin endpoints without admin role → 403 Forbidden

3. **Double Booking:**
   - Two users try to book same seat → Second should fail

4. **Seat Lock Expiry:**
   - Select seats, wait 10+ minutes → Seats become available again

5. **Cancel Reservation:**
   - Cancel a confirmed reservation → Seats become available

6. **Invalid Data:**
   - Try creating movie without required fields → Validation error

---

## 📊 Database Contents

Currently seeded with:
- **3 Users:** 1 admin + 2 regular users
- **3 Theaters:** IMAX (100 seats), Standard (80 seats), Premium (60 seats)
- **240 Seats:** VIP rows + Regular rows in each theater
- **6 Movies:** Matrix, Inception, Dark Knight, Interstellar, Parasite, Shawshank
- **63 Showtimes:** 3 shows per day for 7 days across 3 theaters

---

## 🛠️ If You Encounter Issues

### Frontend Not Loading Movies:
1. Check browser console (F12) for errors
2. Verify backend is running: http://127.0.0.1:8000/docs
3. Check CORS settings in browser network tab

### Login Fails:
1. Verify credentials in console
2. Check backend logs for authentication errors
3. Try using Swagger UI to test login endpoint directly

### Database Connection Issues:
1. Verify PostgreSQL is running
2. Check .env file has correct password
3. Run: `psql -U postgres -d movie_reservation -c "SELECT COUNT(*) FROM users;"`

### Seat Selection Not Working:
1. Check if showtime exists
2. Verify seats are available (not already reserved)
3. Check browser console for JavaScript errors

---

## 🎯 Success Criteria

✅ **System is working if you can:**
1. Login with test accounts
2. See 6 movies in the list
3. Select a movie and view showtimes
4. Click on seats and see them turn purple
5. Create a reservation successfully
6. View your reservation in "My Reservations"
7. Admin can see reports (when logged in as admin)

---

## 📝 Next Steps for Production

1. **Security:**
   - [ ] Change JWT secret key in `.env`
   - [ ] Update CORS to specific origins only
   - [ ] Change admin password
   - [ ] Add rate limiting
   - [ ] Add HTTPS

2. **Features:**
   - [ ] Email notifications
   - [ ] Payment integration
   - [ ] QR code tickets
   - [ ] Search functionality
   - [ ] Movie ratings and reviews

3. **Deployment:**
   - [ ] Deploy backend (Heroku, AWS, etc.)
   - [ ] Deploy frontend (Vercel, Netlify)
   - [ ] Setup production database (AWS RDS, etc.)
   - [ ] Configure environment variables
   - [ ] Setup CI/CD pipeline

---

## 📞 Support

If you need any changes or encounter issues:
1. Check backend logs in terminal
2. Check browser console (F12)
3. Review error messages
4. Ask for specific features or fixes needed

**All code follows the architecture principles from your reference document!** ✨
