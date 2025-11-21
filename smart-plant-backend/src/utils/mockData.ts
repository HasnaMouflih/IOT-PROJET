export interface PlantHistory {
  time: string;
  humidity: number;
  temperature: number;
  light: number;
  soilMoisture: number;
  emotion: string;
}

export interface Plant {
  id: string;
  name: string;
  humidity: number;
  temperature: number;
  light: number;
  soilMoisture: number;
  emotion: string;
  history: PlantHistory[];
}

export const mockPlants: Record<string, Plant> = {
  "PLANT-001": {
    id: "PLANT-001",
    name: "Aloe Vera 🌿",
    humidity: 46,
    temperature: 26,
    light: 800,
    soilMoisture: 35,
    emotion: "neutre",
    history: [
      { time: "10h", humidity: 40, temperature: 22, light: 700, soilMoisture: 30, emotion: "neutre" },
      { time: "11h", humidity: 42, temperature: 23, light: 750, soilMoisture: 32, emotion: "neutre" },
      { time: "12h", humidity: 45, temperature: 25, light: 800, soilMoisture: 34, emotion: "neutre" },
      { time: "13h", humidity: 48, temperature: 27, light: 600, soilMoisture: 36, emotion: "neutre" },
    ],
  },

  "PLANT-002": {
    id: "PLANT-002",
    name: "Basil 🌱",
    humidity: 50,
    temperature: 24,
    light: 600,
    soilMoisture: 40,
    emotion: "neutre",
    history: [
      { time: "10h", humidity: 47, temperature: 22, light: 550, soilMoisture: 38, emotion: "neutre" },
      { time: "11h", humidity: 49, temperature: 23, light: 580, soilMoisture: 39, emotion: "neutre" },
      { time: "12h", humidity: 50, temperature: 24, light: 600, soilMoisture: 40, emotion: "neutre" },
    ],
  },

  "PLANT-003": {
    id: "PLANT-003",
    name: "Cactus 🌵",
    humidity: 25,
    temperature: 30,
    light: 1000,
    soilMoisture: 15,
    emotion: "neutre",
    history: [
      { time: "10h", humidity: 22, temperature: 29, light: 950, soilMoisture: 13, emotion: "neutre" },
      { time: "11h", humidity: 23, temperature: 30, light: 980, soilMoisture: 14, emotion: "neutre" },
      { time: "12h", humidity: 25, temperature: 31, light: 1000, soilMoisture: 15, emotion: "neutre" },
    ],
  },

  "PLANT-004": {
    id: "PLANT-004",
    name: "Peace Lily 🌸",
    humidity: 60,
    temperature: 23,
    light: 500,
    soilMoisture: 45,
    emotion: "neutre",
    history: [
      { time: "10h", humidity: 58, temperature: 22, light: 350, soilMoisture: 42, emotion: "neutre" },
      { time: "11h", humidity: 59, temperature: 23, light: 380, soilMoisture: 43, emotion: "neutre" },
      { time: "12h", humidity: 60, temperature: 23, light: 400, soilMoisture: 45, emotion: "neutre" },
    ],
  },
};

// 🧠 Fonction pour simuler une nouvelle donnée venant du cloud
export function handleNewData(data: any) {
  const plant = mockPlants[data.deviceId];
  if (plant) {
    // 🔄 Mettre à jour les valeurs en temps réel
    plant.humidity = data.humidity;
    plant.temperature = data.temperature;
    plant.light = data.lightLevel;
    plant.soilMoisture = data.soilMoisture;

    if (data.emotion) {
      plant.emotion = data.emotion;
    }

    // 🕒 Ajouter une nouvelle entrée dans l'historique
    plant.history.push({
      time: new Date(data.timestamp).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
      humidity: data.humidity,
      temperature: data.temperature,
      light: data.lightLevel,
      soilMoisture: data.soilMoisture,
      emotion: data.emotion ?? "neutre",
    });

    console.log("✅ Nouvelle donnée ajoutée :", plant);
  } else {
    console.warn("⚠️ Plante inconnue :", data.deviceId);
  }
}
