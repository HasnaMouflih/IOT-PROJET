import React, { useEffect, useState } from "react";
import axios from "axios";
import "../style/dashboard.css";

import { LineChart } from "@mui/x-charts/LineChart";
import { BarChart } from "@mui/x-charts/BarChart";
import { PieChart } from "@mui/x-charts/PieChart";

import { getDatabase, ref, onValue } from "firebase/database";

const API_BASE_URL = "http://localhost:5000";

function ChartsSection({ plantId }) {
  const [history, setHistory] = useState([]);
  const [commandStats, setCommandStats] = useState({
    water: 0,
    light_on: 0,
    light_off: 0,
  });

  // 🔹 Fetch plant history from Flask
  useEffect(() => {
    if (!plantId) return;

    const fetchHistory = async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/plants/${plantId}/history`);

        const cleaned = (res.data || []).map((h) => ({
          humidity: h.humidity ?? 0,
          temperature: h.temperature ?? 0,
          light: h.lightLevel ?? h.light ?? 0,
          soilMoisture: h.soilMoisture ?? 0,
          time: h.timestamp ?? h.time ?? "-",
        }));

        setHistory(cleaned);
      } catch (error) {
        console.error("Erreur lors du chargement de l'historique :", error);
      }
    };

    fetchHistory();
  }, [plantId]);

  // 🔹 Fetch command stats from Firebase
useEffect(() => {
  if (!plantId) return;

  const db = getDatabase();
  const commandsRef = ref(db, `plants/${plantId}/commands`);

  const unsubscribe = onValue(commandsRef, (snapshot) => {
    const commands = snapshot.val() || {};
    const stats = { water: 0, light_on: 0, light_off: 0 };

    Object.values(commands).forEach((cmd) => {
      const type = (cmd.command || "").toLowerCase().trim(); // <-- ici on utilise 'command'
      
      if (type === "water") stats.water += 1;
      if (type === "light_on") stats.light_on += 1;
      if (type === "light_off") stats.light_off += 1;
    });

    console.log("Stats calculées:", stats);
    setCommandStats(stats);
  });

  return () => unsubscribe();
}, [plantId]);



  if (!history || history.length === 0) return null;

  // 🔹 Graph data
  const xAxisData = history.map((h) => h.time);

  const seriesHumidityTemp = [
    { data: history.map((h) => h.humidity), label: "Humidité (%)", stroke: "#4ECDC4" },
    { data: history.map((h) => h.temperature), label: "Température (°C)", stroke: "#FF6B6B" },
  ];

  const seriesLight = [
    { data: history.map((h) => h.light), label: "Luminosité (lux)", stroke: "#FFD93D" },
  ];

  const seriesSoil = [
    { data: history.map((h) => h.soilMoisture), label: "Humidité du sol (%)", stroke: "#8D6E63" },
  ];

  const pieData = [
    { id: 0, value: commandStats.water, label: "Water" },
    { id: 1, value: commandStats.light_on, label: "Light ON" },
    { id: 2, value: commandStats.light_off, label: "Light OFF" },
  ];

  return (
    <div className="charts-section">
      <div className="charts-grid">

        <div className="chart-card" style={{ width: 400, height: 300, padding: 20 }}>
          <h3>Évolution de l’humidité et de la température</h3>
          <LineChart width={400} height={250} xAxis={[{ data: xAxisData, scaleType: "point" }]} series={seriesHumidityTemp} />
        </div>

        <div className="chart-card" style={{ width: 400, height: 300, padding: 20 }}>
          <h3>Intensité lumineuse</h3>
          <LineChart width={400} height={250} xAxis={[{ data: xAxisData, scaleType: "point" }]} series={seriesLight} />
        </div>

        <div className="chart-card" style={{ width: 400, height: 300, padding: 20 }}>
          <h3>Humidité du sol</h3>
          <BarChart width={400} height={250} xAxis={[{ data: xAxisData, scaleType: "band" }]} series={seriesSoil} />
        </div>

        <div className="chart-card" style={{ width: 400, height: 300, padding: 20 }}>
          <h3>Command Usage</h3>
          <PieChart
            width={300}
            height={300}
            series={[{
              data: pieData,
              innerRadius: 30,
              outerRadius: 100,
              paddingAngle: 5,
              cornerRadius: 5,
            }]}
          />
        </div>
      </div>
    </div>
  );
}

export default ChartsSection;
