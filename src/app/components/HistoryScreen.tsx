import { useState, useEffect } from "react";
import { FileText, Download, AlertTriangle, Phone, Trash2, ChevronRight, ChevronDown, Calendar, Pill, Shield } from "lucide-react";
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

const SEVERITY_CONFIG = {
  mild: { color: "text-green-600", bg: "bg-green-50", darkBg: "bg-green-900/30", darkColor: "text-green-400", dot: "bg-green-400" },
  moderate: { color: "text-orange-600", bg: "bg-orange-50", darkBg: "bg-orange-900/30", darkColor: "text-orange-400", dot: "bg-orange-400" },
  severe: { color: "text-red-600", bg: "bg-red-50", darkBg: "bg-red-900/30", darkColor: "text-red-400", dot: "bg-red-400" },
};

interface HistoryScreenProps {
  darkMode: boolean;
}

export function HistoryScreen({ darkMode }: HistoryScreenProps) {
  const [activeTab, setActiveTab] = useState<"history" | "saved" | "settings">("history");
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [savedMeds, setSavedMeds] = useState<SavedMed[]>([]);
  const [showExportSuccess, setShowExportSuccess] = useState(false);
  const [expandedMed, setExpandedMed] = useState<string | null>(null);

  useEffect(() => {
    api.history.list().then((rows) => {
      setEntries(rows.map((r: any) => ({
        id: String(r.id),
        date: new Date(r.date).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
        symptom: r.symptom,
        medicine: r.medicine,
        resolved: !!r.resolved,
        severity: r.severity || "mild",
      })));
    }).catch(() => {});

    api.savedMeds.list().then((rows) => {
      setSavedMeds(rows.map((r: any) => ({
        id: String(r.id),
        name: r.name,
        use: r.use || "",
        icon: r.icon || "💊",
        stock: r.stock || "",
        effects: r.effects || [],
        sideEffects: r.sideEffects || [],
        dosage: r.dosage || "",
        frequency: r.frequency || "",
        timing: r.timing || "",
        duration: r.duration || "",
        warnings: r.warnings || [],
      })));
    }).catch(() => {});
  }, []);

  const handleDelete = async (id: string) => {
    await api.history.remove(id);
    setEntries((prev) => prev.filter((e) => e.id !== id));
  };

  const handleDeleteSavedMed = async (id: string) => {
    await api.savedMeds.remove(id);
    setSavedMeds((prev) => prev.filter((m) => m.id !== id));
  };

  const handleExport = () => {
    setShowExportSuccess(true);
    setTimeout(() => setShowExportSuccess(false), 2500);
  };

  return (
    <div className={`${darkMode ? "bg-gray-950" : "bg-gray-50"}`}>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">

        {/* Page header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h2 className={`${darkMode ? "text-white" : "text-gray-900"}`} style={{ fontSize: "24px", fontWeight: 700 }}>Health Records</h2>
            <p className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "14px" }}>Your symptom history and saved medications</p>
          </div>
          <button onClick={handleExport}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl min-h-[44px] ${darkMode ? "bg-gray-800 text-blue-400 border border-gray-700" : "bg-white text-blue-600 border border-blue-100 shadow-sm"}`}
            style={{ fontSize: "14px", fontWeight: 600 }}>
            <Download className="w-4 h-4" />
            Export to PDF
          </button>
        </div>

        <AnimatePresence>
          {showExportSuccess && (
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="mb-4 p-3 rounded-xl bg-green-500 text-white flex items-center gap-2" style={{ fontSize: "14px" }}>
              <FileText className="w-4 h-4" />
              PDF exported successfully! Ready to share with your doctor.
            </motion.div>
          )}
        </AnimatePresence>

        {/* Emergency Banner */}
        <div className={`mb-6 p-4 rounded-2xl flex flex-col sm:flex-row sm:items-center gap-3 ${darkMode ? "bg-red-950/50 border border-red-800/40" : "bg-red-50 border border-red-200"}`}>
          <AlertTriangle className={`w-5 h-5 flex-shrink-0 ${darkMode ? "text-red-400" : "text-red-500"}`} />
          <div className="flex-1">
            <p className={`${darkMode ? "text-red-300" : "text-red-700"}`} style={{ fontSize: "14px", fontWeight: 600 }}>
              Experiencing severe symptoms? Don't wait — call emergency services immediately.
            </p>
            <p className={`${darkMode ? "text-red-400/70" : "text-red-500"}`} style={{ fontSize: "13px" }}>
              Chest pain, difficulty breathing, sudden severe pain, loss of consciousness
            </p>
          </div>
          <a href="tel:911" className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-red-500 text-white min-h-[44px] flex-shrink-0"
            style={{ fontSize: "14px", fontWeight: 700 }}>
            <Phone className="w-4 h-4" />
            Call 911
          </a>
        </div>

        {/* Tabs */}
        <div className={`flex rounded-xl p-1 mb-6 ${darkMode ? "bg-gray-800" : "bg-gray-100"}`}>
          {[
            { key: "history", label: "Symptom History", icon: Calendar },
            { key: "saved", label: "My Medications", icon: Pill },
            { key: "settings", label: "Settings", icon: Shield },
          ].map(({ key, label, icon: Icon }) => (
            <button key={key} onClick={() => setActiveTab(key as typeof activeTab)}
              className={`flex-1 py-2.5 rounded-lg flex items-center justify-center gap-2 transition-all min-h-[44px] ${
                activeTab === key ? darkMode ? "bg-blue-600 text-white shadow" : "bg-white text-blue-600 shadow" : darkMode ? "text-gray-400" : "text-gray-500"
              }`}
              style={{ fontSize: "13px", fontWeight: 600 }}>
              <Icon className="w-4 h-4" />
              <span className="hidden sm:inline">{label}</span>
              <span className="sm:hidden">{label.split(" ")[0]}</span>
            </button>
          ))}
        </div>

        {activeTab === "history" && (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {entries.map((entry, i) => {
              const sev = SEVERITY_CONFIG[entry.severity];
              return (
                <motion.div key={entry.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
                  className={`rounded-2xl p-4 ${darkMode ? "bg-gray-800 border border-gray-700" : "bg-white border border-gray-100 shadow-sm"}`}>
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full flex-shrink-0 ${sev.dot}`} />
                      <span className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "12px" }}>{entry.date}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className={`px-2 py-0.5 rounded-full text-xs ${darkMode ? sev.darkBg + " " + sev.darkColor : sev.bg + " " + sev.color}`}>{entry.severity}</span>
                      <button onClick={() => handleDelete(entry.id)}
                        className={`w-7 h-7 rounded-lg flex items-center justify-center ${darkMode ? "text-gray-600 hover:bg-gray-700" : "text-gray-400 hover:bg-gray-50"}`}>
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                  <p className={`mb-2 ${darkMode ? "text-white" : "text-gray-900"}`} style={{ fontSize: "14px", fontWeight: 600 }}>{entry.symptom}</p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <Pill className={`w-3.5 h-3.5 ${darkMode ? "text-blue-400" : "text-blue-500"}`} />
                      <span className={`${darkMode ? "text-blue-400" : "text-blue-600"}`} style={{ fontSize: "12px" }}>{entry.medicine}</span>
                    </div>
                    {entry.resolved && (
                      <span className={`text-xs ${darkMode ? "text-green-400" : "text-green-600"}`}>✓ Resolved</span>
                    )}
                  </div>
                </motion.div>
              );
            })}
            {entries.length === 0 && (
              <div className="col-span-full text-center py-16">
                <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
                  <Calendar className="w-8 h-8 text-gray-400" />
                </div>
                <p className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "15px" }}>No symptom history yet. Start a new consultation.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === "saved" && (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {savedMeds.map((med, i) => {
              const isExpanded = expandedMed === med.id;
              return (
                <motion.div key={med.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}
                  className={`rounded-2xl overflow-hidden ${darkMode ? "bg-gray-800 border border-gray-700" : "bg-white border border-gray-100 shadow-sm"}`}>
                  <div className="p-4 flex items-center gap-3">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${darkMode ? "bg-blue-900/30" : "bg-blue-50"}`}>
                      <span style={{ fontSize: "24px" }}>{med.icon}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`${darkMode ? "text-white" : "text-gray-900"}`} style={{ fontSize: "14px", fontWeight: 600 }}>{med.name}</p>
                      <p className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "12px" }}>{med.use}</p>
                      {med.stock && (
                        <p className={`${darkMode ? "text-blue-400" : "text-blue-500"}`} style={{ fontSize: "11px", marginTop: "2px" }}>{med.stock}</p>
                      )}
                    </div>
                    <button onClick={() => setExpandedMed(isExpanded ? null : med.id)}
                      className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 transition-all ${isExpanded ? (darkMode ? "bg-blue-900/30 text-blue-400" : "bg-blue-50 text-blue-600") : (darkMode ? "text-gray-500 hover:bg-gray-700" : "text-gray-400 hover:bg-gray-50")}`}>
                      <ChevronDown className={`w-4 h-4 transition-transform ${isExpanded ? "rotate-180" : ""}`} />
                    </button>
                    <button onClick={() => handleDeleteSavedMed(med.id)}
                      className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${darkMode ? "text-gray-600 hover:bg-red-900/30 hover:text-red-400" : "text-gray-400 hover:bg-red-50 hover:text-red-500"}`}>
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Expanded details */}
                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                      >
                        <div className={`px-4 pb-4 pt-1 border-t ${darkMode ? "border-gray-700" : "border-gray-100"}`}>
                          {/* How to take */}
                          {(med.dosage || med.frequency || med.timing || med.duration) && (
                            <div className="mb-3">
                              <p className={`mb-2 ${darkMode ? "text-gray-300" : "text-gray-700"}`} style={{ fontSize: "12px", fontWeight: 600 }}>How to Take</p>
                              <div className="grid grid-cols-2 gap-2">
                                {med.dosage && (
                                  <div className={`px-3 py-2 rounded-lg ${darkMode ? "bg-gray-700" : "bg-gray-50"}`}>
                                    <p className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "10px" }}>Dosage</p>
                                    <p className={`${darkMode ? "text-white" : "text-gray-800"}`} style={{ fontSize: "12px", fontWeight: 500 }}>{med.dosage}</p>
                                  </div>
                                )}
                                {med.frequency && (
                                  <div className={`px-3 py-2 rounded-lg ${darkMode ? "bg-gray-700" : "bg-gray-50"}`}>
                                    <p className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "10px" }}>Frequency</p>
                                    <p className={`${darkMode ? "text-white" : "text-gray-800"}`} style={{ fontSize: "12px", fontWeight: 500 }}>{med.frequency}</p>
                                  </div>
                                )}
                                {med.timing && (
                                  <div className={`px-3 py-2 rounded-lg ${darkMode ? "bg-gray-700" : "bg-gray-50"}`}>
                                    <p className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "10px" }}>Timing</p>
                                    <p className={`${darkMode ? "text-white" : "text-gray-800"}`} style={{ fontSize: "12px", fontWeight: 500 }}>{med.timing}</p>
                                  </div>
                                )}
                                {med.duration && (
                                  <div className={`px-3 py-2 rounded-lg ${darkMode ? "bg-gray-700" : "bg-gray-50"}`}>
                                    <p className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "10px" }}>Duration</p>
                                    <p className={`${darkMode ? "text-white" : "text-gray-800"}`} style={{ fontSize: "12px", fontWeight: 500 }}>{med.duration}</p>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}

                          {/* Effects */}
                          {med.effects.length > 0 && (
                            <div className="mb-3">
                              <p className={`mb-2 ${darkMode ? "text-gray-300" : "text-gray-700"}`} style={{ fontSize: "12px", fontWeight: 600 }}>Effects</p>
                              <div className="space-y-1">
                                {med.effects.map((e, j) => (
                                  <div key={j} className="flex items-start gap-2">
                                    <div className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${darkMode ? "bg-green-400" : "bg-green-500"}`} />
                                    <span className={`${darkMode ? "text-gray-300" : "text-gray-600"}`} style={{ fontSize: "12px" }}>{e}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Side Effects */}
                          {med.sideEffects.length > 0 && (
                            <div className="mb-3">
                              <p className={`mb-2 ${darkMode ? "text-gray-300" : "text-gray-700"}`} style={{ fontSize: "12px", fontWeight: 600 }}>Side Effects</p>
                              <div className="space-y-1">
                                {med.sideEffects.map((e, j) => (
                                  <div key={j} className="flex items-start gap-2">
                                    <div className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${darkMode ? "bg-yellow-400" : "bg-yellow-500"}`} />
                                    <span className={`${darkMode ? "text-gray-300" : "text-gray-600"}`} style={{ fontSize: "12px" }}>{e}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Warnings */}
                          {med.warnings.length > 0 && (
                            <div className={`p-3 rounded-lg ${darkMode ? "bg-red-900/20 border border-red-800/30" : "bg-red-50 border border-red-100"}`}>
                              <p className={`mb-1.5 ${darkMode ? "text-red-400" : "text-red-600"}`} style={{ fontSize: "12px", fontWeight: 600 }}>Warnings</p>
                              <p className={`${darkMode ? "text-red-300/80" : "text-red-500"}`} style={{ fontSize: "11px" }}>
                                Avoid if: {med.warnings.join(", ")}
                              </p>
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
              <div className="col-span-full text-center py-16">
                <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
                  <Pill className="w-8 h-8 text-gray-400" />
                </div>
                <p className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "15px" }}>No saved medications yet. Bookmark medicines from chat.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === "settings" && (
          <div className="max-w-2xl space-y-4">
            <div className={`rounded-2xl overflow-hidden ${darkMode ? "bg-gray-800 border border-gray-700" : "bg-white border border-gray-100 shadow-sm"}`}>
              {[
                { icon: "🔔", label: "Dosage Reminders", desc: "Get notified when to take your medication", toggle: true },
                { icon: "👤", label: "Health Profile", desc: "Allergies, chronic conditions, blood type", toggle: false },
                { icon: "🔒", label: "Privacy & Data", desc: "Manage how your health data is stored", toggle: false },
                { icon: "📞", label: "Emergency Contacts", desc: "Quick access numbers for emergencies", toggle: false },
                { icon: "🌍", label: "Language", desc: "Change app language", toggle: false },
              ].map((item, i, arr) => (
                <div key={item.label}
                  className={`flex items-center gap-4 px-5 py-4 min-h-[68px] ${i < arr.length - 1 ? (darkMode ? "border-b border-gray-700" : "border-b border-gray-50") : ""}`}>
                  <span style={{ fontSize: "20px" }}>{item.icon}</span>
                  <div className="flex-1">
                    <p className={`${darkMode ? "text-white" : "text-gray-900"}`} style={{ fontSize: "15px", fontWeight: 500 }}>{item.label}</p>
                    <p className={`${darkMode ? "text-gray-500" : "text-gray-500"}`} style={{ fontSize: "12px" }}>{item.desc}</p>
                  </div>
                  {item.toggle ? (
                    <button className={`w-12 h-6 rounded-full transition-all relative bg-blue-500`}>
                      <div className="w-5 h-5 rounded-full bg-white shadow absolute top-0.5 right-0.5 transition-all" />
                    </button>
                  ) : (
                    <ChevronRight className={`w-4 h-4 ${darkMode ? "text-gray-600" : "text-gray-400"}`} />
                  )}
                </div>
              ))}
            </div>

            <div className={`rounded-2xl p-4 ${darkMode ? "bg-gray-800 border border-gray-700" : "bg-white border border-gray-100 shadow-sm"}`}>
              <p className={`mb-0.5 ${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "12px" }}>App Version</p>
              <p className={`${darkMode ? "text-white" : "text-gray-900"}`} style={{ fontSize: "14px", fontWeight: 600 }}>MediGuide v1.0.0</p>
              <p className={`${darkMode ? "text-gray-500" : "text-gray-400"}`} style={{ fontSize: "12px" }}>Medicine database: May 2026 · 500+ medicines indexed</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
