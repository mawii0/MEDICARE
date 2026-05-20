import { useState } from "react";
import { MapPin, Clock, Navigation, Share2, Star, Phone } from "lucide-react";
import { motion } from "motion/react";

interface Pharmacy {
  id: string;
  name: string;
  type: "pharmacy" | "clinic";
  distance: string;
  address: string;
  isOpen: boolean;
  closingTime: string;
  rating: number;
  services: string[];
  phone: string;
  otcAvailable: boolean;
  prescriptionAvailable: boolean;
}

const PHARMACIES: Pharmacy[] = [
  { id: "1", name: "MediCare Pharmacy", type: "pharmacy", distance: "0.3 km", address: "12 Health Street, Central", isOpen: true, closingTime: "10:00 PM", rating: 4.8, services: ["Prescription filling", "24h service", "Home delivery"], phone: "+1-555-0101", otcAvailable: true, prescriptionAvailable: true },
  { id: "2", name: "City Health Clinic", type: "clinic", distance: "0.7 km", address: "45 Wellness Ave, Downtown", isOpen: true, closingTime: "8:00 PM", rating: 4.6, services: ["Doctor consultation", "Prescription writing", "Lab tests"], phone: "+1-555-0102", otcAvailable: false, prescriptionAvailable: true },
  { id: "3", name: "QuickMeds Express", type: "pharmacy", distance: "1.1 km", address: "78 Market Rd, Eastside", isOpen: true, closingTime: "Midnight", rating: 4.4, services: ["Prescription filling", "OTC medicines", "Vitamins"], phone: "+1-555-0103", otcAvailable: true, prescriptionAvailable: true },
  { id: "4", name: "WellCare Medical Center", type: "clinic", distance: "1.5 km", address: "23 Care Lane, Westfield", isOpen: false, closingTime: "Opens at 8:00 AM", rating: 4.9, services: ["Doctor consultation", "Specialist referrals", "Emergency care"], phone: "+1-555-0104", otcAvailable: false, prescriptionAvailable: true },
  { id: "5", name: "NightOwl Pharmacy", type: "pharmacy", distance: "2.0 km", address: "56 Night Street, Northside", isOpen: true, closingTime: "24 hours", rating: 4.3, services: ["24h service", "Prescription filling", "Emergency meds"], phone: "+1-555-0105", otcAvailable: true, prescriptionAvailable: true },
  { id: "6", name: "GreenLeaf Wellness", type: "clinic", distance: "2.3 km", address: "90 Holistic Blvd, Midtown", isOpen: true, closingTime: "7:00 PM", rating: 4.7, services: ["Doctor consultation", "Vaccination", "Blood tests"], phone: "+1-555-0106", otcAvailable: false, prescriptionAvailable: true },
];

const SERVICE_COLORS: Record<string, string> = {
  "24h service": "bg-purple-100 text-purple-700",
  "Home delivery": "bg-blue-100 text-blue-700",
  "Doctor consultation": "bg-teal-100 text-teal-700",
  "Prescription filling": "bg-green-100 text-green-700",
  "Emergency care": "bg-red-100 text-red-700",
  default: "bg-gray-100 text-gray-600",
};

