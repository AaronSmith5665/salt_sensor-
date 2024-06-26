from flask import Flask, request, render_template_string, send_file, jsonify
import os
import time
from datetime import datetime

app = Flask(__name__)
sensor_data_dir = "sensor-data"
water_det_data_dir = "water-level-data"
regen_data_dir = "regen-data"
tank_size_file = "tank_size.txt"
salt_refill_file = "salt_refill.txt" 

# Ensure the data directories exist
os.makedirs(sensor_data_dir, exist_ok=True)
os.makedirs(water_det_data_dir, exist_ok=True)
os.makedirs(regen_data_dir, exist_ok=True)

sensor_data = []
water_level_data = []
regen_data = []
tank_size = None

def get_endpoints():
    endpoints = []
    for rule in app.url_map.iter_rules():
        endpoints.append({
            "endpoint": rule.endpoint,
            "methods": sorted(rule.methods),
            "path": str(rule)
        })
    return endpoints

@app.route('/registered-endpoints')
def registered_endpoints():
    return jsonify(get_endpoints())

@app.route('/store-sensor-data', methods=['POST', 'GET'])
def store_sensor_data():
    global sensor_data
    
    if request.method == 'POST':
        number = request.data.decode()
        epoch_time = int(time.time() * 1000)  # milliseconds since epoch
        current_time = datetime.now()
        timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')  # Date stamp in format YYYY-MM-DD HH:MM:SS
        filename = f"{sensor_data_dir}/{current_time.strftime('%Y-%m-%d')}.txt"  # Changed to daily files
    
        with open(filename, 'a') as file:
            file.write(f"{epoch_time},{number}\n")

        sensor_data.append({'timestamp': timestamp, 'value': number})  # Append timestamp along with value
        
        return "Data stored successfully", 200

    elif request.method == 'GET':
        return jsonify(sensor_data)

