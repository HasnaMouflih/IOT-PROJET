import React from "react";
import "../style/Footer.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faFacebookF, faTwitter, faInstagram } from "@fortawesome/free-brands-svg-icons";

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-left">
          <h3>SmartPlant</h3>
          <p>Surveillez et prenez soin de vos plantes intelligemment.</p>
        </div>

        <div className="footer-center">
          <h4>Liens utiles</h4>
          <ul>
            <li><a href="#!">Mentions légales</a></li>
            <li><a href="#!">Contact</a></li>
          </ul>
        </div>

        <div className="footer-right">
          <h4>Suivez-nous</h4>
          <div className="social-icons">
            <a href="#!"><FontAwesomeIcon icon={faFacebookF} /></a>
            <a href="#!"><FontAwesomeIcon icon={faTwitter} /></a>
            <a href="#!"><FontAwesomeIcon icon={faInstagram} /></a>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <p>© {new Date().getFullYear()} SmartPlant. Tous droits réservés.</p>
      </div>
    </footer>
  );
}

export default Footer;
