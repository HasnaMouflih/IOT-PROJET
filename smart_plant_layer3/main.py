import time
import os
import json
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
from flask import Flask, request, jsonify
from flask_cors import CORS  # <--- NOUVEAU : Pour autoriser React
import firebase_admin
from firebase_admin import credentials, db, auth, storage
from prometheus_flask_exporter import PrometheusMetrics
import cloudinary
import cloudinary.uploader

# Configuration Cloudinary
cloudinary.config(
  cloud_name = "dzsvyfovr",
  api_key = "134458997237921",
  api_secret = "9_ssJtao-41cSsXO9nLfjcI0EDM"
)

import os

# ===================================================================
# ÉTAPE 0 : CONFIGURATION
# ===================================================================

# 1. Chemin par défaut (pour le développement local, si le fichier existe)
LOCAL_KEY_FILE = "smart.json" 

# 2. Chemin temporaire et sécurisé pour le déploiement (Render)
DEPLOY_KEY_FILE = "/tmp/firebase_service_account.json" 

# Récupère le contenu JSON depuis la variable d'environnement (si elle est définie par Render)
firebase_key_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")

if firebase_key_json:
    # Si nous sommes en production/déploiement (FIREBASE_SERVICE_ACCOUNT_JSON est défini)
    
    # Écrit le contenu du secret dans un fichier temporaire sécurisé
    with open(DEPLOY_KEY_FILE, "w") as f:
        f.write(firebase_key_json)
        
    # Le chemin que le DatabaseManager utilisera
    SERVICE_ACCOUNT_FILE = DEPLOY_KEY_FILE 
    print(f"[Config] Mode Production: Utilisation de la clé temporaire {DEPLOY_KEY_FILE}")

else:
    # Si nous sommes en développement local (FIREBASE_SERVICE_ACCOUNT_JSON n'est PAS défini)
    
    # Le chemin que le DatabaseManager utilisera
    SERVICE_ACCOUNT_FILE = LOCAL_KEY_FILE
    print(f"[Config] Mode Local: Utilisation du fichier {LOCAL_KEY_FILE}")


# Configuration MQTT (inchangée)
MQTT_TELEMETRY_TOPIC_TEMPLATE = "plant/+/telemetry"
MQTT_COMMAND_TOPIC_TEMPLATE = "plant/{device_id}/commands"

# ==========================
# 1. MODÈLE DE DONNÉES
# ==========================
class SensorData:
    def __init__(self, deviceId, soilMoisture, temperature, lightLevel, humidity, timestamp=None, **kwargs):
        self.device_id = deviceId
        self.soil_moisture = float(soilMoisture)
        self.temperature = float(temperature)
        self.light_level = float(lightLevel)
        self.humidity = float(humidity)
        ts = datetime.now() if timestamp is None else datetime.fromtimestamp(int(timestamp)/1000)
        self.timestamp = ts.isoformat().replace(":", "_")

    def to_dict(self):
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
    def determine_emotion(self, data: SensorData):
        if data.soil_moisture < 30: return "assoiffé"
        if data.temperature > 35: return "stressé"
        if data.light_level < 15: return "fatigué"
        if 40 < data.soil_moisture < 75 and 18 < data.temperature < 28: return "heureux"
        return "neutre"

# ==========================
# 3. PRENEUR DE DÉCISION
# ==========================
class DecisionMaker:
    def decide_action(self, emotion: str):
        if emotion == "assoiffé": return "WATER:3000"
        if emotion == "stressé": return "FAN:90"
        if emotion == "heureux": return "LED:GREEN"
        return None

