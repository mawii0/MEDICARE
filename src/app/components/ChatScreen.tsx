import { useState, useRef, useEffect } from "react";
import { Send, Phone, ChevronDown, ChevronUp, AlertTriangle, Bookmark, BookmarkCheck, MapPin, Shield, DollarSign, Store } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { api, type MedicineCard, type ChatResponse } from "../../lib/api";

export interface Message {
  id: string;
  role: "user" | "bot";
  text?: string;
  symptomAck?: string;
  medicine?: MedicineCard;
  intent?: string;
  emergency?: boolean;
  rxFlag?: boolean;
  language?: string;
  timestamp: Date;
}

function TypingIndicator({ darkMode }: { darkMode: boolean }) {
  return (
    <div className="flex items-end gap-2.5 mb-4">
      <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-xs ${darkMode ? "bg-blue-950 text-blue-400" : "bg-blue-50 text-blue-600"}`}>
        {"\u2695\ufe0f"}
      </div>
      <div className={`px-4 py-3 rounded-2xl rounded-bl-sm ${darkMode ? "bg-gray-800" : "bg-white border border-gray-200"}`}>
        <div className="flex gap-1 items-center h-4">
          {[0, 1, 2].map((i) => (
            <motion.div key={i} className={`w-1.5 h-1.5 rounded-full ${darkMode ? "bg-gray-500" : "bg-gray-400"}`}
              animate={{ y: [0, -4, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }} />
          ))}
        </div>
      </div>
    </div>
  );
}

function EmergencyBanner({ darkMode, language }: { darkMode: boolean; language: string }) {
  return (
    <motion.div initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }}
      className={`rounded-xl overflow-hidden border ${darkMode ? "bg-red-950/50 border-red-900" : "bg-red-50 border-red-200"}`}>
      <div className="px-4 py-2.5 bg-red-600 flex items-center gap-2">
        <AlertTriangle className="w-4 h-4 text-white" />
        <p className="text-white text-sm font-semibold">
          {language === "tl" ? "EMERGENCY NA DETECTED" : "EMERGENCY DETECTED"}
        </p>
      </div>
      <div className="p-4">
        <p className={`mb-3 text-sm ${darkMode ? "text-red-300" : "text-red-700"}`}>
          {language === "tl"
            ? "Ang mga sintomas na iyong inilarawan ay maaaring mangailangan ng agarang medikal na tulong."
            : "The symptoms you described may require immediate medical attention."}
        </p>
        <div className="space-y-1.5">
          {[{ label: "Emergency", number: "911" }, { label: "Red Cross PH", number: "143" }, { label: "DOH Hotline", number: "1555" }].map(({ label, number }) => (
            <a key={number} href={`tel:${number}`}
              className={`flex items-center justify-between p-2.5 rounded-lg ${darkMode ? "bg-red-900/30" : "bg-white"} border ${darkMode ? "border-red-900" : "border-red-100"}`}>
              <span className={`text-sm ${darkMode ? "text-gray-200" : "text-gray-700"}`}>{label}</span>
              <span className="text-red-500 font-bold text-sm">{number}</span>
            </a>
          ))}
        </div>
      </div>
    </motion.div>
  );
}

function MedicineCardComponent({ med, darkMode, saved, onSave, onFindPharmacy, rxFlag }: {
  med: MedicineCard; darkMode: boolean; saved: boolean; onSave: () => void; onFindPharmacy: () => void; rxFlag?: boolean;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }}
      className={`rounded-xl overflow-hidden border ${darkMode ? "bg-gray-900 border-gray-800" : "bg-white border-gray-200"}`}>

      {/* Header */}
      <div className={`px-4 py-3 border-b ${darkMode ? "border-gray-800" : "border-gray-100"}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xl">{med.icon}</span>
            <div>
              <div className="flex items-center gap-2">
                <h3 className={`text-sm font-semibold ${darkMode ? "text-white" : "text-gray-900"}`}>{med.name}</h3>
                <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${med.otc ? "bg-green-100 text-green-700" : "bg-orange-100 text-orange-700"}`}>
                  {med.otc ? "OTC" : "Rx"}
                </span>
              </div>
              {med.drugClass && <p className={`text-xs ${darkMode ? "text-gray-500" : "text-gray-400"}`}>{med.drugClass}</p>}
            </div>
          </div>
          <button onClick={onSave} className={`p-1.5 rounded-lg ${darkMode ? "hover:bg-gray-800" : "hover:bg-gray-100"}`}>
            {saved ? <BookmarkCheck className="w-4 h-4 text-blue-500" /> : <Bookmark className={`w-4 h-4 ${darkMode ? "text-gray-500" : "text-gray-400"}`} />}
          </button>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Rx Warning */}
        {med.rxWarning && (
          <div className={`p-2.5 rounded-lg flex items-start gap-2 text-xs ${darkMode ? "bg-orange-950/30 border border-orange-900/50 text-orange-300" : "bg-orange-50 border border-orange-200 text-orange-700"}`}>
            <Shield className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
            {med.rxWarning}
          </div>
        )}

        {/* Brand Names */}
        {med.brandNames && (
          <div>
            <p className={`text-[11px] font-medium uppercase tracking-wider mb-1 ${darkMode ? "text-gray-500" : "text-gray-400"}`}>
              {med.language === "tl" ? "Mga Brand Name" : "Brand Names"}
            </p>
            <p className={`text-sm ${darkMode ? "text-white" : "text-gray-900"}`}>{med.brandNames}</p>
          </div>
        )}

        {/* What it does + Effects */}
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <p className={`text-[11px] font-medium uppercase tracking-wider mb-1 ${darkMode ? "text-gray-500" : "text-gray-400"}`}>
              {med.language === "tl" ? "Ginagawa" : "What It Does"}
            </p>
            <p className={`text-sm leading-relaxed ${darkMode ? "text-gray-300" : "text-gray-600"}`}>{med.whatItDoes}</p>
          </div>
          <div>
            <p className={`text-[11px] font-medium uppercase tracking-wider mb-1 ${darkMode ? "text-gray-500" : "text-gray-400"}`}>
              {med.language === "tl" ? "Mga Inaasahang Epekto" : "Expected Effects"}
            </p>
            <ul className="space-y-0.5">
              {med.effects.map((e, i) => (
                <li key={i} className={`text-sm flex items-start gap-1.5 ${darkMode ? "text-gray-300" : "text-gray-600"}`}>
                  <span className="text-green-500 mt-0.5 text-xs">{"\u2713"}</span>{e}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* How to take */}
        {(med.dosage || med.frequency || med.timing) && (
          <div>
            <p className={`text-[11px] font-medium uppercase tracking-wider mb-2 ${darkMode ? "text-gray-500" : "text-gray-400"}`}>
              {med.language === "tl" ? "Paano Uminom" : "How To Take"}
            </p>
            <div className="grid grid-cols-3 gap-2">
              {[
                { label: med.language === "tl" ? "Dosis" : "Dosage", value: med.dosage },
                { label: med.language === "tl" ? "Dalas" : "Frequency", value: med.frequency },
                { label: med.language === "tl" ? "Oras" : "Timing", value: med.timing },
              ].filter(item => item.value).map((item) => (
                <div key={item.label} className={`p-2.5 rounded-lg border ${darkMode ? "bg-gray-800 border-gray-700" : "bg-gray-50 border-gray-100"}`}>
                  <p className={`text-[10px] font-medium uppercase tracking-wider mb-0.5 ${darkMode ? "text-gray-500" : "text-gray-400"}`}>{item.label}</p>
                  <p className={`text-xs font-medium ${darkMode ? "text-white" : "text-gray-900"}`}>{item.value}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Price & Availability */}
        {(med.genericPrice || med.whereToFind) && (
          <div className={`p-3 rounded-lg border ${darkMode ? "bg-gray-800 border-gray-700" : "bg-gray-50 border-gray-100"}`}>
            <div className="flex items-center gap-1.5 mb-2">
              <DollarSign className={`w-3.5 h-3.5 ${darkMode ? "text-gray-400" : "text-gray-500"}`} />
              <p className={`text-[11px] font-medium uppercase tracking-wider ${darkMode ? "text-gray-400" : "text-gray-500"}`}>
                {med.language === "tl" ? "Presyo" : "Price & Availability"}
              </p>
            </div>
            <div className="grid grid-cols-2 gap-2 mb-2">
              {med.genericPrice && (
                <div>
                  <p className={`text-[10px] ${darkMode ? "text-gray-500" : "text-gray-400"}`}>Generic</p>
                  <p className="text-sm font-semibold text-green-600">{med.genericPrice}</p>
                </div>
              )}
              {med.brandedPrice && (
                <div>
                  <p className={`text-[10px] ${darkMode ? "text-gray-500" : "text-gray-400"}`}>Branded</p>
                  <p className={`text-sm font-semibold ${darkMode ? "text-white" : "text-gray-900"}`}>{med.brandedPrice}</p>
                </div>
              )}
            </div>
            {med.whereToFind && (
              <div className="flex items-start gap-1.5">
                <Store className={`w-3 h-3 mt-0.5 flex-shrink-0 ${darkMode ? "text-gray-500" : "text-gray-400"}`} />
                <p className={`text-xs ${darkMode ? "text-gray-400" : "text-gray-500"}`}>{med.whereToFind}</p>
              </div>
            )}
          </div>
        )}

        {/* Expandable side effects & warnings */}
        {(med.sideEffects.length > 0 || med.warnings.length > 0) && (
          <>
            <button onClick={() => setExpanded(v => !v)}
              className={`w-full flex items-center justify-between py-2 px-3 rounded-lg text-xs font-medium ${darkMode ? "bg-gray-800 text-gray-300" : "bg-gray-50 text-gray-600"}`}>
              {med.language === "tl" ? "Mga Epekto at Babala" : "Side Effects & Warnings"}
              {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
            <AnimatePresence>
              {expanded && (
                <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.2 }} className="overflow-hidden">
                  <div className="grid sm:grid-cols-2 gap-3">
                    {med.sideEffects.length > 0 && (
                      <div>
                        <p className={`text-[11px] font-medium uppercase tracking-wider mb-1 ${darkMode ? "text-gray-500" : "text-gray-400"}`}>
                          {med.language === "tl" ? "Mga Side Effect" : "Side Effects"}
                        </p>
                        <ul className="space-y-0.5">
                          {med.sideEffects.map((s, i) => (
                            <li key={i} className={`text-xs flex items-start gap-1.5 ${darkMode ? "text-gray-400" : "text-gray-500"}`}>
                              <span className="text-orange-400 mt-0.5">!</span>{s}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {med.warnings.length > 0 && (
                      <div>
                        <p className={`text-[11px] font-medium uppercase tracking-wider mb-1 ${darkMode ? "text-gray-500" : "text-gray-400"}`}>
                          {med.language === "tl" ? "Mga Babala" : "Warnings"}
                        </p>
                        <div className="flex flex-wrap gap-1">
                          {med.warnings.map((w) => (
                            <span key={w} className={`px-2 py-0.5 rounded text-[10px] font-medium ${darkMode ? "bg-red-950 text-red-400 border border-red-900" : "bg-red-50 text-red-600 border border-red-100"}`}>{w}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </>
        )}

        {/* Disclaimer */}
        {med.disclaimer && (
          <p className={`text-[11px] leading-relaxed ${darkMode ? "text-gray-600" : "text-gray-400"}`}>{med.disclaimer}</p>
        )}

        {/* Find Near Me */}
        <button onClick={onFindPharmacy}
          className="w-full py-2.5 rounded-lg bg-blue-600 text-white text-sm font-medium flex items-center justify-center gap-2 hover:bg-blue-700 transition-colors">
          <MapPin className="w-4 h-4" />
          {med.language === "tl" ? "Hanapin Malapit" : "Find Near Me"}
        </button>
      </div>
    </motion.div>
  );
}

interface ChatScreenProps {
  initialSymptom: string;
  darkMode: boolean;
  onNavigateToPharmacy: () => void;
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  autoSentSymptom: string | null;
  onAutoSentSymptom: (symptom: string) => void;
}

export function ChatScreen({ initialSymptom, darkMode, onNavigateToPharmacy, messages, setMessages, autoSentSymptom, onAutoSentSymptom }: ChatScreenProps) {
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [savedMeds, setSavedMeds] = useState<Set<string>>(new Set());
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (initialSymptom && autoSentSymptom !== initialSymptom) {
      sendMessage(initialSymptom, true);
      onAutoSentSymptom(initialSymptom);
    }
  }, [initialSymptom, autoSentSymptom, onAutoSentSymptom]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const sendMessage = async (text: string, _isInitial = false) => {
    const userMsg: Message = { id: Date.now().toString(), role: "user", text, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInputValue("");
    setIsTyping(true);
    try {
      const result = await api.chat.send(text);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: "bot",
        symptomAck: result.ack,
        medicine: result.medicine,
        intent: result.intent,
        emergency: result.emergency,
        rxFlag: result.rxFlag,
        language: result.language,
        timestamp: new Date(),
      }]);
      const severity = result.emergency ? "severe" : result.rxFlag ? "moderate" : "mild";
      api.history.add({ symptom: text, medicine: result.medicine.name, severity }).catch(() => {});
    } catch {
      setMessages(prev => [...prev, { id: (Date.now() + 1).toString(), role: "bot", text: "Sorry, something went wrong. Please try again.", timestamp: new Date() }]);
    } finally {
      setIsTyping(false);
    }
  };

  const toggleSave = (medName: string, med?: MedicineCard) => {
    const isSaved = savedMeds.has(medName);
    setSavedMeds(prev => { const n = new Set(prev); isSaved ? n.delete(medName) : n.add(medName); return n; });
    if (!isSaved && med) {
      api.savedMeds.add({
        name: med.name, use: med.whatItDoes?.slice(0, 80), icon: med.icon, stock: med.whereToFind || "",
        effects: med.effects, sideEffects: med.sideEffects, dosage: med.dosage, frequency: med.frequency,
        timing: med.timing, duration: med.duration, warnings: med.warnings,
      }).catch(() => {});
    }
  };

  return (
    <div className={`flex flex-col ${darkMode ? "bg-[#09090b]" : "bg-[#fafafa]"}`} style={{ height: "calc(100vh - 64px)" }}>
      {/* Header */}
      <div className={`px-4 lg:px-6 py-3 flex items-center gap-3 border-b flex-shrink-0 ${darkMode ? "bg-[#09090b] border-gray-800" : "bg-white border-gray-200"}`}>
        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${darkMode ? "bg-blue-950 text-blue-400" : "bg-blue-50 text-blue-600"}`}>
          {"\u2695\ufe0f"}
        </div>
        <div className="flex-1">
          <p className={`text-sm font-semibold ${darkMode ? "text-white" : "text-gray-900"}`}>Pharmacare Assistant</p>
          <p className={`text-[11px] ${darkMode ? "text-green-400" : "text-green-600"}`}>Ready to help</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 lg:px-6 py-4">
        <div className="max-w-2xl mx-auto space-y-3">
          {messages.length === 0 && !isTyping && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-16">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 ${darkMode ? "bg-blue-950" : "bg-blue-50"}`}>
                <span className="text-xl">{"\u2695\ufe0f"}</span>
              </div>
              <p className={`text-sm ${darkMode ? "text-gray-300" : "text-gray-600"}`}>
                Tell me your symptoms.
              </p>
              <p className={`text-xs mt-1 ${darkMode ? "text-gray-600" : "text-gray-400"}`}>
                English and Taglish supported
              </p>
            </motion.div>
          )}

          {messages.map((msg) => (
            <div key={msg.id}>
              {msg.role === "user" ? (
                <div className="flex justify-end mb-3">
                  <motion.div initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }}
                    className="max-w-md px-3.5 py-2.5 rounded-xl rounded-br-sm bg-blue-600 text-white text-sm">
                    {msg.text}
                  </motion.div>
                </div>
              ) : (
                <div className="flex items-end gap-2.5 mb-3">
                  <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-xs ${darkMode ? "bg-blue-950 text-blue-400" : "bg-blue-50 text-blue-600"}`}>
                    {"\u2695\ufe0f"}
                  </div>
                  <div className="flex-1 space-y-2.5 min-w-0">
                    {msg.emergency && msg.language && (
                      <EmergencyBanner darkMode={darkMode} language={msg.language} />
                    )}
                    {!msg.emergency && msg.symptomAck && (
                      <motion.div initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }}
                        className={`px-3.5 py-2.5 rounded-xl rounded-bl-sm text-sm leading-relaxed ${darkMode ? "bg-gray-800 text-gray-200" : "bg-white text-gray-700 border border-gray-200"}`}>
                        {msg.symptomAck.split("**").map((part, i) => i % 2 === 1 ? <strong key={i}>{part}</strong> : part)}
                      </motion.div>
                    )}
                    {msg.medicine && !msg.emergency && (
                      <MedicineCardComponent med={msg.medicine} darkMode={darkMode}
                        saved={savedMeds.has(msg.medicine.name)} onSave={() => toggleSave(msg.medicine!.name, msg.medicine!)}
                        onFindPharmacy={onNavigateToPharmacy} rxFlag={msg.rxFlag} />
                    )}
                    {!msg.medicine && !msg.emergency && msg.text && (
                      <motion.div initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }}
                        className={`px-3.5 py-2.5 rounded-xl rounded-bl-sm text-sm ${darkMode ? "bg-gray-800 text-gray-200" : "bg-white text-gray-700 border border-gray-200"}`}>
                        {msg.text}
                      </motion.div>
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

      {/* Input */}
      <div className={`px-4 lg:px-6 pb-4 pt-2 border-t flex-shrink-0 ${darkMode ? "bg-[#09090b] border-gray-800" : "bg-white border-gray-200"}`}>
        <div className="max-w-2xl mx-auto flex items-end gap-2">
          <div className={`flex-1 flex items-end rounded-xl px-3.5 py-2.5 border ${darkMode ? "bg-gray-900 border-gray-800" : "bg-gray-50 border-gray-200"}`}>
            <textarea value={inputValue} onChange={e => setInputValue(e.target.value)}
              placeholder="Describe your symptoms..."
              className={`flex-1 resize-none outline-none bg-transparent text-sm max-h-20 ${darkMode ? "text-white placeholder-gray-600" : "text-gray-900 placeholder-gray-400"}`}
              rows={1}
              onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); if (inputValue.trim()) sendMessage(inputValue.trim()); } }} />
          </div>
          <button onClick={() => inputValue.trim() && sendMessage(inputValue.trim())}
            disabled={!inputValue.trim() || isTyping}
            className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors ${
              inputValue.trim() && !isTyping ? "bg-blue-600 text-white" : darkMode ? "bg-gray-800 text-gray-600" : "bg-gray-100 text-gray-400"
            }`}>
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
