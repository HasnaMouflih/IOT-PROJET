import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import Header from "./components/Header";
import HeroSection from "./components/HeroSection";
import FeaturesSection from "./components/FeaturesSection";
import Footer from "./components/Footer";
import AboutUs from "./components/AboutUs";
import ContactUs from "./components/ContactUs";
import Dashboard from "./components/Dashboard";


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
