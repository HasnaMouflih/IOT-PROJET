import React from "react";
import "../style/AboutUs.css";

function AboutUs() {
  return (
    <section className="about-section">
      <div className="about-overlay">
        <div className="about-container">
          <h1>À propos de SmartPlant</h1>
          <p>
            SmartPlant est une solution innovante qui relie la nature et la technologie.
            Notre mission est d’aider les amoureux des plantes à mieux comprendre
            et à prendre soin de leurs compagnons verts grâce à des capteurs intelligents
            et une analyse en temps réel des conditions environnementales.
          </p>
          <p>
            Fondée par une équipe passionnée d’ingénieurs et de chercheurs, SmartPlant
            vise à rendre la surveillance des plantes intuitive, éducative et durable.
            Nous croyons que chaque plante mérite une attention personnalisée —
            et que la technologie peut rendre cela possible.
          </p>
          <p>
            Rejoignez-nous dans notre mission pour un monde plus vert et plus connecté 🌿.
          </p>
        </div>
      </div>
    </section>
  );
}

export default AboutUs;