# ==========================
# 4. GESTIONNAIRE DE BASE DE DONNÉES (CORRIGÉ)
# ==========================
class DatabaseManager:
    def __init__(self, service_account_file):
        print(f"[DatabaseManager] Tentative de connexion avec le fichier : {service_account_file}")
        
        # On vérifie si le fichier existe
        if not os.path.exists(service_account_file):
            print(f"❌ ERREUR CRITIQUE : Le fichier '{service_account_file}' est introuvable !")
            print("Assurez-vous que le fichier JSON est bien dans le même dossier que ce script.")
            exit(1) # On arrête le script ici

        try:
            cred = credentials.Certificate(service_account_file)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://smart-plant-free-default-rtdb.firebaseio.com/',
                    'storageBucket': 'smart-plant-iot-c-30ed4.appspot.com'
                })
            self.db_root = db.reference("/")
            self.bucket = storage.bucket()
            print("[DatabaseManager] ✅ Realtime Database initialisée avec succès.")
        except Exception as e:
            print(f"❌ ERREUR CRITIQUE Firebase : {e}")
            # On force l'arrêt pour ne pas avoir l'erreur NoneType plus tard
            raise e 

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

    def get_latest_state(self, plant_id):
        # Plus de try/except ici pour voir l'erreur brute si elle survient
        return self.db_root.child("plants").child(plant_id).child("last_update").get()

    def get_all_readings(self, plant_id):
        readings = self.db_root.child("plants").child(plant_id).child("readings").get()
        return list(readings.values()) if readings else []
# ==========================
# 5. COMMUNICATEUR MQTT
# ==========================
class MqttCommunicator:
    def __init__(self, mqtt_broker, mqtt_port):
        self.client = mqtt.Client()
        self.broker = mqtt_broker
        self.port = mqtt_port
        self.client.on_connect = self._on_connect
        self.client.on_subscribe = self._on_subscribe

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[MQTT] ✅ Connecté au broker MQTT !")
            self.client.subscribe(MQTT_TELEMETRY_TOPIC_TEMPLATE)
        else:
            print(f"[MQTT] Erreur connexion: {rc}")

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        print(f"[MQTT] Souscription réussie avec QoS {granted_qos[0]}")

    def connect(self):
        self.client.connect(self.broker, self.port, 60)

    def start_listening(self):
        self.client.loop_start()

    def publish_command(self, device_id, command):
        topic = MQTT_COMMAND_TOPIC_TEMPLATE.format(device_id=device_id)
        self.client.publish(topic, command)
        print(f"[MQTT] Commande '{command}' envoyée sur '{topic}'")

    def set_on_message_callback(self, callback):
        self.client.on_message = callback

