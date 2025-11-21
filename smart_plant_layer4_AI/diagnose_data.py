"""
Script de diagnostic pour analyser la distribution des émotions dans l'API
"""
import requests
import json
import pandas as pd
from collections import Counter

print("📊 Diagnostic des données Firebase...\n")

# ================================
# 📂 Charger les données
# ================================
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
    
    print(f"✅ {len(all_readings)} enregistrements chargés\n")
except Exception as e:
    print(f"❌ Erreur: {e}\n")
    exit(1)

# ================================
# 📊 Analyse des émotions
# ================================
df = pd.DataFrame(all_readings)

print("=" * 60)
print("📊 DISTRIBUTION DES ÉMOTIONS")
print("=" * 60)

if "emotion" in df.columns:
    emotion_counts = df["emotion"].value_counts()
    emotion_pct = df["emotion"].value_counts(normalize=True) * 100
    
    print(f"\nTotal: {len(df)} enregistrements\n")
    
    for emotion in emotion_counts.index:
        count = emotion_counts[emotion]
        pct = emotion_pct[emotion]
        bar = "█" * int(pct / 5)
        print(f"  {emotion:15s}: {count:3d} ({pct:5.1f}%) {bar}")
else:
    print("❌ Colonne 'emotion' non trouvée")
    print(f"   Colonnes disponibles: {df.columns.tolist()}")

# ================================
# 📊 Analyse des capteurs
# ================================
print("\n" + "=" * 60)
print("📊 STATISTIQUES DES CAPTEURS")
print("=" * 60)

features = ["temperature", "humidity", "lightLevel", "soilMoisture"]

for feat in features:
    if feat in df.columns:
        print(f"\n🔍 {feat}:")
        print(f"   Min: {df[feat].min():.2f}")
        print(f"   Max: {df[feat].max():.2f}")
        print(f"   Moyen: {df[feat].mean():.2f}")
        print(f"   Médian: {df[feat].median():.2f}")

# ================================
# 📊 Analyse par plant
# ================================
print("\n" + "=" * 60)
print("🪴 ANALYSE PAR PLANTE")
print("=" * 60)

if "deviceId" in df.columns:
    for plant_id in df["deviceId"].unique():
        plant_df = df[df["deviceId"] == plant_id]
        print(f"\n{plant_id}:")
        print(f"  Enregistrements: {len(plant_df)}")
        if "emotion" in plant_df.columns:
            for emotion, count in plant_df["emotion"].value_counts().items():
                print(f"    - {emotion}: {count}")
        if "soilMoisture" in plant_df.columns:
            print(f"  Humidité sol: {plant_df['soilMoisture'].min():.1f}% - {plant_df['soilMoisture'].max():.1f}%")

# ================================
# ⚠️ Observations
# ================================
print("\n" + "=" * 60)
print("⚠️ OBSERVATIONS & RECOMMANDATIONS")
print("=" * 60)

if "emotion" in df.columns:
    emotion_counts = df["emotion"].value_counts()
    dominant = emotion_counts.idxmax()
    dominant_pct = (emotion_counts.max() / len(df)) * 100
    
    if dominant_pct > 70:
        print(f"\n⚠️ ALERTE: {dominant} représente {dominant_pct:.1f}% des données!")
        print("   Cela crée un BIAIS dans le modèle.")
        print("\n💡 Solutions:")
        print("   1. Collectez plus de données variées")
        print("   2. Utilisez la stratégie SMOTE pour équilibrer")
        print("   3. Collectez des données quand les plantes vont mieux")
    else:
        print("\n✅ Distribution équilibrée des émotions")

print("\n" + "=" * 60)
