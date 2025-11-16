import React, { useState } from "react";
import { Link } from "react-router-dom";
import "../style/Header.css";

// Font Awesome
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBell, faUser, faLeaf, faBars, faXmark } from "@fortawesome/free-solid-svg-icons";

function Header() {
  const [menuOpen, setMenuOpen] = useState(false);

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  return (
    <header className="header">
      <div className="logo">
        <FontAwesomeIcon icon={faLeaf} /> SmartPlant
      </div>

      <nav className={`nav-links ${menuOpen ? "active" : ""}`}>
        <Link to="/" onClick={toggleMenu}>Accueil</Link>
        <Link to="/dashboard" onClick={toggleMenu}>Tableau de bord</Link>
        <Link to="/about" onClick={toggleMenu}>À propos</Link>
        <Link to="/contact" onClick={toggleMenu}>Contact</Link>
      </nav>

      <div className="header-icons">
        <button className="alert-btn" title="Alertes">
          <FontAwesomeIcon icon={faBell} />
        </button>
        <button className="user-btn" title="Profil">
          <FontAwesomeIcon icon={faUser} />
        </button>

        {/* Hamburger for mobile */}
        <button className="menu-btn" onClick={toggleMenu}>
          <FontAwesomeIcon icon={menuOpen ? faXmark : faBars} />
        </button>
      </div>
    </header>
  );
}
export default Header;
