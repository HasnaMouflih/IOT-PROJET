from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

# Route racine pour vérifier que le serveur fonctionne
@app.route('/')
def home():
    return "Emotion API is running!"

# Route pour récupérer les émotions depuis le fichier JSON
@app.route('/api/emotions', methods=['GET'])
def get_emotions():
    json_path = "results/output_results.json"

    # Vérifie si le fichier existe
    if not os.path.exists(json_path):
        return jsonify({"error": "File not found"}), 404

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 500

    return jsonify(data)

if __name__ == "__main__":
    app.run(port=5001, debug=True)
