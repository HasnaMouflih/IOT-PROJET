import io
import json
import numpy as np
import tensorflow as tf
import xgboost as xgb
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import joblib
import os
import requests

print("🚀 Prédiction en temps réel avec données limitées...\n")

# ================================
# 📦 Chargement des modèles
# ================================
base_path = os.path.dirname(__file__)
model_lstm_path = os.path.join(base_path, "lstm_future_model.h5")
model_xgb_path = os.path.join(base_path, "xgboost_emotion_model.pkl")

print("📦 Chargement des modèles...")
model_lstm = tf.keras.models.load_model(model_lstm_path, compile=False)
model_xgb = joblib.load(model_xgb_path)
print("✅ Modèles chargés avec succès.\n")

# ================================
# 📂 Chargement du dataset depuis l'API
# ================================
print("📂 Chargement du dataset depuis l'API...")
try:
    response = requests.get("http://localhost:5001/get_all_plants_list")
    api_data = response.json()
    
    if not api_data.get("success"):
        raise Exception("API request failed")
    
    records = []
    for plant in api_data.get("plants", []):
        readings = plant.get("data", {})
        for timestamp, reading_data in readings.items():
            if isinstance(reading_data, dict):
                reading_data["deviceId"] = plant.get("plant_id")
                records.append(reading_data)
    
    print(f"✅ {len(records)} enregistrements chargés depuis l'API.\n")
except Exception as e:
    print(f"❌ Erreur: {e}\n")
    exit(1)

# ================================
# ⚙️ Chargement des infos de normalisation
# ================================
scaling_info_path = os.path.join(base_path, "scaling_info.json")
with open(scaling_info_path, "r", encoding="utf-8") as f:
    scaling_info = json.load(f)

X_min = scaling_info["X_min"]
X_max = scaling_info["X_max"]
emotion_map = scaling_info["emotion_map"]
inv_emotion_map = {v: k for k, v in emotion_map.items()}

# ================================
# 🧮 Fonctions utilitaires
# ================================
def normalize(value, feature):
    return (value - X_min[feature]) / (X_max[feature] - X_min[feature])

def denormalize(value, feature):
    """Dénormalise et s'assure que la valeur reste dans les limites valides"""
    denorm_value = value * (X_max[feature] - X_min[feature]) + X_min[feature]
    denorm_value = np.clip(denorm_value, X_min[feature], X_max[feature])
    return denorm_value

def constrain_prediction(pred_value, recent_values, feature):
    """
    Force la prédiction à rester proche de la tendance réelle
    Utile quand il y a peu de données
    """
    recent_mean = np.mean(recent_values)
    recent_std = np.std(recent_values)
    
    # Si la prédiction s'écarte trop, la rapprocher
    if recent_std > 0 and abs(pred_value - recent_mean) > 2 * recent_std:
        # Ramener la prédiction vers la moyenne
        pred_value = recent_mean + np.sign(pred_value - recent_mean) * 1.5 * recent_std
    
    # Clipping final
    pred_value = np.clip(pred_value, X_min[feature], X_max[feature])
    return pred_value

def get_recent_trend(values):
    """Calcule la tendance récente (augmentation ou diminution)"""
    if len(values) < 2:
        return 0
    return np.mean(np.diff(values[-3:]))  # Tendance des 3 derniers points

# ================================
# 🌿 Extraction des plantes
# ================================
plant_ids = sorted(list(set([r["deviceId"] for r in records])))
print(f"🌿 Plantes détectées ({len(plant_ids)}) : {plant_ids}\n")

# ================================
# ⏱️ Paramètres de prédiction ADAPTÉ AUX DONNÉES LIMITÉES
# ================================
SEQUENCE_LENGTH = 5       # Réduit à 5 au lieu de 10 (besoin moins de données)
STEP_HOURS = 24
FUTURE_STEPS = 2

# ================================
# 📁 Dossier de sauvegarde
# ================================
output_dir = os.path.join(base_path, "predictions_graphs")
os.makedirs(output_dir, exist_ok=True)

predictions_json = []

