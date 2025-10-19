import threading
import json
from datetime import datetime
import time
import paho.mqtt.client as mqtt
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

# ===================================================================
# ÉTAPE 0: CONFIGURATION
# ===================================================================
SERVICE_ACCOUNT_FILE = "serviceAccountKey.json"
MQTT_TELEMETRY_TOPIC_TEMPLATE = "plant/+/telemetry" 
MQTT_COMMAND_TOPIC_TEMPLATE = "plant/{device_id}/commands"

# ==========================
# 1. MODÈLE DE DONNÉES
# ==========================
class SensorData:
    """Représente une lecture de capteur."""
    def __init__(self, deviceId, soilMoisture, temperature, lightLevel, humidity, timestamp=None, **kwargs):
        self.device_id = deviceId
        self.soil_moisture = float(soilMoisture)
        self.temperature = float(temperature)
        self.light_level = float(lightLevel)
        self.humidity = float(humidity)
        self.timestamp = datetime.now().isoformat() if timestamp is None else datetime.fromtimestamp(int(timestamp) / 1000).isoformat()

    def to_dict(self):
        """Convertit les données en dictionnaire simple."""
        return {
            "deviceId": self.device_id,
            "soilMoisture": self.soil_moisture,
            "temperature": self.temperature,
            "lightLevel": self.light_level,
            "humidity": self.humidity,
            "timestamp": self.timestamp,
        }

# ==========================
# 2. MOTEUR ÉMOTIONNEL
# ==========================
class EmotionEngine:
    """Traduit les données brutes des capteurs en une émotion."""
    def determine_emotion(self, data: SensorData):
        if data.soil_moisture < 30:
            return "assoiffé"
        if data.temperature > 35:
            return "stressé"
        if data.light_level < 15:
            return "fatigué"
        if 40 < data.soil_moisture < 75 and 18 < data.temperature < 28:
            return "heureux"
        return "neutre"

# ==========================
# 3. PRENEUR DE DÉCISION
# ==========================
class DecisionMaker:
    """Décide quelle action automatique entreprendre."""
    def decide_action(self, emotion: str):
        if emotion == "assoiffé":
            print("[DecisionMaker] La plante a soif. Décision : ARROSER.")
            return "WATER:3000"
        if emotion == "stressé":
            print("[DecisionMaker] La plante est stressée. Décision : VENTILER.")
            return "FAN:90"
        if emotion == "heureux":
            print("[DecisionMaker] La plante est heureuse. Décision : AFFICHER LED VERTE.")
            return "LED:GREEN"
        return None

# ==========================
# 4. GESTIONNAIRE DE BASE DE DONNÉES
# ==========================
class DatabaseManager:
    """Gère toutes les interactions avec Firestore."""
    def __init__(self, service_account_file):
        try:
            cred = credentials.Certificate(service_account_file)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("[DatabaseManager] Firebase initialisé avec succès.")
        except Exception as e:
            print(f"[DatabaseManager] ERREUR d'initialisation Firebase: {e}")
            self.db = None

    def save_reading(self, device_id, data_dict):
        """Enregistre une nouvelle lecture ET l'émotion dans l'historique."""
        if not self.db: return False
        try:
            doc_ref = self.db.collection("plants").document(device_id).collection("readings").document(data_dict["timestamp"])
            doc_ref.set(data_dict)
            plant_doc_ref = self.db.collection("plants").document(device_id)
            plant_doc_ref.set({'last_update': data_dict}, merge=True)
            print(f"[DatabaseManager] Données enregistrées pour {device_id}.")
            return True
        except Exception as e:
            print(f"[DatabaseManager] Erreur save_reading: {e}")
            return False

    def get_latest_state(self, plant_id):
        """Récupère le dernier état connu de la plante."""
        if not self.db: return None
        try:
            plant_ref = self.db.collection("plants").document(plant_id).get()
            return plant_ref.to_dict().get('last_update') if plant_ref.exists else None
        except Exception as e:
            print(f"[DatabaseManager] Erreur get_latest_state: {e}")
            return None

    def get_all_readings(self, plant_id):
        """Récupère tout l'historique des lectures pour une plante."""
        if not self.db: return None
        try:
            readings_ref = self.db.collection("plants").document(plant_id).collection("readings").order_by("timestamp", direction=firestore.Query.ASCENDING).stream()
            history = [doc.to_dict() for doc in readings_ref]
            return history
        except Exception as e:
            print(f"[DatabaseManager] Erreur get_all_readings: {e}")
            return None

