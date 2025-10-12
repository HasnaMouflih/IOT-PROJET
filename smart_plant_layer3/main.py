import threading
import json
from datetime import datetime
import time
import requests
import paho.mqtt.client as mqtt
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore


# ==========================
# SensorData
# ==========================
class SensorData:
    def __init__(self, device_id, soil_moisture, temperature, light_level, humidity, timestamp=None):
        self.device_id = device_id
        self.soil_moisture = soil_moisture
        self.temperature = temperature
        self.light_level = light_level
        self.humidity = humidity
        self.timestamp = timestamp if timestamp else datetime.now().isoformat()

    def to_dict(self):
        return {
            "deviceId": self.device_id,
            "soilMoisture": self.soil_moisture,
            "temperature": self.temperature,
            "lightLevel": self.light_level,
            "humidity": self.humidity,
            "timestamp": self.timestamp,
            "status": self.evaluate_status()
        }

    def evaluate_status(self):
        if self.soil_moisture < 30:
            return "Needs Water"
        elif self.temperature > 35:
            return "Stressed"
        else:
            return "Happy"





# ==========================
# DatabaseManager
# ==========================
class DatabaseManager:
    def __init__(self, service_account_file="serviceAccountKey.json"):
        try:
            cred = credentials.Certificate(service_account_file)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
                print("[DatabaseManager]  Firebase initialisé avec succès")
            self.db = firestore.client()
        except Exception as e:
            print("[DatabaseManager]  Erreur d'initialisation Firebase :", e)

    def saveReading(self, device_id, data):
        try:
            safe_timestamp = data.timestamp.replace(":", "-").replace(" ", "_")
            doc_ref = self.db.collection("plants") \
                             .document(device_id) \
                             .collection("readings") \
                             .document(safe_timestamp)
            data_dict = data.to_dict()
            doc_ref.set(data_dict)
            self.updateEmotionState(device_id, data_dict["status"])
            print(f"[DatabaseManager]  Données enregistrées pour {device_id}")
            return True
        except Exception as e:
            print("[DatabaseManager]  Erreur saveReading :", e)
            return False

    def getPlantState(self, plant_id):
        try:
            readings_ref = self.db.collection("plants") \
                                  .document(plant_id) \
                                  .collection("readings") \
                                  .order_by("timestamp", direction=firestore.Query.DESCENDING) \
                                  .limit(1).stream()
            latest = [doc.to_dict() for doc in readings_ref]
            return latest[0] if latest else None
        except Exception as e:
            print("[DatabaseManager]  Erreur getPlantState :", e)
            return None

    def updateEmotionState(self, plant_id, emotion):
        try:
            self.db.collection("plants").document(plant_id).set({"emotion": emotion}, merge=True)
            print(f"[DatabaseManager]  Émotion mise à jour pour {plant_id} : {emotion}")
        except Exception as e:
            print("[DatabaseManager]  Erreur updateEmotionState :", e)





# ==========================
# DataIngestService
# ==========================
class DataIngestService:
    def __init__(self, mqtt_broker="broker.hivemq.com", mqtt_port=1883,
                 mqtt_topic="smartplant/sensor", api_endpoint="http://localhost:5000"):
        self.mqttClient = mqtt.Client(protocol=mqtt.MQTTv311)
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.apiEndpoint = api_endpoint
        self.db_manager = DatabaseManager()
        self.mqttClient.on_connect = self.onConnect
        self.mqttClient.on_message = self.onMessageReceived

    def start(self):
        print("[DataIngestService]  Connexion au broker MQTT...")
        self.mqttClient.connect(self.mqtt_broker, self.mqtt_port, 60)
        self.mqttClient.loop_forever()

    def onConnect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[DataIngestService]  Connecté au broker MQTT")
            client.subscribe(self.mqtt_topic)
        else:
            print(f"[DataIngestService]  Erreur de connexion MQTT (rc={rc})")

    def parseSensorData(self, rawData):
        data_json = json.loads(rawData)
        return SensorData(
            device_id=data_json["deviceId"],
            soil_moisture=data_json["soilMoisture"],
            temperature=data_json["temperature"],
            light_level=data_json["lightLevel"],
            humidity=data_json["humidity"],
            timestamp=data_json.get("timestamp")
        )

    def forwardToDatabase(self, data):
        self.db_manager.saveReading(data.device_id, data)

    def onMessageReceived(self, client, userdata, msg):
        try:
            print(f"[DataIngestService]  Message reçu sur {msg.topic}: {msg.payload.decode()}")
            sensor_data = self.parseSensorData(msg.payload.decode())
            self.forwardToDatabase(sensor_data)
            try:
                requests.post(f"{self.apiEndpoint}/plants/{sensor_data.device_id}/state", json=sensor_data.to_dict())
            except Exception as e:
                print("[DataIngestService]  Erreur envoi API :", e)
        except Exception as e:
            print("[DataIngestService]  Erreur onMessageReceived :", e)





# ==========================
# APIService
# ==========================
class APIService:
    def __init__(self, basePath="/plants", port=5000):
        self.app = Flask(__name__)
        self.db_manager = DatabaseManager()
        self.basePath = basePath
        self.port = port
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def home():
            return " API Smart Plant fonctionne !"

        @self.app.route(f'{self.basePath}/<plant_id>/state', methods=['GET', 'POST'])
        def plant_state(plant_id):
            if request.method == 'GET':
                state = self.db_manager.getPlantState(plant_id)
                return jsonify(state) if state else jsonify({"message": "Aucune donnée trouvée"}), 200
            elif request.method == 'POST':
                data = request.get_json()
                sensor_data = SensorData(
                    device_id=plant_id,
                    soil_moisture=data.get("soilMoisture"),
                    temperature=data.get("temperature"),
                    light_level=data.get("lightLevel"),
                    humidity=data.get("humidity"),
                    timestamp=data.get("timestamp")
                )
                self.db_manager.saveReading(plant_id, sensor_data)
                return jsonify({"message": "Données reçues et enregistrées"}), 200

        @self.app.route(f'{self.basePath}/<plant_id>/command', methods=['POST'])
        def send_command(plant_id):
            data = request.get_json()
            print(f"[APIService]  Commande reçue pour {plant_id} :", data)
            return jsonify({"message": "Commande reçue"}), 200

    #  Méthode run manquante
    def run(self):
        self.app.run(host="0.0.0.0", port=self.port, debug=True, use_reloader=False)



# ==========================
# MAIN PROGRAM
# ==========================
if __name__ == "__main__":
    mqtt_service = DataIngestService()
    mqtt_thread = threading.Thread(target=mqtt_service.start)
    mqtt_thread.start()
    time.sleep(2)
    api_service = APIService()
    api_service.run()
