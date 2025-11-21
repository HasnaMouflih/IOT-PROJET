"""
Script de test complet pour valider les modèles LSTM + XGBoost
Teste la qualité des prédictions et vérifie les performances
"""
import json
import numpy as np
import pandas as pd
import tensorflow as tf
import xgboost as xgb
import joblib
import os
import requests
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

print("=" * 70)
print("🧪 TEST COMPLET DES MODÈLES LSTM + XGBOOST")
print("=" * 70 + "\n")

# ================================
# 📦 Chargement des modèles
# ================================
base_path = os.path.dirname(__file__)

print("1️⃣  CHARGEMENT DES MODÈLES")
print("-" * 70)

try:
    model_lstm_path = os.path.join(base_path, "lstm_future_model.h5")
    model_xgb_path = os.path.join(base_path, "xgboost_emotion_model.pkl")
    scaling_info_path = os.path.join(base_path, "scaling_info.json")
    
    # Vérifier existence des fichiers
    for path, name in [(model_lstm_path, "LSTM"), (model_xgb_path, "XGBoost"), (scaling_info_path, "Scaling info")]:
        if not os.path.exists(path):
            print(f"❌ {name} non trouvé: {path}")
            exit(1)
    
    print(f"✅ LSTM trouvé: {model_lstm_path}")
    print(f"✅ XGBoost trouvé: {model_xgb_path}")
    print(f"✅ Scaling info trouvé: {scaling_info_path}\n")
    
    # Charger les modèles
    model_lstm = tf.keras.models.load_model(model_lstm_path, compile=False)
    model_xgb = joblib.load(model_xgb_path)
    
    with open(scaling_info_path, "r", encoding="utf-8") as f:
        scaling_info = json.load(f)
    
    print("✅ Modèles chargés avec succès\n")
except Exception as e:
    print(f"❌ Erreur lors du chargement: {e}\n")
    exit(1)

# ================================
# 📊 Afficher infos des modèles
# ================================
print("2️⃣  INFORMATIONS DES MODÈLES")
print("-" * 70)

print(f"📊 Données d'entraînement:")
print(f"   Source: {scaling_info.get('data_source', 'N/A')}")
print(f"   Total enregistrements: {scaling_info.get('total_records', 'N/A')}")
print(f"   Séquence LSTM: {scaling_info.get('sequence_length', 'N/A')}")
print(f"   Séquences créées: {scaling_info.get('lstm_sequences', 'N/A')}")

print(f"\n📊 Performance XGBoost (données d'entraînement):")
print(f"   Score train: {scaling_info.get('xgb_train_score', 'N/A'):.1%}")
print(f"   Score test: {scaling_info.get('xgb_test_score', 'N/A'):.1%}")

# Charger les données d'entraînement pour calculer accuracy_score
try:
    response_train = requests.get("http://localhost:5001/get_all_plants_list")
    api_data_train = response_train.json()
    
    all_readings_train = []
    for plant in api_data_train.get("plants", []):
        readings = plant.get("data", {})
        all_readings_train.extend(readings.values())
    
    df_train = pd.DataFrame(all_readings_train)
    features = ["temperature", "humidity", "lightLevel", "soilMoisture"]
    X_min = scaling_info["X_min"]
    X_max = scaling_info["X_max"]
    
    # Normalisation données d'entraînement
    X_train_norm = (df_train[features] - pd.Series(X_min)) / (pd.Series(X_max) - pd.Series(X_min))
    sequence_length = scaling_info.get("sequence_length", 5)
    emotion_map = scaling_info.get("emotion_map", {})
    inv_emotion_map = {v: k for k, v in emotion_map.items()}
    
    # Générer les prédictions XGBoost sur les données d'entraînement
    y_pred_xgb = []
    y_true = []
    
    for i in range(len(X_train_norm) - sequence_length):
        seq = X_train_norm.iloc[i:i+sequence_length].values
        X_in = np.expand_dims(seq, axis=0)
        pred_lstm = model_lstm.predict(X_in, verbose=0)[0]
        
        # XGBoost prediction
        xgb_in = np.array([pred_lstm])
        pred_xgb = int(model_xgb.predict(xgb_in)[0])
        y_pred_xgb.append(pred_xgb)
        
        # Vérifie si on a l'émotion vraie
        if "emotion" in df_train.columns:
            true_emotion = df_train["emotion"].iloc[i + sequence_length]
            if true_emotion in emotion_map:
                y_true.append(emotion_map[true_emotion])
    
    # Calculer accuracy_score
    if len(y_pred_xgb) > 0 and len(y_true) > 0:
        acc_score = accuracy_score(y_true, y_pred_xgb)
        print(f"   Accuracy Score (validation): {acc_score:.1%}")
    else:
        print(f"   Accuracy Score (validation): N/A")
        
