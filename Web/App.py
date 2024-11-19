from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Existing variables
current_temperature = 58
current_humidity = 65
running_time = 125

@app.route('/')
def display_temperature():
    return render_template('index.html')

@app.route('/data')
def get_data():
    return jsonify({
        "temperature": current_temperature,
        "humidity": current_humidity,
        "running_time": running_time
    })

@app.route('/button-press', methods=['POST'])
def handle_button_press():
    data = request.get_json()
    action = data.get('action')
    print(f"Button pressed: {action}")
    return jsonify({"status": "success", "action_received": action})

if __name__ == '__main__':
    app.run(debug=True)