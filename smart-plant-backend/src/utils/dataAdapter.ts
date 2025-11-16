// utils/dataAdapter.ts

import { mockPlants } from "./mockData";

export function adaptCloudDataToPlant(cloudData) {
  const { deviceId, humidity, temperature, lightLevel, soilMoisture, timestamp, emotion } = cloudData;

  return {
    id: deviceId,
    humidity,
    temperature,
    light: lightLevel,
    soilMoisture,
    emotion: emotion ?? "neutre",
    time: new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  };
}
