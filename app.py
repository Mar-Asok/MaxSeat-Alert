from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = "maxseat_secure_key"

def get_puv_data():
    # Accurate CDO Locations (Agora and Bulua Terminals)
    return [
        {
            "id": 1, "type": "🚌", "company": "Señor Pedro Lines", "plate": "KVR-102", 
            "driver": "Juan Dela Cruz", "passenger": "14/22", "loc_name": "Bulua Westbound", 
            "lat": 8.5018, "lng": 124.6115, "time": "13:04"
        },
        {
            "id": 2, "type": "🚌", "company": "Oro Transit", "plate": "AAB-5501", 
            "driver": "Ricardo Dalisay", "passenger": "23/22", "loc_name": "Agora Eastbound", 
            "lat": 8.4928, "lng": 124.6572, "time": "13:04"
        },
        {
            "id": 3, "type": "🚌", "company": "MisOr Express", "plate": "GA-9921", 
            "driver": "Emilio Aguinaldo", "passenger": "18/22", "loc_name": "Bulua Westbound", 
            "lat": 8.5012, "lng": 124.6120, "time": "13:04"
        },
        {
            "id": 4, "type": "🚌", "company": "CDEO Movers", "plate": "KLY-442", 
            "driver": "Ferdinand Mag", "passenger": "15/22", "loc_name": "Bulua Westbound", 
            "lat": 8.5025, "lng": 124.6105, "time": "13:04"
        },
        {
            "id": 5, "type": "🚌", "company": "Bukidnon Trans", "plate": "XYZ-8821", 
            "driver": "Manny P.", "passenger": "22/22", "loc_name": "Agora Eastbound", 
            "lat": 8.4935, "lng": 124.6580, "time": "13:04"
        },
        {
            "id": 6, "type": "🚌", "company": "Bukidnon Express", "plate": "ABC-1234", 
            "driver": "Jose Rizal", "passenger": "26/22", "loc_name": "Agora Eastbound", 
            "lat": 8.4915, "lng": 124.6565, "time": "13:04"
        }
    ]

@app.route('/')
def index():
    if 'logged_in' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == "admin" and request.form.get('password') == "1234":
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        flash("Invalid Credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'): return redirect(url_for('login'))
    puvs = get_puv_data()
    for p in puvs:
        curr, limit = map(int, p['passenger'].split('/'))
        p['is_violator'] = curr >= limit
    return render_template('dashboard.html', puvs=puvs)

@app.route('/records')
def records():
    if not session.get('logged_in'): return redirect(url_for('login'))
    violators = [p for p in get_puv_data() if int(p['passenger'].split('/')[0]) >= int(p['passenger'].split('/')[1])]
    return render_template('records.html', violators=violators)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)