import type { NextApiRequest, NextApiResponse } from "next";
import { sendCommandToPlant } from "../../../services/plantServices";
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === "POST") {
    const { plantId, command } = req.body as { plantId?: string; command?: string };

    if (!plantId || !command) {
      return res.status(400).json({ error: "Missing plantId or command" });
    }

    const result = await sendCommandToPlant(plantId, command);
    return res.status(200).json(result);
  }

  res.setHeader("Allow", ["POST"]);
  return res.status(405).end(`Method ${req.method} Not Allowed`);
}