# ================================
# 🔮 Prédiction en temps réel
# ================================
for plant_id in plant_ids:
    plant_data = [r for r in records if r["deviceId"] == plant_id]
    df = pd.DataFrame(plant_data)

    if len(df) < SEQUENCE_LENGTH:
        print(f"⚠️ {plant_id} ignorée ({len(df)} données < {SEQUENCE_LENGTH} requises)\n")
        continue

    df = df.sort_values("timestamp")

    # Derniers SEQUENCE_LENGTH enregistrements
    recent_data = df.tail(SEQUENCE_LENGTH)[["temperature", "humidity", "lightLevel", "soilMoisture"]].values
    recent_denorm = recent_data.copy()  # Garder les valeurs dénormalisées pour les contraintes

    # Normalisation
    for i, feat in enumerate(["temperature", "humidity", "lightLevel", "soilMoisture"]):
        recent_data[:, i] = normalize(recent_data[:, i], feat)

    future_hours = []
    temp_futures, hum_futures, light_futures, soil_futures, emo_futures = [], [], [], [], []

    print(f"🪴 {plant_id} — Prédictions temps réel :\n")

    X_input = np.expand_dims(recent_data, axis=0)

    for step in range(1, FUTURE_STEPS + 1):
        # Prédiction LSTM
        pred_future = model_lstm.predict(X_input, verbose=0)
        temp_f, hum_f, light_f, soil_f = pred_future[0]

        # Dénormalisation
        temp_f = denormalize(temp_f, "temperature")
        hum_f = denormalize(hum_f, "humidity")
        light_f = denormalize(light_f, "lightLevel")
        soil_f = denormalize(soil_f, "soilMoisture")

        # ✅ CONTRAINTES: Forcer à rester proche de la tendance
        temp_f = constrain_prediction(temp_f, recent_denorm[:, 0], "temperature")
        hum_f = constrain_prediction(hum_f, recent_denorm[:, 1], "humidity")
        light_f = constrain_prediction(light_f, recent_denorm[:, 2], "lightLevel")
        soil_f = constrain_prediction(soil_f, recent_denorm[:, 3], "soilMoisture")

        # Prédiction émotionnelle
        xgb_input = np.array([[temp_f, hum_f, light_f, soil_f]])
        pred_emotion_idx = model_xgb.predict(xgb_input)[0]
        pred_emotion = inv_emotion_map.get(int(pred_emotion_idx), "inconnue")

        print(f"   ⏳ Dans ~{step * STEP_HOURS} heures :")
        print(f"      🌡️ Température: {temp_f:.2f} °C")
        print(f"      💧 Humidité: {hum_f:.2f} %")
        print(f"      ☀️ Lumière: {light_f:.2f} lux")
        print(f"      🌿 Humidité sol: {soil_f:.2f} %")
        print(f"      🌱 Emotion: {pred_emotion}\n")

        predictions_json.append({
            "deviceId": plant_id,
            "hours_ahead": step * STEP_HOURS,
            "temperature": round(temp_f, 2),
            "humidity": round(hum_f, 2),
            "lightLevel": round(light_f, 2),
            "soilMoisture": round(soil_f, 2),
            "emotion_predicted": pred_emotion,
            "model": "LSTM + Contraintes physiques"
        })

        future_hours.append(step * STEP_HOURS)
        temp_futures.append(temp_f)
        hum_futures.append(hum_f)
        light_futures.append(light_f)
        soil_futures.append(soil_f)
        emo_futures.append(pred_emotion)

        # Mise à jour pour prédiction suivante
        new_row = np.array([[normalize(temp_f, "temperature"),
                             normalize(hum_f, "humidity"),
                             normalize(light_f, "lightLevel"),
                             normalize(soil_f, "soilMoisture")]])
        X_input = np.concatenate([X_input[:, 1:, :], np.expand_dims(new_row, axis=1)], axis=1)

    # ================================
    # 📈 Graphiques
    # ================================
    plt.figure(figsize=(10, 6))
    plt.plot(future_hours, temp_futures, marker='o', linewidth=2, label="Température (°C)", color='red')
    plt.plot(future_hours, hum_futures, marker='s', linewidth=2, label="Humidité (%)", color='blue')
    plt.plot(future_hours, soil_futures, marker='^', linewidth=2, label="Humidité sol (%)", color='green')
    plt.title(f"Prédictions temps réel - {plant_id} (Seq={SEQUENCE_LENGTH})")
    plt.xlabel("Heures dans le futur")
    plt.ylabel("Valeurs")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/{plant_id}_realtime.png")
    plt.close()

# ================================
# 💾 Sauvegarde
# ================================
pred_output_file = os.path.join(base_path, "predictions_realtime.json")
with open(pred_output_file, "w", encoding="utf-8") as f:
    json.dump(predictions_json, f, indent=2, ensure_ascii=False)

print(f"\n💾 Prédictions sauvegardées: {pred_output_file}")
print("✅ Fin des prédictions en temps réel.")
