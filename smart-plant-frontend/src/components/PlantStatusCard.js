import React from "react";
import { FaSmile, FaMeh, FaFrown, FaExclamationTriangle } from "react-icons/fa"; 
import HappyPlantImg from "../assets/happy-plant.png";
import SadPlantImg from "../assets/sad-plant.png";

// Fonction qui retourne l'état émotionnel
function getPlantStatus(humidity, temperature, light) {
  if (humidity < 30 || humidity > 70 || temperature < 16 || temperature > 32 || light < 200 || light > 1300) {
    return {
      img: SadPlantImg,
      icon: <FaExclamationTriangle size={24} color="red" />,
      message: "La plante est en danger"
    };
  }
  if (humidity < 35 || humidity > 65 || temperature < 18 || temperature > 30 || light < 300 || light > 1200) {
    return {
      img: SadPlantImg,
      icon: <FaFrown size={24} color="orange" />,
      message: "La plante est stressée"
    };
  }
  if (humidity < 40 || humidity > 60 || temperature < 20 || temperature > 28 || light < 400 || light > 1000) {
    return {
      img: SadPlantImg,
      icon: <FaMeh size={24} color="orange" />,
      message: "La plante est fatiguée"
    };
  }
  return {
    img: HappyPlantImg,
    icon: <FaSmile size={24} color="green" />,
    message: "La plante est heureuse"
  };
}



function PlantStatusCard({ humidity, temperature, light }) {
  const status = getPlantStatus(humidity, temperature, light);

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
