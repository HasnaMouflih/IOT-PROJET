// PROJECT LINK IN WOKWI: https://wokwi.com/projects/444282871410335745



// =============================================
// SENSOR MANAGER - INIT
// =============================================
#include <DHT.h>

// Pin definitions
#define SOIL_PIN 36
#define DHT_PIN 4
#define LIGHT_PIN 34


// =============================================
// ACTUATOR MANAGER - INIT
// =============================================
#include <ESP32Servo.h>

// Pin definitions
#define PUMP_PIN 25
#define RED_LED_PIN 26
#define GREEN_LED_PIN 27
#define BLUE_LED_PIN 23
#define FAN_PIN 12

// LED Color enum
enum LEDColor {
    RED,
    GREEN,
    BLUE,
    YELLOW,   // RED + GREEN
    PURPLE,   // RED + BLUE
    OFF
};




// =============================================
// DEVICECONTROLLER MANAGER - INIT
// =============================================
enum CommandType {
    WATER_NOW, SET_LED_COLOR, SET_FAN_SPEED
};

struct SensorData {
    String deviceId;
    float soilMoisture;
    float temperature;
    float lightLevel;
    float humidity;
    unsigned long timestamp;
    
    String toJSON() {
        String json = "{";
        json += "\"deviceId\":\"" + deviceId + "\",";
        json += "\"soilMoisture\":" + String(soilMoisture, 1) + ",";
        json += "\"temperature\":" + String(temperature, 1) + ",";
        json += "\"lightLevel\":" + String(lightLevel, 1) + ",";
        json += "\"humidity\":" + String(humidity, 1) + ",";
        json += "\"timestamp\":" + String(timestamp);
        json += "}";
        return json;
    }
};

struct Command {
    CommandType type;
    int duration;
    LEDColor color;
    int speed;
};



// =============================================
// SENSOR MANAGER CLASS
// =============================================
class SensorManager {
  private:
    int soilSensorPin;
    int tempSensorPin;
    int lightSensorPin;
    int humiditySensorPin;  // Same as tempSensorPin (DHT22 does both)
    DHT* dht;

  public:
    // Constructor
    SensorManager(int soilPin, int dhtPin, int lightPin) {
        soilSensorPin = soilPin;
        tempSensorPin = dhtPin;
        humiditySensorPin = dhtPin;  // DHT22 handles both
        lightSensorPin = lightPin;
        dht = new DHT(dhtPin, DHT22);
    }
    
    // Initialize sensors
    void begin() {
        dht->begin();
    }
    
    // Read soil moisture (0-100%)
    float readSoilMoisture() {
        int sum = 0;
        // Take 10 readings and average them
        for(int i = 0; i < 10; i++) {
            sum += analogRead(soilSensorPin);
            delay(10);
        }
        int raw = sum / 10;
        return map(raw, 0, 4095, 0, 100);
    }
    
    // Read temperature (Celsius)
    float readTemperature() {
        float temp = dht->readTemperature();
        if (isnan(temp)) return 0.0;
        return temp;
    }
    
    // Read light intensity (0-100%)
    float readLightIntensity() {
        int raw = analogRead(lightSensorPin);
        return map(raw, 0, 4095, 0, 100);
    }
    
    // Read humidity (0-100%)
    float readHumidity() {
        float hum = dht->readHumidity();
        if (isnan(hum)) return 0.0;
        return hum;
    }
    
    // Calibrate sensors (placeholder for now)
    void calibrateSensors() {
        Serial.println("[SensorManager] Calibrating...");
        delay(2000);
        Serial.println("[SensorManager] Calibration complete");
    }
};



// =============================================
// ACTUATOR MANAGER CLASS
// =============================================
class ActuatorManager {
  private:
      int pumpRelayPin;
      int redLedPin;
      int greenLedPin;
      int blueLedPin;
      int fanPin;
      LEDColor currentColor;
      bool isPumpRunning;
      Servo fanServo;

  public:
    // Constructor
    ActuatorManager(int pumpPin, int redPin, int greenPin, int bluePin, int servoPin) {
        pumpRelayPin = pumpPin;
        redLedPin = redPin;
        greenLedPin = greenPin;
        blueLedPin = bluePin;
        fanPin = servoPin;
        currentColor = OFF;
        isPumpRunning = false;
    }
    
