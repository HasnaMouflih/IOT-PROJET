import React from "react";
import { FaSmile, FaMeh, FaFrown, FaExclamationTriangle } from "react-icons/fa"; 
import HappyPlantImg from "../assets/happy-plant.png";
import SadPlantImg from "../assets/sad-plant.png";

// Fonction qui mappe l'émotion reçue du backend vers image, icône et message
function getPlantStatusFromEmotion(emotion) {
  switch (emotion) {
    case "assoiffé":
      return {
        img: SadPlantImg,
        icon: <FaExclamationTriangle size={24} color="red" />,
        message: "La plante a soif !"
      };
    case "stressé":
      return {
        img: SadPlantImg,
        icon: <FaFrown size={24} color="orange" />,
        message: "La plante est stressée"
      };
    case "fatigué":
      return {
        img: SadPlantImg,
        icon: <FaMeh size={24} color="orange" />,
        message: "La plante est fatiguée"
      };
    case "heureux":
    case "neutre":
    default:
      return {
        img: HappyPlantImg,
        icon: <FaSmile size={24} color="green" />,
        message: "La plante est heureuse"
      };
  }
}

/**
 * Composant PlantStatusCard
 * Utilise directement l'émotion renvoyée par le backend
 */
function PlantStatusCard({ emotion }) {
  const status = getPlantStatusFromEmotion(emotion);

  return (
    <div className="plant-status-card">
      <h2>État émotionnel</h2>
      <div className="status-content">
        <img src={status.img} alt="plant emotion" className="plant-image" />
        <div className="status-message">
          {status.icon} <span>{status.message}</span>
        </div>
      </div>
    </div>
  );
}

export default PlantStatusCard;
