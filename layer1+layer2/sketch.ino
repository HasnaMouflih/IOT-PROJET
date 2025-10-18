// =============================================
// PROJECT LINK IN WOKWI: https://wokwi.com/projects/444282871410335745
// =============================================

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ESP32Servo.h>

// Pin definitions
#define SOIL_PIN 36
#define DHT_PIN 4
#define LIGHT_PIN 34
#define PUMP_PIN 25
#define RED_LED_PIN 26
#define GREEN_LED_PIN 27
#define BLUE_LED_PIN 23
#define FAN_PIN 12

// LED Color enum
enum LEDColor { RED, GREEN, BLUE, YELLOW, PURPLE, OFF };

// CommandType enum
enum CommandType { WATER_NOW, SET_LED_COLOR, SET_FAN_SPEED };

// =============================================
// SENSOR DATA STRUCT
// =============================================
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

// Command struct
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
    int soilSensorPin, tempSensorPin, lightSensorPin, humiditySensorPin;
    DHT* dht;

public:
    SensorManager(int soilPin, int dhtPin, int lightPin) {
        soilSensorPin = soilPin;
        tempSensorPin = dhtPin;
        humiditySensorPin = dhtPin;
        lightSensorPin = lightPin;
        dht = new DHT(dhtPin, DHT22);
    }

    void begin() { dht->begin(); }

    float readSoilMoisture() {
        int sum = 0;
        for (int i = 0; i < 10; i++) { sum += analogRead(soilSensorPin); delay(10); }
        return map(sum / 10, 0, 4095, 0, 100);
    }

    float readTemperature() {
        float temp = dht->readTemperature();
        return isnan(temp) ? 0.0 : temp;
    }

    float readLightIntensity() {
        return map(analogRead(lightSensorPin), 0, 4095, 0, 100);
    }

    float readHumidity() {
        float hum = dht->readHumidity();
        return isnan(hum) ? 0.0 : hum;
    }

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
    int pumpRelayPin, redLedPin, greenLedPin, blueLedPin, fanPin;
    LEDColor currentColor;
    bool isPumpRunning;
    Servo fanServo;

public:
    ActuatorManager(int pumpPin, int r, int g, int b, int f) {
        pumpRelayPin = pumpPin; redLedPin = r; greenLedPin = g; blueLedPin = b; fanPin = f;
        currentColor = OFF; isPumpRunning = false;
    }

    void begin() {
        pinMode(pumpRelayPin, OUTPUT); pinMode(redLedPin, OUTPUT);
        pinMode(greenLedPin, OUTPUT); pinMode(blueLedPin, OUTPUT);
        digitalWrite(pumpRelayPin, LOW); digitalWrite(redLedPin, LOW);
        digitalWrite(greenLedPin, LOW); digitalWrite(blueLedPin, LOW);
        fanServo.attach(fanPin); fanServo.write(0);
        Serial.println("[ActuatorManager] Initialized");
    }

    void pumpOn(int duration) {
        Serial.print("[ActuatorManager] Pump ON for "); Serial.print(duration); Serial.println("ms");
        digitalWrite(pumpRelayPin, HIGH); isPumpRunning = true;
        delay(duration); pumpOff();
    }

    void pumpOff() { digitalWrite(pumpRelayPin, LOW); isPumpRunning = false; }

    void setLEDColor(LEDColor color) {
        currentColor = color;
        digitalWrite(redLedPin, LOW); digitalWrite(greenLedPin, LOW); digitalWrite(blueLedPin, LOW);
        switch (color) {
            case RED: digitalWrite(redLedPin, HIGH); break;
            case GREEN: digitalWrite(greenLedPin, HIGH); break;
            case BLUE: digitalWrite(blueLedPin, HIGH); break;
            case YELLOW: digitalWrite(redLedPin, HIGH); digitalWrite(greenLedPin, HIGH); break;
            case PURPLE: digitalWrite(redLedPin, HIGH); digitalWrite(blueLedPin, HIGH); break;
            case OFF: break;
        }
        Serial.println("[ActuatorManager] LED set");
    }

    void setFanSpeed(int speed) {
        speed = constrain(speed, 0, 180);
        fanServo.write(speed);
        Serial.print("[ActuatorManager] Fan: "); Serial.print(speed); Serial.println("°");
    }

    bool getPumpStatus() { return isPumpRunning; }
};

// =============================================
// DEVICE CONTROLLER CLASS
// =============================================
class DeviceController {
private:
    SensorManager* sensorManager;
    ActuatorManager* actuatorManager;
    String deviceId;

public:
    DeviceController(String id) {
        deviceId = id;
        sensorManager = new SensorManager(SOIL_PIN, DHT_PIN, LIGHT_PIN);
        actuatorManager = new ActuatorManager(PUMP_PIN, RED_LED_PIN, GREEN_LED_PIN, BLUE_LED_PIN, FAN_PIN);
    }

