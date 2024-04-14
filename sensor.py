from flask import Flask, request, render_template_string, send_file, jsonify
import os
import time
from datetime import datetime
import logging

app = Flask(__name__)
sensor_data_dir = "sensor-data"
water_det_data_dir = "water-det-data"
regen_data_dir = "regen-data"
tank_size_file = "tank_size.txt"
salt_refill_file = "salt_refill.txt" 

# Ensure the data directories exist
os.makedirs(sensor_data_dir, exist_ok=True)
os.makedirs(water_det_data_dir, exist_ok=True)
os.makedirs(regen_data_dir, exist_ok=True)

sensor_data = []
water_det_data = []
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
        timestamp = current_time.strftime('%Y-%m-%d')  # Date stamp in format YYYY-MM-DD
        filename = f"{sensor_data_dir}/{current_time.strftime('%Y-%m-%d')}.txt"  # Changed to daily files
    
        with open(filename, 'a') as file:
            file.write(f"{epoch_time},{number}\n")

        #sensor_data.append({'timestamp': timestamp, 'value': number})  # Append timestamp along with value
        
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

@app.route('/delete-water-det-data', methods=['POST'])
def delete_water_det_data():
    global water_det_data
    water_det_data = []
    for filename in os.listdir(water_det_data_dir):
        file_path = os.path.join(water_det_data_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return "All water detection data deleted", 200

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

        water_det_data.append(current_time.strftime('%Y-%m-%d'))
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

        regen_data.append(current_time.strftime('%Y-%m-%d'))
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

def safe_key_extractor(data):
    try:
        # Attempt to return the first element for sorting
        return data[0]
    except (IndexError, TypeError, KeyError) as e:
        # Log the error and the problematic data
        print(f"Error accessing the first element for sorting: {e}, Data: {data}")
        # Return 0 as a fallback sort key
        return 0

@app.route('/')
def index():
    global sensor_data, water_det_data, regen_data

    # sensor_data_dir = "path/to/sensor_data"
    # water_det_data_dir = "path/to/water_det_data"

    # Populate sensor_data, water_det_data, and regen_data
    sensor_data = []
    water_det_data = []
    regen_data = []

    # Read sensor data files and accumulate data
    for filename in sorted(os.listdir(sensor_data_dir)):
        with open(f"{sensor_data_dir}/{filename}", 'r') as file:
            for line in file:
                epoch, value = line.strip().split(',')
                sensor_data.append([int(epoch), int(value)])
    
    # Read water detection data files and accumulate data
    for filename in sorted(os.listdir(water_det_data_dir)):
        with open(f"{water_det_data_dir}/{filename}", 'r') as file:
            for line in file:
                epoch = line.strip()
                water_det_data.append([int(epoch), 1])

        # Read water detection data files and accumulate data
    for filename in sorted(os.listdir(regen_data_dir)):
        with open(f"{regen_data_dir}/{filename}", 'r') as file:
            for line in file:
                epoch = line.strip()
                regen_data.append([int(epoch), 1])

    # You might want to similarly handle regeneration data...

    # Generate JavaScript-compatible data strings for Google Charts
    sensor_data_js = [[epoch, value] for epoch, value in sensor_data]
    water_det_data_js = [[epoch, value] for epoch, value in water_det_data]
    regen_data_js = [[epoch, value] for epoch, value in regen_data]

    table_rows = "".join(
    f"<tr><td>{datetime.fromtimestamp(epoch/1000).strftime('%Y-%m-%d %H:%M:%S')}</td><td>{sensor_value}</td><td>{water_det}</td><td>{regen_signal}</td></tr>"
    for (epoch, sensor_value), (_, water_det), (_, regen_signal) in zip(sensor_data[-10:], water_det_data[-10:], regen_data[-10:])
    )

    return render_template_string(HTML_CONTENT, sensor_data_js=sensor_data_js,table_rows = table_rows, water_det_data_js=water_det_data_js, regen_data_js=regen_data_js)

HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Sensor Data Dashboard</title>
    <!-- Load Google Charts -->
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
      google.charts.load('current', {'packages':['corechart']});
      google.charts.setOnLoadCallback(drawChart);

      function drawChart(ChartType) {
        ChartType = ChartType || "Sensor Data"
        var data = new google.visualization.DataTable();
        data.addColumn('datetime', 'Time');
        data.addColumn('number', 'Value');

        var sensorData = {{ sensor_data_js }};
        var waterDetData = {{ water_det_data_js }};
        var regenData = {{ regen_data_js }};

        var chartData = {
          'Sensor Data': sensorData,
          'Water Detection': waterDetData,
          'Regeneration Signal': regenData
        }[ChartType];

        chartData.forEach(function(row) {
          data.addRow([new Date(row[0]), row[1]]);
        });

        var options = {
          title: 'Sensor Data Over Time',
          curveType: 'function',
          legend: { position: 'bottom' },
          hAxis: {
            format: 'dd MMM yyyy HH:mm:ss'
          },
          height: 350
        };

        var chart = new google.visualization.LineChart(document.getElementById('chart-container'));
        chart.draw(data, options);
      }

      function changeChart() {
        var chartType = document.getElementById("chart-selector").value;
        drawChart(chartType);
      }

      function deleteSensorData() {
        fetch('/delete-sensor-data', { method: 'POST' })
        .then(response => response.text())
        .then(data => {
            alert(data);
            location.reload();
        });
      }

      function deleteWaterDetData() {
        fetch('/delete-water-det-data', { method: 'POST' })
        .then(response => response.text())
        .then(data => {
            alert(data);
            location.reload();
        });
      }

      function deleteRegenData() {
        fetch('/delete-regen-data', { method: 'POST' })
        .then(response => response.text())
        .then(data => {
            alert(data);
            location.reload();
        });
      }

      function setTankSize() {
        var tankSize = document.getElementById("tank-size-input").value;
        fetch('/set-tank-size', {
            method: 'POST',
            headers: {'Content-Type': 'text/plain'},
            body: tankSize
        })
        .then(response => response.text())
        .then(data => {
            alert(data);
        });
      }

      function recordSaltRefill() {
        fetch('/record-salt-refill', { method: 'POST' })
        .then(response => response.text())
        .then(data => {
            alert(data);
        });
      }
    </script>
</head>
<body>
    <h1>Sensor Data Dashboard</h1>
    <select id="chart-selector" onchange="changeChart()">
        <option value="Sensor Data">Sensor Data</option>
        <option value="Water Detection">Water Detection</option>
        <option value="Regeneration Signal">Regeneration Signal</option>
    </select>
    <div id="chart-container" style="height: 350px;"></div>

    <h2>Latest Sensor Data</h2>
    <button onclick="deleteSensorData()">Delete All Sensor Data</button>
    <button onclick="deleteWaterDetData()">Delete All Water Detection Data</button>
    <button onclick="deleteRegenData()">Delete All Regeneration Data</button>

    <h2>Set Tank Size</h2>
    <input type="text" id="tank-size-input" placeholder="Enter Tank Size">
    <button onclick="setTankSize()">Set Tank Size</button>

    <table border="1">
        <tr>
            <th>Time</th>
            <th>Sensor Data</th>
            <th>Water Detection</th>
            <th>Regeneration Signal</th>
        </tr>
        {{table_rows}}
    </table>

</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)
