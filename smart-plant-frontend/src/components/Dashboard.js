import React, { useState } from "react";
import Sidebar from "./Sidebar";
import PlantStateCards from "./PlantStateCards";
import "../style/dashboard.css";

function Dashboard() {
  const [activeTab, setActiveTab] = useState("etat");
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleTabClick = (tab) => {
    setActiveTab(tab);
  };

  return (
    <div className="dashboard-container">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={handleTabClick}
        isOpen={sidebarOpen}
        setIsOpen={setSidebarOpen}
      />

      <main className={`dashboard-main ${sidebarOpen ? "" : "collapsed"}`}>
        <button
          className="toggle-btn"
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          ☰
        </button>

        <h1>Tableau de bord SmartPlant 🌿</h1>

        {activeTab === "etat" && (
          <PlantStateCards
            humidity={45}
            temperature={25}
            light={800}
            plantMood="heureuse"
            aiMessage="La plante aura besoin d’eau dans 2 heures 💧"
          />
        )}

        {activeTab === "historique" && (
          <section className="card">
            <h2>Historique des mesures</h2>
            <p>Graphiques et tableaux d’historique ici.</p>
          </section>
        )}

        {activeTab === "parametres" && (
          <section className="card">
            <h2>Paramètres</h2>
            <p>Modifier fréquence d’envoi, unités, ajouter/supprimer plante...</p>
          </section>
        )}
      </main>
    </div>
  );
}

export default Dashboard;