    void setupDevice() {
        Serial.println("========================================");
        Serial.println("DEVICE INIT");
        Serial.println("Device ID: " + deviceId);
        sensorManager->begin(); actuatorManager->begin(); sensorManager->calibrateSensors();
        Serial.println("Device ready!\n");
    }

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

    Command parseCommandString(String cmdStr) {
        Command cmd; cmd.duration = 0; cmd.color = OFF; cmd.speed = 0;
        cmdStr.trim(); cmdStr.toUpperCase();
        if (cmdStr.startsWith("WATER:")) { cmd.type = WATER_NOW; cmd.duration = cmdStr.substring(6).toInt(); }
        else if (cmdStr.startsWith("LED:")) {
            cmd.type = SET_LED_COLOR;
            String c = cmdStr.substring(4);
            if (c=="RED") cmd.color=RED; else if(c=="GREEN") cmd.color=GREEN;
            else if(c=="BLUE") cmd.color=BLUE; else if(c=="YELLOW") cmd.color=YELLOW;
            else if(c=="PURPLE") cmd.color=PURPLE; else cmd.color=OFF;
        }
        else if (cmdStr.startsWith("FAN:")) { cmd.type = SET_FAN_SPEED; cmd.speed = cmdStr.substring(4).toInt(); }
        return cmd;
    }

    void executeCommand(Command cmd) {
        switch(cmd.type){
            case WATER_NOW: actuatorManager->pumpOn(cmd.duration); break;
            case SET_LED_COLOR: actuatorManager->setLEDColor(cmd.color); break;
            case SET_FAN_SPEED: actuatorManager->setFanSpeed(cmd.speed); break;
        }
    }

    void executeCommand(String cmdStr) {
        executeCommand(parseCommandString(cmdStr));
    }

    void loop() {
        // Place for future logic
    }
};

// =============================================
// NETWORK/MQTT MANAGER
// =============================================
class MyNetworkManager {
private:
    const char* ssid; const char* pass; const char* broker; int port;
    WiFiClient espClient; PubSubClient client;
public:
    MyNetworkManager(const char* s,const char* p,const char* b,int po)
        : ssid(s), pass(p), broker(b), port(po), client(espClient) {}
    void connectWiFi(){
        WiFi.begin(ssid,pass); Serial.print("Connecting to WiFi");
        int a=0; while(WiFi.status()!=WL_CONNECTED && a<20){ delay(500); Serial.print("."); a++; }
        if(WiFi.status()==WL_CONNECTED) Serial.println("\nWiFi Connected! IP: "+WiFi.localIP().toString());
        else Serial.println("\nWiFi connection failed!");
    }
    void connectMQTT(){
        client.setServer(broker,port); 
        String clientId="ESP32Plant-"+String(random(0xffff),HEX);
        if(client.connect(clientId.c_str())) Serial.println("MQTT Connected: "+clientId);
        else Serial.println("MQTT failed, rc="+String(client.state()));
    }
    void loop(){ client.loop(); }
    PubSubClient& getClient(){ return client; }
};

// Data Publisher
class DataPublisher {
private:
    MyNetworkManager* netMgr; const char* topic; unsigned long lastPub;
public:
    DataPublisher(MyNetworkManager* n,const char* t):netMgr(n),topic(t),lastPub(0){}
    void publish(String json){
        if(millis()-lastPub>3000){
            lastPub=millis();
            if(netMgr->getClient().publish(topic,json.c_str()))
                Serial.println(" "+json);
            else Serial.println("Publish failed");
        }
    }
};

// Command Subscriber
class CommandSubscriber {
private:
    MyNetworkManager* netMgr; const char* topic;
public:
    CommandSubscriber(MyNetworkManager* n,const char* t):netMgr(n),topic(t){}
    void subscribe(void (*callback)(char*,byte*,unsigned int)){
        netMgr->getClient().setCallback(callback);
        netMgr->getClient().subscribe(topic);
        Serial.println("Subscribed to "+String(topic));
    }
};

// =============================================
// GLOBAL INSTANCES
// =============================================
DeviceController* device;
MyNetworkManager* network;
DataPublisher* publisher;
CommandSubscriber* subscriber;

// Callback for MQTT commands
void handleCommand(char* topic, byte* payload, unsigned int length){
    String cmd=""; for(unsigned int i=0;i<length;i++) cmd+=(char)payload[i];
    Serial.println("Received command: "+cmd);
    device->executeCommand(cmd);
}

// =============================================
// SETUP
// =============================================
void setup(){
    Serial.begin(115200); delay(1000);
    device=new DeviceController("PLANT-001");
    device->setupDevice();

    network=new MyNetworkManager("Wokwi-GUEST","","broker.hivemq.com",1883);
    network->connectWiFi();
    network->connectMQTT();

    publisher=new DataPublisher(network,"plant/PLANT-001/telemetry");
    subscriber=new CommandSubscriber(network,"plant/PLANT-001/commands");
    subscriber->subscribe(handleCommand);

    Serial.println("System ready!");
}

// =============================================
// LOOP
// =============================================
void loop(){
    network->loop();
    String json=device->collectSensorData();
    publisher->publish(json);
    delay(2000);
}
