#include <DHT.h>
#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ==== Pins ====
#define DHT11_SENSOR_PIN      5

#define BUTTON_TEMP_UP        26
#define BUTTON_TEMP_DOWN      27
#define BUTTON_TIME_UP        14
#define BUTTON_TIME_DOWN      12

#define BUZZER_PIN            2

#define RGB_LED_GREEN         33
#define RGB_LED_RED           32
#define RGB_LED_BLUE          25

// ==== Network Configuration ====
#define WIFI_SSID             "Pi-Hotspot"
#define WIFI_PASSWORD         "admin2raspi"

// ==== Display Configuration ====
#define SCREEN_WIDTH          128
#define SCREEN_HEIGHT         64
#define SCREEN_ADDRESS        0x3C
#define OLED_RESET            -1

// ==== Thermostat Configuration ====
#define RUNNING_INDEFINITELY  200

// ==== RGB Led Pulsing Configuration ====
#define SECONDARY_RED_PULSE   100
#define SECONDARY_GREEN_PULSE 50
#define SECONDARY_BLUE_PULSE  50

// ==== Components ====
DHT dht11(DHT11_SENSOR_PIN, DHT11); // DHT11 temperature & humidity sensor
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET); // I2C oled dispay

// ==== RGB Led Structure ====
struct RgbLed {
  uint8_t red, green, blue;

  uint8_t pulse_red, pulse_green, pulse_blue;
  uint8_t current_nop, required_nop; // NOP = Number of pulses
  uint8_t pulses_interval;
  unsigned long last_pulse;

  RgbLed() {
    red = green = blue = 0;

    resetPulse();
  }

  RgbLed(uint8_t r, uint8_t g, uint8_t b) {
    red = r;
    green = g;
    blue = b;

    resetPulse();

    setColor(red, green, blue);
  }

  void setColor(uint8_t r, uint8_t g, uint8_t b) {
    red = r;
    green = g;
    blue = b;

    analogWrite(RGB_LED_RED, red);
    analogWrite(RGB_LED_GREEN, green);
    analogWrite(RGB_LED_BLUE, blue);
  }

  void setColorTemporary(uint8_t r, uint8_t g, uint8_t b) {
    analogWrite(RGB_LED_RED, r);
    analogWrite(RGB_LED_GREEN, g);
    analogWrite(RGB_LED_BLUE, b);
  }

  void resetPulse() {
    pulse_red = pulse_green = pulse_blue = 0;
    current_nop = required_nop = 0;
    pulses_interval = 0;
    last_pulse = 0;
  }
  
  void pulseColor(uint8_t r, uint8_t g, uint8_t b, uint8_t times, uint8_t interval) {
    if(required_nop > 0) // Don't overlap pulses, one is enough to clarify that the thermostat is accessed remotely
      return;

    pulse_red = r;
    pulse_green = g;
    pulse_blue = b;

    pulses_interval = interval;

    last_pulse = millis();
    required_nop = times;
  }

  void updatePulseColor() {
    if(required_nop == 0)
      return;

    unsigned long current_millis = millis();

    if(current_millis - last_pulse < pulses_interval)
      return;

    if(current_nop == required_nop) {
      resetPulse();
      setColorTemporary(red, green, blue);

      return;
    }
    
    last_pulse = current_millis;

    if(current_nop % 2 == 0)
      setColorTemporary(pulse_red, pulse_green, pulse_blue);
    else
      setColorTemporary(SECONDARY_RED_PULSE, SECONDARY_GREEN_PULSE, SECONDARY_BLUE_PULSE);
    
    current_nop += 1;
  }
};
RgbLed RGBLed;

// ==== Thermostat Structure ====
struct ThermostatProgram {
  uint8_t targetTemperature = 15;
  volatile uint8_t runningTime = 0;

  void increaseTargetTemp() {
    if(targetTemperature <= 35)
      ++targetTemperature;
  }

