import React from "react";
import { FaLeaf, FaChartLine, FaCog, FaSignOutAlt ,FaChartBar, FaSeedling, FaHistory, FaBrain, FaRobot } from "react-icons/fa";
import "../style/Sidebar.css";
import PersonImage from "../assets/person.png";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

function Sidebar({ activeItem, setActiveItem }) {
  const navigate = useNavigate();
  const { logout } = useAuth();

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <FaLeaf /> <span>SmartPlant</span>
      </div>

      <ul className="sidebar-menu">
        <li className={activeItem === "plant" ? "active" : ""} onClick={() => setActiveItem("plant")}>
          <FaSeedling /> État de la plante
        </li>

        <li className={activeItem === "statistiques" ? "active" : ""} onClick={() => setActiveItem("statistiques")}>
          <FaChartBar /> Statistiques et Analyses
        </li>

        <li className={activeItem === "history" ? "active" : ""} onClick={() => setActiveItem("history")}>
          <FaHistory /> Historique
        </li>

        <li className={activeItem === "prediction" ? "active" : ""} onClick={() => setActiveItem("prediction")}>
          <FaRobot /> AI Prédiction
        </li>

        <li className={activeItem === "settings" ? "active" : ""} onClick={() => setActiveItem("settings")}>
          <FaCog /> Paramètres
        </li>

        {/* 🔥 Déconnexion */}
        <li
          onClick={async () => {
            await logout();
            navigate("/");
          }}
        >
          <FaSignOutAlt /> Déconnexion
        </li>
      </ul>

      <div className="sidebar-bottom-image">
        <img src={PersonImage} alt="Person" />
      </div>
    </aside>
  );
}

export default Sidebar;
