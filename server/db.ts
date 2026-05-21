import Database from "better-sqlite3";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dbPath = path.join(__dirname, "..", "mediguide.db");

const db = new Database(dbPath);

db.pragma("journal_mode = WAL");
db.pragma("foreign_keys = ON");

db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS history_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    symptom TEXT NOT NULL,
    medicine TEXT NOT NULL,
    severity TEXT DEFAULT 'mild',
    resolved INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
  );

  CREATE TABLE IF NOT EXISTS saved_meds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    use_text TEXT,
    icon TEXT,
    stock TEXT,
    effects TEXT,
    side_effects TEXT,
    dosage TEXT,
    frequency TEXT,
    timing TEXT,
    duration TEXT,
    warnings TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
  );
`);

// Add new columns if they don't exist (migration for existing DBs)
const addCol = (col: string) => {
  try { db.exec(`ALTER TABLE saved_meds ADD COLUMN ${col} TEXT`); } catch {}
};
["effects", "side_effects", "dosage", "frequency", "timing", "duration", "warnings"].forEach(addCol);

export default db;
