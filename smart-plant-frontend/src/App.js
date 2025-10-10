import React from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import Header from "./components/Header";
import HeroSection from "./components/HeroSection";
import FeaturesSection from "./components/FeaturesSection";
import Footer from "./components/Footer";
import Dashboard from "./components/Dashboard";
import AboutUs from "./components/AboutUs";       // Nouvelle page
import ContactUs from "./components/ContactUs";   // Nouvelle page

// Wrapper pour gérer le footer conditionnel
function AppWrapper() {
  const location = useLocation();

  // cacher le footer uniquement sur le dashboard
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
            </>
          }
        />

        {/* Dashboard */}
        <Route path="/dashboard" element={<Dashboard />} />

        {/* À propos de nous */}
        <Route path="/about" element={<AboutUs />} />

        {/* Contact */}
        <Route path="/contact" element={<ContactUs />} />
      </Routes>

      {/* Affiche le footer uniquement si hideFooter est false */}
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
