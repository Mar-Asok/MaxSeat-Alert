from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import timedelta
import time

app = Flask(__name__)
app.secret_key = "maxseat_enterprise_premium_secure_key"
app.permanent_session_lifetime = timedelta(days=7)

# --- GLOBAL DATABASE ---
users = {
    "admin": {"password": "123", "role": "admin", "email": "admin@maxseat.ph"},
    "PNP-Police": {"password": "123", "role": "enforcer", "email": "cdo.precinct@pnp.gov.ph"}
}

# Live GNSS and Status Database
puv_database = [
    {"id": 1, "username": "dummy1", "company": "Señor Pedro Lines", "plate": "KVR-102", "driver": "Juan Dela Cruz", "passengers": 14, "capacity": 22, "loc_name": "Bulua Highway", "lat": 8.4965, "lng": 124.6235, "status": "Active", "speed": "45 km/h", "last_update": "Just now", "show_name": True, "schedule": "06:00 AM - 08:00 PM"},
    {"id": 2, "username": "dummy2", "company": "Oro Transit", "plate": "AAB-5501", "driver": "Ricardo Dalisay", "passengers": 25, "capacity": 22, "loc_name": "CM Recto Ave", "lat": 8.4865, "lng": 124.6508, "status": "Active", "speed": "30 km/h", "last_update": "1 min ago", "show_name": False, "schedule": "05:00 AM - 09:00 PM"}
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
        role = request.form.get('role')
        username = request.form.get('username').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash("Passwords do not match.", "error")
        elif len(username) >= 4 and len(password) >= 6 and username not in users:
            users[username] = {"password": password, "role": role, "email": f"{username.lower().replace(' ', '')}@maxseat.ph"}
            
            # If Driver registers, create their PUV instance in the database
            if role == 'driver':
                new_puv = {
                    "id": len(puv_database) + 1,
                    "username": username,
                    "company": request.form.get('company'),
                    "plate": request.form.get('plate'),
                    "driver": username,  # Using username as driver name for now
                    "passengers": 0,
                    "capacity": int(request.form.get('capacity', 22)),
                    "schedule": request.form.get('schedule'),
                    "loc_name": "Dispatch Terminal",
                    "lat": 8.4860, "lng": 124.6500,
                    "status": "Idle", "speed": "0 km/h",
                    "last_update": "System Init",
                    "show_name": False
                }
                puv_database.append(new_puv)
                
            return render_template('register.html', success=True)
        else:
            flash("Registration failed. Ensure username (min 4) is unique and password (min 6) are valid.", "error")
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- SENSOR SIMULATION APIs (For Driver Dashboard) ---
@app.route('/api/update_sensor', methods=['POST'])
def update_sensor():
    if session.get('role') != 'driver': return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    action = data.get('action') # 'add' or 'sub'
    
    puv = next((p for p in puv_database if p['username'] == session['username']), None)
    if puv:
        if action == 'add': puv['passengers'] += 1
        elif action == 'sub' and puv['passengers'] > 0: puv['passengers'] -= 1
        return jsonify({"success": True, "passengers": puv['passengers'], "capacity": puv['capacity']})
    return jsonify({"error": "PUV not found"}), 404

@app.route('/api/toggle_name', methods=['POST'])
def toggle_name():
    if session.get('role') != 'driver': return jsonify({"error": "Unauthorized"}), 403
    puv = next((p for p in puv_database if p['username'] == session['username']), None)
    if puv:
        puv['show_name'] = not puv['show_name']
        return jsonify({"success": True, "show_name": puv['show_name']})
    return jsonify({"error": "PUV not found"}), 404

# --- CORE DASHBOARDS ---
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'): return redirect(url_for('login'))
    role = session['role']
    
    for p in puv_database:
        p['is_violator'] = p['passengers'] > p['capacity']
        p['load_percentage'] = int((p['passengers'] / p['capacity']) * 100) if p['capacity'] > 0 else 0

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
    elif role == 'driver':
        my_puv = next((p for p in puv_database if p['username'] == session['username']), None)
        return render_template('dashboard_driver.html', puv=my_puv, role=role)
    else:
        return redirect(url_for('logout'))

# --- APP ROUTING (SIDEBAR MENUS) ---
@app.route('/intercepts')
def intercepts():
    if not session.get('logged_in'): return redirect(url_for('login'))
    violators = [p for p in puv_database if p['passengers'] > p['capacity']]
    return render_template('intercepts.html', role=session['role'], puvs=violators)

@app.route('/fleet')
def fleet():
    if not session.get('logged_in'): return redirect(url_for('login'))
    return render_template('fleet.html', role=session['role'], puvs=puv_database)

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

if __name__ == '__main__':
    app.run(debug=True)