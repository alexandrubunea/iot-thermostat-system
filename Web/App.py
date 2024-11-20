import time
import requests
from flask import Flask, render_template, jsonify, request
import threading
from threading import Lock

ESP32_IP_ADDRESS = 'http://192.168.1.140/api/'

app = Flask(__name__)

current_data = {
    'currentTemperature': None,
    'currentHumidity': None,
    'targetTemperature': None,
    'runningTime': None
}

data_lock = Lock()

def fetch_esp32_data():
    global current_data
    try:
        response = requests.get(f'{ESP32_IP_ADDRESS}fetch_data', headers={'Content-Type': 'application/json'})
        response.raise_for_status()  # Raise an exception for 4xx/5xx responses
        data = response.json()

        with data_lock:
            current_data.update({
                'temperature': data['currentTemperature'],
                'humidity': data['currentHumidity'],
                'target_temperature': data['targetTemperature'],
                'running_time': data['runningTime']
            })

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from ESP32: {e}")
    except ValueError as e:
        print(f"Error parsing response JSON: {e}")

@app.route('/')
def display_temperature():
    with data_lock:
        data = current_data
    return render_template('index.html', **data)

@app.route('/data')
def get_data():
    with data_lock:
        data = current_data
    return jsonify(data)

@app.route('/button-press', methods=['POST'])
def handle_button_press():
    data = request.get_json()
    action = data.get('action')
    try:
        response = requests.post(f'{ESP32_IP_ADDRESS}{action}')
        response.raise_for_status()  # Check for errors
        return response.text
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Error sending action to ESP32: {e}"}), 500

def esp32_thread():
    while True:
        fetch_esp32_data()
        time.sleep(1)  # Fetch every second

if __name__ == '__main__':
    # Start a background thread to fetch ESP32 data periodically
    threading.Thread(target=esp32_thread).start()

    app.run(debug=True)
