import type { NextApiRequest, NextApiResponse } from "next";
import { getAllPlants } from "../../../services/plantServices";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === "GET") {
    const plants = await getAllPlants();
    return res.status(200).json(plants);
  }

  res.setHeader("Allow", ["GET"]);
  return res.status(405).end(`Method ${req.method} Not Allowed`);
}
