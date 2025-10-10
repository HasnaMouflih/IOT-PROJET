import React from "react";
import * as FaIcons from "react-icons/fa";

function RealtimeMeasureCard({ title, value, icon, color ,backcolor }) {
  const IconComponent = FaIcons[icon];

  return (
    <div className="card measure-card"  style={{ background: `linear-gradient(145deg, ${backcolor}, #ffffff)` }}>
      {IconComponent && <IconComponent size={40} color={color} />}
      <h3>{title}</h3>
      <p>{value}</p>
    </div>
  );
}

export default RealtimeMeasureCard;
