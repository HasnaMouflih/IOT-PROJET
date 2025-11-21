"""
Script pour réentraîner le modèle DIRECTEMENT avec les données de l'API Firebase
"""
import json
import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
import xgboost as xgb
import joblib
import os
import requests

print(" Réentraînement du modèle avec données API (temps réel)...\n")

# ================================
# Chargement des données depuis l'API
# ================================
print(" Chargement des données depuis l'API...")
try:
    response = requests.get("http://localhost:5001/get_all_plants_list")
    api_data = response.json()
    
    if not api_data.get("success"):
        raise Exception("API request failed")
    
    # Extraire les readings
    all_readings = []
    for plant in api_data.get("plants", []):
        readings = plant.get("data", {})
        all_readings.extend(readings.values())
    
    print(f" {len(all_readings)} enregistrements chargés depuis l'API.\n")
except Exception as e:
    print(f" Erreur: {e}\n")
    exit(1)

if len(all_readings) < 20:
    print(f" ATTENTION: Seulement {len(all_readings)} enregistrements!")
    print("   Le modèle aura du mal à apprendre avec si peu de données.\n")

# ================================
# Préparation des données
# ================================
df = pd.DataFrame(all_readings)
print(f"DataFrame: {len(df)} lignes\n")

features = ["temperature", "humidity", "lightLevel", "soilMoisture"]
label_col = "emotion"

# Vérifier qu'on a les colonnes nécessaires
missing_cols = [col for col in features + [label_col] if col not in df.columns]
if missing_cols:
    print(f" Colonnes manquantes: {missing_cols}")
    print(f"   Colonnes disponibles: {df.columns.tolist()}")
    exit(1)

# Encodage des émotions
emotion_map = {v: i for i, v in enumerate(df[label_col].unique())}
df["emotion_encoded"] = df[label_col].map(emotion_map)

print(f" Émotions détectées: {emotion_map}")
print(f" Distribution:\n{df[label_col].value_counts()}\n")

# Normalisation
X_min, X_max = df[features].min(), df[features].max()
df_norm = (df[features] - X_min) / (X_max - X_min)

print(f" Min/Max détectés:")
for feat in features:
    print(f"   {feat}: [{X_min[feat]:.2f}, {X_max[feat]:.2f}]")
print()

# ================================
#  Construction des séquences LSTM
# ================================
sequence_length = min(5, len(df) // 2)  # Adapté à la taille des données
print(f" Séquence LSTM: {sequence_length} enregistrements\n")

X_sequences, y_future = [], []

for i in range(len(df_norm) - sequence_length):
    seq = df_norm.iloc[i:i + sequence_length].values
    next_values = df_norm.iloc[i + sequence_length].values
    X_sequences.append(seq)
    y_future.append(next_values)

X_sequences, y_future = np.array(X_sequences), np.array(y_future)

if len(X_sequences) < 5:
    print(f"⚠️ ERREUR: Seulement {len(X_sequences)} séquences pour entraînement!")
    print("   Minimum requis: 5 séquences")
    print("   Vous avez {0} enregistrements, besoin d'au moins {1}.\n".format(
        len(df), sequence_length * 3))
    print("💡 Solutions:")
    print("   1. Collectez plus de données (au moins 20-30 enregistrements)")
    print("   2. Réduisez sequence_length")
    print("   3. Vérifiez que l'API retourne des données\n")
    exit(1)

print(f"✅ Données LSTM: {X_sequences.shape}")
print(f"✅ Labels futurs: {y_future.shape}\n")

# ================================
#  Modèle LSTM
# ================================
print(" Construction du modèle LSTM...")
model_lstm = Sequential([
    Input(shape=(sequence_length, len(features))),
    LSTM(32, activation='relu', return_sequences=False),  # Réduit pour peu de données
    Dense(len(features), activation='linear')
])

model_lstm.compile(optimizer=Adam(learning_rate=0.001), loss='mse')

print(" Entraînement du modèle LSTM...")
model_lstm.fit(X_sequences, y_future, epochs=50, batch_size=4, verbose=0)
print("Entraînement du LSTM terminé.\n")

# ================================
# 🔄 Prédictions pour XGBoost
# ================================
print(" Génération des prédictions LSTM...")
predicted_future = model_lstm.predict(X_sequences, verbose=0)
print(" Prédictions générées.\n")

# ================================
#  Modèle XGBoost
# ================================
y_emotions = df["emotion_encoded"].iloc[sequence_length:].values
X_train, X_test, y_train, y_test = train_test_split(
    predicted_future, y_emotions, test_size=0.2, random_state=42
)

print(f" Données XGBoost:")
print(f"   Train: {X_train.shape}, Test: {X_test.shape}\n")

print("Entraînement du modèle XGBoost...")
xgb_model = xgb.XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=4,
    random_state=42
)
xgb_model.fit(X_train, y_train)
print("✅ Entraînement du XGBoost terminé.\n")

# Évaluation
train_score = xgb_model.score(X_train, y_train)
test_score = xgb_model.score(X_test, y_test)
print(f"Score XGBoost:")
print(f"   Train: {train_score:.3f}")
print(f"   Test: {test_score:.3f}\n")

# ================================
#  Sauvegarde
# ================================
base_path = os.path.dirname(__file__)

print(" Sauvegarde des modèles...")
model_lstm.save(os.path.join(base_path, "lstm_future_model.h5"))
joblib.dump(xgb_model, os.path.join(base_path, "xgboost_emotion_model.pkl"))

# Sauvegarde des paramètres
scaling_info = {
    "X_min": X_min.to_dict(),
    "X_max": X_max.to_dict(),
    "emotion_map": emotion_map,
    "data_source": "API Firebase (temps réel)",
    "total_records": len(df),
    "sequence_length": sequence_length,
    "lstm_sequences": len(X_sequences),
    "xgb_train_score": float(train_score),
    "xgb_test_score": float(test_score)
}

with open(os.path.join(base_path, "scaling_info.json"), "w", encoding="utf-8") as f:
    json.dump(scaling_info, f, indent=4, ensure_ascii=False)

print(" Modèles sauvegardés:")
print("   - lstm_future_model.h5")
print("   - xgboost_emotion_model.pkl")
print("   - scaling_info.json\n")

print(" Résumé:")
print(f"   Données utilisées: {len(df)} enregistrements de l'API")
print(f"   Séquences LSTM: {len(X_sequences)}")
print(f"   Émotions: {list(emotion_map.keys())}")
print(f"   Score XGBoost (test): {test_score:.1%}\n")

print(" Réentraînement terminé!")
 