  void decreaseTargetTemp() {
    if(targetTemperature >= 15)
      --targetTemperature;
  }

  void increaseRunningTime() {
    if(runningTime >= RUNNING_INDEFINITELY) {
      runningTime = 0;
      RGBLed.setColor(50, 0, 0);

      return;
    }
    
    if(runningTime == 0)
      RGBLed.setColor(0, 50, 0);
    
    runningTime += 15;
  }

  void decreaseRunningTime() {
    if(runningTime >= RUNNING_INDEFINITELY) {
      runningTime = 195;
      
      return;
    }

    if(runningTime == 0) {
      runningTime = RUNNING_INDEFINITELY;
      RGBLed.setColor(0, 50, 0);
      
      return;
    }
    
    runningTime -= 15;

    if(runningTime >= RUNNING_INDEFINITELY) // Check for underflow
      runningTime = 0;

    if(runningTime == 0)
      RGBLed.setColor(50, 0, 0);
  }
};

struct ThermostatStatus {
  float currentTemperature;
  float currentHumidity;

  void fetchTempHumidityData() {
    currentTemperature = dht11.readTemperature();
    currentHumidity = dht11.readHumidity();
  }
};


ThermostatProgram T_Program;
ThermostatStatus T_Status;

// ==== Buttons ====
uint8_t buttonsPins[] = {BUTTON_TEMP_UP, BUTTON_TEMP_DOWN, BUTTON_TIME_UP, BUTTON_TIME_DOWN};
#define NUMBER_OF_BUTTONS 4

void initButtons() {
  for(uint8_t i = 0; i < NUMBER_OF_BUTTONS; ++i)
    pinMode(buttonsPins[i], INPUT);
}

uint8_t getPressedButton() {
  for(uint8_t i = 0; i < NUMBER_OF_BUTTONS; ++i)
    if(digitalRead(buttonsPins[i]) == HIGH)
      return buttonsPins[i];
}

// ==== Thermostat Control ====
void phyiscalControl() {
  uint8_t button = getPressedButton();

  switch(button) {
    case BUTTON_TEMP_UP: {
      T_Program.increaseTargetTemp();
      playBuzzer();
      break;
    }
    case BUTTON_TEMP_DOWN: {
      T_Program.decreaseTargetTemp();
      playBuzzer();
      break;
    }
    case BUTTON_TIME_UP: {
      T_Program.increaseRunningTime();
      playBuzzer();
      break;
    }
    case BUTTON_TIME_DOWN: {
      T_Program.decreaseRunningTime();
      playBuzzer();
      break;
    }
  }
}

// ==== Buzzer ====
void initBuzzer() {
  pinMode(BUZZER_PIN, OUTPUT);
}
void playBuzzer() {
  tone(BUZZER_PIN, 440);
  delay(100);
  noTone(BUZZER_PIN);
}

// ==== Network Configuration ====
void connectToWifi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    RGBLed.setColor(255,0,0);
    delay(500);
    RGBLed.setColor(0,255,0);
    delay(500);
    RGBLed.setColor(0,0,255);
  }
}

// ==== Web Server ====
AsyncWebServer server(80);

