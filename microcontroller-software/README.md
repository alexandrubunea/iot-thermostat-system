# Microcontroller Thermostat

A smart thermostat system built with ESP32 that provides both physical and web-based control interfaces. The system monitors temperature and humidity while allowing users to set target temperatures and running times.

## Features

- Real-time temperature and humidity monitoring using DHT11 sensor
- OLED display showing current status and settings
- Physical control interface with 4 buttons
- Web API for remote control and monitoring
- RGB LED status indicator
- Configurable running time with auto-shutdown
- Buzzer feedback for physical interactions

## Hardware Requirements

- ESP32 microcontroller
- DHT11 temperature and humidity sensor
- SSD1306 OLED display (128x64)
- 4 push buttons
- RGB LED
- Buzzer
- Connecting wires

## Pin Configuration

| Component          | Pin Number |
|-------------------|------------|
| DHT11 Sensor      | 5         |
| Temperature Up    | 26        |
| Temperature Down  | 27        |
| Time Up          | 14        |
| Time Down        | 12        |
| Buzzer           | 2         |
| RGB LED (Green)   | 33        |
| RGB LED (Red)     | 32        |
| RGB LED (Blue)    | 25        |

## Network Configuration

The device connects to WiFi with these default credentials:
- SSID: "Pi-Hotspot"
- Password: "admin2raspi"

## Web API Endpoints

### GET `/api/fetch_data`
Returns current thermostat status including:
- Current temperature
- Current humidity
- Target temperature
- Running time

### POST Endpoints
- `/api/increase-target-temp`: Increase target temperature
- `/api/decrease-target-temp`: Decrease target temperature
- `/api/increase-running-time`: Increase running time
- `/api/decrease-running-time`: Decrease running time

All POST endpoints return a JSON response with success status.

## Display Information

The OLED display shows:
- Current temperature (°C)
- Current humidity (%)
- Running status:
  - Off
  - Running time in minutes
  - "Running indefinitely" for continuous operation
- Target temperature (when running)

## Operating Ranges

- Temperature Setting: 15°C - 35°C
- Running Time: 0-195 minutes or indefinite (200)
- Time Increment: 15-minute steps

## LED Color Codes

- Red: Thermostat off
- Green: Thermostat running
- Red-Green-Blue pulse: Trying to connect to the Wi-Fi
- Yellow-Pink pulse: Trying to initialize the OLED display
- Blue pulse: Remote access indicator

## Dependencies

- DHT sensor library
- WiFi library
- ESPAsyncWebServer
- ArduinoJson
- Wire
- Adafruit_GFX
- Adafruit_SSD1306

## Known Issues

- DHT11.begin() generates a PSRAM ERROR but does not affect functionality

## Building and Uploading

1. Install all required libraries through the Arduino Library Manager
2. Configure your WiFi credentials in the code
3. Select ESP32 as your board in the Arduino IDE
4. Upload the code to your ESP32

## Usage

### Physical Control
- Temperature Up/Down buttons: Adjust target temperature
- Time Up/Down buttons: Adjust running time
  - Press Time Up at 0 to start with 15 minutes
  - Press Time Down at 0 to run indefinitely
  - Press Time Up when indefinite to stop
  - Each press changes time by 15 minutes

### Remote Control
Access the web API endpoints using HTTP requests to control the thermostat remotely. The RGB LED will pulse blue to indicate remote access.
