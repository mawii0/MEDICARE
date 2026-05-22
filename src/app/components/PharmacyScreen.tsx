import { useState, useEffect, useRef } from "react";
import { MapPin, Clock, Navigation, Phone, Loader2, Locate } from "lucide-react";
import { motion } from "motion/react";
import L from "leaflet";
import { api } from "../../lib/api";

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
  lat: number;
  lng: number;
}

function makeIcon(color: string): L.DivIcon {
  return L.divIcon({
    className: "",
    iconSize: [28, 36],
    iconAnchor: [14, 36],
    popupAnchor: [0, -36],
    html: `<svg width="28" height="36" viewBox="0 0 28 36" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M14 0C6.268 0 0 6.268 0 14c0 10.5 14 22 14 22s14-11.5 14-22C28 6.268 21.732 0 14 0z" fill="${color}"/>
      <circle cx="14" cy="14" r="6" fill="white" opacity="0.9"/>
    </svg>`,
  });
}

const pharmacyIcon = makeIcon("#22c55e");
const clinicIcon = makeIcon("#3b82f6");
const userIcon = L.divIcon({
  className: "",
  iconSize: [20, 20],
  iconAnchor: [10, 10],
  html: `<div style="width:20px;height:20px;border-radius:50%;background:#2563eb;border:3px solid white;box-shadow:0 0 8px rgba(37,99,235,0.5)"></div>`,
});

function LeafletMap({ userPos, pharmacies, radiusKm }: { userPos: [number, number] | null; pharmacies: Pharmacy[]; radiusKm: number }) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<L.Layer[]>([]);

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;
    const map = L.map(mapRef.current, { zoomControl: false, scrollWheelZoom: true }).setView(userPos || [14.5995, 120.9842], 14);
    L.control.zoom({ position: "topright" }).addTo(map);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map);
    mapInstanceRef.current = map;
    return () => { map.remove(); mapInstanceRef.current = null; };
  }, []);

  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;
    markersRef.current.forEach(m => map.removeLayer(m));
    markersRef.current = [];

    if (userPos) {
      const um = L.marker(userPos, { icon: userIcon, zIndexOffset: 1000 }).addTo(map).bindPopup(`<div style="text-align:center"><strong>You are here</strong></div>`);
      markersRef.current.push(um);
      const circle = L.circle(userPos, { radius: radiusKm * 1000, color: "#3b82f6", fillColor: "#3b82f6", fillOpacity: 0.06, weight: 1.5, dashArray: "6 4" }).addTo(map);
      markersRef.current.push(circle);
    }

    pharmacies.forEach(p => {
      if (!p.lat || !p.lng) return;
      const icon = p.type === "pharmacy" ? pharmacyIcon : clinicIcon;
      const marker = L.marker([p.lat, p.lng], { icon }).addTo(map)
        .bindPopup(`<div style="min-width:180px;line-height:1.5">
          <div style="font-weight:600;font-size:14px">${p.name}</div>
          <div style="font-size:11px;color:#666;margin-top:2px">${p.type === "pharmacy" ? "Pharmacy" : "Clinic/Hospital"}</div>
          <div style="font-size:12px;color:#3b82f6;font-weight:500;margin-top:4px">${p.distance}</div>
          <div style="margin-top:6px">
            <a href="https://www.google.com/maps/dir/?api=1&destination=${p.lat},${p.lng}" target="_blank" rel="noopener" style="display:inline-block;padding:4px 10px;background:#2563eb;color:white;border-radius:6px;font-size:11px;text-decoration:none;font-weight:500">Directions</a>
            ${p.phone ? `<a href="tel:${p.phone}" style="display:inline-block;padding:4px 10px;background:#e5e7eb;color:#374151;border-radius:6px;font-size:11px;text-decoration:none;margin-left:4px;font-weight:500">Call</a>` : ""}
          </div>
        </div>`);
      markersRef.current.push(marker);
    });

    if (pharmacies.length > 0) {
      const bounds = L.latLngBounds(pharmacies.map(p => [p.lat, p.lng] as [number, number]));
      if (userPos) bounds.extend(userPos);
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 });
    } else if (userPos) {
      map.setView(userPos, 14);
    }
  }, [userPos, pharmacies, radiusKm]);

  return <div ref={mapRef} className="w-full rounded-xl overflow-hidden" style={{ height: "clamp(280px, 45vw, 400px)" }} />;
}

