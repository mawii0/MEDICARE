import { useState, useRef, useEffect } from "react";
import { Send, Phone, ChevronDown, ChevronUp, AlertTriangle, Bookmark, BookmarkCheck, MapPin } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { api } from "../../lib/api";

interface MedicineCard {
  name: string;
  icon: string;
  whatItDoes: string;
  effects: string[];
  sideEffects: string[];
  dosage: string;
  frequency: string;
  timing: string;
  duration: string;
  warnings: string[];
  otc: boolean;
}

interface Message {
  id: string;
  role: "user" | "bot";
  text?: string;
  symptomAck?: string;
  medicine?: MedicineCard;
  timestamp: Date;
}

const MOCK_RESPONSES: Record<string, MedicineCard> = {
  default: {
    name: "Ibuprofen 400mg",
    icon: "💊",
    whatItDoes: "Ibuprofen is a non-steroidal anti-inflammatory drug (NSAID) that works by blocking prostaglandins—chemicals in your body that cause pain, fever, and inflammation. It's widely used to relieve mild to moderate pain and reduce swelling.",
    effects: ["Reduces pain within 30–60 minutes", "Lowers fever effectively", "Reduces inflammation and swelling"],
    sideEffects: ["Possible stomach upset if taken on empty stomach", "May cause mild dizziness", "Avoid with blood thinners or kidney issues"],
    dosage: "1 tablet (400mg)", frequency: "Every 6–8 hours", timing: "With food or milk", duration: "3–5 days",
    warnings: ["Pregnancy", "Kidney disease", "Stomach ulcers", "Blood thinners"], otc: true,
  },
  Headache: {
    name: "Paracetamol 500mg", icon: "🔵",
    whatItDoes: "Paracetamol works centrally to block pain signals in the brain and helps reduce fever. It's one of the safest over-the-counter pain relievers, gentle on the stomach and suitable for most adults.",
    effects: ["Relieves headache in 30–45 min", "Reduces fever effectively", "Safe for most adults"],
    sideEffects: ["Rare liver risk with high doses", "Generally very well tolerated", "Avoid alcohol while taking"],
    dosage: "1–2 tablets (500mg–1g)", frequency: "Every 4–6 hours", timing: "With or without food", duration: "Up to 3 days",
    warnings: ["Liver disease", "Heavy alcohol use", "Max 4g/day"], otc: true,
  },
  Fever: {
    name: "Paracetamol 500mg + Hydration", icon: "🌡️",
    whatItDoes: "For fever management, Paracetamol reduces body temperature by acting on the temperature-regulating center in the brain. Combined with adequate hydration, it helps your immune system fight the underlying cause.",
    effects: ["Temperature reduction within 1 hour", "Relieves associated body aches", "Non-drowsy formula"],
    sideEffects: ["Minimal side effects at recommended doses", "Drink plenty of fluids", "Rest is advised"],
    dosage: "1–2 tablets (500mg–1g)", frequency: "Every 4–6 hours", timing: "With a full glass of water", duration: "Until fever breaks (max 3 days)",
    warnings: ["Liver disease", "Max 4g/day", "See doctor if fever > 39°C for 48h"], otc: true,
  },
  Cough: {
    name: "Dextromethorphan Syrup 15mg", icon: "🍯",
    whatItDoes: "Dextromethorphan is a cough suppressant that acts on the cough center in the brain to reduce the urge to cough. Best suited for dry, irritating coughs.",
    effects: ["Suppresses dry cough for 4–6 hours", "Helps you sleep more comfortably", "Non-sedating at standard doses"],
    sideEffects: ["Mild drowsiness possible", "Do not use for productive (wet) cough", "Avoid driving if drowsy"],
    dosage: "10ml (1 full spoon)", frequency: "Every 6–8 hours", timing: "After meals", duration: "Up to 7 days",
    warnings: ["MAOI medications", "Productive cough", "Under 12 years"], otc: true,
  },
  "Stomach Pain": {
    name: "Buscopan (Hyoscine) 10mg", icon: "🟢",
    whatItDoes: "Hyoscine butylbromide relieves intestinal spasms and cramps by relaxing the smooth muscles of the gut. It works locally in the digestive tract for fast, targeted relief.",
    effects: ["Relieves cramps within 15–30 min", "Reduces bloating", "Targeted gut relief"],
    sideEffects: ["Dry mouth possible", "Slight blurred vision temporarily", "Do not drive if vision affected"],
    dosage: "1–2 tablets (10–20mg)", frequency: "Every 6–8 hours", timing: "Before or with meals", duration: "3–5 days",
    warnings: ["Glaucoma", "Enlarged prostate", "Pregnancy"], otc: true,
  },
  Allergies: {
    name: "Cetirizine 10mg", icon: "🌿",
    whatItDoes: "Cetirizine is a second-generation antihistamine that blocks H1 receptors, preventing histamine from causing allergy symptoms. Provides 24-hour relief with minimal drowsiness.",
    effects: ["Controls sneezing and runny nose", "Relieves itchy, watery eyes", "24-hour protection per dose"],
    sideEffects: ["Mild drowsiness in some people", "Dry mouth occasionally", "Avoid alcohol"],
    dosage: "1 tablet (10mg)", frequency: "Once daily", timing: "Evening (may cause mild drowsiness)", duration: "As needed or daily during allergy season",
    warnings: ["Kidney impairment", "Pregnancy (consult doctor)", "Avoid with alcohol"], otc: true,
  },
};

