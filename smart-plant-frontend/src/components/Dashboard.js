import React, { useState } from "react";
import Sidebar from "../components/Sidebar";
import PlantStatusCard from "../components/PlantStatusCard";
import RealtimeMeasureCard from "../components/RealtimeMeasureCard";
import ChartsSection from "../components/ChartsSection";
import "../style/dashboard.css";

function Dashboard() {
  const [activeItem, setActiveItem] = useState("plant"); // état actif

  const renderContent = () => {
    switch (activeItem) {
      case "plant":
        return (
          <div className="dashboard-content">
            <div className="measures-container">
              <RealtimeMeasureCard title="Humidité" value="45%" icon="FaTint" color="#4ECDC4" backcolor="#DFF2EB" />
              <RealtimeMeasureCard title="Température" value="25°C" icon="FaThermometerHalf" color="#FF6B6B" backcolor="#FCEF91" />
              <RealtimeMeasureCard title="Lumière" value="800 lux" icon="FaSun" color="#FFD93D" backcolor="#FCF9EA" />
            </div>
            <PlantStatusCard humidity={25} temperature={35} light={150} />
            <ChartsSection />
          </div>
        );
      case "history":
        return (
          <div className="dashboard-content">
            <h2>Historique des mesures</h2>
            <p>Les données historiques de la plante seront affichées ici.</p>
          </div>
        );
      case "settings":
        return (
          <div className="dashboard-content">
            <h2>Paramètres</h2>
            <p>Modifier les réglages de la plante et de l'application.</p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="dashboard-container">
      <Sidebar activeItem={activeItem} setActiveItem={setActiveItem} />
      <main className="dashboard-main">{renderContent()}</main>
    </div>
  );
}

export default Dashboard;
