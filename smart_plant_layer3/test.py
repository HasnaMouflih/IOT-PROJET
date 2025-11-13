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
