const BASE = "/api";
const NLP_BASE = "http://localhost:5000";

function getToken(): string | null {
  return localStorage.getItem("mediguide_token");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: "Request failed" }));
    throw new Error(body.error || `HTTP ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export interface MedicineCard {
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
  language?: string;
  brandNames?: string;
  drugClass?: string;
  genericPrice?: string;
  brandedPrice?: string;
  whereToFind?: string;
  rxWarning?: string;
  disclaimer?: string;
}

export interface ChatResponse {
  ack: string;
  medicine: MedicineCard;
  intent: string;
  emergency: boolean;
  rxFlag: boolean;
  language: string;
  latencySeconds: number;
}

function transformFlaskResponse(data: any): ChatResponse {
  const s = data.structured || {};
  const isEmergency = data.emergency === true;
  const isRx = data.rx_flag === true;
  const isControlled = data.intent === "controlled_substance_info";

  let icon = "\ud83d\udc8a";
  if (isEmergency) icon = "\u26a0\ufe0f";
  else if (isRx) icon = "\ud83d\udc8a";
  else if (data.intent === "side_effect_info") icon = "\u26a0\ufe0f";
  else if (data.intent === "price_inquiry") icon = "\ud83d\udcb0";

  const effects = s.indications
    ? s.indications.split(",").map((i: string) => i.trim()).filter(Boolean)
    : [];

  const sideEffects = s.common_side_effects
    ? s.common_side_effects.split(",").map((i: string) => i.trim()).filter(Boolean)
    : [];

  const warnings: string[] = [];
  if (isRx) warnings.push("Prescription Required");
  if (isControlled) warnings.push("Controlled Substance (RA 9165)");
  if (s.drug_class?.toLowerCase().includes("pregnancy")) warnings.push("Pregnancy");

  const dosageParts = s.dosage_adult?.split(/\s+every\s+/i) || [];
  const dosage = s.dosage_adult || "";
  const frequency = dosageParts.length > 1 ? `Every ${dosageParts[1]}` : "";

  let rxWarning: string | undefined;
  if (isRx && data.language === "tl") {
    rxWarning = "\u26a0\ufe0f PRESCRIPTION REQUIRED: Ang gamot na ito ay nangangailangan ng valid na reseta mula sa lisensyadong doktor sa Pilipinas.";
  } else if (isRx) {
    rxWarning = "\u26a0\ufe0f PRESCRIPTION REQUIRED: This medicine requires a valid prescription from a licensed physician in the Philippines.";
  }

  let disclaimer: string | undefined;
  if (data.language === "tl") {
    disclaimer = "Ang impormasyong ito ay para lamang sa pangkalahatang edukasyon at hindi kapalit ng propesyonal na medikal na payo. Laging kumonsulta sa lisensyadong doktor o parmasista bago uminom ng anumang gamot.";
  } else {
    disclaimer = "This information is for general educational purposes only and is not a substitute for professional medical advice. Always consult a licensed physician or pharmacist before taking any medication.";
  }

  return {
    ack: data.response || "",
    medicine: {
      name: s.drug_name || "Unknown",
      icon,
      whatItDoes: s.indications || "",
      effects,
      sideEffects,
      dosage,
      frequency,
      timing: s.instructions || "",
      duration: "",
      warnings,
      otc: !isRx,
      language: data.language || "en",
      brandNames: s.brand_names || "",
      drugClass: s.drug_class || "",
      genericPrice: s.generic_price || "",
      brandedPrice: s.branded_price || "",
      whereToFind: s.where_to_find || "",
      rxWarning,
      disclaimer,
    },
    intent: data.intent || "unknown",
    emergency: isEmergency,
    rxFlag: isRx,
    language: data.language || "en",
    latencySeconds: data.latency_seconds || 0,
  };
}

export const api = {
  auth: {
    register: (data: { email: string; password: string; name: string }) =>
      request<{ token: string; user: { id: number; email: string; name: string } }>("/auth/register", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    login: (data: { email: string; password: string }) =>
      request<{ token: string; user: { id: number; email: string; name: string } }>("/auth/login", {
        method: "POST",
        body: JSON.stringify(data),
      }),
  },

  chat: {
    send: async (message: string): Promise<ChatResponse> => {
      const res = await fetch(`${NLP_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({ error: "Request failed" }));
        throw new Error(body.error || `NLP API error: ${res.status}`);
      }
      const data = await res.json();
      return transformFlaskResponse(data);
    },
  },

  pharmacy: {
    nearby: (lat: number, lng: number, radius?: number) => {
      const params = new URLSearchParams({ lat: String(lat), lng: String(lng) });
      if (radius) params.set("radius", String(radius));
      return request<any[]>(`/pharmacy/nearby?${params}`);
    },
  },

  history: {
    list: () => request<any[]>("/history"),
    add: (data: { symptom: string; medicine: string; severity?: string }) =>
      request<any>("/history", { method: "POST", body: JSON.stringify(data) }),
    remove: (id: number | string) =>
      request<void>(`/history/${id}`, { method: "DELETE" }),
  },

  savedMeds: {
    list: () => request<any[]>("/saved-meds"),
    add: (data: { name: string; use?: string; icon?: string; stock?: string; effects?: string[]; sideEffects?: string[]; dosage?: string; frequency?: string; timing?: string; duration?: string; warnings?: string[] }) =>
      request<any>("/saved-meds", { method: "POST", body: JSON.stringify(data) }),
    remove: (id: number | string) =>
      request<void>(`/saved-meds/${id}`, { method: "DELETE" }),
  },
};
