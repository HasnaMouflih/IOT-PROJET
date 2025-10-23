import React, { useState, useEffect } from "react";
import CircularProgress from "@mui/material/CircularProgress";
import Sidebar from "../components/Sidebar";
import PlantStatusCard from "../components/PlantStatusCard";
import RealtimeMeasureCard from "../components/RealtimeMeasureCard";
import ChartsSection from "../components/ChartsSection";
import CommandPanel from "../components/CommandPanel"
import "../style/dashboard.css";

function Dashboard() {
  const [activeItem, setActiveItem] = useState("plant");
  const [selectedPlant, setSelectedPlant] = useState("PLANT-001");
  const [plants, setPlants] = useState([]);
  const [plantData, setPlantData] = useState(null);

  
  useEffect(() => {
    const fetchPlants = async () => {
      try {
        const response = await fetch("http://localhost:5000/api/plants");
        const data = await response.json();
        setPlants(data);
      } catch (error) {
        console.error("Erreur lors du chargement des plantes:", error);
      }
    };
    fetchPlants();
  }, []);

  useEffect(() => {
    const fetchPlantData = async () => {
      try {
        const response = await fetch(`http://localhost:5000/api/plants?id=${selectedPlant}`);
        const data = await response.json();
        setPlantData(data);
      } catch (error) {
        console.error("Erreur lors du chargement des données de la plante:", error);
      }
    };
    fetchPlantData();
  }, [selectedPlant]);

  const renderContent = () => {
    switch (activeItem) {
      case "plant":
        return (
          <div className="dashboard-content">
         
            <div className="plant-selector">
              <label>Plante: </label>
              <select
                onChange={(e) => setSelectedPlant(e.target.value)}
                value={selectedPlant}
              >
                {plants.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

           
            {plantData ? (
              <>
                <div className="measures-container">
                  <RealtimeMeasureCard
                    title="Humidité"
                    value={plantData.humidity + "%"}
                    icon="FaTint"
                    color="#4ECDC4"
                    backcolor="#DFF2EB"
                  />
                  <RealtimeMeasureCard
                    title="Température"
                    value={plantData.temperature + "°C"}
                    icon="FaThermometerHalf"
                    color="#FF6B6B"
                    backcolor="#FCEF91"
                  />
                  <RealtimeMeasureCard
                    title="Lumière"
                    value={plantData.light + " lux"}
                    icon="FaSun"
                    color="#FFD93D"
                    backcolor="#FCF9EA"
                  />
                </div>
          

                <div className="plant-overview">
              <PlantStatusCard
                humidity={plantData.humidity}
                temperature={plantData.temperature}
                light={plantData.light}
              />

            <CommandPanel plants={plants} selectedPlant={selectedPlant} />
            </div>


                <ChartsSection plantData={plantData} />
              </>
            ) : (
              <div className="loading-spinner">
                <CircularProgress size={32} color="success" />
              </div>
            )}
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
