import React from "react";
import { Link } from "react-router-dom";
import "../style/Header.css";

// Font Awesome
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBell, faUser, faLeaf } from "@fortawesome/free-solid-svg-icons";

function Header() {
  return (
    <header className="header">
      <div className="logo">
        <FontAwesomeIcon icon={faLeaf} /> SmartPlant
      </div>

      <nav className="nav-links">
        <Link to="/">Accueil</Link>
        <Link to="/dashboard">Tableau de bord</Link>
        <Link to="/about">À propos</Link>
        <Link to="/contact">Contact</Link>
      </nav>

      <div className="header-icons">
        <button className="alert-btn" title="Alertes">
          <FontAwesomeIcon icon={faBell} />
        </button>
        <button className="user-btn" title="Profil">
          <FontAwesomeIcon icon={faUser} />
        </button>
      </div>
    </header>
  );
}

export default Header;