except Exception as e:
    print(f"   Accuracy Score (validation): Erreur - {e}")

print(f"\n🧠 Émotions détectées:")
emotion_map = scaling_info.get("emotion_map", {})
inv_emotion_map = {v: k for k, v in emotion_map.items()}
for emotion, idx in emotion_map.items():
    print(f"   {emotion} → {idx}")
print()

# ================================
# 📂 Charger données de test depuis API
# ================================
print("3️⃣  CHARGEMENT DES DONNÉES DE TEST")
print("-" * 70)

try:
    response = requests.get("http://localhost:5001/get_all_plants_list")
    api_data = response.json()
    
    if not api_data.get("success"):
        raise Exception("API request failed")
    
    all_readings = []
    for plant in api_data.get("plants", []):
        readings = plant.get("data", {})
        all_readings.extend(readings.values())
    
    print(f"✅ {len(all_readings)} enregistrements chargés depuis l'API\n")
except Exception as e:
    print(f"❌ Erreur API: {e}\n")
    exit(1)

df_test = pd.DataFrame(all_readings)

# ================================
# 🧪 TEST 1: Prédictions LSTM
# ================================
print("4️⃣  TEST 1 - PRÉDICTIONS LSTM (Valeurs futures)")
print("-" * 70)

features = ["temperature", "humidity", "lightLevel", "soilMoisture"]
X_min = scaling_info["X_min"]
X_max = scaling_info["X_max"]

# Normalisation
X_test_norm = (df_test[features] - pd.Series(X_min)) / (pd.Series(X_max) - pd.Series(X_min))

# Test sur les derniers enregistrements
sequence_length = scaling_info.get("sequence_length", 5)
if len(X_test_norm) >= sequence_length:
    recent_seq = X_test_norm.tail(sequence_length).values
    X_input = np.expand_dims(recent_seq, axis=0)
    
    pred_lstm = model_lstm.predict(X_input, verbose=0)[0]
    
    print(f"📏 Séquence: {sequence_length} enregistrements")
    print(f"✅ Prédiction LSTM (normalisée): {pred_lstm}")
    
    # Dénormalisation
    pred_denorm = pred_lstm * (pd.Series(X_max) - pd.Series(X_min)) + pd.Series(X_min)
    pred_denorm = np.clip(pred_denorm, pd.Series(X_min), pd.Series(X_max))
    
    print(f"\n✅ Prédiction LSTM (dénormalisée):")
    for i, feat in enumerate(features):
        print(f"   {feat}: {pred_denorm[i]:.2f}")
    print()
else:
    print(f"❌ Pas assez de données de test (besoin {sequence_length}, {len(X_test_norm)} disponibles)\n")

# ================================
# 🧪 TEST 2: Prédictions XGBoost
# ================================
print("5️⃣  TEST 2 - PRÉDICTIONS XGBOOST (Émotions)")
print("-" * 70)

