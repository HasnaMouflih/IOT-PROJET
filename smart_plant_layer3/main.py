import os
import json
import time
import ssl
import requests
from datetime import datetime, timedelta

import paho.mqtt.client as mqtt
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db, auth, storage
from prometheus_flask_exporter import PrometheusMetrics
import cloudinary

# ------------------------
# Configuration (modifiables via ENV)
# ------------------------
# MQTT
MQTT_BROKER = os.environ.get("MQTT_BROKER", "028e2afc7bff49aa9758e69dfebd7b17.s1.eu.hivemq.cloud")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 8883))
MQTT_USERNAME = os.environ.get("MQTT_USERNAME", "hope_231")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", "Japodisehell1234")
# Topic par défaut compatible avec la plupart des ESP : "plant/+/telemetry"
MQTT_TELEMETRY_TOPIC_TEMPLATE = os.environ.get("MQTT_TELEMETRY_TOPIC_TEMPLATE", "plant/+/telemetry")
MQTT_COMMAND_TOPIC_TEMPLATE = os.environ.get("MQTT_COMMAND_TOPIC_TEMPLATE", "plant/{device_id}/commands")

# Cloudinary (optionnel)
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
    api_key=os.environ.get("CLOUDINARY_API_KEY", ""),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", "")
)

# Firebase service account file location
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "smart.json")
FIREBASE_KEY_ENV = os.environ.get("FIREBASE_KEY", None)

# If the environment provides the key, write it (only if non-empty)
if FIREBASE_KEY_ENV:
    try:
        with open(SERVICE_ACCOUNT_FILE, "w") as f:
            f.write(FIREBASE_KEY_ENV)
        print("[CONFIG] Firebase service account file written from ENV.")
    except Exception as e:
        print("[CONFIG] Impossible d'écrire le fichier de service Firebase:", e)


# ==========================
# 1. Model
# ==========================
class SensorData:
    def __init__(self, deviceId, soilMoisture, temperature, lightLevel, humidity, timestamp=None, **kwargs):
        self.device_id = deviceId
        self.soil_moisture = float(soilMoisture)
        self.temperature = float(temperature)
        self.light_level = float(lightLevel)
        self.humidity = float(humidity)
        if timestamp is None:
            ts = datetime.now()
        else:
            # attendu timestamp en ms (comme sur beaucoup d'ESP)
            try:
                ts = datetime.fromtimestamp(int(timestamp) / 1000)
            except Exception:
                ts = datetime.now()
        self.timestamp = ts.strftime("%Y%m%d_%H%M%S_%f")

    def to_dict(self):
        return {
            "deviceId": self.device_id,
            "soilMoisture": self.soil_moisture,
            "temperature": self.temperature,
            "lightLevel": self.light_level,
            "humidity": self.humidity,
            "timestamp": self.timestamp
        }

# ==========================
# 2. Emotion / Decision
# ==========================
class EmotionEngine:
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

class DecisionMaker:
    def decide_action(self, emotion: str):
        if emotion == "assoiffé": return "WATER_PUMP:3000"
        if emotion == "stressé": return "SET_FAN_SPEED:150"
        if emotion == "heureux": return "SET_LED_COLOR:GREEN"
        return None

# ==========================
# 3. Database Manager
# ==========================
class DatabaseManager:
    def __init__(self, service_account_file):
        print(f"[DatabaseManager] Tentative de connexion avec {service_account_file}")
        if not os.path.exists(service_account_file):
            raise FileNotFoundError(f"Le fichier de clé Firebase '{service_account_file}' est introuvable.")
        cred = credentials.Certificate(service_account_file)
        # Initialise l'app si nécessaire
        if not firebase_admin._apps:
            try:
                firebase_admin.initialize_app(cred, {
                    'databaseURL': os.environ.get('FIREBASE_DATABASE_URL', 'https://smart-plant-free-default-rtdb.firebaseio.com/')
                })
                print("[DatabaseManager] Firebase initialisé.")
            except Exception as e:
                print("[DatabaseManager] Erreur initialisation Firebase:", e)
                raise e
        self.db_root = db.reference("/")
        # optional: storage bucket
        try:
            bucket_name = os.environ.get("FIREBASE_STORAGE_BUCKET")
            if bucket_name:
                self.bucket = storage.bucket(bucket_name)
                print(f"[DatabaseManager] Bucket Firebase initialisé: {bucket_name}")
            else:
                self.bucket = None
                print("[DatabaseManager] Aucun bucket storage configuré.")
        except Exception as e:
            print("[DatabaseManager] Erreur initialisation bucket:", e)
            self.bucket = None

    def save_reading(self, device_id, data_dict):
        try:
            readings_ref = self.db_root.child("plants").child(device_id).child("readings")
            readings_ref.child(data_dict["timestamp"]).set(data_dict)
            self.db_root.child("plants").child(device_id).child("last_update").set(data_dict)
            print(f"[DatabaseManager] Données enregistrées pour {device_id}.")
            return True
        except Exception as e:
            print(f"[DatabaseManager] Erreur save_reading: {e}")
            return False

    def save_command(self, device_id, command):
        timestamp = datetime.now().isoformat().replace(":", "_").replace(".", "_")
        data_to_save = {"deviceId": device_id, "command": command, "timestamp": timestamp}
        try:
            self.db_root.child("plants").child(device_id).child("commands").child(timestamp).set(data_to_save)
            self.db_root.child("plants").child(device_id).child("last_command").set(data_to_save)
            print(f"[DatabaseManager] Commande enregistrée pour {device_id}: {command}")
            return True
        except Exception as e:
            print(f"[DatabaseManager] Erreur save_command: {e}")
            return False

    def get_latest_state(self, plant_id):
        return self.db_root.child("plants").child(plant_id).child("last_update").get()

    def get_all_readings(self, plant_id):
        readings = self.db_root.child("plants").child(plant_id).child("readings").get()
        return list(readings.values()) if readings else []

