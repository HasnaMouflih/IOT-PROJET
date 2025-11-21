from flask import Flask, jsonify
import firebase_admin
from firebase_admin import credentials, db
import numpy as np
import json
import os
import joblib
from tensorflow.keras.models import load_model

app = Flask(__name__)

# =============================
#   CHARGEMENT MODELES IA
# =============================
BASE_PATH = os.path.dirname(__file__)
lstm_model = load_model(
    os.path.join(BASE_PATH, "lstm_future_model.h5"),
    compile=False
)
xgb_model = joblib.load(os.path.join(BASE_PATH, "xgboost_emotion_model.pkl"))

with open(os.path.join(BASE_PATH, "scaling_info.json"), "r") as f:
    scaling = json.load(f)

X_min = scaling["X_min"]
X_max = scaling["X_max"]
emotion_map = scaling["emotion_map"]
emotion_map_reverse = {v: k for k, v in emotion_map.items()}

FEATURES = ["temperature", "humidity", "lightLevel", "soilMoisture"]
SEQUENCE_LENGTH = 5  # Réduit à 5 pour mieux gérer les données limitées

# =============================
#   INITIALISATION FIREBASE
# =============================
cred = credentials.Certificate("smart.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smart-plant-free-default-rtdb.firebaseio.com/'
})

# =============================
#   NORMALISATION
# =============================
def normalize(v, feature):
    return (v - X_min[feature]) / (X_max[feature] - X_min[feature])

def denormalize(v, feature):
    """Dénormalise une valeur en clippant aux plages valides"""
    denorm = v * (X_max[feature] - X_min[feature]) + X_min[feature]
    return np.clip(denorm, X_min[feature], X_max[feature])

# =============================
#   ENDPOINT → LIRE LAYER 3
 

#

# =============================
#   ENDPOINT → DEBUG - LISTER TOUS LES PLANTS
# =============================
@app.route('/get_all_plants_list', methods=['GET'])
def get_all_plants_list():
    """
    Get readings from all plants in the same format as get_plant1_readings
    """
    try:
        ref = db.reference("/plants")
        all_plants_data = ref.get()
        
        if not all_plants_data:
            return jsonify({"error": "No data found in database"}), 404
        
        all_plants = []
        
        # Iterate through all plants
        for plant_id, plant_data in all_plants_data.items():
            if isinstance(plant_data, dict) and "readings" in plant_data:
                readings = plant_data.get("readings", {})
                all_plants.append({
                    "plant_id": plant_id,
                    "total_readings": len(readings),
                    "data": readings
                })
        
        return jsonify({
            "success": True,
            "total_plants": len(all_plants),
            "plants": all_plants,
            "message": "All plants readings retrieved successfully"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================
 

# =============================
 

@app.route('/get_predictions', methods=['GET'])
def get_predictions():
    """
    Retourne toutes les prédictions contenues dans predictions_realtime.json
    """
    try:
        file_path = os.path.join(BASE_PATH, "predictions_realtime.json")

        if not os.path.exists(file_path):
            return jsonify({"error": "predictions_realtime.json introuvable"}), 404

        with open(file_path, "r") as f:
            predictions = json.load(f)

        return jsonify({
            "success": True,
            "total_predictions": len(predictions),
            "predictions": predictions
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
