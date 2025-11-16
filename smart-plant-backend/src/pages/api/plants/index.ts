import type { NextApiRequest, NextApiResponse } from "next";
import applyCors from "../../../utils/cors";
import { Plant, mockPlants } from "../../../utils/mockData";

const USE_MOCK = true; // ⚡ Passe à false pour activer le cloud
const FLASK_BASE_URL = "http://localhost:5000";

type ResponseData = Plant | Plant[] | { error: string };

// 🔹 Fonction de normalisation (pour convertir les données Flask → format Plant)
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

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ResponseData>
) {
  await applyCors(req, res);

  if (req.method === "GET") {
    const { id } = req.query;

    // --- 🔸 MODE MOCK ---
    if (USE_MOCK) {
      if (id && typeof id === "string") {
        const plant = mockPlants[id];
        if (!plant) return res.status(404).json({ error: "Plant not found" });
        return res.status(200).json(plant);
      }
      return res.status(200).json(Object.values(mockPlants));
    }

    // --- 🔸 MODE CLOUD ---
    try {
      if (id && typeof id === "string") {
        // Récupération d'une seule plante
        const [stateRes, historyRes] = await Promise.all([
          fetch(`${FLASK_BASE_URL}/plants/${id}/state`),
          fetch(`${FLASK_BASE_URL}/plants/${id}/history`),
        ]);

        if (!stateRes.ok || !historyRes.ok)
          return res.status(404).json({ error: "Plant not found in cloud" });

        const stateData = await stateRes.json();
        const historyData = await historyRes.json();
        return res.status(200).json(normalizePlant(stateData, historyData));
      }

      // Récupération de toutes les plantes
      const plantIds = ["PLANT-001", "PLANT-002", "PLANT-003", "PLANT-004"];
      const plants = await Promise.all(
        plantIds.map(async (pid) => {
          const [stateRes, historyRes] = await Promise.all([
            fetch(`${FLASK_BASE_URL}/plants/${pid}/state`),
            fetch(`${FLASK_BASE_URL}/plants/${pid}/history`),
          ]);
          const stateData = await stateRes.json();
          const historyData = await historyRes.json();
          return normalizePlant(stateData, historyData);
        })
      );

      return res.status(200).json(plants);
    } catch (err) {
      console.error("❌ Error fetching plants from cloud:", err);
      return res.status(500).json({ error: "Failed to fetch plants from cloud" });
    }
  }

  res.setHeader("Allow", ["GET"]);
  return res.status(405).end(`Method ${req.method} Not Allowed`);
}
