import React from "react";
import "../style/Sidebar.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faLeaf,
  faChartLine,
  faCog,
  faSignOutAlt
} from "@fortawesome/free-solid-svg-icons";

function Sidebar({ activeTab, setActiveTab, isOpen }) {
  return (
    <aside className={`sidebar ${isOpen ? "open" : "closed"}`}>
      <div className="sidebar-logo">
        <FontAwesomeIcon icon={faLeaf} className="leaf-icon" />
        {isOpen && <span className="logo-text">SmartPlant</span>}
      </div>

      <ul>
        <li
          className={activeTab === "etat" ? "active" : ""}
          onClick={() => setActiveTab("etat")}
        >
          <FontAwesomeIcon icon={faLeaf} /> {isOpen && "État de la plante"}
        </li>
        <li
          className={activeTab === "historique" ? "active" : ""}
          onClick={() => setActiveTab("historique")}
        >
          <FontAwesomeIcon icon={faChartLine} /> {isOpen && "Historique des mesures"}
        </li>
        <li
          className={activeTab === "parametres" ? "active" : ""}
          onClick={() => setActiveTab("parametres")}
        >
          <FontAwesomeIcon icon={faCog} /> {isOpen && "Paramètres"}
        </li>
        <li className="logout">
          <FontAwesomeIcon icon={faSignOutAlt} /> {isOpen && "Déconnexion"}
        </li>
      </ul>
    </aside>
  );
}

export default Sidebar;
