const BASE = "/api";

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
    send: (message: string) =>
      request<{ ack: string; medicine: any }>("/chat", {
        method: "POST",
        body: JSON.stringify({ message }),
      }),
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
