import React from "react";
import "../../src/style/features.css";

// Font Awesome
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTemperatureHigh, faTint, faSun, faRobot } from "@fortawesome/free-solid-svg-icons";

function FeaturesSection() {
  const features = [
    { icon: faTemperatureHigh, title: "Température", description: "Mesurez et contrôlez la température idéale pour votre plante." },
    { icon: faTint, title: "Humidité", description: "Surveillez le niveau d’humidité du sol et de l’air." },
    { icon: faSun, title: "Lumière", description: "Analysez la luminosité pour un développement optimal." },
    { icon: faRobot, title: "Émotions & Prédictions", description: "SmartPlant prédit les besoins et l’état émotionnel de votre plante." },
  ];

  return (
    <section className="features">
      <h2 className="features-title">Fonctionnalités principales</h2>
      <div className="features-cards">
        {features.map((feature, index) => (
          <div key={index} className="feature-card">
            <FontAwesomeIcon icon={feature.icon} className="feature-icon" />
            <h3>{feature.title}</h3>
            <p>{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default FeaturesSection;
