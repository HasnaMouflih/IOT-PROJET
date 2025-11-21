import React, { useState, useEffect } from "react";
import { DataGrid } from "@mui/x-data-grid";
import CircularProgress from "@mui/material/CircularProgress";
import { getPlantsList, getPlantState } from "../services/PlantServices.js"; // ton service mock

export default function PlantHistoryGrid() {
  const [plants, setPlants] = useState([]);
  const [selectedPlant, setSelectedPlant] = useState("");
  const [allHistory, setAllHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadPlants = async () => {
      setLoading(true);
      try {
        const list = await getPlantsList();
        setPlants(list);

        if (list.length > 0) {
          const defaultPlant = list[0].id;
          setSelectedPlant(defaultPlant);
          const plantState = await getPlantState(defaultPlant);
          const historyList = plantState.history.map((h, index) => ({
            id: index,
            plantName: `Plante ${defaultPlant}`,
            time: h.timestamp,
            humidity: h.humidity,
            temperature: h.temperature,
            light: h.light,
            soilMoisture: h.soilMoisture,
            emotion: h.emotion,
          }));
          setAllHistory(historyList);
        }
      } catch (err) {
        console.error("Erreur:", err);
      } finally {
        setLoading(false);
      }
    };

    loadPlants();
  }, []);

  const handleChangePlant = async (e) => {
    const deviceId = e.target.value;
    setSelectedPlant(deviceId);
    setLoading(true);
    try {
      const plantState = await getPlantState(deviceId);
      const historyList = plantState.history.map((h, index) => ({
        id: index,
        plantName: `Plante ${deviceId}`,
        time: h.timestamp,
        humidity: h.humidity,
        temperature: h.temperature,
        light: h.light,
        soilMoisture: h.soilMoisture,
        emotion: h.emotion,
      }));
      setAllHistory(historyList);
    } catch (err) {
      console.error(err);
      setAllHistory([]);
    } finally {
      setLoading(false);
    }
  };

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
      {/* Selecteur de plante */}
      <div style={{ marginBottom: 16 }}>
        <label>Choisir une plante : </label>
        <select value={selectedPlant} onChange={handleChangePlant}>
          {plants.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </div>

      {/* DataGrid avec toolbar, recherche, impression et téléchargement */}
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
