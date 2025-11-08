import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

print("🚀 Démarrage du test Firebase Realtime Database...")

# Initialisation Firebase
cred = credentials.Certificate("key_private.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smart-plant-free-default-rtdb.firebaseio.com/'
})

try:
    ref = db.reference("/plants/test_plant/readings")
    timestamp = datetime.now().isoformat().replace(":", "_").replace(".", "_")
    data = {
        "deviceId": "test_plant",
        "humidity": 60,
        "lightLevel": 80,
        "soilMoisture": 50,
        "temperature": 25,
        "timestamp": str(datetime.now())
    }
    ref.child(timestamp).set(data)
    print("✅ Écriture réussie !")

    snapshot = ref.get()
    print("✅ Lecture réussie ! Données actuelles :")
    print(snapshot)

except Exception as e:
    print("❌ Erreur :", e)
