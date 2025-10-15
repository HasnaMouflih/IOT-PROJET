import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
} from "recharts";
import "../style/dashboard.css";


function ChartsSection({ plantData }) {
  return (
    <div className="charts-section">
      <h2>📈 Suivi des mesures</h2>
      <div className="charts-grid">
        <div className="chart-card">
          <h3>Évolution de l’humidité</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={plantData.history}>
                           <defs>
                <linearGradient id="colorHum" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#4ECDC4" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#4ECDC4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="time" />
              <YAxis />
              <CartesianGrid strokeDasharray="3 3" />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="humidity"
                stroke="#4ECDC4"
                fillOpacity={1}
                fill="url(#colorHum)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Évolution de la température</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={plantData.history}>
              <XAxis dataKey="time" />
              <YAxis />
              <CartesianGrid strokeDasharray="3 3" />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="temperature"
                stroke="#FF6B6B"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Intensité lumineuse</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={plantData.history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="light" fill="#FFD93D" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}


export default ChartsSection;
