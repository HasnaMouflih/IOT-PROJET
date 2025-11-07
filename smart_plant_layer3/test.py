from firebase_admin import credentials, initialize_app, storage

cred = credentials.Certificate("smart_key.json")
app = initialize_app(cred, {'storageBucket': 'smart-plant-iot-30ed4.appspot.com'})
bucket = storage.bucket()

# Test : créer un fichier test.txt et l'uploader
blob = bucket.blob("test.txt")
blob.upload_from_string("Hello Firebase Storage!")
print("✅ Fichier uploadé :", blob.public_url)
