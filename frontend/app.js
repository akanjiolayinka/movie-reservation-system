// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

// Global State
let authToken = null;
let currentUser = null;
let currentMovie = null;
let currentShowtime = null;
let selectedSeats = [];

// ==================== Utility Functions ====================

function showLoading() {
    document.getElementById('loadingSpinner').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingSpinner').classList.add('hidden');
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.classList.remove('hidden');
}

function hideError(elementId) {
    const element = document.getElementById(elementId);
    element.classList.add('hidden');
}

// ==================== API Functions ====================

async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || data.message || 'Request failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ==================== Authentication ====================

async function login(event) {
    event.preventDefault();
    hideError('loginError');
    showLoading();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        // Create form data
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }

        authToken = data.access_token;
        
        // Get user profile
        await getUserProfile();
        
        // Update UI
        document.getElementById('loginSection').classList.add('hidden');
        document.getElementById('appSection').classList.remove('hidden');
        document.getElementById('userInfo').classList.remove('hidden');
        document.getElementById('userName').textContent = currentUser.full_name;

        // Show admin tab if user is admin
        if (currentUser.is_admin) {
            document.querySelectorAll('.admin-only').forEach(el => {
                el.classList.remove('hidden');
            });
        }

        showToast('Login successful!');
        loadMovies();
    } catch (error) {
        showError('loginError', error.message);
    } finally {
        hideLoading();
    }
}

async function getUserProfile() {
    const data = await apiCall('/auth/me');
    currentUser = data;
}

function logout() {
    authToken = null;
    currentUser = null;
    selectedSeats = [];
    
    document.getElementById('loginSection').classList.remove('hidden');
    document.getElementById('appSection').classList.add('hidden');
    document.getElementById('userInfo').classList.add('hidden');
    
    document.querySelectorAll('.admin-only').forEach(el => {
        el.classList.add('hidden');
    });

    showToast('Logged out successfully');
}

// ==================== Movies ====================

