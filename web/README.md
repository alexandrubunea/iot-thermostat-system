# Flask Server for ESP32 Thermostat

## Overview

This Python Flask server acts as an interface to control a thermostat running on an ESP32 device. It provides endpoints for fetching sensor data (temperature and humidity) and controlling the thermostat's target temperature and running time.

## Features

- Display current temperature and humidity.
- Adjust the target temperature of the thermostat.
- Modify the running time of the thermostat.
- Fetch real-time data from the ESP32 device periodically.

## Prerequisites

- Python 3.x
- Flask

## Installation

1. Clone the repository.
2. Navigate to the project directory.
3. Ensure the ESP32 device is running and accessible via the specified API endpoint (`http://192.168.50.100`).
4. Start the server.

## Usage

### Starting the Server

Run the following command to start the Flask server:

```bash
python app.py
```

The server will be available at `http://localhost:5000` by default.

### Endpoints

#### 1. `GET /`

- **Description**: Renders the main page displaying the current temperature.

#### 2. `GET /data`

- **Description**: Fetches the current temperature, humidity, target temperature, and running time from the ESP32 device.
- **Response**:
  ```json
  {
    "currentTemperature": float,
    "currentHumidity": float,
    "targetTemperature": float,
    "runningTime": float
  }
  ```

#### 3. `POST /button-press`

- **Description**: Handles button press actions to modify the thermostat's settings.
- **Request Body**:
  ```json
  {
    "action": "increase-target-temp" | "decrease-target-temp" | "increase-running-time" | "decrease-running-time"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success"
  }
  ```

## ESP32 Class

The `ESP32` class is responsible for communicating with the ESP32 device and updating its status periodically.

### Initialization

```python
esp32_device = ESP32(esp32_api='http://192.168.50.100', update_interval=0.25)
```

### Methods

- `get_current_temperature()`: Returns the current temperature.
- `get_current_humidity()`: Returns the current humidity.
- `get_current_running_time()`: Returns the current running time.
- `get_current_target_temperature()`: Returns the current target temperature.
- `increase_target_temperature()`: Increases the target temperature.
- `decrease_target_temperature()`: Decreases the target temperature.
- `increase_running_time()`: Increases the running time.
- `decrease_running_time()`: Decreases the running time.
- `kill()`: Stops the periodic update thread.

### Periodic Updates

The class periodically fetches data from the ESP32 device every `update_interval` seconds. This ensures the server has up-to-date information from the device.

## Signal Handling

The server listens for SIGINT and SIGTERM signals to ensure graceful shutdown by calling `esp32_device.kill()`.

## Template and Static Files

- Templates are stored in the `templates` folder.
- Static files (e.g., CSS, JS) are stored in the `static` folder.

## License

This project is licensed under the GNU GPL v3.0