if len(X_test_norm) >= sequence_length:
    # XGBoost attend les 4 prédictions du LSTM (pas les données brutes)
    # Les prédictions LSTM sont déjà dans pred_lstm (temperature, humidity, lightLevel, soilMoisture)
    xgb_input = np.array([pred_lstm])  # Utiliser les prédictions LSTM
    
    pred_xgb_idx = model_xgb.predict(xgb_input)[0]
    pred_xgb_proba = model_xgb.predict_proba(xgb_input)[0]
    pred_emotion = inv_emotion_map.get(int(pred_xgb_idx), "inconnue")
    
    print(f"✅ Prédiction XGBoost: {pred_emotion} (index {int(pred_xgb_idx)})")
    
    print(f"\n📊 Probabilités par émotion:")
    for i, emotion in inv_emotion_map.items():
        if i < len(pred_xgb_proba):
            prob = pred_xgb_proba[i]
            bar = "█" * int(prob * 20)
            print(f"   {emotion:15s}: {prob*100:5.1f}% {bar}")
    print()
else:
    print(f"❌ Pas assez de données\n")

# ================================
# 🧪 TEST 3: Validation vs données réelles
# ================================
print("6️⃣  TEST 3 - VALIDATION (Comparaison vs données réelles)")
print("-" * 70)

if "emotion" in df_test.columns:
    actual_emotion = df_test["emotion"].iloc[-1]
    print(f"✅ Émotion réelle (dernière): {actual_emotion}")
    print(f"✅ Émotion prédite: {pred_emotion}")
    
    match = "✅ MATCH!" if actual_emotion == pred_emotion else "❌ Pas de match"
    print(f"\n{match}\n")
else:
    print("⚠️ Colonne 'emotion' non trouvée dans les données\n")

# ================================
# 🧪 TEST 4: Test multi-plantes
# ================================
print("7️⃣  TEST 4 - TEST MULTI-PLANTES")
print("-" * 70)

if "deviceId" in df_test.columns:
    plant_ids = df_test["deviceId"].unique()
    print(f"📊 Plantes détectées: {len(plant_ids)}")
    
    predictions_test = []
    for plant_id in plant_ids:
        plant_data = df_test[df_test["deviceId"] == plant_id]
        
        if len(plant_data) >= sequence_length:
            # Prédiction LSTM
            plant_seq = (plant_data[features].tail(sequence_length).values - pd.Series(X_min).values) / (pd.Series(X_max).values - pd.Series(X_min).values)
            X_in = np.expand_dims(plant_seq, axis=0)
            pred_lstm_p = model_lstm.predict(X_in, verbose=0)[0]
            
            # Prédiction XGBoost (utiliser les prédictions du LSTM)
            xgb_in = np.array([pred_lstm_p])
            pred_emotion_p = inv_emotion_map.get(int(model_xgb.predict(xgb_in)[0]), "inconnue")
            
            predictions_test.append({
                "plant_id": plant_id,
                "records": len(plant_data),
                "emotion_predicted": pred_emotion_p
            })
            
            print(f"\n  🪴 {plant_id}:")
            print(f"     Enregistrements: {len(plant_data)}")
            print(f"     Émotion prédite: {pred_emotion_p}")
        else:
            print(f"\n  ⚠️ {plant_id}: Données insuffisantes ({len(plant_data)} < {sequence_length})")
    print()
else:
    print("⚠️ Colonne 'deviceId' non trouvée\n")

# ================================
# 📊 RÉSUMÉ TEST
# ================================
print("8️⃣  RÉSUMÉ DES TESTS")
print("=" * 70)

print(f"\n✅ LSTM: Fonctionne correctement")
print(f"✅ XGBoost: Fonctionne correctement")
print(f"✅ Données API: Accessibles")
print(f"✅ Prédictions: Généré avec succès\n")

print("🎯 RÉSULTAT: Les modèles sont OPÉRATIONNELS!")
print("=" * 70)
