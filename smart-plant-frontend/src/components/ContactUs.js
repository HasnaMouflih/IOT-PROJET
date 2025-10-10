import React from "react";
import "../style/ContactUs.css";

function ContactUs() {
  return (
    <section className="contact-section">
      <div className="contact-overlay">
        <div className="contact-container">
          <h1>Contactez-nous</h1>
          <p className="contact-intro">
            Vous avez une question, une idée ou souhaitez collaborer ? Écrivez-nous, nous serons ravis d’échanger avec vous 🌱
          </p>

          <div className="contact-content">
            {/* Formulaire */}
            <form className="contact-form">
              <input type="text" placeholder="Nom complet" required />
              <input type="email" placeholder="Adresse e-mail" required />
              <textarea rows="5" placeholder="Votre message..." required></textarea>
              <button type="submit">Envoyer le message</button>
            </form>

            {/* Informations */}
            <div className="contact-info">
              <h3>Nos coordonnées</h3>
              <p><strong>Email :</strong> support@smartplant.io</p>
              <p><strong>Téléphone :</strong> +212 6 12 34 56 78</p>
              <p><strong>Adresse :</strong> Technopark, Casablanca, Maroc</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default ContactUs;
