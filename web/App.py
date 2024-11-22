from flask import Flask, render_template, jsonify, request
from services.ESP32 import ESP32
import signal
import sys

app = Flask(__name__, template_folder='templates', static_folder='static')

# Instantiate the ESP32 class
esp32_device = ESP32(esp32_api='http://192.168.50.100', update_interval=0.25)

@app.route('/')
def display_temperature():
    return render_template('index.html')

@app.route('/data')
def get_data():
    return jsonify({
        'currentTemperature': esp32_device.get_current_temperature(),
        'currentHumidity': esp32_device.get_current_humidity(),
        'targetTemperature': esp32_device.get_current_target_temperature(),
        'runningTime': esp32_device.get_current_running_time()
    })

@app.route('/button-press', methods=['POST'])
def handle_button_press():
    data = request.get_json()
    action = data.get('action')

    match action:
        case 'increase-target-temp':
            esp32_device.increase_target_temperature()
        case 'decrease-target-temp':
            esp32_device.decrease_target_temperature()
        case 'increase-running-time':
            esp32_device.increase_running_time()
        case 'decrease-running-time':
            esp32_device.decrease_running_time()

    return jsonify({'status': 'success'})


def signal_handler(sig, frame):
    esp32_device.kill()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    app.run(debug=True)