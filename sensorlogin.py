from flask import Flask, request, render_template_string, send_file, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Dummy user database
users = {'user@example.com': {'password': 'password'}}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            # Create user-specific directories when the user logs in
            user_data_dir = f"sensor-data/{current_user.id}"
            os.makedirs(user_data_dir, exist_ok=True)
            os.makedirs(f"{user_data_dir}/water-level-data", exist_ok=True)
            os.makedirs(f"{user_data_dir}/regen-data", exist_ok=True)
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'
    return '''
        <form method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/store-sensor-data', methods=['POST'])
@login_required
def store_sensor_data():
    number = request.data.decode()
    epoch_time = int(time.time() * 1000)  # milliseconds since epoch
    current_time = datetime.now()
    user_data_dir = f"sensor-data/{current_user.id}"
    filename = f"{user_data_dir}/{current_time.strftime('%Y-%m-%d')}.txt"  # Changed to daily files
    
    with open(filename, 'a') as file:
        file.write(f"{epoch_time},{number}\n")
    
    return "Data stored successfully", 200

@app.route('/delete-sensor-data', methods=['POST'])
@login_required
def delete_sensor_data():
    user_data_dir = f"sensor-data/{current_user.id}"
    for filename in os.listdir(user_data_dir):
        file_path = os.path.join(user_data_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return "All sensor data deleted", 200

@app.route('/store-water-level', methods=['POST'])
@login_required
def store_water_level():
    level = request.data.decode()
    epoch_time = int(time.time() * 1000)  # milliseconds since epoch
    current_time = datetime.now()
    user_data_dir = f"sensor-data/{current_user.id}/water-level-data"
    filename = f"{user_data_dir}/{current_time.strftime('%Y-%m-%d')}.txt"  # Changed to daily files
    
    with open(filename, 'a') as file:
        file.write(f"{epoch_time},{level}\n")
    
    return "Water level data stored successfully", 200

@app.route('/store-regen-signal', methods=['POST'])
@login_required
def store_regen_signal():
    signal = request.data.decode()
    epoch_time = int(time.time() * 1000)  # milliseconds since epoch
    current_time = datetime.now()
    user_data_dir = f"sensor-data/{current_user.id}/regen-data"
    filename = f"{user_data_dir}/{current_time.strftime('%Y-%m-%d')}.txt"  # Changed to daily files
    
    with open(filename, 'a') as file:
        file.write(f"{epoch_time},{signal}\n")
    
    return "Regeneration signal data stored successfully", 200

@app.route('/set-tank-size', methods=['POST'])
@login_required
def set_tank_size():
    tank_size = request.data.decode()
    user_data_dir = f"sensor-data/{current_user.id}"
    tank_size_file = f"{user_data_dir}/tank_size.txt"
    with open(tank_size_file, 'w') as file:
        file.write(tank_size)
    return "Tank size set successfully", 200

@app.route('/record-salt-refill', methods=['POST'])
@login_required
def record_salt_refill():
    refill_date = datetime.now().strftime('%Y-%m-%d')
    user_data_dir = f"sensor-data/{current_user.id}"
    salt_refill_file = f"{user_data_dir}/salt_refill.txt"
    with open(salt_refill_file, 'a') as file:
        file.write(f"{refill_date}\n")
    return "Salt refill recorded", 200

@app.route('/camera-feed')
@login_required
def camera_feed():
    # For demonstration purposes, returning a static image
    # In a real scenario, you would capture and return a video frame from your camera
    return send_file("static/camera_image.jpg", mimetype='image/jpeg')

@app.route('/')
@login_required
def index():
    user_data_dir = f"sensor-data/{current_user.id}"
    sensor_data = []
    water_level_data = []
    regen_data = []
    
    # Read all files and accumulate data
    sensor_dir = f"{user_data_dir}"
    water_level_dir = f"{user_data_dir}/water-level-data"
    regen_dir = f"{user_data_dir}/regen-data"
    if os.path.exists(sensor_dir):
        for filename in sorted(os.listdir(sensor_dir)):
            with open(f"{sensor_dir}/{filename}", 'r') as file:
                for line in file:
                    epoch, value = line.strip().split(',')
                    sensor_data.append([int(epoch), int(value)])

    if os.path.exists(water_level_dir):
        for filename in sorted(os.listdir(water_level_dir)):
            with open(f"{water_level_dir}/{filename}", 'r') as file:
                for line in file:
                    epoch, level = line.strip().split(',')
                    water_level_data.append([int(epoch), int(level)])

    if os.path.exists(regen_dir):
        for filename in sorted(os.listdir(regen_dir)):
            with open(f"{regen_dir}/{filename}", 'r') as file:
                for line in file:
                    epoch, signal = line.strip().split(',')
                    regen_data.append([int(epoch), int(signal)])
    
    # Sort the data by timestamp
    sensor_data.sort(key=lambda x: x[0])
    water_level_data.sort(key=lambda x: x[0])
    regen_data.sort(key=lambda x: x[0])

    # Prepare data for ApexCharts - using timestamp for x-axis
    sensor_data_js = str([[epoch, value] for epoch, value in sensor_data]).replace("'", "")
    water_level_data_js = str([[epoch, level] for epoch, level in water_level_data]).replace("'", "")
    regen_data_js = str([[epoch, signal] for epoch, signal in regen_data]).replace("'", "")

    # HTML content with ApexCharts
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sensor Data Dashboard</title>
        <!-- Include ApexCharts -->
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        <script>
        function deleteSensorData() {{
            fetch('/delete-sensor-data', {{ method: 'POST' }})
            .then(response => response.text())
            .then(data => {{
                alert(data);
                location.reload(); // Reload the page to update the chart
            }});
        }}

        function setTankSize() {{
            var tankSize = document.getElementById("tank-size-input").value;
            fetch('/set-tank-size', {{
                method: 'POST',
                body: tankSize
            }})
            .then(response => response.text())
            .then(data => {{
                alert(data);
            }});
        }}

        function recordSaltRefill() {{
            fetch('/record-salt-refill', {{ method: 'POST' }})
            .then(response => response.text())
            .then(data => {{
                alert(data);
            }});
        }}
        </script>
    </head>
    
    <body>
        <h1>Sensor Data Dashboard</h1>
        <div>
            <select id="chart-selector" onchange="changeChart()">
                <option value="sensor_chart">Sensor Data</option>
                <option value="water_level_chart">Water Level</option>
                <option value="regen_chart">Regeneration Signal</option>
            </select>
            <div id="chart-container" style="height: 350px;"></div>
        </div>
        <div style="float: right;">
            <h2>Tank Settings</h2>
            <label for="tank-size-input">Tank Size (Liters):</label>
            <input type="number" id="tank-size-input" name="tank-size" min="0">
            <button onclick="setTankSize()">Set Tank Size</button>
            <br>
            <button onclick="recordSaltRefill()">Record Salt Refill</button>
        </div>
        <div style="clear: both;"></div>
        <script>
            var sensorOptions = {{
                series: [{{
                    "name": 'Sensor Value',
                    "data": {sensor_data_js}
                }}],
                chart: {{
                    type: 'line',
                    height: 350
                }},
                xaxis: {{
                    type: 'datetime',
                }},
                stroke: {{
                    curve: 'smooth'
                }},
                title: {{
                    text: 'Sensor Data Over Time',
                    align: 'left'
                }},
                tooltip: {{
                    x: {{
                        format: 'dd MMM yyyy HH:mm:ss'
                    }}
                }}
            }};

            var waterLevelOptions = {{
                series: [{{
                    "name": 'Water Level',
                    "data": {water_level_data_js}
                }}],
                chart: {{
                    type: 'line',
                    height: 350
                }},
                xaxis: {{
                    type: 'datetime',
                }},
                stroke: {{
                    curve: 'smooth'
                }},
                title: {{
                    text: 'Water Level Over Time',
                    align: 'left'
                }},
                tooltip: {{
                    x: {{
                        format: 'dd MMM yyyy HH:mm:ss'
                    }}
                }}
            }};

            var regenOptions = {{
                series: [{{
                    "name": 'Regeneration Signal',
                    "data": {regen_data_js}
                }}],
                chart: {{
                    type: 'line',
                    height: 350
                }},
                xaxis: {{
                    type: 'datetime',
                }},
                stroke: {{
                    curve: 'smooth'
                }},
                title: {{
                    text: 'Regeneration Signals Over Time',
                    align: 'left'
                }},
                tooltip: {{
                    x: {{
                        format: 'dd MMM yyyy HH:mm:ss'
                    }}
                }}
            }};

            var chartContainer = document.getElementById("chart-container");
            var sensorChart = new ApexCharts(chartContainer, sensorOptions);
            var waterLevelChart = new ApexCharts(chartContainer, waterLevelOptions);
            var regenChart = new ApexCharts(chartContainer, regenOptions);

            var currentChart = sensorChart;
            currentChart.render();

            function changeChart() {{
                var selectedChart = document.getElementById("chart-selector").value;
                currentChart.destroy();
                if (selectedChart === "sensor_chart") {{
                    currentChart = sensorChart;
                }} else if (selectedChart === "water_level_chart") {{
                    currentChart = waterLevelChart;
                }} else if (selectedChart === "regen_chart") {{
                    currentChart = regenChart;
                }}
                currentChart.render();
            }}
        </script>

        <h2>Latest Sensor Data</h2>
        <button onclick="deleteSensorData()">Delete All Sensor Data</button>
        <table border="1">
            <tr>
                <th>Time</th>
                <th>Sensor Data</th>
                <th>Water Level</th>
                <th>Regeneration Signal</th>
            </tr>
            {"".join(f"<tr><td>{datetime.fromtimestamp(int(epoch)/1000).strftime('%Y-%m-%d %H:%M:%S')}</td><td>{sensor_value}</td><td>{water_level}</td><td>{regen_signal}</td></tr>" for (epoch, sensor_value), (_, water_level), (_, regen_signal) in zip(sensor_data[-10:], water_level_data[-10:], regen_data[-10:]))}
        </table>
        <a href="/logout">Logout</a>
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(debug=True)