# ==========================
# 4. MQTT Communicator
# ==========================
class MqttCommunicator:
    def __init__(self, mqtt_broker, mqtt_port, username=None, password=None, use_tls=False):
        self.client = mqtt.Client()
        self.broker = mqtt_broker
        self.port = mqtt_port
        self.username = username
        self.password = password
        # TLS only if explicit
        if use_tls:
            try:
                self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS_CLIENT)
                print("[MQTT] TLS configuré.")
            except Exception as e:
                print("[MQTT] Erreur configuration TLS:", e)
        self.client.on_connect = self._on_connect
        self.client.on_subscribe = self._on_subscribe
        self.client.on_message = None  # sera défini par set_on_message_callback

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[MQTT] Connecté au broker MQTT.")
            # S'abonner au topic telemetry wildcard
            client.subscribe(MQTT_TELEMETRY_TOPIC_TEMPLATE)
            print(f"[MQTT] Souscrit à {MQTT_TELEMETRY_TOPIC_TEMPLATE}")
        else:
            print(f"[MQTT] Échec connexion MQTT, code: {rc}")

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        print(f"[MQTT] Souscription réussie (mid={mid}, qos={granted_qos})")

    def connect(self):
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.broker, self.port, 60)
        # start loop after connect
        self.client.loop_start()

    def start_listening(self):
        # si on s'est connecté via connect(), loop_start() est déjà lancé.
        print("[MQTT] Listening started (loop thread running).")

    def publish_command(self, device_id, command):
        topic = MQTT_COMMAND_TOPIC_TEMPLATE.format(device_id=device_id)
        self.client.publish(topic, command)
        print(f"[MQTT] Commande '{command}' envoyée sur '{topic}'")

    def set_on_message_callback(self, callback):
        self.client.on_message = callback

# ==========================
# 5. Notification Service
# ==========================
class NotificationService:
    def __init__(self):
        self.ref = db.reference("/notifications")

    def push(self, plant_id, message):
        notif = {
            "plantId": plant_id,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "seen": False
        }
        try:
            notif_ref = self.ref.child(plant_id).push(notif)
            print(f"[NOTIF] {message} (ID = {notif_ref.key})")
        except Exception as e:
            print(f"[NOTIF] Erreur push notification: {e}")