function TypingIndicator({ darkMode }: { darkMode: boolean }) {
  return (
    <div className="flex items-end gap-2 mb-4">
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${darkMode ? "bg-blue-900" : "bg-blue-100"}`}>
        <span style={{ fontSize: "14px" }}>⚕️</span>
      </div>
      <div className={`px-4 py-3 rounded-2xl rounded-bl-sm ${darkMode ? "bg-gray-800" : "bg-white shadow-sm border border-gray-100"}`}>
        <div className="flex gap-1 items-center h-5">
          {[0, 1, 2].map((i) => (
            <motion.div key={i} className={`w-2 h-2 rounded-full ${darkMode ? "bg-blue-400" : "bg-blue-400"}`}
              animate={{ y: [0, -6, 0] }} transition={{ duration: 0.8, repeat: Infinity, delay: i * 0.15 }} />
          ))}
        </div>
        <p className={`mt-1 ${darkMode ? "text-gray-400" : "text-gray-400"}`} style={{ fontSize: "12px" }}>Consulting database...</p>
      </div>
    </div>
  );
}

function MedicineCardComponent({ med, darkMode, saved, onSave, onFindPharmacy }: {
  med: MedicineCard; darkMode: boolean; saved: boolean; onSave: () => void; onFindPharmacy: () => void;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
      className={`rounded-2xl overflow-hidden shadow-md ${darkMode ? "bg-gray-800 border border-gray-700" : "bg-white border border-blue-50"}`}
    >
      <div className={`px-4 py-3 ${darkMode ? "bg-blue-900/40" : "bg-blue-500"} flex items-center justify-between`}>
        <div className="flex items-center gap-3">
          <span style={{ fontSize: "28px" }}>{med.icon}</span>
          <div>
            <p className="text-white" style={{ fontSize: "16px", fontWeight: 700 }}>{med.name}</p>
            <span className={`text-xs px-2 py-0.5 rounded-full ${med.otc ? "bg-green-400/30 text-green-100" : "bg-orange-400/30 text-orange-100"}`}>
              {med.otc ? "Over-the-Counter" : "Prescription Required"}
            </span>
          </div>
        </div>
        <button onClick={onSave} className="p-2 rounded-full bg-white/20 min-w-[44px] min-h-[44px] flex items-center justify-center">
          {saved ? <BookmarkCheck className="w-5 h-5 text-yellow-300" /> : <Bookmark className="w-5 h-5 text-white" />}
        </button>
      </div>

      <div className="p-4">
        <div className="grid md:grid-cols-2 gap-4 mb-4">
          {/* What it does */}
          <div>
            <p className={`mb-1 ${darkMode ? "text-blue-400" : "text-blue-600"}`} style={{ fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>What It Does</p>
            <p className={`${darkMode ? "text-gray-300" : "text-gray-700"}`} style={{ fontSize: "14px", lineHeight: 1.6 }}>{med.whatItDoes}</p>
          </div>
          {/* Effects */}
          <div>
            <p className={`mb-2 ${darkMode ? "text-teal-400" : "text-teal-600"}`} style={{ fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>Expected Effects</p>
            <ul className="space-y-1">
              {med.effects.map((e, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-teal-400 mt-1">✓</span>
                  <span className={`${darkMode ? "text-gray-300" : "text-gray-600"}`} style={{ fontSize: "14px" }}>{e}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* How to take */}
        <div className={`rounded-xl p-3 mb-4 ${darkMode ? "bg-gray-700/50" : "bg-blue-50"}`}>
          <p className={`mb-3 ${darkMode ? "text-blue-400" : "text-blue-600"}`} style={{ fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>How To Take</p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {[
              { icon: "💊", label: "Dosage", value: med.dosage },
              { icon: "⏱️", label: "Frequency", value: med.frequency },
              { icon: "🍽️", label: "Timing", value: med.timing },
              { icon: "📅", label: "Duration", value: med.duration },
            ].map((item) => (
              <div key={item.label} className={`rounded-lg p-2 ${darkMode ? "bg-gray-700" : "bg-white"} shadow-sm`}>
                <div className="flex items-center gap-1.5 mb-1">
                  <span style={{ fontSize: "14px" }}>{item.icon}</span>
                  <span className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "11px" }}>{item.label}</span>
                </div>
                <p className={`${darkMode ? "text-white" : "text-gray-800"}`} style={{ fontSize: "13px", fontWeight: 600 }}>{item.value}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Expandable */}
        <button onClick={() => setExpanded((v) => !v)}
          className={`w-full flex items-center justify-between py-2 px-3 rounded-xl mb-3 min-h-[44px] ${darkMode ? "bg-gray-700 text-gray-300" : "bg-gray-50 text-gray-600"}`}>
          <span style={{ fontSize: "13px", fontWeight: 600 }}>Side Effects & Warnings</span>
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        <AnimatePresence>
          {expanded && (
            <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.25 }} className="overflow-hidden">
              <div className="grid md:grid-cols-2 gap-3 mb-3">
                <div>
                  <p className={`mb-2 ${darkMode ? "text-orange-400" : "text-orange-600"}`} style={{ fontSize: "11px", fontWeight: 600, textTransform: "uppercase" }}>Side Effects</p>
                  <ul className="space-y-1">
                    {med.sideEffects.map((s, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-orange-400 mt-0.5" style={{ fontSize: "12px" }}>!</span>
                        <span className={`${darkMode ? "text-gray-300" : "text-gray-600"}`} style={{ fontSize: "13px" }}>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                {med.warnings.length > 0 && (
                  <div className={`rounded-xl p-3 ${darkMode ? "bg-red-950/40 border border-red-800/30" : "bg-red-50 border border-red-100"}`}>
                    <div className="flex items-center gap-2 mb-2">
                      <AlertTriangle className={`w-4 h-4 ${darkMode ? "text-red-400" : "text-red-500"}`} />
                      <span className={`${darkMode ? "text-red-400" : "text-red-600"}`} style={{ fontSize: "12px", fontWeight: 600 }}>Contraindications</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {med.warnings.map((w) => (
                        <span key={w} className={`px-2 py-1 rounded-full text-xs ${darkMode ? "bg-red-900/50 text-red-300" : "bg-red-100 text-red-700"}`}>{w}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <button onClick={onFindPharmacy}
          className="w-full mt-2 py-3 rounded-xl bg-teal-500 text-white flex items-center justify-center gap-2 min-h-[44px] active:scale-98 transition-transform"
          style={{ fontSize: "15px", fontWeight: 600 }}>
          <MapPin className="w-4 h-4" />
          Find Near Me
        </button>
      </div>
    </motion.div>
  );
}

interface ChatScreenProps {
  initialSymptom: string;
  darkMode: boolean;
  onNavigateToPharmacy: () => void;
}

export function ChatScreen({ initialSymptom, darkMode, onNavigateToPharmacy }: ChatScreenProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [savedMeds, setSavedMeds] = useState<Set<string>>(new Set());
  const bottomRef = useRef<HTMLDivElement>(null);
  const hasInitialized = useRef(false);

  useEffect(() => {
    if (!hasInitialized.current && initialSymptom) {
      hasInitialized.current = true;
      sendMessage(initialSymptom, true);
    }
  }, [initialSymptom]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const sendMessage = async (text: string, _isInitial = false) => {
    const userMsg: Message = { id: Date.now().toString(), role: "user", text, timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);
    setInputValue("");
    setIsTyping(true);
    try {
      const { ack, medicine } = await api.chat.send(text);
      setMessages((prev) => [...prev, { id: (Date.now() + 1).toString(), role: "bot", symptomAck: ack, medicine, timestamp: new Date() }]);
      // Persist to history
      api.history.add({ symptom: text, medicine: medicine.name, severity: "mild" }).catch(() => {});
    } catch {
      setMessages((prev) => [...prev, { id: (Date.now() + 1).toString(), role: "bot", text: "Sorry, something went wrong. Please try again.", timestamp: new Date() }]);
    } finally {
      setIsTyping(false);
    }
  };

  const toggleSave = (medName: string, med?: MedicineCard) => {
    const isSaved = savedMeds.has(medName);
    setSavedMeds((prev) => { const n = new Set(prev); isSaved ? n.delete(medName) : n.add(medName); return n; });
    if (!isSaved && med) {
      api.savedMeds.add({
        name: med.name,
        use: med.whatItDoes?.slice(0, 80),
        icon: med.icon,
        stock: "",
        effects: med.effects,
        sideEffects: med.sideEffects,
        dosage: med.dosage,
        frequency: med.frequency,
        timing: med.timing,
        duration: med.duration,
        warnings: med.warnings,
      }).catch(() => {});
    }
  };

  return (
    <div className={`flex flex-col ${darkMode ? "bg-gray-950" : "bg-gray-50"}`} style={{ height: "calc(100vh - 64px)" }}>
      {/* Chat header */}
      <div className={`px-4 lg:px-6 py-3 flex items-center gap-3 shadow-sm flex-shrink-0 ${darkMode ? "bg-gray-900 border-b border-gray-800" : "bg-white border-b border-gray-100"}`}>
        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${darkMode ? "bg-blue-900" : "bg-blue-100"}`}>
          <span style={{ fontSize: "20px" }}>⚕️</span>
        </div>
        <div className="flex-1">
          <p className={`${darkMode ? "text-white" : "text-gray-900"}`} style={{ fontSize: "15px", fontWeight: 600 }}>MediGuide Assistant</p>
          <p className={`${darkMode ? "text-green-400" : "text-green-500"}`} style={{ fontSize: "12px" }}>● Online — responds instantly</p>
        </div>
        <a href="tel:911" className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-red-500 text-white min-h-[44px]" style={{ fontSize: "13px", fontWeight: 600 }}>
          <Phone className="w-4 h-4" />
          Emergency
        </a>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 lg:px-6 py-4">
        <div className="max-w-3xl mx-auto space-y-3">
          {messages.length === 0 && !isTyping && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-16 px-6">
              <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-4">
                <span style={{ fontSize: "32px" }}>⚕️</span>
              </div>
              <p className={`${darkMode ? "text-gray-300" : "text-gray-600"}`} style={{ fontSize: "16px" }}>
                Hello! I'm your MediGuide assistant. Tell me your symptoms and I'll help find the right care.
              </p>
            </motion.div>
          )}

          {messages.map((msg) => (
            <div key={msg.id}>
              {msg.role === "user" ? (
                <div className="flex justify-end mb-4">
                  <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}
                    className="max-w-lg px-4 py-3 rounded-2xl rounded-br-sm bg-blue-500 text-white shadow-md"
                    style={{ fontSize: "15px", lineHeight: 1.5 }}>
                    {msg.text}
                  </motion.div>
                </div>
              ) : (
                <div className="flex items-end gap-2 mb-4">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${darkMode ? "bg-blue-900" : "bg-blue-100"}`}>
                    <span style={{ fontSize: "14px" }}>⚕️</span>
                  </div>
                  <div className="flex-1 space-y-3">
                    {msg.symptomAck && (
                      <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
                        className={`px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm ${darkMode ? "bg-gray-800 text-gray-200" : "bg-white text-gray-700 border border-gray-100"}`}
                        style={{ fontSize: "14px", lineHeight: 1.6 }}>
                        {msg.symptomAck.split("**").map((part, i) => i % 2 === 1 ? <strong key={i}>{part}</strong> : part)}
                      </motion.div>
                    )}
                    {msg.medicine && (
                      <MedicineCardComponent med={msg.medicine} darkMode={darkMode}
                        saved={savedMeds.has(msg.medicine.name)} onSave={() => toggleSave(msg.medicine!.name, msg.medicine!)}
                        onFindPharmacy={onNavigateToPharmacy} />
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}

          {isTyping && <TypingIndicator darkMode={darkMode} />}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Speak to Pharmacist */}
      <div className={`px-4 lg:px-6 pb-2 pt-1 ${darkMode ? "bg-gray-950" : "bg-gray-50"}`}>
        <div className="max-w-3xl mx-auto">
          <button className={`w-full py-2.5 rounded-xl flex items-center justify-center gap-2 min-h-[44px] ${darkMode ? "bg-teal-900/50 text-teal-300 border border-teal-800/50" : "bg-teal-50 text-teal-700 border border-teal-200"}`}
            style={{ fontSize: "13px", fontWeight: 600 }}>
            <Phone className="w-4 h-4" />
            Speak to Human Pharmacist
          </button>
        </div>
      </div>

      {/* Input */}
      <div className={`px-4 lg:px-6 pb-4 pt-2 flex-shrink-0 ${darkMode ? "bg-gray-900 border-t border-gray-800" : "bg-white border-t border-gray-100"}`}>
        <div className="max-w-3xl mx-auto flex items-end gap-2">
          <div className={`flex-1 flex items-end rounded-2xl px-4 py-3 min-h-[52px] ${darkMode ? "bg-gray-800 border border-gray-700" : "bg-gray-50 border border-gray-200"}`}>
            <textarea value={inputValue} onChange={(e) => setInputValue(e.target.value)}
              placeholder="Describe your symptoms..."
              className={`flex-1 resize-none outline-none bg-transparent max-h-24 ${darkMode ? "text-white placeholder-gray-500" : "text-gray-800 placeholder-gray-400"}`}
              style={{ fontSize: "16px" }} rows={1}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); if (inputValue.trim()) sendMessage(inputValue.trim()); } }} />
          </div>
          <button onClick={() => inputValue.trim() && sendMessage(inputValue.trim())}
            disabled={!inputValue.trim() || isTyping}
            className={`w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0 transition-all ${
              inputValue.trim() && !isTyping ? "bg-blue-500 text-white shadow-md active:scale-95" : darkMode ? "bg-gray-800 text-gray-600" : "bg-gray-100 text-gray-400"
            }`}>
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
