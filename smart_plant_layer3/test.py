<<<<<<< HEAD
import cloudinary
import cloudinary.uploader

cloudinary.config(
  cloud_name = "dzsvyfovr",          # Ton Cloud name
  api_key = "134458997237921",            # Remplace ici par ta clé API
  api_secret = "9_ssJtao-41cSsXO9nLfjcI0EDM"      # Remplace ici par ton secret
)
def test_upload():
    try:
        result = cloudinary.uploader.upload("pic.png")
        print("✅ Fichier uploadé :", result["secure_url"])
    except Exception as e:
        print("❌ Erreur :", e)

test_upload()
=======
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
>>>>>>> af48798e79a8c66ec48a9b47efade0bb3fa425f8