async function loadMovies() {
    showLoading();
    try {
        const data = await apiCall('/movies');
        displayMovies(data);
    } catch (error) {
        showToast('Failed to load movies: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

function displayMovies(movies) {
    const container = document.getElementById('moviesList');
    
    if (movies.length === 0) {
        container.innerHTML = '<p>No movies available</p>';
        return;
    }

    container.innerHTML = movies.map(movie => `
        <div class="movie-card" onclick="selectMovie('${movie.id}')">
            <h3>${movie.title}</h3>
            <span class="genre">${movie.genre}</span>
            <p class="duration">Duration: ${movie.duration_minutes} minutes</p>
            <p class="description">${movie.description}</p>
        </div>
    `).join('');
}

async function selectMovie(movieId) {
    showLoading();
    try {
        currentMovie = await apiCall(`/movies/${movieId}`);
        await loadShowtimes(movieId);
        showTab('showtimes');
    } catch (error) {
        showToast('Failed to load movie details: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// ==================== Showtimes ====================

async function loadShowtimes(movieId) {
    try {
        const data = await apiCall(`/showtimes?movie_id=${movieId}`);
        displayShowtimes(data);
    } catch (error) {
        showToast('Failed to load showtimes: ' + error.message, 'error');
    }
}

function displayShowtimes(showtimes) {
    document.getElementById('movieTitle').textContent = currentMovie.title;
    const container = document.getElementById('showtimesList');
    
    if (showtimes.length === 0) {
        container.innerHTML = '<p>No showtimes available for this movie</p>';
        return;
    }

    container.innerHTML = showtimes.map(showtime => {
        const startTime = new Date(showtime.start_time);
        return `
            <div class="showtime-card" onclick="selectShowtime('${showtime.id}')">
                <div class="theater">${showtime.theater_name}</div>
                <div class="time">${startTime.toLocaleString()}</div>
                <div class="price">$${showtime.price}</div>
            </div>
        `;
    }).join('');
}

async function selectShowtime(showtimeId) {
    showLoading();
    try {
        currentShowtime = await apiCall(`/showtimes/${showtimeId}`);
        await loadSeats(showtimeId);
        showTab('seats');
    } catch (error) {
        showToast('Failed to load showtime: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// ==================== Seats ====================

async function loadSeats(showtimeId) {
    try {
        const data = await apiCall(`/reservations/showtime/${showtimeId}/seats`);
        displaySeats(data);
    } catch (error) {
        showToast('Failed to load seats: ' + error.message, 'error');
    }
}

function displaySeats(seatsData) {
    const startTime = new Date(currentShowtime.start_time);
    document.getElementById('showtimeInfo').innerHTML = `
        <strong>${currentMovie.title}</strong><br>
        ${currentShowtime.theater_name}<br>
        ${startTime.toLocaleString()}<br>
        Price: $${currentShowtime.price}
    `;

    const container = document.getElementById('seatsGrid');
    selectedSeats = [];
    updateBookingSummary();

    // Group seats by row
    const seatsByRow = {};
    seatsData.forEach(seat => {
        if (!seatsByRow[seat.row_label]) {
            seatsByRow[seat.row_label] = [];
        }
        seatsByRow[seat.row_label].push(seat);
    });

    // Sort rows alphabetically
    const sortedRows = Object.keys(seatsByRow).sort();

    container.innerHTML = sortedRows.map(row => {
        const seats = seatsByRow[row].sort((a, b) => a.seat_number - b.seat_number);
        
        return `
            <div class="seat-row">
                <div class="seat-row-label">${row}</div>
                ${seats.map(seat => {
                    const classes = ['seat'];
                    if (seat.is_available) {
                        classes.push('available');
                        if (seat.seat_type === 'VIP') classes.push('vip');
                    } else {
                        classes.push('reserved');
                    }
                    
                    return `
                        <div class="${classes.join(' ')}" 
                             data-seat-id="${seat.id}"
                             data-seat-type="${seat.seat_type}"
                             onclick="toggleSeat('${seat.id}', ${seat.is_available}, '${seat.seat_type}', '${row}${seat.seat_number}')">
                            ${seat.seat_number}
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }).join('');
}

function toggleSeat(seatId, isAvailable, seatType, seatLabel) {
    if (!isAvailable) return;

    const seatElement = document.querySelector(`[data-seat-id="${seatId}"]`);
    const index = selectedSeats.findIndex(s => s.id === seatId);

    if (index > -1) {
        // Deselect seat
        selectedSeats.splice(index, 1);
        seatElement.classList.remove('selected');
    } else {
        // Select seat
        selectedSeats.push({ id: seatId, type: seatType, label: seatLabel });
        seatElement.classList.add('selected');
    }

    updateBookingSummary();
}

function updateBookingSummary() {
    document.getElementById('selectedSeatsCount').textContent = selectedSeats.length;
    
    const basePrice = parseFloat(currentShowtime.price);
    const totalPrice = selectedSeats.reduce((total, seat) => {
        return total + (seat.type === 'VIP' ? basePrice * 1.5 : basePrice);
    }, 0);
    
    document.getElementById('totalPrice').textContent = totalPrice.toFixed(2);
    document.getElementById('bookBtn').disabled = selectedSeats.length === 0;
}

// ==================== Reservations ====================

async function createReservation() {
    if (selectedSeats.length === 0) return;

    showLoading();
    try {
        const payload = {
            showtime_id: currentShowtime.id,
            seat_ids: selectedSeats.map(s => s.id)
        };

        const data = await apiCall('/reservations', {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        showToast('Reservation created successfully!');
        showTab('reservations');
        loadReservations();
    } catch (error) {
        showToast('Failed to create reservation: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function loadReservations() {
    showLoading();
    try {
        const data = await apiCall('/reservations/my');
        displayReservations(data);
    } catch (error) {
        showToast('Failed to load reservations: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

function displayReservations(reservations) {
    const container = document.getElementById('reservationsList');
    
    if (reservations.length === 0) {
        container.innerHTML = '<p>No reservations found</p>';
        return;
    }

    container.innerHTML = reservations.map(reservation => {
        const createdAt = new Date(reservation.created_at);
        return `
            <div class="reservation-card">
                <h3>Reservation #${reservation.id.substring(0, 8)}</h3>
                <div class="info"><strong>Movie:</strong> ${reservation.showtime.movie_title}</div>
                <div class="info"><strong>Theater:</strong> ${reservation.showtime.theater_name}</div>
                <div class="info"><strong>Time:</strong> ${new Date(reservation.showtime.start_time).toLocaleString()}</div>
                <div class="info"><strong>Seats:</strong> ${reservation.seats.map(s => `${s.row_label}${s.seat_number}`).join(', ')}</div>
                <div class="info"><strong>Total Price:</strong> $${reservation.total_price}</div>
                <div class="info"><strong>Booked:</strong> ${createdAt.toLocaleString()}</div>
                <span class="status ${reservation.status.toLowerCase()}">${reservation.status}</span>
                ${reservation.status === 'CONFIRMED' ? `
                    <button onclick="cancelReservation('${reservation.id}')" class="btn btn-danger" style="margin-top: 10px;">Cancel Reservation</button>
                ` : ''}
            </div>
        `;
    }).join('');
}

async function cancelReservation(reservationId) {
    if (!confirm('Are you sure you want to cancel this reservation?')) return;

    showLoading();
    try {
        await apiCall(`/reservations/${reservationId}`, {
            method: 'DELETE'
        });
        showToast('Reservation cancelled successfully');
        loadReservations();
    } catch (error) {
        showToast('Failed to cancel reservation: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// ==================== Admin Functions ====================

async function loadAdminReports() {
    showLoading();
    try {
        const [capacity, revenue] = await Promise.all([
            apiCall('/admin/capacity-report'),
            apiCall('/admin/revenue-report')
        ]);
        
        displayCapacityReport(capacity);
        displayRevenueReport(revenue);
    } catch (error) {
        showToast('Failed to load reports: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

function displayCapacityReport(data) {
    const container = document.getElementById('capacityReport');
    
    if (!data.theaters || data.theaters.length === 0) {
        container.innerHTML = '<p>No data available</p>';
        return;
    }

    container.innerHTML = `
        <table class="report-table">
            <thead>
                <tr>
                    <th>Theater</th>
                    <th>Total Seats</th>
                    <th>Reserved Seats</th>
                    <th>Available Seats</th>
                    <th>Utilization</th>
                </tr>
            </thead>
            <tbody>
                ${data.theaters.map(theater => `
                    <tr>
                        <td>${theater.theater_name}</td>
                        <td>${theater.total_seats}</td>
                        <td>${theater.reserved_seats}</td>
                        <td>${theater.available_seats}</td>
                        <td>${theater.utilization_percentage.toFixed(1)}%</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function displayRevenueReport(data) {
    const container = document.getElementById('revenueReport');
    
    if (!data.movies || data.movies.length === 0) {
        container.innerHTML = '<p>No data available</p>';
        return;
    }

    container.innerHTML = `
        <div style="margin-bottom: 15px;">
            <strong>Total Revenue:</strong> $${data.total_revenue}
        </div>
        <table class="report-table">
            <thead>
                <tr>
                    <th>Movie</th>
                    <th>Total Reservations</th>
                    <th>Total Seats Sold</th>
                    <th>Revenue</th>
                </tr>
            </thead>
            <tbody>
                ${data.movies.map(movie => `
                    <tr>
                        <td>${movie.movie_title}</td>
                        <td>${movie.total_reservations}</td>
                        <td>${movie.total_seats_sold}</td>
                        <td>$${movie.revenue}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

async function addMovie(event) {
    event.preventDefault();
    showLoading();

    try {
        const payload = {
            title: document.getElementById('movieTitle').value,
            description: document.getElementById('movieDescription').value,
            genre: document.getElementById('movieGenre').value,
            duration_minutes: parseInt(document.getElementById('movieDuration').value),
            release_date: document.getElementById('movieReleaseDate').value || null
        };

        await apiCall('/movies', {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        showToast('Movie added successfully!');
        document.getElementById('addMovieForm').reset();
        loadMovies();
    } catch (error) {
        showToast('Failed to add movie: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// ==================== Tab Navigation ====================

function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Hide all tab buttons active state
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    if (tabName === 'movies') {
        document.getElementById('moviesTab').classList.add('active');
        document.querySelector('.tab-btn').classList.add('active');
    } else if (tabName === 'showtimes') {
        document.getElementById('showtimesTab').classList.add('active');
    } else if (tabName === 'seats') {
        document.getElementById('seatsTab').classList.add('active');
    } else if (tabName === 'reservations') {
        document.getElementById('reservationsTab').classList.add('active');
        document.querySelectorAll('.tab-btn')[1].classList.add('active');
        loadReservations();
    } else if (tabName === 'admin') {
        document.getElementById('adminTab').classList.add('active');
        document.querySelectorAll('.tab-btn')[2].classList.add('active');
        loadAdminReports();
    }
}

// ==================== Initialize ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Movie Reservation System loaded');
});
