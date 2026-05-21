import { Router, Response } from "express";
import db from "../db";
import { authMiddleware, AuthRequest } from "../middleware/auth";

const router = Router();

router.use(authMiddleware);

router.get("/", (req: AuthRequest, res: Response) => {
  const rows = db
    .prepare(
      `SELECT id, name, use_text as "use", icon, stock,
              effects, side_effects, dosage, frequency, timing, duration, warnings
       FROM saved_meds WHERE user_id = ? ORDER BY created_at DESC`
    )
    .all(req.userId);

  // Parse JSON fields
  const result = rows.map((r: any) => ({
    id: r.id,
    name: r.name,
    use: r.use,
    icon: r.icon,
    stock: r.stock,
    effects: r.effects ? JSON.parse(r.effects) : [],
    sideEffects: r.side_effects ? JSON.parse(r.side_effects) : [],
    dosage: r.dosage || "",
    frequency: r.frequency || "",
    timing: r.timing || "",
    duration: r.duration || "",
    warnings: r.warnings ? JSON.parse(r.warnings) : [],
  }));

  res.json(result);
});

router.post("/", (req: AuthRequest, res: Response) => {
  const { name, use: useText, icon, stock, effects, sideEffects, dosage, frequency, timing, duration, warnings } = req.body;

  if (!name) {
    return res.status(400).json({ error: "name is required" });
  }

  const result = db
    .prepare(`INSERT INTO saved_meds
      (user_id, name, use_text, icon, stock, effects, side_effects, dosage, frequency, timing, duration, warnings)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`)
    .run(
      req.userId, name, useText || "", icon || "\ud83d\udc8a", stock || "",
      effects ? JSON.stringify(effects) : null,
      sideEffects ? JSON.stringify(sideEffects) : null,
      dosage || null, frequency || null, timing || null, duration || null,
      warnings ? JSON.stringify(warnings) : null
    );

  res.status(201).json({
    id: result.lastInsertRowid, name, use: useText || "", icon: icon || "\ud83d\udc8a", stock: stock || "",
    effects: effects || [], sideEffects: sideEffects || [], dosage, frequency, timing, duration, warnings: warnings || [],
  });
});

router.delete("/:id", (req: AuthRequest, res: Response) => {
  const { id } = req.params;
  db.prepare("DELETE FROM saved_meds WHERE id = ? AND user_id = ?").run(id, req.userId);
  res.status(204).send();
});

export default router;
