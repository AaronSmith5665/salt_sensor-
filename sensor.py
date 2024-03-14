from flask import Flask, request, render_template_string, send_file, jsonify
import os
import time
from datetime import datetime

app = Flask(__name__)
sensor_data_dir = "sensor-data"
water_level_data_dir = "water-level-data"
regen_data_dir = "regen-data"
tank_size_file = "tank_size.txt"
salt_refill_file = "salt_refill.txt" 

# Ensure the data directories exist
os.makedirs(sensor_data_dir, exist_ok=True)
os.makedirs(water_level_data_dir, exist_ok=True)
os.makedirs(regen_data_dir, exist_ok=True)

sensor_data = []

@app.route('/store-sensor-data', methods=['POST','GET'])
def store_sensor_data():

    global sensor_data
    
    if request.method == 'POST':
        number = request.data.decode()
        sensor_data = request.data.decode()
        epoch_time = int(time.time() * 1000)  # milliseconds since epoch
        current_time = datetime.now()
        filename = f"{sensor_data_dir}/{current_time.strftime('%Y-%m-%d')}.txt"  # Changed to daily files
    
        with open(filename, 'a') as file:
            file.write(f"{epoch_time},{number}\n")

        
        
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

@app.route('/store-water-level', methods=['POST'])
def store_water_level():
    level = request.data.decode()
    epoch_time = int(time.time() * 1000)  # milliseconds since epoch
    current_time = datetime.now()
    filename = f"{water_level_data_dir}/{current_time.strftime('%Y-%m-%d')}.txt"  # Changed to daily files
    
    with open(filename, 'a') as file:
        file.write(f"{epoch_time},{level}\n")
    
    # Check if the water level is above a certain threshold
    if int(level) > 0.732:
        # Send a message to the service worker to show a notification
        message = {
            "title": "Water Level Alert",
            "body": "The water level is approaching overflow."
        }
        # You need to implement the logic to send this message to the service worker
        
    return "Water level data stored successfully", 200

@app.route('/store-regen-signal', methods=['POST'])
# @app.route('/store-regen-signal', methods=['GET'])
def store_regen_signal():
  #   if request.method == 'POST':
    signal = request.data.decode()
    epoch_time = int(time.time() * 1000)  # milliseconds since epoch
    current_time = datetime.now()
    filename = f"{regen_data_dir}/{current_time.strftime('%Y-%m-%d')}.txt"  # Changed to daily files
    # elif request.method == 'GET':
      #   return jsonify(sensor_data)
    
    with open(filename, 'a') as file:
        file.write(f"{epoch_time},{signal}\n")
    
    return "Regeneration signal data stored successfully", 200

@app.route('/set-tank-size', methods=['POST'])
def set_tank_size():
    tank_size = request.data.decode()
    with open(tank_size_file, 'w') as file:
        file.write(tank_size)
    return "Tank size set successfully", 200

@app.route('/record-salt-refill', methods=['POST'])
def record_salt_refill():
    refill_date = datetime.now().strftime('%Y-%m-%d')
    with open(salt_refill_file, 'a') as file:
        file.write(f"{refill_date}\n")
    return "Salt refill recorded", 200

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
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(debug=True)