    // Initialize actuators
    void begin() {
        pinMode(pumpRelayPin, OUTPUT);
        pinMode(redLedPin, OUTPUT);
        pinMode(greenLedPin, OUTPUT);
        pinMode(blueLedPin, OUTPUT);
        
        digitalWrite(pumpRelayPin, LOW);
        digitalWrite(redLedPin, LOW);
        digitalWrite(greenLedPin, LOW);
        digitalWrite(blueLedPin, LOW);
        
        fanServo.attach(fanPin);
        fanServo.write(0);
        
        Serial.println("[ActuatorManager] Initialized");
    }
    
    // Turn pump ON for duration (milliseconds)
    void pumpOn(int duration) {
        Serial.print("[ActuatorManager] Pump ON for ");
        Serial.print(duration);
        Serial.println("ms");
        
        digitalWrite(pumpRelayPin, HIGH);
        isPumpRunning = true;
        delay(duration);
        pumpOff();
    }
    
    // Turn pump OFF
    void pumpOff() {
        Serial.println("[ActuatorManager] Pump OFF");
        digitalWrite(pumpRelayPin, LOW);
        isPumpRunning = false;
    }
    
    // Set LED color
    void setLEDColor(LEDColor color) {
        currentColor = color;
        
        // Turn all off first
        digitalWrite(redLedPin, LOW);
        digitalWrite(greenLedPin, LOW);
        digitalWrite(blueLedPin, LOW);
        
        // Set new color
        switch(color) {
            case RED:
                digitalWrite(redLedPin, HIGH);
                Serial.println("[ActuatorManager] LED: RED");
                break;
            case GREEN:
                digitalWrite(greenLedPin, HIGH);
                Serial.println("[ActuatorManager] LED: GREEN");
                break;
            case BLUE:
                digitalWrite(blueLedPin, HIGH);
                Serial.println("[ActuatorManager] LED: BLUE");
                break;
            case YELLOW:
                digitalWrite(redLedPin, HIGH);
                digitalWrite(greenLedPin, HIGH);
                Serial.println("[ActuatorManager] LED: YELLOW");
                break;
            case PURPLE:
                digitalWrite(redLedPin, HIGH);
                digitalWrite(blueLedPin, HIGH);
                Serial.println("[ActuatorManager] LED: PURPLE");
                break;
            case OFF:
                Serial.println("[ActuatorManager] LED: OFF");
                break;
        }
    }
    
    // Set fan speed (0-180 degrees for servo)
    void setFanSpeed(int speed) {
        if (speed < 0) speed = 0;
        if (speed > 180) speed = 180;
        
        fanServo.write(speed);
        Serial.print("[ActuatorManager] Fan: ");
        Serial.print(speed);
        Serial.println("°");
    }
    
    // Get pump status
    bool getPumpStatus() {
        return isPumpRunning;
    }
};


// =============================================
// DEVICE CONTROLLER
// =============================================
class DeviceController {
  private:
      SensorManager* sensorManager;
      ActuatorManager* actuatorManager;
      String deviceId;
      unsigned long lastReadingTime;

  public:
      DeviceController(String id) {
          deviceId = id;
          lastReadingTime = 0;
          sensorManager = new SensorManager(SOIL_PIN, DHT_PIN, LIGHT_PIN);
          actuatorManager = new ActuatorManager(PUMP_PIN, RED_LED_PIN, GREEN_LED_PIN, BLUE_LED_PIN, FAN_PIN);
      }
      
      // Setup device
      void setupDevice() {
          Serial.println("\n========================================");
          Serial.println("EMOTIONAL PLANT - LAYER 1");
          Serial.println("========================================");
          Serial.print("Device ID: ");
          Serial.println(deviceId);
          Serial.println("========================================\n");
          
          sensorManager->begin();
          actuatorManager->begin();
          sensorManager->calibrateSensors();
          
          Serial.println("Device ready!\n");
      }
      
      // Collect sensor data and return JSON
      String collectSensorData() {
          SensorData data;
          data.deviceId = deviceId;
          data.soilMoisture = sensorManager->readSoilMoisture();
          data.temperature = sensorManager->readTemperature();
          data.lightLevel = sensorManager->readLightIntensity();
          data.humidity = sensorManager->readHumidity();
          data.timestamp = millis();
          
          return data.toJSON();
      }
      