export function PharmacyScreen({ darkMode }: { darkMode: boolean }) {
  const [pharmacies, setPharmacies] = useState<Pharmacy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [userPos, setUserPos] = useState<[number, number] | null>(null);
  const [radiusKm, setRadiusKm] = useState(10);
  const [addressName, setAddressName] = useState("Detecting your location...");

  useEffect(() => {
    let cancelled = false;
    async function fetchPharmacies() {
      try {
        const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
          if (!navigator.geolocation) reject(new Error("Geolocation not supported"));
          navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 10000, enableHighAccuracy: true });
        });
        if (cancelled) return;
        const { latitude, longitude } = pos.coords;
        setUserPos([latitude, longitude]);

        fetch(`https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`, {
          headers: { "User-Agent": "PharmacareApp/1.0" },
        }).then(r => r.json()).then(d => { if (!cancelled && d.display_name) setAddressName(d.display_name.split(",").slice(0, 3).join(", ")); }).catch(() => {});

        const data = await api.pharmacy.nearby(latitude, longitude, radiusKm);
        if (cancelled) return;
        const mapped: Pharmacy[] = data.map((p: any) => {
          const nameRaw = (p.name || "").toLowerCase();
          const addr = (p.address || "").toLowerCase();
          const isPharmacy = p.type === "pharmacy" || /pharmacy|chemist|drugstore/i.test(nameRaw + " " + addr);
          const isClinic = /clinic|hospital|medical/i.test(nameRaw + " " + addr);
          return {
            id: p.id, name: p.name, type: isClinic && !isPharmacy ? "clinic" : isPharmacy ? "pharmacy" : "pharmacy",
            distance: p.distance, address: p.address, isOpen: p.isOpen, closingTime: "N/A", rating: 0, services: [],
            phone: p.phone, otcAvailable: isPharmacy, prescriptionAvailable: true, lat: p.lat, lng: p.lng,
          };
        });
        setPharmacies(mapped);
      } catch {
        if (!cancelled) { setError("Location access needed. Please enable location in your browser."); setUserPos([14.5995, 120.9842]); }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetchPharmacies();
    return () => { cancelled = true; };
  }, [radiusKm]);

  return (
    <div className={darkMode ? "bg-[#09090b]" : "bg-[#fafafa]"}>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 lg:py-8">
        {/* Header */}
        <div className="mb-4">
          <h2 className={`text-xl font-bold ${darkMode ? "text-white" : "text-gray-900"}`}>Find Nearby</h2>
          <p className={`flex items-center gap-1.5 mt-1 text-xs ${darkMode ? "text-gray-500" : "text-gray-400"}`}>
            <MapPin className="w-3 h-3 flex-shrink-0" />
            <span className="truncate">{addressName}</span>
          </p>
          {error && <p className="mt-1 text-xs text-amber-500">{error}</p>}
        </div>

        {/* Radius */}
        <div className="flex items-center gap-2 mb-4">
          <span className={`text-xs ${darkMode ? "text-gray-500" : "text-gray-400"}`}>Radius:</span>
          {[2, 5, 10, 20].map(r => (
            <button key={r} onClick={() => { setRadiusKm(r); setLoading(true); }}
              className={`px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${
                radiusKm === r ? "bg-blue-600 text-white" : darkMode ? "bg-gray-800 text-gray-400 hover:bg-gray-700" : "bg-gray-100 text-gray-500 hover:bg-gray-200"
              }`}>
              {r} km
            </button>
          ))}
          <span className={`ml-auto text-xs ${darkMode ? "text-gray-600" : "text-gray-400"}`}>
            {loading ? "Searching..." : `${pharmacies.length} found`}
          </span>
        </div>

        <div className="grid lg:grid-cols-5 gap-4">
          {/* Map */}
          <div className="lg:col-span-2 space-y-3">
            <div className="relative">
              <LeafletMap userPos={userPos} pharmacies={pharmacies} radiusKm={radiusKm} />
              <button onClick={() => {
                const map = document.querySelector(".leaflet-container") as any;
                if (map && map._leaflet_id && userPos) {
                  // Re-center handled by map instance
                }
              }} className="absolute bottom-3 right-3 z-[1000] w-8 h-8 rounded-md bg-white shadow flex items-center justify-center hover:bg-gray-50">
                <Locate className="w-4 h-4 text-blue-600" />
              </button>
            </div>

            {/* Legend */}
            <div className={`p-3 rounded-xl border ${darkMode ? "bg-gray-900 border-gray-800" : "bg-white border-gray-200"}`}>
              <p className={`text-xs font-semibold mb-2 ${darkMode ? "text-gray-300" : "text-gray-700"}`}>Map Legend</p>
              <div className="space-y-1.5">
                {[{ color: "#2563eb", label: "Your location" }, { color: "#22c55e", label: "Pharmacy" }, { color: "#3b82f6", label: "Clinic / Hospital" }].map(item => (
                  <div key={item.label} className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
                    <span className={`text-xs ${darkMode ? "text-gray-400" : "text-gray-500"}`}>{item.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* List */}
          <div className="lg:col-span-3 space-y-2">
            {loading && (
              <div className="flex flex-col items-center justify-center py-16">
                <Loader2 className="w-5 h-5 text-blue-600 animate-spin mb-2" />
                <p className={`text-sm ${darkMode ? "text-gray-500" : "text-gray-400"}`}>Searching nearby...</p>
              </div>
            )}
            {!loading && pharmacies.map((p, i) => (
              <motion.div key={p.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}
                className={`p-3.5 rounded-xl border ${darkMode ? "bg-gray-900 border-gray-800" : "bg-white border-gray-200"}`}>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-start gap-2.5">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 text-sm ${p.type === "pharmacy" ? darkMode ? "bg-green-950 text-green-400" : "bg-green-50" : darkMode ? "bg-blue-950 text-blue-400" : "bg-blue-50"}`}>
                      {p.type === "pharmacy" ? "\ud83d\udc8a" : "\ud83c\udfe5"}
                    </div>
                    <div>
                      <p className={`text-sm font-semibold ${darkMode ? "text-white" : "text-gray-900"}`}>{p.name}</p>
                      <div className="flex items-center gap-1 mt-0.5">
                        <MapPin className={`w-3 h-3 ${darkMode ? "text-gray-600" : "text-gray-400"}`} />
                        <span className={`text-xs truncate max-w-[200px] ${darkMode ? "text-gray-500" : "text-gray-400"}`}>{p.address}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1 ml-2 flex-shrink-0">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${p.isOpen ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                      {p.isOpen ? "Open" : "Closed"}
                    </span>
                    <span className={`text-xs font-semibold ${darkMode ? "text-blue-400" : "text-blue-600"}`}>{p.distance}</span>
                  </div>
                </div>

                <div className="flex gap-1.5">
                  <a href={`https://www.google.com/maps/dir/?api=1&destination=${p.lat},${p.lng}`} target="_blank" rel="noopener noreferrer"
                    className="flex-1 py-2 rounded-lg bg-blue-600 text-white flex items-center justify-center gap-1.5 text-xs font-medium hover:bg-blue-700 transition-colors">
                    <Navigation className="w-3.5 h-3.5" />Directions
                  </a>
                  {p.phone ? (
                    <a href={`tel:${p.phone}`}
                      className={`px-3 py-2 rounded-lg flex items-center gap-1.5 text-xs font-medium ${darkMode ? "bg-gray-800 text-gray-300" : "bg-gray-100 text-gray-700"}`}>
                      <Phone className="w-3.5 h-3.5" />Call
                    </a>
                  ) : (
                    <button disabled className={`px-3 py-2 rounded-lg flex items-center gap-1.5 text-xs ${darkMode ? "bg-gray-800 text-gray-600" : "bg-gray-50 text-gray-400"}`}>
                      <Phone className="w-3.5 h-3.5" />N/A
                    </button>
                  )}
                </div>
              </motion.div>
            ))}
            {!loading && pharmacies.length === 0 && !error && (
              <div className={`text-center py-16 ${darkMode ? "text-gray-600" : "text-gray-400"}`}>
                <MapPin className="w-6 h-6 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No pharmacies found within {radiusKm} km</p>
                <button onClick={() => { setRadiusKm(20); setLoading(true); }} className="mt-2 text-blue-600 text-xs font-medium">Expand to 20 km</button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
