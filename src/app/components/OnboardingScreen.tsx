import { useState } from "react";
import { Mic, Search, ShieldCheck, ChevronRight, Pill, Activity, Thermometer, Wind, Zap } from "lucide-react";
import { motion } from "motion/react";

const SYMPTOM_CHIPS = ["Headache", "Fever", "Cough", "Stomach Pain", "Allergies", "Back Pain", "Sore Throat", "Fatigue"];

const FEATURE_CARDS = [
  { icon: <Activity className="w-5 h-5" />, title: "Symptom Analysis", desc: "AI-powered assessment of your symptoms in seconds", color: "bg-blue-500" },
  { icon: <Pill className="w-5 h-5" />, title: "Medicine Guidance", desc: "Clear explanations of dosage, effects, and warnings", color: "bg-teal-500" },
  { icon: <Thermometer className="w-5 h-5" />, title: "Track History", desc: "Keep a record of past consultations for your doctor", color: "bg-indigo-500" },
  { icon: <Wind className="w-5 h-5" />, title: "Find Nearby", desc: "Locate pharmacies and clinics open near you now", color: "bg-purple-500" },
];

interface OnboardingScreenProps {
  onStart: (symptom: string) => void;
  darkMode: boolean;
}

export function OnboardingScreen({ onStart, darkMode }: OnboardingScreenProps) {
  const [inputValue, setInputValue] = useState("");
  const [isListening, setIsListening] = useState(false);

  const handleSubmit = () => {
    if (inputValue.trim()) onStart(inputValue.trim());
  };

  const toggleVoice = () => {
    setIsListening((v) => !v);
    if (!isListening) setTimeout(() => setIsListening(false), 3000);
  };

  return (
    <div className={`${darkMode ? "bg-gray-950" : "bg-gradient-to-br from-blue-50 via-white to-teal-50"}`}>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">

        {/* Hero section */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:gap-16 mb-10 lg:mb-14">
          {/* Left: text + input */}
          <div className="flex-1 lg:max-w-xl">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="flex items-center gap-2 mb-4"
            >
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${darkMode ? "bg-blue-900/50 text-blue-300 border border-blue-700/40" : "bg-blue-100 text-blue-700"}`}>
                AI-Powered
              </span>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${darkMode ? "bg-teal-900/50 text-teal-300 border border-teal-700/40" : "bg-teal-100 text-teal-700"}`}>
                Free to use
              </span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1, duration: 0.5 }}
              className={`mb-4 ${darkMode ? "text-white" : "text-blue-900"}`}
              style={{ fontSize: "clamp(26px, 4vw, 40px)", fontWeight: 800, lineHeight: 1.2 }}
            >
              Describe your symptoms and I'll help you find the right care
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className={`mb-6 ${darkMode ? "text-gray-400" : "text-gray-500"}`}
              style={{ fontSize: "16px", lineHeight: 1.7 }}
            >
              Get instant, evidence-based medicine recommendations from our pharmaceutical AI. Available 24/7, completely private.
            </motion.p>

            {/* Input card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              className={`rounded-2xl shadow-lg overflow-hidden mb-4 ${darkMode ? "bg-gray-800 border border-gray-700" : "bg-white border border-blue-100"}`}
            >
              <div className="flex items-start gap-3 p-4">
                <Search className={`w-5 h-5 mt-1 flex-shrink-0 ${darkMode ? "text-blue-400" : "text-blue-400"}`} />
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="e.g. I have a throbbing headache and feel nauseous since this morning..."
                  className={`flex-1 resize-none outline-none bg-transparent min-h-[80px] ${darkMode ? "text-white placeholder-gray-500" : "text-gray-800 placeholder-gray-400"}`}
                  style={{ fontSize: "16px" }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSubmit(); }
                  }}
                />
              </div>
              <div className={`flex items-center justify-between px-3 py-2 border-t ${darkMode ? "border-gray-700" : "border-gray-100"}`}>
                <button
                  onClick={toggleVoice}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-lg transition-all whitespace-nowrap ${
                    isListening ? "bg-red-100 text-red-500" : darkMode ? "bg-gray-700 text-blue-400" : "bg-blue-50 text-blue-500"
                  }`}
                >
                  <Mic className="w-4 h-4 flex-shrink-0" />
                  <span style={{ fontSize: "13px" }}>{isListening ? "Listening..." : "Voice input"}</span>
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={!inputValue.trim()}
                  className={`flex items-center gap-1.5 px-4 py-2 rounded-lg font-semibold transition-all whitespace-nowrap ${
                    inputValue.trim() ? "bg-blue-500 text-white shadow-md active:scale-95" : darkMode ? "bg-gray-700 text-gray-500" : "bg-gray-100 text-gray-400"
                  }`}
                  style={{ fontSize: "13px" }}
                >
                  Analyze Symptoms
                  <ChevronRight className="w-3.5 h-3.5 flex-shrink-0" />
                </button>
              </div>
            </motion.div>

            {/* Chips */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.45, duration: 0.4 }}
            >
              <p className={`mb-2 ${darkMode ? "text-gray-500" : "text-gray-400"}`} style={{ fontSize: "12px", fontWeight: 500 }}>
                Quick select:
              </p>
              <div className="flex flex-wrap gap-2">
                {SYMPTOM_CHIPS.map((chip) => (
                  <button
                    key={chip}
                    onClick={() => setInputValue(chip)}
                    className={`px-3 py-1.5 rounded-full min-h-[36px] transition-all ${
                      inputValue === chip
                        ? "bg-blue-500 text-white shadow"
                        : darkMode
                        ? "bg-gray-800 text-gray-300 border border-gray-700 hover:border-blue-600"
                        : "bg-white text-gray-700 border border-gray-200 hover:border-blue-300 shadow-sm"
                    }`}
                    style={{ fontSize: "13px" }}
                  >
                    {chip}
                  </button>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Right: illustration (hidden on small screens) */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="hidden lg:flex flex-col items-center justify-center"
          >
            <div className="relative">
              <div className="w-56 h-56 rounded-full bg-gradient-to-br from-blue-400 to-teal-400 flex items-center justify-center shadow-2xl">
                <svg width="96" height="96" viewBox="0 0 96 96" fill="none">
                  <rect x="16" y="44" width="64" height="8" rx="4" fill="white" opacity="0.9" />
                  <rect x="44" y="16" width="8" height="64" rx="4" fill="white" opacity="0.9" />
                </svg>
              </div>
              {/* Floating badges */}
              <div className={`absolute -top-4 -right-6 px-3 py-2 rounded-xl shadow-lg ${darkMode ? "bg-gray-800 border border-gray-700" : "bg-white border border-gray-100"}`}>
                <p className={`${darkMode ? "text-white" : "text-gray-900"}`} style={{ fontSize: "13px", fontWeight: 700 }}>500+</p>
                <p className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "11px" }}>Medicines</p>
              </div>
              <div className={`absolute -bottom-4 -left-6 px-3 py-2 rounded-xl shadow-lg ${darkMode ? "bg-gray-800 border border-gray-700" : "bg-white border border-gray-100"}`}>
                <p className="text-green-500" style={{ fontSize: "13px", fontWeight: 700 }}>99.2%</p>
                <p className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "11px" }}>Accuracy</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Feature cards grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8"
        >
          {FEATURE_CARDS.map((card, i) => (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + i * 0.08 }}
              className={`rounded-2xl p-4 ${darkMode ? "bg-gray-800/60 border border-gray-700/60" : "bg-white border border-gray-100 shadow-sm"}`}
            >
              <div className={`w-9 h-9 rounded-xl ${card.color} flex items-center justify-center text-white mb-3`}>
                {card.icon}
              </div>
              <p className={`mb-1 ${darkMode ? "text-white" : "text-gray-900"}`} style={{ fontSize: "14px", fontWeight: 600 }}>
                {card.title}
              </p>
              <p className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "12px", lineHeight: 1.5 }}>
                {card.desc}
              </p>
            </motion.div>
          ))}
        </motion.div>

        {/* Disclaimer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
          className={`p-4 rounded-2xl flex gap-3 ${darkMode ? "bg-amber-950/40 border border-amber-800/30" : "bg-amber-50 border border-amber-200"}`}
        >
          <ShieldCheck className={`w-5 h-5 flex-shrink-0 mt-0.5 ${darkMode ? "text-amber-400" : "text-amber-600"}`} />
          <p className={`${darkMode ? "text-amber-300" : "text-amber-700"}`} style={{ fontSize: "13px", lineHeight: 1.6 }}>
            <strong>Medical Disclaimer:</strong> MediGuide is an informational tool only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider before starting any medication.
          </p>
        </motion.div>
      </div>
    </div>
  );
}
