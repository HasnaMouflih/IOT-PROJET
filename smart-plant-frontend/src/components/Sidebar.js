import React from "react";
import { FaLeaf, FaChartLine, FaCog, FaSignOutAlt } from "react-icons/fa";
import "../style/Sidebar.css";
import PersonImage from "../assets/person.png"; // ton image PNG sans background

function Sidebar({ activeItem, setActiveItem }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <FaLeaf /> <span>SmartPlant</span>
      </div>

      <ul className="sidebar-menu">
        <li
          className={activeItem === "plant" ? "active" : ""}
          onClick={() => setActiveItem("plant")}
        >
          <FaChartLine /> État de la plante
        </li>
        <li
          className={activeItem === "history" ? "active" : ""}
          onClick={() => setActiveItem("history")}
        >
          <FaChartLine /> Historique
        </li>
        <li
          className={activeItem === "settings" ? "active" : ""}
          onClick={() => setActiveItem("settings")}
        >
          <FaCog /> Paramètres
        </li>
        <li>
          <FaSignOutAlt /> Déconnexion
        </li>
      </ul>

      {/* Image en bas */}
      <div className="sidebar-bottom-image">
        <img src={PersonImage} alt="Person" />
      </div>
    </aside>
  );
}

export default Sidebar;
