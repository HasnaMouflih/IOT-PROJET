import json
from emotion_layer import EmotionEngine, DecisionMaker

# =====================================================
#  TEST DU MODULE D’INTELLIGENCE & D’ÉMOTION DE LA PLANTE
#  Auteur : Aicha Hasni
# =====================================================

# --- Initialisation du moteur IA ---
engine = EmotionEngine()
decision = DecisionMaker()

# --- Données simulées ou de test (ex: fichier test_data.json) ---
sensor_data_samples = [
    {
        "deviceId": "Plant_01112",
        "soilMoisture": 42,
        "temperature": 28.5,
        "lightLevel": 600,
        "humidity": 75,
        "timestamp": "2025-10-12 14:15:00"
    },
    {
        "deviceId": "Plant_001113",
        "soilMoisture": 25,
        "temperature": 30.0,
        "lightLevel": 500,
        "humidity": 70,
        "timestamp": "2025-10-12 14:16:00"
    },
    {
        "deviceId": "Plant_01114",
        "soilMoisture": 50,
        "temperature": 38.0,
        "lightLevel": 650,
        "humidity": 60,
        "timestamp": "2025-10-12 14:17:00"
    },
    {
        "deviceId": "Plant_01115",
        "soilMoisture": 10,
        "temperature": 25.0,
        "lightLevel": 300,
        "humidity": 55,
        "timestamp": "2025-10-12 14:18:00"
    },
    {
        "deviceId": "Plant_01116",
        "soilMoisture": 35,
        "temperature": 32.0,
        "lightLevel": 700,
        "humidity": 80,
        "timestamp": "2025-10-12 14:19:00"
    }
]

# --- Résultats à sauvegarder ---
results = []

print("===== ANALYSE DES ÉTATS ÉMOTIONNELS DE LA PLANTE 🌿 =====\n")

# --- Boucle d’analyse ---
for data in sensor_data_samples:
    emotion = engine.computeEmotion(data)
    should_water = decision.shouldWaterPlant(data)
    is_optimal = decision.isEnvironmentOptimal(data)

    print(f"🌿 Plante : {data['deviceId']}")
    print(f"  🌡 Température : {data['temperature']}°C | 💧 Humidité : {data['humidity']}% | ☀️ Lumière : {data['lightLevel']}")
    print(f"  🧠 Émotion prédite : {emotion}")
    print(f"  🤖 Action : {'Arroser 💦' if should_water else 'Aucune action'}\n")

    results.append({
        "deviceId": data["deviceId"],
        "temperature": data["temperature"],
        "humidity": data["humidity"],
        "lightLevel": data["lightLevel"],
        "emotion": emotion,
        "action": "WATER" if should_water else "NONE",
        "optimal_environment": is_optimal
    })

# --- Sauvegarde des résultats dans un fichier JSON ---
import os
os.makedirs("results", exist_ok=True)

with open("results/output_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print("✅ Résultats sauvegardés dans 'results/output_results.json'")
