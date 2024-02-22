from flask import Flask, request, render_template_string
import os
import time
from datetime import datetime

app = Flask(__name__)
sensor_data_dir = "sensor-data"

# Ensure the sensor-data directory exists
os.makedirs(sensor_data_dir, exist_ok=True)

@app.route('/store-sensor-data', methods=['POST'])
def store_sensor_data():
    number = request.data.decode()
    epoch_time = int(time.time() * 1000)  # milliseconds since epoch
    current_time = datetime.now()
    filename = f"{sensor_data_dir}/{current_time.strftime('%Y-%m-%d-%H')}.txt"
    
    with open(filename, 'a') as file:
        file.write(f"{epoch_time},{number}\n")
    
    return "Data stored successfully", 200

@app.route('/delete-sensor-data', methods=['POST'])
def delete_sensor_data():
    for filename in os.listdir(sensor_data_dir):
        file_path = os.path.join(sensor_data_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return "All sensor data deleted", 200

@app.route('/')
def index():
    files = sorted(os.listdir(sensor_data_dir), reverse=True)[:10]  # Sort and get the latest 10 files
    series_data = []

    for filename in files:
        with open(f"{sensor_data_dir}/{filename}", 'r') as file:
            for line in file:
                epoch, value = line.strip().split(',')
                # Convert epoch to milliseconds since Unix epoch (for JavaScript)
                timestamp = int(epoch)
                series_data.append([timestamp, int(value)])
    
    # Correcting the format for JavaScript
    series_data_js = str(series_data).replace("'", "")

    # Serving an HTML page with the sensor data and an ApexChart
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sensor Data with addition</title>
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
    </script>
    </head>
    
    <body>
        <h1>Sensor Data Chart over time</h1>
        <div id="chart"></div>
        <script>
            var options = {{
                series: [{{
                    "name": 'Sensor Value',
                    "data": {series_data_js}
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

            var chart = new ApexCharts(document.querySelector("#chart"), options);
            chart.render();
        </script>

        <button onclick="deleteSensorData()">Delete All Sensor Data</button>
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(debug=True)
