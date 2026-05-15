from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta
import time

app = Flask(__name__)
app.secret_key = "maxseat_enterprise_premium_secure_key"
app.permanent_session_lifetime = timedelta(days=7)

# --- DUMMY DATABASE ---
users = {
    "admin": {"password": "123", "role": "admin", "email": "admin@maxseat.ph"},
    "Oro Transit": {"password": "123", "role": "cooperative", "email": "contact@orotransit.com"},
    "PNP-Police": {"password": "123", "role": "enforcer", "email": "cdo.precinct@pnp.gov.ph"}
}

# Global database for PUVs
puv_database = [
    {"id": 1, "company": "Señor Pedro Lines", "plate": "KVR-102", "driver": "Juan Dela Cruz", "passenger": "14/22", "loc_name": "Bulua Highway", "lat": 8.4965, "lng": 124.6235, "status": "Active", "speed": "45 km/h", "last_update": "Just now"},
    {"id": 2, "company": "Oro Transit", "plate": "AAB-5501", "driver": "Ricardo Dalisay", "passenger": "28/22", "loc_name": "CM Recto Ave", "lat": 8.4865, "lng": 124.6508, "status": "Active", "speed": "30 km/h", "last_update": "1 min ago"},
    {"id": 3, "company": "MisOr Express", "plate": "GA-9921", "driver": "Emilio Aguinaldo", "passenger": "18/22", "loc_name": "Kauswagan Highway", "lat": 8.4950, "lng": 124.6360, "status": "Idle", "speed": "0 km/h", "last_update": "5 mins ago"},
    {"id": 4, "company": "Oro Transit", "plate": "KLY-442", "driver": "Ferdinand Mag", "passenger": "26/22", "loc_name": "Lapasan Highway", "lat": 8.4845, "lng": 124.6648, "status": "Active", "speed": "50 km/h", "last_update": "Just now"},
    {"id": 5, "company": "Bukidnon Express", "plate": "XYZ-998", "driver": "Jose Rizal", "passenger": "30/22", "loc_name": "Puerto Flyover", "lat": 8.4755, "lng": 124.7042, "status": "Stopped", "speed": "0 km/h", "last_update": "10 mins ago"},
    {"id": 6, "company": "Señor Pedro Lines", "plate": "BBA-112", "driver": "Andres B.", "passenger": "20/22", "loc_name": "Divisoria Center", "lat": 8.4815, "lng": 124.6432, "status": "Active", "speed": "15 km/h", "last_update": "2 mins ago"}
]

# --- AUTHENTICATION ---
@app.route('/')
def index():
    if session.get('logged_in'): return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        username = request.form.get('username')
        password = request.form.get('password')
        user = users.get(username)
        if user and user['password'] == password and user['role'] == role:
            session.permanent = True
            session['logged_in'] = True
            session['username'] = username
            session['role'] = role
            return redirect(url_for('dashboard'))
        flash("Invalid credentials for the selected role.", "error")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        
        if password != confirm_password:
            flash("Passwords do not match.", "error")
        elif len(username) >= 4 and len(password) >= 6 and username not in users:
            users[username] = {"password": password, "role": role, "email": f"{username.lower().replace(' ', '')}@maxseat.ph"}
            return render_template('register.html', success=True)
        else:
            flash("Registration failed. Ensure username (min 4) is unique and password (min 6) are valid.", "error")
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- CORE DASHBOARDS ---
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'): return redirect(url_for('login'))
    role = session['role']
    
    for p in puv_database:
        curr, limit = map(int, p['passenger'].split('/'))
        p['is_violator'] = curr > limit
        p['load_percentage'] = int((curr / limit) * 100)

    stats = {
        "total_units": len(puv_database),
        "active_violations": len([p for p in puv_database if p['is_violator']]),
        "moving_units": len([p for p in puv_database if p['status'] == 'Active']),
    }

    if role == 'admin':
        return render_template('dashboard_admin.html', puvs=puv_database, role=role, stats=stats)
    elif role == 'enforcer':
        filtered = [p for p in puv_database if p['is_violator']]
        return render_template('dashboard_enforcer.html', puvs=filtered, role=role, stats=stats)
    else:
        filtered = [p for p in puv_database if p['company'].lower() == session['username'].lower()]
        coop_stats = {
            "my_fleet": len(filtered),
            "moving": len([p for p in filtered if p['status'] == 'Active']),
            "overloaded": len([p for p in filtered if p['is_violator']])
        }
        return render_template('dashboard_coop.html', puvs=filtered, role=role, stats=coop_stats)

@app.route('/add_puv', methods=['POST'])
def add_puv():
    if session.get('role') != 'cooperative': return redirect(url_for('dashboard'))
    plate = request.form.get('plate')
    driver = request.form.get('driver')
    capacity = request.form.get('capacity')
    
    new_puv = {
        "id": len(puv_database) + 1,
        "company": session['username'],
        "plate": plate,
        "driver": driver,
        "passenger": f"0/{capacity}",
        "loc_name": "Dispatch Terminal",
        "lat": 8.4860,
        "lng": 124.6500,
        "status": "Idle",
        "speed": "0 km/h",
        "last_update": "Just added"
    }
    puv_database.append(new_puv)
    return redirect(url_for('dashboard'))

# --- APP ROUTING (SIDEBAR MENUS) ---
@app.route('/intercepts')
def intercepts():
    if not session.get('logged_in'): return redirect(url_for('login'))
    role = session['role']
    username = session['username']
    violators = [p for p in puv_database if int(p['passenger'].split('/')[0]) > int(p['passenger'].split('/')[1])]
    if role == 'cooperative': violators = [p for p in violators if p['company'].lower() == username.lower()]
    return render_template('intercepts.html', role=role, puvs=violators)

@app.route('/fleet')
def fleet():
    if not session.get('logged_in'): return redirect(url_for('login'))
    role = session['role']
    username = session['username']
    if role == 'cooperative': filtered_fleet = [p for p in puv_database if p['company'].lower() == username.lower()]
    else: filtered_fleet = puv_database
    return render_template('fleet.html', role=role, puvs=filtered_fleet)

@app.route('/user_management')
def user_management():
    if session.get('role') != 'admin': return redirect(url_for('dashboard'))
    return render_template('user_management.html', role=session['role'], users_db=users)

@app.route('/audit_logs')
def audit_logs():
    if session.get('role') != 'admin': return redirect(url_for('dashboard'))
    return render_template('audit_logs.html', role=session['role'])

@app.route('/citations')
def citations():
    if session.get('role') != 'enforcer': return redirect(url_for('dashboard'))
    return render_template('citations.html', role=session['role'])

@app.route('/settings')
def settings():
    if not session.get('logged_in'): return redirect(url_for('login'))
    user_data = users.get(session['username'], {})
    return render_template('settings.html', role=session['role'], user_data=user_data)

@app.route('/update_settings', methods=['POST'])
def update_settings():
    # Dummy route to make settings functional
    flash("Settings updated successfully!", "success")
    return redirect(url_for('settings'))

if __name__ == '__main__':
    app.run(debug=True)