function MapView({ darkMode }: { darkMode: boolean }) {
  const pins = [
    { x: "22%", y: "32%", label: "0.3km", color: "#22c55e" },
    { x: "48%", y: "52%", label: "0.7km", color: "#3b82f6" },
    { x: "66%", y: "27%", label: "1.1km", color: "#22c55e" },
    { x: "18%", y: "63%", label: "1.5km", color: "#6b7280" },
    { x: "72%", y: "65%", label: "2.0km", color: "#a855f7" },
    { x: "85%", y: "40%", label: "2.3km", color: "#14b8a6" },
  ];

  return (
    <div className={`relative w-full rounded-2xl overflow-hidden ${darkMode ? "bg-gray-800" : "bg-blue-50"}`} style={{ height: "clamp(180px, 25vw, 280px)" }}>
      <svg width="100%" height="100%" className="absolute inset-0 opacity-30">
        <defs>
          <pattern id="grid2" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke={darkMode ? "#4b5563" : "#93c5fd"} strokeWidth="0.5" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid2)" />
        <line x1="0" y1="80" x2="100%" y2="80" stroke={darkMode ? "#374151" : "#bfdbfe"} strokeWidth="3" />
        <line x1="0" y1="140" x2="100%" y2="140" stroke={darkMode ? "#374151" : "#bfdbfe"} strokeWidth="2" />
        <line x1="150" y1="0" x2="150" y2="100%" stroke={darkMode ? "#374151" : "#bfdbfe"} strokeWidth="3" />
        <line x1="300" y1="0" x2="300" y2="100%" stroke={darkMode ? "#374151" : "#bfdbfe"} strokeWidth="2" />
        <line x1="450" y1="0" x2="450" y2="100%" stroke={darkMode ? "#374151" : "#bfdbfe"} strokeWidth="2" />
      </svg>
      <div className="absolute" style={{ left: "46%", top: "44%", transform: "translate(-50%,-50%)" }}>
        <div className="w-5 h-5 rounded-full bg-blue-500 border-2 border-white shadow-lg flex items-center justify-center">
          <div className="w-2 h-2 rounded-full bg-white" />
        </div>
        <div className="absolute -bottom-5 left-1/2 -translate-x-1/2 bg-blue-500 text-white px-1.5 py-0.5 rounded text-xs whitespace-nowrap">You</div>
      </div>
      {pins.map((pin, i) => (
        <motion.div key={i} initial={{ scale: 0, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ delay: i * 0.1 + 0.3 }}
          className="absolute flex flex-col items-center" style={{ left: pin.x, top: pin.y, transform: "translate(-50%, -100%)" }}>
          <div className="w-8 h-8 rounded-full flex items-center justify-center shadow-md" style={{ backgroundColor: pin.color }}>
            <MapPin className="w-4 h-4 text-white" />
          </div>
          <div className="w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent" style={{ borderTopColor: pin.color }} />
          <span className="text-white px-1 py-0.5 rounded mt-0.5 shadow" style={{ backgroundColor: pin.color, fontSize: "10px" }}>{pin.label}</span>
        </motion.div>
      ))}
      <div className={`absolute bottom-2 right-2 px-2 py-1 rounded-lg ${darkMode ? "bg-gray-900/80" : "bg-white/90"} shadow text-xs ${darkMode ? "text-gray-400" : "text-gray-500"}`}>
        Simulated map
      </div>
    </div>
  );
}

interface PharmacyScreenProps {
  darkMode: boolean;
}

