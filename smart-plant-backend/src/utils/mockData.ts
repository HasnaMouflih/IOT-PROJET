export interface PlantHistory {
  time: string;
  humidity: number;
  temperature: number;
  light: number;
}

export interface Plant {
  id: string;
  name: string;
  humidity: number;
  temperature: number;
  light: number;
  history: PlantHistory[];
}

export const mockPlants: Record<string, Plant> = {
  "PLANT-001": {
    id: "PLANT-001",
    name: "Aloe Vera 🌿",
    humidity: 45,
    temperature: 25,
    light: 800,
    history: [
      { time: "10h", humidity: 40, temperature: 22, light: 700 },
      { time: "11h", humidity: 42, temperature: 23, light: 750 },
      { time: "12h", humidity: 45, temperature: 25, light: 800 },
      { time: "13h", humidity: 48, temperature: 27, light: 850 },
    ],
  },
  "PLANT-002": {
    id: "PLANT-002",
    name: "Basil 🌱",
    humidity: 50,
    temperature: 24,
    light: 600,
    history: [
      { time: "10h", humidity: 47, temperature: 22, light: 550 },
      { time: "11h", humidity: 49, temperature: 23, light: 580 },
      { time: "12h", humidity: 50, temperature: 24, light: 600 },
    ],
  },
  "PLANT-003": {
    id: "PLANT-003",
    name: "Cactus 🌵",
    humidity: 25,
    temperature: 30,
    light: 1000,
    history: [
      { time: "10h", humidity: 22, temperature: 29, light: 950 },
      { time: "11h", humidity: 23, temperature: 30, light: 980 },
      { time: "12h", humidity: 25, temperature: 31, light: 1000 },
    ],
  },
  "PLANT-004": {
    id: "PLANT-004",
    name: "Peace Lily 🌸",
    humidity: 60,
    temperature: 23,
    light: 400,
    history: [
      { time: "10h", humidity: 58, temperature: 22, light: 350 },
      { time: "11h", humidity: 59, temperature: 23, light: 380 },
      { time: "12h", humidity: 60, temperature: 23, light: 400 },
    ],
  },
};
