
import "../style/dashboard.css";
import { LineChart } from "@mui/x-charts/LineChart";
import { BarChart } from '@mui/x-charts/BarChart';
import Stack from '@mui/material/Stack';
import { Gauge } from '@mui/x-charts/Gauge';
import { PieChart } from '@mui/x-charts/PieChart';

function ChartsSection({ plantData , commandStats}) {
      if (!plantData?.history) return null;
  
    const pieData = [
      { id: 0, value: commandStats.water, label: 'Water' },
      { id: 1, value: commandStats.light_on, label: 'Light ON' },
      { id: 2, value: commandStats.light_off, label: 'Light OFF' }
    ];
  const xAxisData = plantData.history.map((h) => h.time);
  const series = [
    {
      data: plantData.history.map((h) => h.humidity),
      label: "Humidité (%)",
      stroke: "#4ECDC4",
      area: false,        // area under the line
      fillOpacity: 0.3,
      fill: "#4ECDC4",
    },
    {
      data: plantData.history.map((h) => h.temperature),
      label: "Température (°C)",
      stroke: "#FF6B6B",
      strokeWidth: 2,
    },
   
  ];

  const lightdata = [
      {
      data: plantData.history.map((h) => h.light),
      label: "luminosite (°C)",
      stroke: "#FFD93D",
      strokeWidth: 2,
    },

   
  ];

  const soilMoisturedata = [
      {
      data: plantData.history.map((h) => h.soilMoisture),
      label: "Humidité du sol (%)",
      stroke: "#FFD93D",
      strokeWidth: 2,
    },

   
  ];
 
  return (
    <div className="charts-section">
      <div className="charts-grid">
        <div className="chart-card" style={{ width: 400, height: 300, padding: 20 }}>
            <h3>Évolution de l’humidité et de la température</h3>
            <div style={{ width: "100%", height: "100%" }}>
              <LineChart
                width={400}   // match the parent width
                height={250}  // slightly smaller than parent to leave space for title
                xAxis={[{ data: xAxisData, scaleType: "point" }]}
                series={series}
              />
            </div>
        </div>
        <div className="chart-card" style={{ width: 400, height: 300, padding: 20 }}>
            <h3>Intensité lumineuse</h3>
              <div style={{ width: "100%", height: "100%" }}>
                <LineChart
                  width={400}   
                  height={250}  
                  xAxis={[{ data: xAxisData, scaleType: "point" }]}
                  series={lightdata}
                />
              </div>
        </div>

        <div className="chart-card" style={{ width: 400, height: 300, padding: 20 }}>
            <h3>l'humidité du sol</h3>
              <div style={{ width: "100%", height: "100%" }}>
                <BarChart
                  xAxis={[{ data: xAxisData, scaleType: "band" }]}
                  series={soilMoisturedata}
                   width={400}   
                  height={250}
                />
           
       
              </div>
        </div>
        <div className="chart-card" style={{ width: 400, height: 300, padding: 20 }}>
                 <h3>Command Usage</h3>
                <PieChart
                  series={[
                    {
                      data: pieData,
                      innerRadius: 30,
                      outerRadius: 100,
                      paddingAngle: 5,
                      cornerRadius: 5,
                      startAngle: -45,
                      endAngle: 225,
                      cx: 150,
                      cy: 150,
                    }
                  ]}
                  width={300}
                  height={300}
                />
         </div>


      </div>
    </div>
  );
}


export default ChartsSection;
