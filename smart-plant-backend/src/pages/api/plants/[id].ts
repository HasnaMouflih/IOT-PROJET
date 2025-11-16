import { mockPlants, Plant } from "../../../utils/mockData";

const USE_MOCK = true; // ⚡ Passe à false pour activer la connexion au cloud Flask
const FLASK_BASE_URL = "http://localhost:5000";

// 🔹 Fonction de normalisation du format cloud → format Plant
function normalizePlant(stateData: any, historyData: any[]): Plant {
  const history = (historyData || []).map((h) => ({
    time: new Date(h.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    temperature: h.temperature,
    humidity: h.humidity,
    light: h.lightLevel,
    soilMoisture: h.soilMoisture,
  }));

  return {
    id: stateData.deviceId,
    name: `Plant ${stateData.deviceId} 🌿`,
    emotion: stateData.emotion ?? "neutre",
    temperature: stateData.temperature,
    humidity: stateData.humidity,
    light: stateData.lightLevel,
    soilMoisture: stateData.soilMoisture,
    history,
  };
}

// 🔹 Récupérer une plante par ID
export async function getPlantById(id: string): Promise<Plant | null> {
  if (USE_MOCK) {
    return mockPlants[id] || null;
  }

  try {
    const [stateRes, historyRes] = await Promise.all([
      fetch(`${FLASK_BASE_URL}/plants/${id}/state`),
      fetch(`${FLASK_BASE_URL}/plants/${id}/history`),
    ]);

    if (!stateRes.ok || !historyRes.ok) {
      console.warn(`⚠️ Impossible de récupérer la plante ${id} depuis le cloud`);
      return null;
    }

    const stateData = await stateRes.json();
    const historyData = await historyRes.json();

    return normalizePlant(stateData, historyData);
  } catch (error) {
    console.error(`❌ Erreur lors de la récupération de la plante ${id}:`, error);
    return null;
  }
}
