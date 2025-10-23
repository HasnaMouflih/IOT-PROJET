import React, { useState } from "react";
import CircularProgress from "@mui/material/CircularProgress";

function CommandPanel({ plants, selectedPlant }) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const sendCommand = async (command) => {
    setLoading(true);
    setMessage("");
    try {
        const res = await fetch("http://localhost:5000/api/commands", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plantId: selectedPlant, command }),
      });
      const data = await res.json();
      setMessage(res.ok ? `Command "${command}" sent!` : `Error: ${data.error}`);
    } catch {
      setMessage("Network error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="command-panel-card">
      <h3>Contrôles de la plante</h3>
      <div className="command-buttons">
        <button onClick={() => sendCommand("water")}>Water</button>
        <button onClick={() => sendCommand("light_on")}>Light On</button>
        <button onClick={() => sendCommand("light_off")}>Light Off</button>
      </div>
          {loading && (
      <div className="loading-spinner">
        <CircularProgress size={32} color="success" />
      </div>
    )}

      {message && <p>{message}</p>}
    </div>

  );
}

export default CommandPanel;
