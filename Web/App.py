from flask import Flask, render_template

app = Flask(__name__)


current_temperature = 58
current_humidity = 65

@app.route('/')
def display_temperature():
    return render_template('index.html', temperature=current_temperature, humidity=current_humidity)

if __name__ == '__main__':
    app.run(debug=True)