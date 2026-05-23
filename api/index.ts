import type { VercelRequest, VercelResponse } from "@vercel/node";
import app from "../server/app";

export const config = {
  api: {
    bodyParser: false,
  },
};

export default function handler(req: VercelRequest, res: VercelResponse) {
  app(req, res);
}
