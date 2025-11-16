import { mockPlants, Plant } from "../utils/mockData";

const USE_MOCK = true; // ⚡ passe à false quand le cloud sera dispo
const FLASK_BASE_URL = "http://localhost:5000";

export async function getAllPlants(): Promise<Plant[]> {
  if (USE_MOCK) return Object.values(mockPlants);

  const plantIds = ["PLANT-001", "PLANT-002", "PLANT-003", "PLANT-004"];
  const plants = await Promise.all(
    plantIds.map(async (id) => {
      const stateRes = await fetch(`${FLASK_BASE_URL}/plants/${id}/state`);
      const historyRes = await fetch(`${FLASK_BASE_URL}/plants/${id}/history`);
      const stateData = await stateRes.json();
      const historyData = await historyRes.json();

      const history = historyData.map((h: any) => ({
        time: new Date(h.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        temperature: h.temperature,
        humidity: h.humidity,
        light: h.lightLevel,
        soilMoisture: h.soilMoisture,
      }));

      return {
        id: stateData.deviceId,
        name: `Plant ${stateData.deviceId}`,
        temperature: stateData.temperature,
        humidity: stateData.humidity,
        light: stateData.lightLevel,
        soilMoisture: stateData.soilMoisture,
        history,
      };
    })
  );
  return plants;
}

export async function getPlantById(id: string): Promise<Plant | null> {
  if (USE_MOCK) return mockPlants[id] || null;

  const stateRes = await fetch(`${FLASK_BASE_URL}/plants/${id}/state`);
  const historyRes = await fetch(`${FLASK_BASE_URL}/plants/${id}/history`);
  const stateData = await stateRes.json();
  const historyData = await historyRes.json();

  const history = historyData.map((h: any) => ({
    time: new Date(h.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    temperature: h.temperature,
    humidity: h.humidity,
    light: h.lightLevel,
    soilMoisture: h.soilMoisture,
  }));

  return {
    id: stateData.deviceId,
    name: `Plant ${stateData.deviceId}`,
    temperature: stateData.temperature,
    humidity: stateData.humidity,
    light: stateData.lightLevel,
    soilMoisture: stateData.soilMoisture,
    history,
  };
}

export async function sendCommandToPlant(id: string, command: string) {
  if (USE_MOCK) {
    console.log(`Sending command '${command}' to plant ${id} (mock)`);
    return { success: true, command, timestamp: new Date().toISOString() };
  }

  const res = await fetch(`${FLASK_BASE_URL}/plants/${id}/command`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ command }),
  });
  return res.json();
}
