import type { NextApiRequest, NextApiResponse } from "next";
import { getPlantById } from "../../../services/plantServices";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { id } = req.query as { id?: string };

  if (req.method === "GET") {
    const plant = await getPlantById(id as string);
    if (!plant) {
      return res.status(404).json({ error: "Plant not found" });
    }
    return res.status(200).json(plant);
  }

  res.setHeader("Allow", ["GET"]);
  return res.status(405).end(`Method ${req.method} Not Allowed`);
}
