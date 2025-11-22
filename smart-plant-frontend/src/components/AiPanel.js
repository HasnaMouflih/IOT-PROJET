import React, { useState } from "react";
import { FaRobot } from "react-icons/fa";
import "../style/AiPanel.css";

function AiPanel({ plantData }) {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);

  const handlePredict = async () => {
    try {
      setLoading(true);

      const res = await fetch("http://localhost:8000/get_predictions", {
        method: "GET",
      });

      const data = await res.json();
      console.log("PREDICTION RECEIVED:", data);

      if (data.success) {
        setPredictions(data.predictions); // 🔹 on prend seulement la liste des prédictions
      } else {
        console.error("Erreur API:", data.error);
      }
    } catch (error) {
      console.error("Prediction error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-card large">
      <FaRobot className="ai-icon" />
      <h2 className="ai-title">AI Prediction</h2>
      <p className="ai-subtitle">Prédire l'état futur de votre plante</p>

      <button
        className={`ai-btn ${loading ? "loading" : ""}`}
        onClick={handlePredict}
        disabled={loading}
      >
        {loading ? <span className="spinner"></span> : "Lancer la prédiction"}
      </button>

      {/* AFFICHAGE DES PRÉDICTIONS */}
      {predictions.length > 0 && (
        <div className="ai-result">
          <h3>Résultats de la prédiction :</h3>

          <div className="predictions-container">
            {predictions.map((p, index) => (
              <div key={index} className="prediction-card">
                <h3>🌿 Plante : {p.deviceId}</h3>
                <p>⏳ Dans {p.hours_ahead} heures</p>
                <p>🌡 Température : {p.temperature}°C</p>
                <p>💧 Humidité : {p.humidity}%</p>
                <p>🌞 Lumière : {p.lightLevel}</p>
                <p>🌱 Humidité sol : {p.soilMoisture}%</p>
                <p>
                  ⚠️ <strong>État prévu :</strong> {p.emotion_predicted}
                </p>
                <small>Modèle : {p.model}</small>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default AiPanel;
