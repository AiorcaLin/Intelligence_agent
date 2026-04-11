import axios from "axios";
import { getAccessToken, storeTokens, clearTokens, getRefreshToken } from "@/lib/auth";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const refresh = getRefreshToken();
        if (refresh) {
          const { data } = await axios.post(
            `${api.defaults.baseURL}/auth/refresh`,
            { refresh_token: refresh }
          );
          storeTokens(data.access_token, data.refresh_token);
          original.headers.Authorization = `Bearer ${data.access_token}`;
          return api(original);
        }
      } catch {
        clearTokens();
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

// ── Auth ──
export const authAPI = {
  login: (email: string, password: string) =>
    api.post("/auth/login", { email, password }),
  register: (data: {
    email: string;
    password: string;
    name: string;
    industry?: string;
    company?: string;
  }) => api.post("/auth/register", data),
  refresh: (refreshToken: string) =>
    api.post("/auth/refresh", { refresh_token: refreshToken }),
};

// ── Subscriptions ──
export const subscriptionAPI = {
  list: () => api.get("/subscriptions"),
  create: (data: Record<string, unknown>) => api.post("/subscriptions", data),
  get: (id: string) => api.get(`/subscriptions/${id}`),
  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/subscriptions/${id}`, data),
  toggle: (id: string) => api.patch(`/subscriptions/${id}/toggle`),
  delete: (id: string) => api.delete(`/subscriptions/${id}`),
};

// ── Intel / Reports ──
export const intelAPI = {
  getToday: () => api.get("/intel/today"),
  getReport: (reportId: string) => api.get(`/intel/reports/${reportId}`),
  getHistory: (itemId: string) => api.get(`/intel/history/${itemId}`),
  regenerate: (reportId: string, feedback?: string) =>
    api.post(`/intel/reports/${reportId}/regenerate`, { feedback }),
  feedback: (reportId: string, data: Record<string, unknown>) =>
    api.post(`/intel/reports/${reportId}/feedback`, data),
};

// ── Templates / Cocreate ──
export const templateAPI = {
  list: (params?: { domain?: string; sort?: string }) =>
    api.get("/templates", { params }),
  get: (id: string) => api.get(`/templates/${id}`),
  lineage: (id: string) => api.get(`/templates/${id}/lineage`),
  tryTemplate: (id: string) => api.post(`/templates/${id}/try`),
  adopt: (id: string) => api.post(`/templates/${id}/adopt`),
  fork: (id: string, data: { name: string; description?: string }) =>
    api.post(`/templates/${id}/fork`, data),
};

// ── Credits ──
export const creditAPI = {
  balance: () => api.get("/credits/balance"),
  recharge: (data: { tier: string; paymentMethod: string }) =>
    api.post("/credits/recharge", data),
  records: (params?: { page?: number; limit?: number }) =>
    api.get("/credits/records", { params }),
  earnings: (params?: { page?: number; limit?: number }) =>
    api.get("/credits/earnings", { params }),
};

export default api;