# ==========================
# 5. COMMUNICATEUR MQTT (AMÉLIORÉ AVEC PLUS DE LOGS)
# ==========================
class MqttCommunicator:
    """Classe centrale pour gérer toute la communication MQTT."""
    def __init__(self, mqtt_broker, mqtt_port):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.broker = mqtt_broker
        self.port = mqtt_port
        # --- NOUVEAU : Callbacks de débogage ---
        self.client.on_connect = self._on_connect
        self.client.on_subscribe = self._on_subscribe

    # --- NOUVEAU : Gère la connexion et la souscription ---
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[MqttCommunicator] Connexion au broker MQTT réussie !")
            # On s'abonne ici, APRÈS une connexion réussie
            topic = "plant/+/telemetry"
            self.client.subscribe(topic)
        else:
            print(f"[MqttCommunicator] ERREUR de connexion, code de retour: {rc}")

    # --- NOUVEAU : Confirme la souscription ---
    def _on_subscribe(self, client, userdata, mid, granted_qos):
        print(f"[MqttCommunicator] Souscription au topic réussie avec QoS: {granted_qos[0]}")

    def connect(self):
        print(f"[MqttCommunicator] Tentative de connexion à {self.broker}:{self.port}...")
        self.client.connect(self.broker, self.port, 60)

    def start_listening(self):
        self.client.loop_start()

    def publish_command(self, device_id, command):
        topic = MQTT_COMMAND_TOPIC_TEMPLATE.format(device_id=device_id)
        self.client.publish(topic, command)
        print(f"[MqttCommunicator] Commande '{command}' publiée sur le topic '{topic}'")

    def set_on_message_callback(self, on_message_callback):
        self.client.on_message = on_message_callback
        print("[MqttCommunicator] Le gestionnaire de messages est prêt.")

# ==========================
# 6. SERVICE D'INGESTION
# ==========================
class DataIngestService:
    """Reçoit, analyse, décide, et stocke."""
    def __init__(self, communicator: MqttCommunicator, db_manager: DatabaseManager, emotion_engine: EmotionEngine, decision_maker: DecisionMaker):
        self.communicator = communicator
        self.db_manager = db_manager
        self.emotion_engine = emotion_engine
        self.decision_maker = decision_maker
        self.communicator.set_on_message_callback(self.on_message_received)

    def on_message_received(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            print(f"\n[DataIngestService] Message reçu sur {msg.topic}: {payload}")
            
            data_json = json.loads(payload)
            sensor_data = SensorData(**data_json)
            
            emotion = self.emotion_engine.determine_emotion(sensor_data)
            print(f"[EmotionEngine] Émotion déterminée : '{emotion}'")

            command_to_send = self.decision_maker.decide_action(emotion)
            
            if command_to_send:
                self.communicator.publish_command(sensor_data.device_id, command_to_send)

            data_to_save = sensor_data.to_dict()
            data_to_save['emotion'] = emotion
            
            self.db_manager.save_reading(sensor_data.device_id, data_to_save)
        except Exception as e:
            print(f"[DataIngestService] ERREUR lors du traitement du message: {e}")

# ==========================
# 7. SERVICE API
# ==========================
class APIService:
    """Interface pour que l'application externe puisse interagir."""
    def __init__(self, communicator: MqttCommunicator, db_manager: DatabaseManager):
        self.app = Flask(__name__)
        self.communicator = communicator
        self.db_manager = db_manager
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/', methods=['GET'])
        def home():
            return """<h1>API du Pot de Fleurs Émotionnel</h1>
                      <p>Le service est en ligne.</p>
                      <p>Endpoints disponibles :</p>
                      <ul>
                        <li>GET /plants/&lt;plant_id&gt;/state : Récupère le dernier état connu.</li>
                        <li>GET /plants/&lt;plant_id&gt;/history : Récupère tout l'historique des données.</li>
                        <li>POST /plants/&lt;plant_id&gt;/command : Envoie une commande manuelle.</li>
                      </ul>"""

        @self.app.route('/plants/<plant_id>/state', methods=['GET'])
        def get_plant_state(plant_id):
            state = self.db_manager.get_latest_state(plant_id)
            return jsonify(state) if state else (jsonify({"error": "Plante non trouvée"}), 404)

        @self.app.route('/plants/<plant_id>/history', methods=['GET'])
        def get_plant_history(plant_id):
            history = self.db_manager.get_all_readings(plant_id)
            return jsonify(history) if history is not None else (jsonify({"error": "Historique non trouvé ou plante inexistante"}), 404)

        @self.app.route('/plants/<plant_id>/command', methods=['POST'])
        def send_manual_command(plant_id):
            data = request.get_json()
            command = data.get('command')
            if not command:
                return jsonify({"error": "La clé 'command' est requise"}), 400
            
            self.communicator.publish_command(plant_id, command)
            return jsonify({"message": f"Commande '{command}' envoyée à {plant_id}"}), 200

    def run(self, host="0.0.0.0", port=5000):
        self.app.run(host=host, port=port, debug=False, use_reloader=False)

# ==========================
# PROGRAMME PRINCIPAL
# ==========================
if __name__ == "__main__":
    print("Lancement du service Cloud pour le Pot de Fleurs Émotionnel...")
    
    db_manager = DatabaseManager(SERVICE_ACCOUNT_FILE)
    emotion_engine = EmotionEngine()
    decision_maker = DecisionMaker()
    
    mqtt_communicator = MqttCommunicator("broker.hivemq.com", 1883)
    
    ingest_service = DataIngestService(mqtt_communicator, db_manager, emotion_engine, decision_maker)
    api_service = APIService(mqtt_communicator, db_manager)

    mqtt_communicator.connect()
    mqtt_communicator.start_listening()
    
    print("\nLe service est prêt. En attente des données de l'ESP32...")
    print(f"L'API est accessible sur http://localhost:5000")
    
    api_service.run()