# ==========================
# 6. SERVICE D'INGESTION
# ==========================
class DataIngestService:
    def __init__(self, communicator, db_manager, emotion_engine, decision_maker):
        self.communicator = communicator
        self.db_manager = db_manager
        self.emotion_engine = emotion_engine
        self.decision_maker = decision_maker
        self.communicator.set_on_message_callback(self.on_message_received)

    def on_message_received(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            print(f"[Ingest] Message reçu sur {msg.topic}: {payload}")
            data_json = json.loads(payload)
            sensor_data = SensorData(**data_json)
            emotion = self.emotion_engine.determine_emotion(sensor_data)
            command = self.decision_maker.decide_action(emotion)
            if command:
                self.communicator.publish_command(sensor_data.device_id, command)
            data_to_save = sensor_data.to_dict()
            data_to_save['emotion'] = emotion
            self.db_manager.save_reading(sensor_data.device_id, data_to_save)
        except Exception as e:
            print(f"[Ingest] Erreur traitement message: {e}")

# ==========================
# 7. SERVICE API + CDN
# ==========================
class APIService:
    def __init__(self, communicator, db_manager):
        self.app = Flask(__name__)
        CORS(self.app) # <--- AJOUT IMPORTANT : Active CORS pour React
        self.communicator = communicator
        self.db_manager = db_manager
        self.metrics = PrometheusMetrics(self.app)
        self.metrics.info('app_info', 'Pot de Fleurs Émotionnel', version='1.0.0')
        self.setup_routes()

    def verify_token(self, id_token):
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token['uid']
        except Exception as e:
            print(f"[Auth] Token invalide: {e}")
            return None

    def setup_routes(self):
        @self.app.route('/')
        def home():
            return "<h1>API du Pot de Fleurs Émotionnel</h1><p>Le service est en ligne.</p>"

        @self.app.route('/plants/<plant_id>/state', methods=['GET'])
        def get_plant_state(plant_id):
            # --- SECTION SÉCURITÉ (Désactivée pour tester) ---
            # Pour réactiver, décommentez ces lignes :
            
            # auth_header = request.headers.get('Authorization')
            # if not auth_header:
            #     return jsonify({"error": "Unauthorized: No token provided"}), 401
            # 
            # # Nettoyage du token (enlève "Bearer " si présent)
            # token = auth_header.split(" ")[1] if " " in auth_header else auth_header
            # 
            # if not self.verify_token(token):
            #     return jsonify({"error": "Unauthorized: Invalid token"}), 401
            
            # --- FIN SECTION SÉCURITÉ ---

            state = self.db_manager.get_latest_state(plant_id)
            print(f"[DEBUG] get_latest_state({plant_id}) returned:", state)
            return jsonify(state) if state else (jsonify({"error": "Plante non trouvée"}), 404)

        @self.app.route('/plants/<plant_id>/history', methods=['GET'])
        def get_plant_history(plant_id):
            # --- SÉCURITÉ DÉSACTIVÉE ---
            # auth_header = request.headers.get('Authorization')
            # if not auth_header: return jsonify({"error": "Unauthorized"}), 401
            # token = auth_header.split(" ")[1] if " " in auth_header else auth_header
            # if not self.verify_token(token): return jsonify({"error": "Unauthorized"}), 401
            # ---------------------------

            history = self.db_manager.get_all_readings(plant_id)
            return jsonify(history) if history else (jsonify({"error": "Historique non trouvé"}), 404)

        @self.app.route('/plants/<plant_id>/command', methods=['POST'])
        def send_manual_command(plant_id):
            # --- SÉCURITÉ DÉSACTIVÉE ---
            # auth_header = request.headers.get('Authorization')
            # if not auth_header: return jsonify({"error": "Unauthorized"}), 401
            # token = auth_header.split(" ")[1] if " " in auth_header else auth_header
            # if not self.verify_token(token): return jsonify({"error": "Unauthorized"}), 401
            # ---------------------------

            data = request.get_json()
            command = data.get('command')
            if not command:
                return jsonify({"error": "La clé 'command' est requise"}), 400
            self.communicator.publish_command(plant_id, command)
            return jsonify({"message": f"Commande '{command}' envoyée à {plant_id}"}), 200

        # ROUTE CDN 
        # Ajoutez ceci sous vos autres routes
        @self.app.route('/admin/all-data', methods=['GET'])
        def get_entire_database():
            # Récupère tout depuis la racine "/"
            try:
                all_data = self.db_manager.db_root.get()
                return jsonify(all_data)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        @self.app.route('/cdn/<user_id>/files', methods=['GET'])
        def list_user_files(user_id):
            # --- SÉCURITÉ DÉSACTIVÉE ---
            # auth_header = request.headers.get('Authorization')
            # if not auth_header: return jsonify({"error": "Unauthorized"}), 401
            # token = auth_header.split(" ")[1] if " " in auth_header else auth_header
            # if not self.verify_token(token): return jsonify({"error": "Unauthorized"}), 401
            # ---------------------------
            
            try:
                bucket = self.db_manager.bucket
                prefix = f"{user_id}/"
                blobs = bucket.list_blobs(prefix=prefix)
                files = [
                    {
                        "name": b.name,
                        "url": b.generate_signed_url(timedelta(hours=1))
                    }
                    for b in blobs
                ]
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
    print("🚀 Lancement du service Cloud du Pot de Fleurs Émotionnel...")

    db_manager = DatabaseManager(SERVICE_ACCOUNT_FILE)
    emotion_engine = EmotionEngine()
    decision_maker = DecisionMaker()

    mqtt_communicator = MqttCommunicator("broker.hivemq.com", 1883)
    ingest_service = DataIngestService(mqtt_communicator, db_manager, emotion_engine, decision_maker)
    api_service = APIService(mqtt_communicator, db_manager)

    mqtt_communicator.connect()
    mqtt_communicator.start_listening()

    print("\n🌼 Le service est prêt. En attente des données de l'ESP32...")
    print("🌐 L'API est accessible sur http://localhost:5000")
    api_service.run()