# ==========================
# 6. Data Ingest Service
# ==========================
class DataIngestService:
    def __init__(self, communicator: MqttCommunicator, db_manager: DatabaseManager,
                 emotion_engine: EmotionEngine, decision_maker: DecisionMaker, notif_service: NotificationService):
        self.communicator = communicator
        self.db_manager = db_manager
        self.emotion_engine = emotion_engine
        self.decision_maker = decision_maker
        self.notif_service = notif_service
        self.communicator.set_on_message_callback(self.on_message_received)

    def on_message_received(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            print(f"[Ingest] Message reçu sur {msg.topic}: {payload}")
            data_json = json.loads(payload)
            sensor_data = SensorData(**data_json)
            emotion = self.emotion_engine.determine_emotion(sensor_data)
            command = self.decision_maker.decide_action(emotion)
            # Sauvegarde + notification
            data_to_save = sensor_data.to_dict()
            data_to_save['emotion'] = emotion
            saved = self.db_manager.save_reading(sensor_data.device_id, data_to_save)
            if saved:
                print(f"[Ingest] Lecture sauvegardée pour {sensor_data.device_id}")
            if command:
                # Envoie commande automatique via API (si service local)
                self.send_auto_command_to_api(sensor_data.device_id, command)
                self.notif_service.push(sensor_data.device_id, f"Commande automatique envoyée ({command})")
        except Exception as e:
            print(f"[Ingest] Erreur traitement message: {e}")

    def send_auto_command_to_api(self, plant_id, command):
        try:
            url = f"http://localhost:5000/plants/{plant_id}/command"
            requests.post(url, json={"command": command}, timeout=5)
        except Exception as e:
            print(f"[AUTO] Erreur appel API auto: {e}")

# ==========================
# 7. Firebase listeners helper (note)
# ==========================
def setup_firebase_listeners(db_manager: DatabaseManager):
    # firebase_admin python SDK n'offre pas de .listen() "realtime" simple cross platform.
    # Ici on liste simplement les plantes existantes pour debug (pas d'écoute push).
    try:
        plants_ref = db_manager.db_root.child("plants")
        plants = plants_ref.get() or {}
        print("[FIREBASE LISTENER] Plantes trouvées:", list(plants.keys()))
        print("[FIREBASE LISTENER] Pour des listeners temps-réel, utiliser une solution basée sur Functions ou WebSockets.")
    except Exception as e:
        print("[FIREBASE LISTENER] Erreur:", e)

# ==========================
# 8. API Service (Flask)
# ==========================
class APIService:
    def __init__(self, communicator, db_manager, notif_service):
        self.app = Flask(__name__)
        CORS(self.app)  # autorise toutes les origines par défaut (pour debug local)
        self.communicator = communicator
        self.db_manager = db_manager
        self.notif_service = notif_service
        self.metrics = PrometheusMetrics(self.app)
        self.metrics.info('app_info', 'Pot de Fleurs Émotionnel', version='1.0.0')
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def home():
            return jsonify({"message": "Smart Garden API running"})

        @self.app.route('/plants/<plant_id>/state', methods=['GET'])
        def get_plant_state(plant_id):
            # sécurité désactivée pour debug local ; si besoin, réactive la vérif token
            state = self.db_manager.get_latest_state(plant_id)
            if state:
                return jsonify(state)
            return jsonify({"error": "Plante non trouvée"}), 404

        @self.app.route('/plants/<plant_id>/history', methods=['GET'])
        def get_plant_history(plant_id):
            history = self.db_manager.get_all_readings(plant_id)
            if history:
                return jsonify(history)
            return jsonify({"error": "Historique non trouvé"}), 404

        @self.app.route('/plants/<plant_id>/command', methods=['POST'])
        def send_manual_command(plant_id):
            data = request.get_json() or {}
            command = data.get('command')
            if not command:
                return jsonify({"error": "La clé 'command' est requise"}), 400
            # sauvegarde + envoi mqtt + notif
            self.db_manager.save_command(plant_id, command)
            self.communicator.publish_command(plant_id, command)
            self.notif_service.push(plant_id, f"Commande manuelle envoyée : {command}")
            return jsonify({"message": f"Commande '{command}' envoyée à {plant_id}"}), 200

        @self.app.route('/admin/all-data', methods=['GET'])
        def get_entire_database():
            try:
                all_data = self.db_manager.db_root.get()
                return jsonify(all_data)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/cdn/<user_id>/files', methods=['GET'])
        def list_user_files(user_id):
            try:
                bucket = self.db_manager.bucket
                if not bucket:
                    return jsonify({"error": "Aucun bucket configuré"}), 500
                prefix = f"{user_id}/"
                blobs = bucket.list_blobs(prefix=prefix)
                files = [{"name": b.name, "url": b.generate_signed_url(timedelta(hours=1))} for b in blobs]
                return jsonify({"files": files})
            except Exception as e:
                print(f"[CDN] Erreur list_user_files: {e}")
                return jsonify({"error": "Erreur lors de la récupération des fichiers"}), 500

    def run(self, host="0.0.0.0", port=5000):
        self.app.run(host=host, port=port, debug=False, use_reloader=False)

# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    print("🚀 Démarrage service...")

    # Init DB
    try:
        db_manager = DatabaseManager(SERVICE_ACCOUNT_FILE)
    except Exception as e:
        print("Impossible d'initialiser DatabaseManager:", e)
        raise SystemExit(1)

    # Components
    emotion_engine = EmotionEngine()
    decision_maker = DecisionMaker()
    notif_service = NotificationService()

    # Configure MQTT TLS usage conditionnellement (port 8883 => TLS)
    use_tls = MQTT_PORT == 8883
    mqtt_communicator = MqttCommunicator(
        mqtt_broker=MQTT_BROKER,
        mqtt_port=MQTT_PORT,
        username=MQTT_USERNAME,
        password=MQTT_PASSWORD,
        use_tls=use_tls
    )

    ingest_service = DataIngestService(mqtt_communicator, db_manager, emotion_engine, decision_maker, notif_service)
    api_service = APIService(mqtt_communicator, db_manager, notif_service)

    # Connect MQTT et lancer loop
    try:
        mqtt_communicator.connect()
        mqtt_communicator.start_listening()
    except Exception as e:
        print("[MAIN] Erreur connexion MQTT:", e)

    # Afficher plantes et activer listeners debug
    setup_firebase_listeners(db_manager)

    print("🌐 API accessible sur http://localhost:5000")
    api_service.run()
