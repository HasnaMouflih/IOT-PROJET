import React from "react";
import { Link } from "react-router-dom";
import "../style/HeroSection.css";
import plantImage from "../../src/assets/hero-2.jpg";

// Font Awesome
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faLeaf } from "@fortawesome/free-solid-svg-icons";

function HeroSection() {
  return (
    <section className="hero">
      <div className="hero-content">
        <h1 className="hero-title">
          Surveillez la santé et les émotions de votre plante <br /> en temps réel !
        </h1>
        <p className="hero-subtitle">
          SmartPlant <FontAwesomeIcon icon={faLeaf} /> analyse la lumière, l’humidité et la température pour prédire les besoins de votre plante.
        </p>
        <Link to="/dashboard" className="hero-button">
          Accéder au Dashboard
        </Link>
      </div>

      <div className="hero-image">
        <img src={plantImage} alt="Pot de fleurs intelligent" />
      </div>
    </section>
  );
}

export default HeroSection;
