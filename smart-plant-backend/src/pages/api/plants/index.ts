import type { NextApiRequest, NextApiResponse } from "next";
import { getAllPlants, getPlantById } from "../../../services/plantServices";
import applyCors from "../../../utils/cors"; // 👈 make sure this path matches where you put the file

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // ✅ Enable CORS so your frontend at localhost:3001 can access the backend
  await applyCors(req, res);

  if (req.method === "GET") {
    const { id } = req.query;

  
    if (id && typeof id === "string") {
      const plant = await getPlantById(id);
      if (!plant) {
        return res.status(404).json({ error: "Plant not found" });
      }
      return res.status(200).json(plant);
    }

   
    const plants = await getAllPlants();
    return res.status(200).json(plants);
  }

  
  res.setHeader("Allow", ["GET"]);
  return res.status(405).end(`Method ${req.method} Not Allowed`);
}