void initAPIServer() {
  server.on("/api/fetch_data", HTTP_GET, [](AsyncWebServerRequest *request) {
    StaticJsonDocument<200> jsonDoc;
    
    jsonDoc["currentTemperature"] = T_Status.currentTemperature;
    jsonDoc["currentHumidity"] = T_Status.currentHumidity;
    jsonDoc["targetTemperature"] = T_Program.targetTemperature;
    jsonDoc["runningTime"] = T_Program.runningTime;

    String jsonResponse;
    serializeJson(jsonDoc, jsonResponse);

    request->send(200, "application/json", jsonResponse);
  });

  server.on("/api/increase-target-temp", HTTP_POST, [](AsyncWebServerRequest *request) {
    T_Program.increaseTargetTemp();
    RGBLed.pulseColor(0, 0, 100, 6, 500);
    request->send(200, "application/json", "{\"status\":\"success\"}");
  });

  server.on("/api/decrease-target-temp", HTTP_POST, [](AsyncWebServerRequest *request) {
    T_Program.decreaseTargetTemp();
    RGBLed.pulseColor(0, 0, 100, 6, 500);
    request->send(200, "application/json", "{\"status\":\"success\"}");
  });

  server.on("/api/increase-running-time", HTTP_POST, [](AsyncWebServerRequest *request) {
    T_Program.increaseRunningTime();
    RGBLed.pulseColor(0, 0, 100, 6, 500);
    request->send(200, "application/json", "{\"status\":\"success\"}");
  });

  server.on("/api/decrease-running-time", HTTP_POST, [](AsyncWebServerRequest *request) {
    T_Program.decreaseRunningTime();
    RGBLed.pulseColor(0, 0, 100, 6, 500);
    request->send(200, "application/json", "{\"status\":\"success\"}");
  });

  server.begin();
}

// ==== Display Functions ====
void initDisplay() {
  bool init_success = display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS);
  while (!init_success){
    RGBLed.setColor(255,255,0);
    delay(1000);
    RGBLed.setColor(255,0,255);
  }

  refreshDisplay();
}

void refreshDisplay() {
  display.clearDisplay();

  display.setTextColor(SSD1306_WHITE);
  
  display.setCursor(0, 0);
  display.setTextSize(2);
  String current_temp = String(T_Status.currentTemperature);
  current_temp.remove(current_temp.length() - 1);
  display.println(current_temp + " " + (char) 247 + "C");

  display.drawFastHLine(0, 20, SCREEN_WIDTH, SSD1306_WHITE);

  display.setCursor(0, 25);
  display.setTextSize(1);
  String current_humidity = String(T_Status.currentHumidity);
  current_humidity.remove(current_humidity.length() - 1);
  display.println(current_humidity + "% Humidity");
  
  String running_status = "Thermostat is off";
  bool thermostat_running = T_Program.runningTime > 0;

  if(thermostat_running)
    running_status = String(T_Program.runningTime) + " minutes";
  if(T_Program.runningTime >= RUNNING_INDEFINITELY)
    running_status = "Running indefinitely";
  display.println(running_status);

  if(thermostat_running)
    display.println("Target: " + String(T_Program.targetTemperature) + " " + (char) 247 + "C");

  display.display();
}

// ==== Thermostat Timer ====
hw_timer_t *timer = NULL;

void IRAM_ATTR onTimer() {
  // Updating thermostat timer
  if(T_Program.runningTime > 0 && T_Program.runningTime < RUNNING_INDEFINITELY) {
    T_Program.runningTime -= 1;

    if(T_Program.runningTime == 0)
      RGBLed.setColor(50, 0, 0);
  }
}

void initThermostatTimer() {
    timer = timerBegin(1000000);
    timerAttachInterrupt(timer, &onTimer);
    timerAlarm(timer, 60000000, true, 0);
}

// ==== RGB Led ====
void initRgbLedPins() {
  pinMode(RGB_LED_RED, OUTPUT);
  pinMode(RGB_LED_GREEN, OUTPUT);
  pinMode(RGB_LED_BLUE, OUTPUT);
}

// ==== Base ====
void setup() {
  dht11.begin(); // This generates a PSARM ERROR, but the program works great.
  initRgbLedPins();
  initBuzzer();
  initButtons();
  connectToWifi();
  initAPIServer();
  initDisplay();
  initThermostatTimer();
  
  T_Status.fetchTempHumidityData();
  RGBLed = RgbLed(50, 0, 0); // The initial color of the RGB led it's red
}

void loop() {
  phyiscalControl();

  T_Status.fetchTempHumidityData();
  refreshDisplay();
  RGBLed.updatePulseColor();

  delay(100);
}
