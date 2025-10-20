import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faSmile,
  faFrown,
  faTired,
  faHeart,
  faTint,
  faTemperatureHigh,
  faSun,
  faBell,
  faBolt
} from "@fortawesome/free-solid-svg-icons";

function PlantStateCards({ humidity, temperature, light, aiMessage, plantMood }) {

  const moodIcon = {
    heureuse: faSmile,
    triste: faFrown,
    fatiguee: faTired,
    epanouie: faHeart
  };

  const moodText = {
    heureuse: "La plante est contente, humidité parfaite 🌿",
    triste: "La plante a besoin d’attention 😢",
    fatiguee: "La plante est fatiguée 💤",
    epanouie: "La plante est épanouie 😍"
  };

  return (
    <div className="cards-grid">

      {/* Carte État Émotionnel */}
      <section className="card emotional-state">
        <h2>État Émotionnel</h2>
        <div className="emojis">
          <FontAwesomeIcon icon={moodIcon[plantMood]} size="3x" />
        </div>
        <p>{moodText[plantMood]}</p>
      </section>

      {/* Carte Mesures en temps réel */}
      <section className="card realtime">
        <h2>Mesures en temps réel</h2>
        <ul>
          <li><FontAwesomeIcon icon={faTint} /> Humidité : {humidity}%</li>
          <li><FontAwesomeIcon icon={faTemperatureHigh} /> Température : {temperature}°C</li>
          <li><FontAwesomeIcon icon={faSun} /> Luminosité : {light} lux</li>
        </ul>
        <div className="chart-placeholder">
          <FontAwesomeIcon icon={faBolt} /> Graphiques à venir
        </div>
      </section>

      {/* Carte Notifications / Alertes */}
      <section className="card alerts">
        <h2><FontAwesomeIcon icon={faBell} /> Notifications / Alertes</h2>
        <ul>
          {humidity < 40 && <li>💧 Attention : La plante a soif !</li>}
          {light > 1000 && <li>☀️ Trop de lumière détectée !</li>}
        </ul>
      </section>

      {/* Carte Prédiction IA */}
      <section className="card ai-prediction">
        <h2>Prédiction IA</h2>
        <p>{aiMessage}</p>
      </section>

    </div>
  );
}

export default PlantStateCards;
