import requests
from flask import Flask, render_template, jsonify, request

ESP32_IP_ADDRESS = 'http://192.168.1.140/api/'

app = Flask(__name__)

current_data = {
    'currentTemperature': None,
    'currentHumidity': None,
    'targetTemperature': None,
    'runningTime': None
}

def fetch_esp32_data():
    global current_data

    response = requests.get(
        f'{ESP32_IP_ADDRESS}fetch_data',
        headers={'Content-Type': 'application/json'}
    )
    data = response.json()

    current_data = {
        'temperature': data['currentTemperature'],
        'humidity': data['currentHumidity'],
        'target_temperature': data['targetTemperature'],
        'running_time': data['runningTime']
    }

@app.route('/')
def display_temperature():
    fetch_esp32_data()
    return render_template('index.html', **current_data)

@app.route('/data')
def get_data():
    return jsonify(current_data)

@app.route('/button-press', methods=['POST'])
def handle_button_press():
    data = request.get_json()
    action = data.get('action')
    response = requests.post(f'{ESP32_IP_ADDRESS}{action}')

    return response.text

if __name__ == '__main__':

    app.run(debug=True)
