const BASE_URL = '/api/v1/daily-reports';

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text.slice(0, 200)}`);
  }
  return res.json();
}

export interface FetchReportsParams {
  skip?: number;
  limit?: number;
  q?: string;
}

export async function fetchReports(params: FetchReportsParams = {}) {
  const qs = new URLSearchParams();
  if (params.skip) qs.set('skip', String(params.skip));
  if (params.limit) qs.set('limit', String(params.limit));
  if (params.q) qs.set('q', params.q);
  return fetchJSON<import('../types').DailyReportList>(
    `${BASE_URL}?${qs.toString()}`
  );
}

export async function fetchReport(date: string) {
  return fetchJSON<import('../types').DailyReport>(`${BASE_URL}/${date}`);
}

export async function fetchToday() {
  return fetchJSON<import('../types').DailyReport>(`${BASE_URL}/today`);
}

export async function fetchTrends(days = 30) {
  return fetchJSON<import('../types').TrendPoint[]>(
    `${BASE_URL}/trends?days=${days}`
  );
}

export async function fetchHealth() {
  return fetchJSON<import('../types').HealthStatus>('/health');
}
