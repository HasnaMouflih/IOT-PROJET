import "../style/dashboard.css";
import { LineChart } from "@mui/x-charts/LineChart";
import { BarChart } from '@mui/x-charts/BarChart';
import { PieChart } from '@mui/x-charts/PieChart';

function ChartsSection({ plantData, commandStats }) {
  if (!plantData?.history || plantData.history.length === 0) return null;

  // 🟢 Préparer les données
  const xAxisData = plantData.history.map(h => h.time ?? "-");

  const seriesHumidityTemp = [
    {
      data: plantData.history.map(h => h.humidity ?? 0),
      label: "Humidité (%)",
      stroke: "#4ECDC4",
      area: false,
      fillOpacity: 0.3,
      fill: "#4ECDC4",
    },
    {
      data: plantData.history.map(h => h.temperature ?? 0),
      label: "Température (°C)",
      stroke: "#FF6B6B",
      strokeWidth: 2,
    }
  ];

  const seriesLight = [
    {
      data: plantData.history.map(h => h.light ?? 0),
      label: "Luminosité (lux)",
      stroke: "#FFD93D",
      strokeWidth: 2,
    }
  ];

  const seriesSoil = [
    {
      data: plantData.history.map(h => h.soilMoisture ?? 0),
      label: "Humidité du sol (%)",
      stroke: "#8D6E63",
      strokeWidth: 2,
    }
  ];

  const pieData = [
    { id: 0, value: commandStats.water ?? 0, label: 'Water' },
    { id: 1, value: commandStats.light_on ?? 0, label: 'Light ON' },
    { id: 2, value: commandStats.light_off ?? 0, label: 'Light OFF' }
  ];

  return (
    <div className="charts-section">
      <div className="charts-grid">

        <div className="chart-card" style={{ width: 400, height: 300, padding: 20 }}>
          <h3>Évolution de l’humidité et de la température</h3>
          <div style={{ width: "100%", height: "100%" }}>
            <LineChart
              width={400}
              height={250}
              xAxis={[{ data: xAxisData, scaleType: "point" }]}
              series={seriesHumidityTemp}
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
              series={seriesLight}
            />
          </div>
        </div>

        <div className="chart-card" style={{ width: 400, height: 300, padding: 20 }}>
          <h3>Humidité du sol</h3>
          <div style={{ width: "100%", height: "100%" }}>
            <BarChart
              xAxis={[{ data: xAxisData, scaleType: "band" }]}
              series={seriesSoil}
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