export function PharmacyScreen({ darkMode }: PharmacyScreenProps) {
  const [activeTab, setActiveTab] = useState<"otc" | "prescription">("otc");

  const filtered = PHARMACIES.filter((p) => activeTab === "otc" ? p.otcAvailable : p.prescriptionAvailable);

  return (
    <div className={`${darkMode ? "bg-gray-950" : "bg-gray-50"}`}>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">

        {/* Page header */}
        <div className="mb-6">
          <h2 className={`${darkMode ? "text-white" : "text-gray-900"}`} style={{ fontSize: "24px", fontWeight: 700 }}>Find Nearby</h2>
          <p className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "14px" }}>Pharmacies and clinics near your location</p>
        </div>

        <div className="grid lg:grid-cols-5 gap-6">
          {/* Left: map + filters */}
          <div className="lg:col-span-2 space-y-4">
            <MapView darkMode={darkMode} />

            <button className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-500 to-teal-500 text-white flex items-center justify-center gap-2 min-h-[48px] shadow-md"
              style={{ fontSize: "14px", fontWeight: 600 }}>
              <Share2 className="w-4 h-4" />
              Send Recommendation to Pharmacist
            </button>

            {/* Legend */}
            <div className={`rounded-2xl p-4 ${darkMode ? "bg-gray-800 border border-gray-700" : "bg-white border border-gray-100 shadow-sm"}`}>
              <p className={`mb-3 ${darkMode ? "text-gray-300" : "text-gray-700"}`} style={{ fontSize: "13px", fontWeight: 600 }}>Map Legend</p>
              <div className="space-y-2">
                {[
                  { color: "#22c55e", label: "Pharmacy (OTC available)" },
                  { color: "#3b82f6", label: "Clinic (consultation)" },
                  { color: "#a855f7", label: "Extended hours" },
                  { color: "#6b7280", label: "Currently closed" },
                ].map((item) => (
                  <div key={item.label} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
                    <span className={`${darkMode ? "text-gray-400" : "text-gray-600"}`} style={{ fontSize: "12px" }}>{item.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right: list */}
          <div className="lg:col-span-3 space-y-4">
            {/* Tabs */}
            <div className={`flex rounded-xl p-1 ${darkMode ? "bg-gray-800" : "bg-gray-100"}`}>
              {[{ key: "otc", label: "Over-the-Counter" }, { key: "prescription", label: "Get Prescription" }].map((tab) => (
                <button key={tab.key} onClick={() => setActiveTab(tab.key as "otc" | "prescription")}
                  className={`flex-1 py-2.5 rounded-lg transition-all min-h-[44px] ${
                    activeTab === tab.key ? darkMode ? "bg-blue-600 text-white shadow" : "bg-white text-blue-600 shadow" : darkMode ? "text-gray-400" : "text-gray-500"
                  }`}
                  style={{ fontSize: "13px", fontWeight: 600 }}>
                  {tab.label}
                </button>
              ))}
            </div>

            <div className="space-y-3">
              {filtered.map((pharmacy, i) => (
                <motion.div key={pharmacy.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}
                  className={`rounded-2xl overflow-hidden ${darkMode ? "bg-gray-800 border border-gray-700" : "bg-white border border-gray-100 shadow-sm"}`}>
                  <div className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-start gap-3">
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${pharmacy.type === "pharmacy" ? darkMode ? "bg-green-900/40" : "bg-green-50" : darkMode ? "bg-blue-900/40" : "bg-blue-50"}`}>
                          <span style={{ fontSize: "20px" }}>{pharmacy.type === "pharmacy" ? "💊" : "🏥"}</span>
                        </div>
                        <div>
                          <p className={`${darkMode ? "text-white" : "text-gray-900"}`} style={{ fontSize: "15px", fontWeight: 600 }}>{pharmacy.name}</p>
                          <div className="flex items-center gap-1 mt-0.5">
                            <MapPin className={`w-3 h-3 ${darkMode ? "text-gray-500" : "text-gray-400"}`} />
                            <span className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "12px" }}>{pharmacy.address}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-1 ml-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${pharmacy.isOpen ? darkMode ? "bg-green-900/40 text-green-400" : "bg-green-50 text-green-600" : darkMode ? "bg-gray-700 text-gray-400" : "bg-gray-100 text-gray-500"}`}>
                          {pharmacy.isOpen ? "Open Now" : "Closed"}
                        </span>
                        <span className={`${darkMode ? "text-blue-400" : "text-blue-500"}`} style={{ fontSize: "13px", fontWeight: 600 }}>{pharmacy.distance}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 mb-3">
                      <div className="flex items-center gap-1">
                        <Clock className={`w-3 h-3 ${darkMode ? "text-gray-500" : "text-gray-400"}`} />
                        <span className={`${darkMode ? "text-gray-400" : "text-gray-500"}`} style={{ fontSize: "12px" }}>
                          {pharmacy.isOpen ? `Closes ${pharmacy.closingTime}` : pharmacy.closingTime}
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                        <span className={`${darkMode ? "text-gray-300" : "text-gray-700"}`} style={{ fontSize: "12px", fontWeight: 600 }}>{pharmacy.rating}</span>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-1.5 mb-3">
                      {pharmacy.services.map((s) => (
                        <span key={s} className={`px-2 py-1 rounded-full text-xs ${SERVICE_COLORS[s] || SERVICE_COLORS.default}`}>{s}</span>
                      ))}
                    </div>

                    <div className="flex gap-2">
                      <button className={`flex-1 py-2.5 rounded-xl flex items-center justify-center gap-1.5 min-h-[44px] ${darkMode ? "bg-blue-600 text-white" : "bg-blue-500 text-white"}`}
                        style={{ fontSize: "13px", fontWeight: 600 }}>
                        <Navigation className="w-4 h-4" />
                        Directions
                      </button>
                      <button className={`flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl min-h-[44px] ${darkMode ? "bg-gray-700 text-gray-300" : "bg-gray-100 text-gray-700"}`}
                        style={{ fontSize: "13px", fontWeight: 600 }}>
                        <Phone className="w-4 h-4" />
                        Call
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
