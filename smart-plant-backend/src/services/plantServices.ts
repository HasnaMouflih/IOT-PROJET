import { mockPlants, Plant } from "../utils/mockData";

// 🔹 Environment-controlled flags
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true";
const FLASK_BASE_URL = process.env.NEXT_PUBLIC_FLASK_BASE_URL || "http://localhost:5000";

// 🔹 Helper: normalize Flask data to frontend Plant type
function normalizePlantData(stateData: any, historyData: any[]): Plant {
  const history = (historyData || []).map((h) => ({
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

// 🔹 Get all plants
export async function getAllPlants(): Promise<Plant[]> {
  if (USE_MOCK) return Object.values(mockPlants);

  try {
    const plantIds = ["PLANT-001", "PLANT-002", "PLANT-003", "PLANT-004"];
    const plants = await Promise.all(
      plantIds.map(async (id) => {
        const [stateRes, historyRes] = await Promise.all([
          fetch(`${FLASK_BASE_URL}/plants/${id}/state`),
          fetch(`${FLASK_BASE_URL}/plants/${id}/history`),
        ]);

        if (!stateRes.ok || !historyRes.ok) {
          console.warn(`⚠️ Failed to fetch plant ${id} from cloud`);
          return null;
        }

        const stateData = await stateRes.json();
        const historyData = await historyRes.json();
        return normalizePlantData(stateData, historyData);
      })
    );

    // Filter out any nulls if some fetches failed
    return plants.filter((p): p is Plant => p !== null);
  } catch (error) {
    console.error("❌ Error fetching all plants from cloud:", error);
    return [];
  }
}

// 🔹 Get plant by ID
export async function getPlantById(id: string): Promise<Plant | null> {
  if (USE_MOCK) return mockPlants[id] || null;

  try {
    const [stateRes, historyRes] = await Promise.all([
      fetch(`${FLASK_BASE_URL}/plants/${id}/state`),
      fetch(`${FLASK_BASE_URL}/plants/${id}/history`),
    ]);

    if (!stateRes.ok || !historyRes.ok) {
      console.warn(`⚠️ Failed to fetch plant ${id} from cloud`);
      return null;
    }

    const stateData = await stateRes.json();
    const historyData = await historyRes.json();
    return normalizePlantData(stateData, historyData);
  } catch (error) {
    console.error(`❌ Error fetching plant ${id} from cloud:`, error);
    return null;
  }
}

// 🔹 Send command to a plant
export async function sendCommandToPlant(id: string, command: string) {
  if (USE_MOCK) {
    console.log(`Sending command '${command}' to plant ${id} (mock)`);
    return { success: true, command, timestamp: new Date().toISOString() };
  }

  try {
    const res = await fetch(`${FLASK_BASE_URL}/plants/${id}/command`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command }),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Failed to send command: ${res.status} ${text}`);
    }

    return res.json();
  } catch (error) {
    console.error(`❌ Error sending command to plant ${id}:`, error);
    return { success: false, error: (error as Error).message };
  }
}
