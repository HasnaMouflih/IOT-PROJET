import type { NextApiRequest, NextApiResponse } from "next";
import { sendCommandToPlant } from "../../../services/plantServices";
import applyCors from "../../../utils/cors";

// Type pour la requête POST
interface CommandRequest {
  plantId: string;
  command: string;
}

// Type pour la réponse
interface CommandResponse {
  success: boolean;
  message?: string;
  error?: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<CommandResponse>
) {
  // Appliquer CORS
  await applyCors(req, res);

  if (req.method !== "POST") {
    res.setHeader("Allow", ["POST"]);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  const { plantId, command } = req.body as Partial<CommandRequest>;

  if (!plantId || !command) {
    return res
      .status(400)
      .json({ success: false, error: "Missing plantId or command" });
  }

  try {
    // Envoi de la commande (mock ou cloud)
    const result = await sendCommandToPlant(plantId, command);

    // Normaliser le message pour le front
    return res.status(200).json({
      success: result.success ?? true,
      message: result.message ?? `Command '${command}' sent to ${plantId}`,
      error: result.success === false ? result.error : undefined,
    });
  } catch (error: any) {
    console.error(`❌ Error sending command to ${plantId}:`, error);
    return res
      .status(500)
      .json({ success: false, error: error.message || "Unknown error" });
  }
}
