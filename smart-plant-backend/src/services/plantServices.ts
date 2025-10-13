import { mockPlants, Plant } from "../utils/mockData";

export async function getAllPlants(): Promise<Plant[]> {
  return Object.values(mockPlants);
}

export async function getPlantById(id: string): Promise<Plant | null> {
  return mockPlants[id] || null;
}

export async function sendCommandToPlant(
  id: string,
  command: string
): Promise<{ success: boolean; command: string; timestamp: string }> {
  console.log(`Sending command '${command}' to plant ${id}`);
  // Simulate delay and return success
  return {
    success: true,
    command,
    timestamp: new Date().toISOString(),
  };
}
