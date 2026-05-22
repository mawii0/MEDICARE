import { useState } from "react";
import { ArrowRight, Pill, MapPin, Languages, Bot, Shield, Activity, AlertTriangle } from "lucide-react";
import { motion } from "motion/react";

const SYMPTOM_CHIPS = [
  "Headache", "Fever", "Cough", "Stomach Pain", "Allergies",
  "Amoxicillin price", "Biogesic dosage", "Neozep side effects",
];

const FEATURES = [
  { icon: <Bot className="w-5 h-5" />, title: "AI Symptom Analysis", desc: "Fine-tuned TinyLlama with BM25 retrieval from 80+ PH drugs" },
  { icon: <Pill className="w-5 h-5" />, title: "PH Drug Database", desc: "Filipino brand names, prices in PHP, availability at Mercury Drug & more" },
  { icon: <Languages className="w-5 h-5" />, title: "Bilingual Support", desc: "English and Taglish — responds in the language you use" },
  { icon: <MapPin className="w-5 h-5" />, title: "Find Nearby", desc: "Locate pharmacies and clinics near you with real-time map" },
];

interface OnboardingScreenProps {
  onStart: (symptom: string) => void;
  darkMode: boolean;
}

export function OnboardingScreen({ onStart, darkMode }: OnboardingScreenProps) {
  const [inputValue, setInputValue] = useState("");

  const handleSubmit = () => {
    if (inputValue.trim()) onStart(inputValue.trim());
  };

  return (
    <div className={`min-h-full ${darkMode ? "bg-[#09090b]" : "bg-[#fafafa]"}`}>
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-12 lg:py-20">

        {/* Hero */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>

          <h1 className={`text-3xl sm:text-4xl font-bold mb-3 leading-tight ${darkMode ? "text-white" : "text-gray-900"}`}>
            Pharmacare
          </h1>
          <p className={`text-base mb-8 max-w-xl leading-relaxed ${darkMode ? "text-gray-400" : "text-gray-500"}`}>
            Track symptoms, review medicine details, and get clear guidance in one place.
          </p>
        </motion.div>

        {/* Input */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1, duration: 0.4 }}>
          <div className={`rounded-xl border overflow-hidden mb-3 ${darkMode ? "bg-gray-900 border-gray-800" : "bg-white border-gray-200"}`}>
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Describe your symptoms..."
              className={`w-full px-4 py-3 resize-none outline-none bg-transparent min-h-[80px] text-sm ${darkMode ? "text-white placeholder-gray-600" : "text-gray-900 placeholder-gray-400"}`}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSubmit(); } }}
            />
            <div className={`flex items-center justify-between px-4 py-2.5 border-t ${darkMode ? "border-gray-800" : "border-gray-100"}`}>
              <span className={`text-xs ${darkMode ? "text-gray-600" : "text-gray-400"}`}>
                Shift+Enter for new line
              </span>
              <button onClick={handleSubmit} disabled={!inputValue.trim()}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  inputValue.trim()
                    ? "bg-blue-600 text-white hover:bg-blue-700"
                    : darkMode ? "bg-gray-800 text-gray-600" : "bg-gray-100 text-gray-400"
                }`}>
                Ask Pharmacare
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Chips */}
          <div className="flex flex-wrap gap-1.5">
            {SYMPTOM_CHIPS.map((chip) => (
              <button key={chip} onClick={() => setInputValue(chip)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  inputValue === chip
                    ? "bg-blue-600 text-white"
                    : darkMode
                      ? "bg-gray-900 text-gray-400 border border-gray-800 hover:border-gray-700"
                      : "bg-white text-gray-600 border border-gray-200 hover:border-gray-300"
                }`}>
                {chip}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Features */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2, duration: 0.4 }}
          className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-12">
          {FEATURES.map((f, i) => (
            <div key={i} className={`p-4 rounded-xl border ${darkMode ? "bg-gray-900 border-gray-800" : "bg-white border-gray-200"}`}>
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center mb-3 ${darkMode ? "bg-gray-800 text-gray-300" : "bg-gray-100 text-gray-600"}`}>
                {f.icon}
              </div>
              <h3 className={`text-sm font-semibold mb-1 ${darkMode ? "text-white" : "text-gray-900"}`}>{f.title}</h3>
              <p className={`text-xs leading-relaxed ${darkMode ? "text-gray-500" : "text-gray-500"}`}>{f.desc}</p>
            </div>
          ))}
        </motion.div>

        {/* Pipeline */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3, duration: 0.4 }}
          className={`mt-6 p-4 rounded-xl border ${darkMode ? "bg-gray-900 border-gray-800" : "bg-white border-gray-200"}`}>
          <div className="flex items-center gap-2 mb-3">
            <Activity className={`w-4 h-4 ${darkMode ? "text-gray-400" : "text-gray-500"}`} />
            <span className={`text-xs font-semibold ${darkMode ? "text-gray-300" : "text-gray-700"}`}>NLP Pipeline</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {["Text Preprocessing", "TF-IDF Classification", "BM25 Retrieval", "Word2Vec", "QLoRA LoRA", "Safety Guardrails"].map((s) => (
              <span key={s} className={`px-2 py-1 rounded text-xs ${darkMode ? "bg-gray-800 text-gray-400" : "bg-gray-100 text-gray-500"}`}>
                {s}
              </span>
            ))}
          </div>
        </motion.div>

        {/* Safety */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.35, duration: 0.4 }}
          className={`mt-3 p-4 rounded-xl border ${darkMode ? "bg-gray-900 border-gray-800" : "bg-white border-gray-200"}`}>
          <div className="flex items-center gap-2 mb-3">
            <Shield className={`w-4 h-4 ${darkMode ? "text-gray-400" : "text-gray-500"}`} />
            <span className={`text-xs font-semibold ${darkMode ? "text-gray-300" : "text-gray-700"}`}>Safety Features</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {["Rx Restriction", "RA 9165 Controlled Substance", "Mandatory Disclaimer"].map((s) => (
              <span key={s} className={`px-2 py-1 rounded text-xs ${darkMode ? "bg-red-950 text-red-400 border border-red-900" : "bg-red-50 text-red-600 border border-red-100"}`}>
                {s}
              </span>
            ))}
          </div>
        </motion.div>

        {/* Disclaimer */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4, duration: 0.4 }}
          className={`mt-6 p-4 rounded-xl flex gap-3 ${darkMode ? "bg-amber-950/30 border border-amber-900/50" : "bg-amber-50 border border-amber-200"}`}>
          <AlertTriangle className={`w-4 h-4 flex-shrink-0 mt-0.5 ${darkMode ? "text-amber-400" : "text-amber-500"}`} />
          <p className={`text-xs leading-relaxed ${darkMode ? "text-amber-300" : "text-amber-700"}`}>
            <strong>Medical Disclaimer:</strong> Pharmacare is an educational NLP tool. It is not a substitute for professional medical advice. Always consult a licensed physician or pharmacist before taking any medication.
          </p>
        </motion.div>
      </div>
    </div>
  );
}
