import { useState, useEffect } from "react";
import { AlertTriangle, Phone, Trash2, ChevronDown, Calendar, Pill, Settings } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { api } from "../../lib/api";

interface HistoryEntry {
  id: string;
  date: string;
  symptom: string;
  medicine: string;
  resolved: boolean;
  severity: "mild" | "moderate" | "severe";
}

interface SavedMed {
  id: string;
  name: string;
  use: string;
  icon: string;
  stock: string;
  effects: string[];
  sideEffects: string[];
  dosage: string;
  frequency: string;
  timing: string;
  duration: string;
  warnings: string[];
}

const SEVERITY: Record<string, { bg: string; text: string; darkBg: string; darkText: string }> = {
  mild: { bg: "bg-green-50", text: "text-green-700", darkBg: "bg-green-950", darkText: "text-green-400" },
  moderate: { bg: "bg-orange-50", text: "text-orange-700", darkBg: "bg-orange-950", darkText: "text-orange-400" },
  severe: { bg: "bg-red-50", text: "text-red-700", darkBg: "bg-red-950", darkText: "text-red-400" },
};

export function HistoryScreen({ darkMode }: { darkMode: boolean }) {
  const [activeTab, setActiveTab] = useState<"history" | "saved" | "settings">("history");
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [savedMeds, setSavedMeds] = useState<SavedMed[]>([]);
  const [expandedMed, setExpandedMed] = useState<string | null>(null);

  useEffect(() => {
    api.history.list().then(rows => {
      setEntries(rows.map((r: any) => ({
        id: String(r.id),
        date: new Date(r.date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
        symptom: r.symptom, medicine: r.medicine, resolved: !!r.resolved, severity: r.severity || "mild",
      })));
    }).catch(() => {});
    api.savedMeds.list().then(rows => {
      setSavedMeds(rows.map((r: any) => ({
        id: String(r.id), name: r.name, use: r.use || "", icon: r.icon || "\ud83d\udc8a", stock: r.stock || "",
        effects: r.effects || [], sideEffects: r.sideEffects || [], dosage: r.dosage || "", frequency: r.frequency || "",
        timing: r.timing || "", duration: r.duration || "", warnings: r.warnings || [],
      })));
    }).catch(() => {});
  }, []);

  const handleDelete = async (id: string) => { await api.history.remove(id); setEntries(p => p.filter(e => e.id !== id)); };
  const handleDeleteSavedMed = async (id: string) => { await api.savedMeds.remove(id); setSavedMeds(p => p.filter(m => m.id !== id)); };

  return (
    <div className={darkMode ? "bg-[#09090b]" : "bg-[#fafafa]"}>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 lg:py-8">
        {/* Header */}
        <div className="mb-6">
          <h2 className={`text-xl font-bold ${darkMode ? "text-white" : "text-gray-900"}`}>Health Records</h2>
          <p className={`text-xs mt-0.5 ${darkMode ? "text-gray-500" : "text-gray-400"}`}>Your symptom history and saved medications</p>
        </div>

        {/* Emergency Banner */}
        <div className={`mb-5 p-3 rounded-xl flex flex-col sm:flex-row sm:items-center gap-2.5 ${darkMode ? "bg-red-950/30 border border-red-900/50" : "bg-red-50 border border-red-200"}`}>
          <AlertTriangle className={`w-4 h-4 flex-shrink-0 ${darkMode ? "text-red-400" : "text-red-500"}`} />
          <div className="flex-1">
            <p className={`text-sm font-semibold ${darkMode ? "text-red-300" : "text-red-700"}`}>Experiencing severe symptoms?</p>
            <p className={`text-xs ${darkMode ? "text-red-400/70" : "text-red-500"}`}>Chest pain, difficulty breathing, sudden severe pain</p>
          </div>
          <a href="tel:911" className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-red-600 text-white text-xs font-semibold flex-shrink-0">
            <Phone className="w-3.5 h-3.5" />Call 911
          </a>
        </div>

        {/* Tabs */}
        <div className={`flex rounded-lg p-0.5 mb-5 border ${darkMode ? "bg-gray-900 border-gray-800" : "bg-gray-100 border-gray-200"}`}>
          {[
            { key: "history", label: "History", icon: Calendar },
            { key: "saved", label: "Medications", icon: Pill },
            { key: "settings", label: "Settings", icon: Settings },
          ].map(({ key, label, icon: Icon }) => (
            <button key={key} onClick={() => setActiveTab(key as typeof activeTab)}
              className={`flex-1 py-2 rounded-md flex items-center justify-center gap-1.5 text-xs font-medium transition-colors ${
                activeTab === key ? "bg-blue-600 text-white" : darkMode ? "text-gray-500 hover:text-gray-300" : "text-gray-500 hover:text-gray-700"
              }`}>
              <Icon className="w-3.5 h-3.5" />{label}
            </button>
          ))}
        </div>

        {/* History Tab */}
        {activeTab === "history" && (
          <div className="space-y-2">
            {entries.map((entry, i) => {
              const s = SEVERITY[entry.severity] || SEVERITY.mild;
              return (
                <motion.div key={entry.id} initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}
                  className={`p-3.5 rounded-xl border ${darkMode ? "bg-gray-900 border-gray-800" : "bg-white border-gray-200"}`}>
                  <div className="flex items-start justify-between mb-1.5">
                    <div className="flex items-center gap-2">
                      <span className={`text-xs ${darkMode ? "text-gray-500" : "text-gray-400"}`}>{entry.date}</span>
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${darkMode ? s.darkBg + " " + s.darkText : s.bg + " " + s.text}`}>{entry.severity}</span>
                    </div>
                    <button onClick={() => handleDelete(entry.id)}
                      className={`p-1 rounded ${darkMode ? "text-gray-600 hover:text-red-400" : "text-gray-400 hover:text-red-500"}`}>
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <p className={`text-sm font-medium mb-1 ${darkMode ? "text-white" : "text-gray-900"}`}>{entry.symptom}</p>
                  <div className="flex items-center gap-1.5">
                    <Pill className={`w-3 h-3 ${darkMode ? "text-blue-400" : "text-blue-600"}`} />
                    <span className={`text-xs ${darkMode ? "text-blue-400" : "text-blue-600"}`}>{entry.medicine}</span>
                    {entry.resolved && <span className={`text-[10px] ml-auto ${darkMode ? "text-green-400" : "text-green-600"}`}>Resolved</span>}
                  </div>
                </motion.div>
              );
            })}
            {entries.length === 0 && (
              <div className="text-center py-16">
                <Calendar className={`w-8 h-8 mx-auto mb-2 ${darkMode ? "text-gray-700" : "text-gray-300"}`} />
                <p className={`text-sm ${darkMode ? "text-gray-600" : "text-gray-400"}`}>No symptom history yet</p>
              </div>
            )}
          </div>
        )}

        {/* Saved Meds Tab */}
        {activeTab === "saved" && (
          <div className="space-y-2">
            {savedMeds.map((med, i) => {
              const isExpanded = expandedMed === med.id;
              return (
                <motion.div key={med.id} initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}
                  className={`rounded-xl border overflow-hidden ${darkMode ? "bg-gray-900 border-gray-800" : "bg-white border-gray-200"}`}>
                  <div className="p-3.5 flex items-center gap-3">
                    <span className="text-lg">{med.icon}</span>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-semibold ${darkMode ? "text-white" : "text-gray-900"}`}>{med.name}</p>
                      <p className={`text-xs truncate ${darkMode ? "text-gray-500" : "text-gray-400"}`}>{med.use}</p>
                    </div>
                    <button onClick={() => setExpandedMed(isExpanded ? null : med.id)}
                      className={`p-1 rounded ${darkMode ? "text-gray-500" : "text-gray-400"}`}>
                      <ChevronDown className={`w-4 h-4 transition-transform ${isExpanded ? "rotate-180" : ""}`} />
                    </button>
                    <button onClick={() => handleDeleteSavedMed(med.id)}
                      className={`p-1 rounded ${darkMode ? "text-gray-600 hover:text-red-400" : "text-gray-400 hover:text-red-500"}`}>
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.2 }} className="overflow-hidden">
                        <div className={`px-3.5 pb-3.5 pt-1 border-t ${darkMode ? "border-gray-800" : "border-gray-100"}`}>
                          {(med.dosage || med.frequency || med.timing) && (
                            <div className="mb-3">
                              <p className={`text-[11px] font-medium uppercase tracking-wider mb-1.5 ${darkMode ? "text-gray-500" : "text-gray-400"}`}>How to Take</p>
                              <div className="grid grid-cols-3 gap-1.5">
                                {med.dosage && <div className={`p-2 rounded-lg ${darkMode ? "bg-gray-800" : "bg-gray-50"}`}><p className={`text-[10px] ${darkMode ? "text-gray-500" : "text-gray-400"}`}>Dosage</p><p className={`text-xs font-medium ${darkMode ? "text-white" : "text-gray-900"}`}>{med.dosage}</p></div>}
                                {med.frequency && <div className={`p-2 rounded-lg ${darkMode ? "bg-gray-800" : "bg-gray-50"}`}><p className={`text-[10px] ${darkMode ? "text-gray-500" : "text-gray-400"}`}>Frequency</p><p className={`text-xs font-medium ${darkMode ? "text-white" : "text-gray-900"}`}>{med.frequency}</p></div>}
                                {med.timing && <div className={`p-2 rounded-lg ${darkMode ? "bg-gray-800" : "bg-gray-50"}`}><p className={`text-[10px] ${darkMode ? "text-gray-500" : "text-gray-400"}`}>Timing</p><p className={`text-xs font-medium ${darkMode ? "text-white" : "text-gray-900"}`}>{med.timing}</p></div>}
                              </div>
                            </div>
                          )}
                          {med.effects.length > 0 && (
                            <div className="mb-2">
                              <p className={`text-[11px] font-medium uppercase tracking-wider mb-1 ${darkMode ? "text-gray-500" : "text-gray-400"}`}>Effects</p>
                              {med.effects.map((e, j) => <p key={j} className={`text-xs ${darkMode ? "text-gray-400" : "text-gray-500"}`}>{"\u2713"} {e}</p>)}
                            </div>
                          )}
                          {med.warnings.length > 0 && (
                            <div className={`p-2 rounded-lg ${darkMode ? "bg-red-950/30 border border-red-900/50" : "bg-red-50 border border-red-100"}`}>
                              <p className={`text-[10px] font-medium ${darkMode ? "text-red-400" : "text-red-600"}`}>Warnings: {med.warnings.join(", ")}</p>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              );
            })}
            {savedMeds.length === 0 && (
              <div className="text-center py-16">
                <Pill className={`w-8 h-8 mx-auto mb-2 ${darkMode ? "text-gray-700" : "text-gray-300"}`} />
                <p className={`text-sm ${darkMode ? "text-gray-600" : "text-gray-400"}`}>No saved medications yet</p>
              </div>
            )}
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === "settings" && (
          <div className="max-w-lg space-y-3">
            <div className={`rounded-xl border overflow-hidden ${darkMode ? "bg-gray-900 border-gray-800" : "bg-white border-gray-200"}`}>
              {[
                { label: "Dosage Reminders", desc: "Get notified when to take medication", toggle: true },
                { label: "Health Profile", desc: "Allergies, conditions, blood type" },
                { label: "Privacy & Data", desc: "Manage health data storage" },
                { label: "Emergency Contacts", desc: "Quick access numbers" },
                { label: "Language", desc: "Change app language" },
              ].map((item, i, arr) => (
                <div key={item.label} className={`flex items-center gap-3 px-4 py-3 ${i < arr.length - 1 ? (darkMode ? "border-b border-gray-800" : "border-b border-gray-100") : ""}`}>
                  <div className="flex-1">
                    <p className={`text-sm font-medium ${darkMode ? "text-white" : "text-gray-900"}`}>{item.label}</p>
                    <p className={`text-xs ${darkMode ? "text-gray-600" : "text-gray-400"}`}>{item.desc}</p>
                  </div>
                  {item.toggle ? (
                    <div className={`w-9 h-5 rounded-full bg-blue-600 relative`}>
                      <div className="w-4 h-4 rounded-full bg-white shadow absolute top-0.5 right-0.5" />
                    </div>
                  ) : (
                    <ChevronDown className={`w-4 h-4 ${darkMode ? "text-gray-700" : "text-gray-300"}`} />
                  )}
                </div>
              ))}
            </div>
            <div className={`p-3 rounded-xl border ${darkMode ? "bg-gray-900 border-gray-800" : "bg-white border-gray-200"}`}>
              <p className={`text-xs ${darkMode ? "text-gray-600" : "text-gray-400"}`}>Pharmacare v1.0.0</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
