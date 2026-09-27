const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      ...options,
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: "An error occurred" }));
      throw new Error(errorData.detail || `HTTP error! status: ${res.status}`);
    }

    return await res.json();
  } catch (err: any) {
    console.warn(`[API Warning] Endpoint ${endpoint} unreachable:`, err?.message || err);
    throw err;
  }
}

export const api = {
  // Competitors
  getCompetitors: (search?: string, status?: string) => {
    const params = new URLSearchParams();
    if (search) params.append("search", search);
    if (status) params.append("status", status);
    params.append("limit", "500");
    return fetchApi<any[]>(`/competitors?${params.toString()}`).catch(() => []);
  },
  getCompetitor: (id: number) => fetchApi<any>(`/competitors/${id}`),
  createCompetitor: (data: any) => fetchApi<any>("/competitors", { method: "POST", body: JSON.stringify(data) }),
  updateCompetitor: (id: number, data: any) => fetchApi<any>(`/competitors/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteCompetitor: (id: number) => fetchApi<any>(`/competitors/${id}`, { method: "DELETE" }),
  analyzeCompetitor: (id: number) => fetchApi<any>(`/competitors/${id}/analyze`, { method: "POST" }),
  checkCompetitorNow: (id: number) => fetchApi<any>(`/competitors/${id}/check-now`, { method: "POST" }),
  pauseCompetitor: (id: number) => fetchApi<any>(`/competitors/${id}/pause`, { method: "POST" }),
  resumeCompetitor: (id: number) => fetchApi<any>(`/competitors/${id}/resume`, { method: "POST" }),

  // Articles
  getArticles: (params?: { competitor_id?: number; search?: string; method?: string; within_target?: boolean; skip?: number; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.competitor_id) query.append("competitor_id", params.competitor_id.toString());
    if (params?.search) query.append("search", params.search);
    if (params?.method) query.append("method", params.method);
    if (params?.within_target !== undefined) query.append("within_target", params.within_target.toString());
    if (params?.skip !== undefined) query.append("skip", params.skip.toString());
    if (params?.limit !== undefined) query.append("limit", params.limit.toString());
    return fetchApi<any[]>(`/articles?${query.toString()}`).catch(() => []);
  },
  getArticle: (id: number) => fetchApi<any>(`/articles/${id}`),

  // Monitoring Logs
  getMonitoringChecks: (competitor_id?: number, success?: boolean) => {
    const query = new URLSearchParams();
    if (competitor_id) query.append("competitor_id", competitor_id.toString());
    if (success !== undefined) query.append("success", success.toString());
    return fetchApi<any[]>(`/monitoring/checks?${query.toString()}`).catch(() => []);
  },
  getNotifications: () => fetchApi<any[]>("/monitoring/notifications").catch(() => []),

  // Analytics
  getAnalyticsOverview: () => fetchApi<any>("/analytics/overview").catch(() => null),
  getDetectionDelaysChart: () => fetchApi<any[]>("/analytics/detection-delays").catch(() => []),
  getMethodBreakdown: () => fetchApi<any[]>("/analytics/methods").catch(() => []),

  // Scale Test
  seedScaleTest: () => fetchApi<any>("/scale-test/seed", { method: "POST" }),
  startScaleTest: () => fetchApi<any>("/scale-test/start", { method: "POST" }),
  stopScaleTest: () => fetchApi<any>("/scale-test/stop", { method: "POST" }),
  clearScaleTest: () => fetchApi<any>("/scale-test/clear", { method: "POST" }),
  getScaleTestStatus: () => fetchApi<any>("/scale-test/status").catch(() => null),

  // Evidence Checklist
  getEvidenceVerification: () => fetchApi<any[]>("/evidence/verification").catch(() => []),

  // Demo Site Publisher
  publishDemoArticle: (data: any) => fetchApi<any>("/demo-site/publish", { method: "POST", body: JSON.stringify(data) }),
};
