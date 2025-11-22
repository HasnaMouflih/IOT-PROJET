import React, { useState, useEffect } from "react";
import axios from "axios";
import { DataGrid } from "@mui/x-data-grid";
import CircularProgress from "@mui/material/CircularProgress";

export default function PlantHistoryGrid({ selectedPlant }) {
  const [allHistory, setAllHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  // Charger l'historique quand selectedPlant change
  useEffect(() => {
    if (!selectedPlant) return;

    const loadHistory = async () => {
      setLoading(true);
      try {
        const res = await axios.get(
          `http://127.0.0.1:5000/plants/${selectedPlant}/history`
        );

        const history = res.data || [];

        const formatted = history.map((h, index) => ({
          id: index,
          plantName: selectedPlant,
          time: h.timestamp,
          humidity: h.humidity,
          temperature: h.temperature,
          light: h.lightLevel,
          soilMoisture: h.soilMoisture,
          emotion: h.emotion,
        }));

        setAllHistory(formatted);
      } catch (err) {
        console.error("Erreur récupération history:", err);
        setAllHistory([]);
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
  }, [selectedPlant]);

  const columns = [
    { field: "plantName", headerName: "Plante", flex: 1 },
    { field: "time", headerName: "Heure", flex: 1 },
    { field: "humidity", headerName: "Humidité", flex: 1 },
    { field: "temperature", headerName: "Température", flex: 1 },
    { field: "light", headerName: "Lumière", flex: 1 },
    { field: "soilMoisture", headerName: "Humidité du sol", flex: 1 },
    { field: "emotion", headerName: "Émotion", flex: 1 },
  ];

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", marginTop: 50 }}>
        <CircularProgress size={40} color="success" />
      </div>
    );
  }

  return (
    <div style={{ height: 500, width: "100%" }}>
      <DataGrid
        rows={allHistory}
        columns={columns}
        showToolbar
        pageSizeOptions={[5, 10, 20]}
        initialState={{
          pagination: { paginationModel: { pageSize: 10 } },
        }}
      />
    </div>
  );
}