      // Execute a command
      void executeCommand(Command cmd) {
          Serial.println("\n[DeviceController] Executing command...");
          
          switch(cmd.type) {
              case WATER_NOW:
                  actuatorManager->pumpOn(cmd.duration);
                  break;
              case SET_LED_COLOR:
                  actuatorManager->setLEDColor(cmd.color);
                  break;
              case SET_FAN_SPEED:
                  actuatorManager->setFanSpeed(cmd.speed);
                  break;
          }
      }
      
      // Parse command string (format: "TYPE:VALUE")
      Command parseCommandString(String commandStr) {
          Command cmd;

          // Initialize all fields to default values
          cmd.duration = 0;
          cmd.color = OFF;
          cmd.speed = 0;


          commandStr.trim();
          commandStr.toUpperCase();
          
          if (commandStr.startsWith("WATER:")) {
              cmd.type = WATER_NOW;
              cmd.duration = commandStr.substring(6).toInt();
          }
          else if (commandStr.startsWith("LED:")) {
              cmd.type = SET_LED_COLOR;
              String colorStr = commandStr.substring(4);
              if (colorStr == "RED") cmd.color = RED;
              else if (colorStr == "GREEN") cmd.color = GREEN;
              else if (colorStr == "BLUE") cmd.color = BLUE;
              else if (colorStr == "YELLOW") cmd.color = YELLOW;
              else if (colorStr == "PURPLE") cmd.color = PURPLE;
              else cmd.color = OFF;
          }
          else if (commandStr.startsWith("FAN:")) {
              cmd.type = SET_FAN_SPEED;
              cmd.speed = commandStr.substring(4).toInt();
          }
          
          return cmd;
      }
      
      // Main loop
       void loop(){

       }

    // TEST
    /*
    void loop() {
        static int testPhase = 0;
        static unsigned long lastTestTime = 0;
        unsigned long currentTime = millis();
        
        // Auto test sequence every 3 seconds
        if (currentTime - lastTestTime >= 3000) {
            lastTestTime = currentTime;
            
            Serial.println("\n========================================");
            Serial.print("TEST PHASE ");
            Serial.println(testPhase);
            Serial.println("========================================");
            
            switch(testPhase) {
                case 0:
                    Serial.println("Testing collectSensorData()...");
                    Serial.println(collectSensorData());
                    break;
                    
                case 1:
                    Serial.println("Testing WATER command (2 sec)...");
                    executeCommand(parseCommandString("WATER:2000"));
                    break;
                    
                case 2:
                    Serial.println("Testing LED:RED...");
                    executeCommand(parseCommandString("LED:RED"));
                    delay(1000);
                    Serial.println(collectSensorData());
                    break;
                    
                case 3:
                    Serial.println("Testing LED:YELLOW...");
                    executeCommand(parseCommandString("LED:YELLOW"));
                    break;
                    
                case 4:
                    Serial.println("Testing FAN:90...");
                    executeCommand(parseCommandString("FAN:90"));
                    break;
                    
                case 5:
                    Serial.println("Testing LED:BLUE + sensor data...");
                    executeCommand(parseCommandString("LED:BLUE"));
                    Serial.println(collectSensorData());
                    break;
                    
                case 6:
                    Serial.println("Testing FAN:180...");
                    executeCommand(parseCommandString("FAN:180"));
                    break;
                    
                case 7:
                    Serial.println("Testing LED:PURPLE...");
                    executeCommand(parseCommandString("LED:PURPLE"));
                    break;
                    
                case 8:
                    Serial.println("Testing invalid command...");
                    executeCommand(parseCommandString("INVALID:123"));
                    break;
                    
                case 9:
                    Serial.println("Testing LED:OFF + FAN:0...");
                    executeCommand(parseCommandString("LED:OFF"));
                    executeCommand(parseCommandString("FAN:0"));
                    Serial.println(collectSensorData());
                    break;
                    
                case 10:
                    Serial.println("Testing edge cases...");
                    executeCommand(parseCommandString("FAN:200"));  // Over limit
                    delay(500);
                    executeCommand(parseCommandString("FAN:-10"));  // Negative
                    break;
                    
                case 11:
                    Serial.println("\n*** FINAL SENSOR DATA ***");
                    Serial.println(collectSensorData());
                    Serial.println("\n*** ALL TESTS COMPLETE ***");
                    Serial.println("*** RESTARTING IN 5 SECONDS ***\n");
                    delay(5000);
                    testPhase = -1;  // Will become 0 on next increment
                    break;
            }
            
            testPhase++;
        }
        
        // Manual command input still works
        if (Serial.available() > 0) {
            String input = Serial.readStringUntil('\n');
            Serial.print("\n>>> Manual Command: ");
            Serial.println(input);
            Command cmd = parseCommandString(input);
            executeCommand(cmd);
            Serial.println(collectSensorData());
        }
    }

    */
};





