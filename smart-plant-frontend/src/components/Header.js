import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../style/Header.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBell, faUser, faLeaf, faBars, faXmark } from "@fortawesome/free-solid-svg-icons";
import { db } from "../firebase";
import { ref, onValue, update } from "firebase/database";
import { useAuth } from "./AuthContext";

function Header() {
  const { currentUser } = useAuth();
  const navigate = useNavigate();

  const [menuOpen, setMenuOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);

  const toggleMenu = () => setMenuOpen(!menuOpen);

  const toggleNotif = () => {
    setNotifOpen(!notifOpen);

    if (!notifOpen) {
      notifications.forEach((n) => {
        if (!n.read) {
          update(ref(db, `notifications/${n.plantId}/${n.key}`), { read: true });
        }
      });
    }
  };

  useEffect(() => {
    const notifRef = ref(db, "notifications");

    const unsubscribe = onValue(notifRef, (snapshot) => {
      const data = snapshot.val() || {};
      const notifList = Object.entries(data).flatMap(([plantId, plantNotifs]) =>
        Object.entries(plantNotifs).map(([key, notif]) => ({
          key,
          plantId,
          ...notif,
        }))
      );

      notifList.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      setNotifications(notifList.slice(0, 6));
    });

    return () => unsubscribe();
  }, []);

  const unreadCount = notifications.filter((n) => !n.read).length;

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
        <div className="notif-container">
          <button className="alert-btn" title="Alertes" onClick={toggleNotif}>
            <FontAwesomeIcon icon={faBell} />
            {unreadCount > 0 && <span className="notif-count">{unreadCount}</span>}
          </button>

          <div className={`notif-dropdown ${notifOpen ? "open" : ""}`}>
            {notifications.length === 0 ? (
              <div className="notif-item">Pas de notifications</div>
            ) : (
              notifications.map((n) => (
                <div key={n.key} className={`notif-item ${n.read ? "read" : "unread"}`}>
                  <strong>{n.plantId}:</strong> {n.message}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Afficher User ou Se connecter */}
        {currentUser ? (
          <button className="user-btn" title="Profil" >
            <FontAwesomeIcon icon={faUser} />
          </button>
        ) : (
          <button
            style={{
              backgroundColor: "#2b7a4b",
              color: "#fff",
              padding: "6px 12px", // réduit le padding
              fontSize: "0.85rem",  // police plus petite
              borderRadius: "20px",
              border: "none",
              cursor: "pointer",
            }}
            onClick={() => navigate("/login")}
          >
            Se connecter
          </button>

        )}

        <button className="menu-btn" onClick={toggleMenu}>
          <FontAwesomeIcon icon={menuOpen ? faXmark : faBars} />
        </button>
      </div>
    </header>
  );
}

export default Header;
