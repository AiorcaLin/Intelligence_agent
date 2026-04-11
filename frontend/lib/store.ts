import { create } from "zustand";
import { creditAPI, subscriptionAPI } from "@/lib/api";

export interface User {
  id: string;
  name: string;
  email: string;
  tokenBalance: number;
  freeCreditsRemaining: number;
  industry?: string;
  company?: string;
}

export interface Subscription {
  id: string;
  name: string;
  domain: string;
  customKeywords?: string[];
  density: "brief" | "standard" | "research";
  formats: string[];
  frequency: "daily" | "weekly" | "breaking";
  pushTime: string;
  templateId?: string;
  isActive: boolean;
  createdAt: string;
}

export interface ReportItem {
  id: string;
  title: string;
  summary: string;
  importanceScore: number;
  domain: string;
  sources: { name: string; url: string }[];
  actionItems: string[];
  isImportant: boolean;
  historyItems?: HistoryItem[];
}

export interface Report {
  id: string;
  date: string;
  subscriptionId: string;
  items: ReportItem[];
}

export interface HistoryItem {
  date: string;
  title: string;
  summary: string;
}

interface AppState {
  user: User | null;
  subscriptions: Subscription[];
  currentReport: Report | null;
  todayReports: Report[];

  setUser: (user: User | null) => void;
  setSubscriptions: (subs: Subscription[]) => void;
  setCurrentReport: (report: Report | null) => void;
  setTodayReports: (reports: Report[]) => void;

  fetchUser: () => Promise<void>;
  fetchSubscriptions: () => Promise<void>;
}

export const useStore = create<AppState>((set) => ({
  user: null,
  subscriptions: [],
  currentReport: null,
  todayReports: [],

  setUser: (user) => set({ user }),
  setSubscriptions: (subscriptions) => set({ subscriptions }),
  setCurrentReport: (currentReport) => set({ currentReport }),
  setTodayReports: (todayReports) => set({ todayReports }),

  fetchUser: async () => {
    try {
      const { data } = await creditAPI.balance();
      set((state) => ({
        user: state.user
          ? { ...state.user, tokenBalance: data.balance, freeCreditsRemaining: data.freeRemaining }
          : null,
      }));
    } catch {
      // silent fail
    }
  },

  fetchSubscriptions: async () => {
    try {
      const { data } = await subscriptionAPI.list();
      set({ subscriptions: data });
    } catch {
      // silent fail
    }
  },
}));
