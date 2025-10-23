import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import Header from "./components/Header";
import HeroSection from "./components/HeroSection";
import FeaturesSection from "./components/FeaturesSection";
import Footer from "./components/Footer";
import AboutUs from "./components/AboutUs";
import ContactUs from "./components/ContactUs";

// Composant qui récupère et affiche les émotions
function EmotionsTable() {
  const [plants, setPlants] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:5001/api/emotions")
      .then((res) => res.json())
      .then((data) => setPlants(data))
      .catch((err) => console.error("Erreur de chargement:", err));
  }, []);

  if (plants.length === 0) {
    return <p>Chargement des émotions...</p>;
  }

  return (
    <div className="min-h-screen bg-green-50 flex flex-col items-center p-6">
      <h2 className="text-2xl font-bold text-green-800 mb-4">
        🌿 Tableau des émotions - Smart Plant
      </h2>

      <table className="bg-white rounded-lg shadow-md">
        <thead>
          <tr className="bg-green-100">
            <th className="px-4 py-2">ID</th>
            <th className="px-4 py-2">Température</th>
            <th className="px-4 py-2">Humidité</th>
            <th className="px-4 py-2">Lumière</th>
            <th className="px-4 py-2">Émotion</th>
            <th className="px-4 py-2">Action</th>
          </tr>
        </thead>
        <tbody>
          {plants.map((p, i) => (
            <tr key={i} className="text-center hover:bg-green-50">
              <td className="border px-4 py-2">{p.deviceId}</td>
              <td className="border px-4 py-2">{p.temperature}°C</td>
              <td className="border px-4 py-2">{p.humidity}%</td>
              <td className="border px-4 py-2">{p.lightLevel}</td>
              <td className="border px-4 py-2">{p.emotion}</td>
              <td className="border px-4 py-2">
                {p.action === "WATER" ? "💧 Arroser" : "✔️ Aucune"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Wrapper pour gérer le footer conditionnel
function AppWrapper() {
  const location = useLocation();
  const hideFooter = location.pathname === "/dashboard";

  return (
    <>
      <Header />
      <Routes>
        {/* Page d'accueil */}
        <Route
          path="/"
          element={
            <>
              <HeroSection />
              <FeaturesSection />
              <EmotionsTable /> {/* Ajout du tableau sur la page d’accueil */}
            </>
          }
        />

        {/* Dashboard */}
        <Route path="/dashboard" element={<EmotionsTable />} />

        {/* À propos de nous */}
        <Route path="/about" element={<AboutUs />} />

        {/* Contact */}
        <Route path="/contact" element={<ContactUs />} />
      </Routes>
      {!hideFooter && <Footer />}
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppWrapper />
    </BrowserRouter>
  );
}

export default App;
