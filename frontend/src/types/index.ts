export interface RepoItem {
  name: string;
  url: string;
  description: string;
  stars: number;
  forks: number;
  owner: string;
  language?: string;
  source: string;
  extra_tags: string[];
  trend_badge: string;
  updated_at?: string;
}

export interface DailyReport {
  id: number;
  date: string;
  title: string;
  summary: string;
  items: RepoItem[];
  sources: string[];
  created_at: string;
}

export interface DailyReportList {
  total: number;
  items: DailyReport[];
}

export interface TrendPoint {
  date: string;
  count: number;
  avg_stars: number;
  sources: Record<string, number>;
}

export interface HealthStatus {
  status: string;
  version: string;
  uptime_seconds: number;
  database: string;
  total_reports: number;
  latest_report_date: string | null;
  sources: Record<string, boolean>;
  llm_summary: boolean;
}
