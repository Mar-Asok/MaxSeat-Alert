from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "maxseat_enterprise_2026_secure"
app.permanent_session_lifetime = timedelta(days=7)

# Dummy Database
users = {
    "admin": {"password": "123", "role": "admin"},
    "Oro Transit": {"password": "123", "role": "cooperative"},
    "PNP-Police": {"password": "123", "role": "enforcer"}
}

def get_puv_data():
    return [
        {"id": 1, "company": "Señor Pedro Lines", "plate": "KVR-102", "driver": "Juan Dela Cruz", "passenger": "14/22", "loc_name": "Bulua Highway", "lat": 8.4820, "lng": 124.6150},
        {"id": 2, "company": "Oro Transit", "plate": "AAB-5501", "driver": "Ricardo Dalisay", "passenger": "28/22", "loc_name": "CM Recto Ave", "lat": 8.4865, "lng": 124.6508},
        {"id": 3, "company": "MisOr Express", "plate": "GA-9921", "driver": "Emilio Aguinaldo", "passenger": "18/22", "loc_name": "Kauswagan High", "lat": 8.4910, "lng": 124.6315}
    ]

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
            session['logged_in'], session['username'], session['role'] = True, username, role
            return redirect(url_for('dashboard'))
        flash("Invalid credentials for the selected role.", "error")
    return render_template('login.html')

# FIX PARA SA IMAGE_BC79FD.PNG
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        role = request.form.get('role')
        if len(username) < 4 or len(password) < 6 or username in users:
            flash("Check restrictions: Username (min 4), Password (min 6), or Duplicate.", "error")
        else:
            users[username] = {"password": password, "role": role}
            return render_template('register.html', success=True)
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'): return redirect(url_for('login'))
    role = session['role']
    puvs = get_puv_data()
    for p in puvs:
        curr, limit = map(int, p['passenger'].split('/'))
        p['is_violator'] = curr > limit

    if role == 'admin':
        return render_template('dashboard_admin.html', puvs=puvs, role=role)
    elif role == 'enforcer':
        filtered = [p for p in puvs if p['is_violator']]
        return render_template('dashboard_enforcer.html', puvs=filtered, role=role)
    else:
        filtered = [p for p in puvs if p['company'].lower() == session['username'].lower()]
        return render_template('dashboard_coop.html', puvs=filtered, role=role)

# SIDEBAR ROUTES
@app.route('/intercepts')
def intercepts():
    if not session.get('logged_in'): return redirect(url_for('login'))
    return render_template('intercepts.html', role=session['role'])

@app.route('/fleet')
def fleet():
    if not session.get('logged_in'): return redirect(url_for('login'))
    return render_template('fleet.html', role=session['role'])

@app.route('/settings')
def settings():
    if not session.get('logged_in'): return redirect(url_for('login'))
    return render_template('settings.html', role=session['role'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)