@app.route('/delete-sensor-data', methods=['POST'])
def delete_sensor_data():
    global sensor_data
    sensor_data = []
    for filename in os.listdir(sensor_data_dir):
        file_path = os.path.join(sensor_data_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return "All sensor data deleted", 200

@app.route('/delete-water-level-data', methods=['POST'])
def delete_water_level_data():
    global water_level_data
    water_level_data = []
    for filename in os.listdir(water_det_data_dir):
        file_path = os.path.join(water_det_data_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return "All water level data deleted", 200

@app.route('/delete-regen-data', methods=['POST'])
def delete_regen_data():
    global regen_data
    regen_data = []
    for filename in os.listdir(regen_data_dir):
        file_path = os.path.join(regen_data_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return "All regeneration data deleted", 200

@app.route('/store-water-det', methods=['POST', 'GET'])
def store_water_det():
    global water_det_data

    if request.method == 'POST':
        epoch_time = int(time.time() * 1000)  # milliseconds since epoch
        current_time = datetime.now()
        filename = f"{water_det_data_dir}/{current_time.strftime('%Y-%m-%d')}.txt"  # Daily files

        with open(filename, 'a') as file:
            file.write(f"{epoch_time}\n")

        water_det_data.append(1)
        return "Water detection data stored successfully", 200

    elif request.method == 'GET':
        timestamps = [epoch_time for epoch_time in water_det_data]  # Extract timestamps from water_det_data
        return jsonify(timestamps), 200


@app.route('/store-regen-signal', methods=['POST', 'GET'])
def store_regen_signal():
    global regen_data

    if request.method == 'POST':
        epoch_time = int(time.time() * 1000)  # milliseconds since epoch
        current_time = datetime.now()
        filename = f"{regen_data_dir}/{current_time.strftime('%Y-%m-%d')}.txt"  # Daily files

        with open(filename, 'a') as file:
            file.write(f"{epoch_time}\n")  # Store only the timestamp

        regen_data.append(1)  # Append 1 to signify a regen cycle
        return "Regeneration signal data stored successfully", 200

    elif request.method == 'GET':
        timestamps = [epoch_time for epoch_time in regen_data]  # Extract timestamps from regen_data
        return jsonify(timestamps), 200

@app.route('/set-tank-size', methods=['POST'])
def set_tank_size():
    global tank_size

    tank_size_data = request.data.decode()  # Decode request data
    with open(tank_size_file, 'w') as file:
        file.write(tank_size_data)  # Write tank size data to the file
    tank_size = tank_size_data  # Update tank size variable
    logging.debug("Tank size set to: %s", tank_size)
    return "Tank size set successfully", 200

@app.route('/get-tank-size', methods=['GET'])
def get_tank_size():
    try:
        with open(tank_size_file, 'r') as file:
            tank_size_data = file.readline().strip()  # Read tank size from file
            if tank_size_data:
                tank_size = int(tank_size_data)  # Convert tank size data to integer
                return str(tank_size), 200  # Return the tank size as a string
            else:
                return "Tank size not found", 404
    except FileNotFoundError:
        return "Tank size not found", 404

@app.route('/record-salt-refill', methods=['POST', 'GET'])
def record_salt_refill():
    global salt_refill
    
    if request.method == 'POST':
        refill_date = datetime.now().strftime('%Y-%m-%d')
        with open(salt_refill_file, 'a') as file:
            file.write(f"{refill_date}\n")
        return "Salt refill recorded", 200

    elif request.method == 'GET':
        try:
            with open(salt_refill_file, 'r') as file:
                refill_dates = [line.strip() for line in file.readlines()]
                return jsonify({"refill_dates": refill_dates}), 200
        except FileNotFoundError:
            return jsonify({"error": "File not found"}), 404  # Return a 404 status code if file not found

@app.route('/camera-feed')
def camera_feed():
    # For demonstration purposes, returning a static image
    # In a real scenario, you would capture and return a video frame from your camera
    return send_file("static/camera_image.jpg", mimetype='image/jpeg')

@app.route('/')
def index():
    sensor_data = []
    water_level_data = []
    regen_data = []
    
    # Read all files and accumulate data
    for filename in sorted(os.listdir(sensor_data_dir)):
        with open(f"{sensor_data_dir}/{filename}", 'r') as file:
            for line in file:
                epoch, value = line.strip().split(',')
                sensor_data.append([int(epoch), int(value)])

    for filename in sorted(os.listdir(water_level_data_dir)):
        with open(f"{water_level_data_dir}/{filename}", 'r') as file:
            for line in file:
                epoch, level = line.strip().split(',')
                water_level_data.append([int(epoch), int(level)])

    for filename in sorted(os.listdir(regen_data_dir)):
        with open(f"{regen_data_dir}/{filename}", 'r') as file:
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

        function deleteWaterLevelData() {{
            fetch('/delete-water-level-data', {{ method: 'POST' }})
            .then(response => response.text())
            .then(data => {{
                alert(data);
                location.reload();
            }});
        }}
        
        function deleteRegenData() {{
            fetch('/delete-regen-data', {{ method: 'POST' }})
            .then(response => response.text())
            .then(data => {{
                alert(data);
                location.reload();
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
        <button onclick="deleteWaterLevelData()">Delete All Water Level Data</button>
        <button onclick="deleteRegenData()">Delete All Regeneration Data</button>
        <table border="1">
            <tr>
                <th>Time</th>
                <th>Sensor Data</th>
                <th>Water Level</th>
                <th>Regeneration Signal</th>
            </tr>
          {"".join(f"<tr><td>{datetime.fromtimestamp(int(epoch)/1000).strftime('%Y-%m-%d %H:%M:%S')}</td><td>{sensor_value}</td><td>{water_level}</td><td>{regen_signal}</td></tr>" for (epoch, sensor_value), (_, water_level), (_, regen_signal) in zip(sensor_data[-10:], water_level_data[-10:], regen_data[-10:]))}
        </table>
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(debug=True)
