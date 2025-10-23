import React from "react";

function SensorCard({ icon, label, value }) {
  return (
    <div className="sensor-card">
      <div className="icon">{icon}</div>
      <h4>{label}</h4>
      <p className="value">{value}</p>
    </div>
  );
}

export default SensorCard;
