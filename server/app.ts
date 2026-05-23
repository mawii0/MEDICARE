import express from "express";
import cors from "cors";
import authRoutes from "./routes/auth";
import chatRoutes from "./routes/chat";
import pharmacyRoutes from "./routes/pharmacy";
import historyRoutes from "./routes/history";
import savedMedsRoutes from "./routes/saved-meds";

const app = express();

app.use(cors());
app.use(express.json());

app.get("/api/health", (_req, res) => {
  res.json({ status: "ok", service: "MediGuide API" });
});

// Helpful root page for browser visits
app.get("/", (_req, res) => {
  res.send(
    "<!doctype html><html><head><meta charset=\"utf-8\"><title>MediGuide API</title></head><body><h1>MediGuide API</h1><p>API is running. Try <a href=\"/api/health\">/api/health</a>.</p></body></html>"
  );
});

app.use("/api/auth", authRoutes);
app.use("/api/chat", chatRoutes);
app.use("/api/pharmacy", pharmacyRoutes);
app.use("/api/history", historyRoutes);
app.use("/api/saved-meds", savedMedsRoutes);

export default app;