// =============================================
// LAYER 2 CLASSES...
// =============================================
// write classes and their funcs as above





// =============================================
// TESTING MODULS
// =============================================

/*
SensorManager* sensors;
ActuatorManager* actuators;
*/

DeviceController* device;

void setup() {
    Serial.begin(115200);
    delay(1000);
    

  /*
    Serial.println("\n=== SENSOR MANAGER TEST ===\n");
    // Create sensor manager
    sensors = new SensorManager(SOIL_PIN, DHT_PIN, LIGHT_PIN);
    sensors->begin();
    sensors->calibrateSensors();



    Serial.println("\n=== ACTUATOR MANAGER TEST ===\n");
    // Create actuator manager
    actuators = new ActuatorManager(PUMP_PIN, RED_LED_PIN, GREEN_LED_PIN, BLUE_LED_PIN, FAN_PIN);
    actuators->begin();
  */

    device = new DeviceController("PLANT-001");
    device->setupDevice();

  /* 
    Serial.println("Commands:");
    Serial.println("  WATER:3000    - Water for 3 seconds");
    Serial.println("  LED:RED       - Set LED color");
    Serial.println("  FAN:90        - Set fan angle\n");
  */





    // =============================================
    // LAYER 2 SETUP...
    // =============================================
    // network = new NetworkManager("SSID", "pass", "broker", 1883);
    // network->connectWiFi();
    // network->connectMQTT();
    // 
    // publisher = new DataPublisher("plant/PLANT-001/telemetry");
    // 
    // subscriber = new CommandSubscriber("plant/PLANT-001/commands");
    // subscriber->setCallback(handleCommand);
    // subscriber->subscribeToCommands();

}

void loop() {
  /*
    Serial.println("--- Reading Sensors ---");
    
    Serial.print("Soil: ");
    Serial.print(sensors->readSoilMoisture());
    Serial.println("%");
    
    Serial.print("Temperature: ");
    Serial.print(sensors->readTemperature());
    Serial.println("°C");
    
    Serial.print("Light: ");
    Serial.print(sensors->readLightIntensity());
    Serial.println("%");
    
    Serial.print("Humidity: ");
    Serial.print(sensors->readHumidity());
    Serial.println("%");
    
    Serial.println();
    delay(2000);
  */


  /*
    Serial.println("\n--- Testing Actuators ---");
    
    // Test pump
    actuators->pumpOn(2000);  // 2 seconds
    delay(500);
    
    // Test LEDs
    actuators->setLEDColor(RED);
    delay(1000);
    actuators->setLEDColor(GREEN);
    delay(1000);
    actuators->setLEDColor(BLUE);
    delay(1000);
    actuators->setLEDColor(YELLOW);
    delay(1000);
    actuators->setLEDColor(PURPLE);
    delay(1000);
    actuators->setLEDColor(OFF);
    delay(1000);
    
    // Test fan
    actuators->setFanSpeed(0);
    delay(500);
    actuators->setFanSpeed(90);
    delay(1000);
    actuators->setFanSpeed(180);
    delay(1000);
    actuators->setFanSpeed(0);
    
    // Check pump status
    Serial.print("Pump running? ");
    Serial.println(actuators->getPumpStatus() ? "YES" : "NO");
    
    delay(2000);
  */

  device->loop();



    // =============================================
    // LAYER 2 LOOP...
    // =============================================
    // String json = device->collectSensorData();
    // publisher->publishTelemetry(json);
    // network->checkConnection();
}