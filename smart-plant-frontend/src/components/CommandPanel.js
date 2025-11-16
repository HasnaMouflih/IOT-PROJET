import React, { useState } from "react";
import CircularProgress from "@mui/material/CircularProgress";
import WaterDropIcon from '@mui/icons-material/WaterDrop';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import DarkModeIcon from '@mui/icons-material/DarkMode';

import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";
import Slide from "@mui/material/Slide";

function CommandPanel({ plants, selectedPlant, commandStats, setCommandStats }) {
  const [loading, setLoading] = useState(false);
  const [alertMessage, setAlertMessage] = useState("");
  const [alertType, setAlertType] = useState(""); 
  const [open, setOpen] = useState(false);

  const handleClose = (_, reason) => {
    if (reason === "clickaway") return; // keep behavior consistent
    setOpen(false);
  };

  const sendCommand = async (command) => {
    setLoading(true);
    setAlertMessage("");
    setAlertType("");

    try {
      const res = await fetch("http://localhost:9000/api/commands", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plantId: selectedPlant, command }),
      });

      const data = await res.json();

      if (res.ok) {
        setAlertMessage(`Command "${command}" sent successfully!`);
        setAlertType("success");

        setCommandStats((prev) => ({
          ...prev,
          [command]: (prev[command] || 0) + 1,
        }));
      } else {
        setAlertMessage(data?.error || "Command failed");
        setAlertType("error");
      }
    } catch {
      setAlertMessage("Network error");
      setAlertType("error");
    } finally {
      setLoading(false);
      setOpen(true); // show popup
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

      {/* Centered popup Snackbar with Slide animation */}
      <Snackbar
        open={open}
        onClose={handleClose}
        autoHideDuration={3000}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        // keep the Snackbar element visible while the Slide animates the Alert
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
