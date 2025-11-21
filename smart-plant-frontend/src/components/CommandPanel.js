import React, { useState, useEffect } from "react";
import CircularProgress from "@mui/material/CircularProgress";
import WaterDropIcon from '@mui/icons-material/WaterDrop';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";
import Slide from "@mui/material/Slide";

import { mockPlants } from "../data/mockPlants";

function CommandPanel({ selectedPlant, commandStats, setCommandStats }) {
  const [loading, setLoading] = useState(false);
  const [alertMessage, setAlertMessage] = useState("");
  const [alertType, setAlertType] = useState("");
  const [open, setOpen] = useState(false);

  const handleClose = (_, reason) => {
    if (reason === "clickaway") return;
    setOpen(false);
  };

  /* -------------------------------------------------------
      🔥 1. WebSocket qui reçoit les commandes AUTOMATIQUES
  -------------------------------------------------------- */
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:9000/ws/commands");

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Exemple attendu :
        // { plantId: "PLANT-001", emotion: "assoiffé", command: "WATER:3000" }

        if (data.plantId === selectedPlant) {
          setAlertMessage(
            `⚠️ Plante ${data.plantId} est ${data.emotion} → Commande auto: ${data.command}`
          );
          setAlertType("info");
          setOpen(true);
        }
      } catch (err) {
        console.error("Message WS invalide :", err);
      }
    };

    return () => ws.close();
  }, [selectedPlant]);

  /* -------------------------------------------------------
      🔥 2. Commande manuelle (toujours mockée pour l'instant)
  -------------------------------------------------------- */
  const sendCommand = async (command) => {
    setLoading(true);
    setAlertMessage("");
    setAlertType("");

    try {
      // simuler un envoi local mock
      if (!mockPlants[selectedPlant]) throw new Error("Plante inconnue");

      // Mettre à jour les stats
      setCommandStats((prev) => ({
        ...prev,
        [command]: (prev[command] || 0) + 1,
      }));

      setAlertMessage(`Commande "${command}" envoyée !`);
      setAlertType("success");

      /* -------------------------------------------------------
            📌 C’EST ICI que tu ajouteras le POST plus tard :
            await fetch(`/plants/${selectedPlant}/command`, { ... })
      -------------------------------------------------------- */

    } catch (err) {
      setAlertMessage(err.message || "Erreur lors de la commande");
      setAlertType("error");
    } finally {
      setLoading(false);
      setOpen(true);
    }
  };

  return (
    <div className="command-panel-card">
      <h3>Contrôles de la plante</h3>

      <div className="command-buttons">
        <button
          className="btn water"
          onClick={() => sendCommand("water")}
          disabled={loading}
        >
          <WaterDropIcon style={{ marginRight: 6 }} /> Water
        </button>

        <button
          className="btn light-on"
          onClick={() => sendCommand("light_on")}
          disabled={loading}
        >
          <LightbulbIcon style={{ marginRight: 6 }} /> Light ON
        </button>

        <button
          className="btn light-off"
          onClick={() => sendCommand("light_off")}
          disabled={loading}
        >
          <DarkModeIcon style={{ marginRight: 6 }} /> Light OFF
        </button>
      </div>

      {loading && (
        <div className="loading-spinner">
          <CircularProgress size={32} color="success" />
        </div>
      )}

      <Snackbar
        open={open}
        onClose={handleClose}
        autoHideDuration={3000}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Slide direction="down" in={open}>
          <Alert
            onClose={handleClose}
            severity={alertType || "info"}
            variant="filled"
            sx={{ minWidth: 300, textAlign: "center" }}
          >
            {alertMessage}
          </Alert>
        </Slide>
      </Snackbar>
    </div>
  );
}

export default CommandPanel;
