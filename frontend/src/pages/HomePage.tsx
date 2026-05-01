import { useEffect, useState } from 'react';
import { DailyReport, HealthStatus } from '../types';
import { fetchReports, fetchHealth } from '../hooks/api';
import ReportCard from '../components/ReportCard';
import { RefreshCw, Activity, BarChart3 } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function HomePage() {
  const [reports, setReports] = useState<DailyReport[]>([]);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function load() {
    setLoading(true);
    setError('');
    try {
      const [r, h] = await Promise.all([
        fetchReports({ limit: 10 }),
        fetchHealth(),
      ]);
      setReports(r.items);
      setHealth(h);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <div className="space-y-6">
      {/* 状态栏 */}
      {health && (
        <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500 bg-gray-900/50 border border-gray-800 rounded-lg px-4 py-3">
          <span className="flex items-center gap-1">
            <Activity size={12} className={health.database === 'ok' ? 'text-green-400' : 'text-red-400'} />
            DB: {health.database}
          </span>
          <span>报告: {health.total_reports}</span>
          <span>
            数据源: {Object.entries(health.sources).filter(([, v]) => v).length}/4 活跃
          </span>
          <span>
            AI摘要: {health.llm_summary ? '✅' : '❌'}
          </span>
        </div>
      )}

      {/* 操作栏 */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <BarChart3 size={20} className="text-blue-400" />
          AI 每日简报
        </h1>
        <div className="flex items-center gap-2">
          <Link
            to="/search"
            className="text-sm px-3 py-1.5 rounded-lg bg-gray-800 text-gray-300 hover:bg-gray-700 transition-colors"
          >
            搜索
          </Link>
          <Link
            to="/trends"
            className="text-sm px-3 py-1.5 rounded-lg bg-gray-800 text-gray-300 hover:bg-gray-700 transition-colors"
          >
            趋势
          </Link>
          <button
            onClick={load}
            disabled={loading}
            className="flex items-center gap-1 text-sm px-3 py-1.5 rounded-lg bg-blue-600 text-white hover:bg-blue-500 disabled:opacity-50 transition-colors"
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            刷新
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-800 rounded-lg p-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {loading && !error && (
        <div className="flex items-center justify-center py-20 text-gray-500">
          <RefreshCw size={24} className="animate-spin mr-2" />
          加载中...
        </div>
      )}

      {!loading && !error && reports.length === 0 && (
        <div className="text-center py-20 text-gray-500">
          暂无日报数据。请先生成日报。
        </div>
      )}

      <div className="space-y-3">
        {reports.map((r) => (
          <ReportCard key={r.id} report={r} defaultExpanded={false} />
        ))}
      </div>
    </div>
  );
}
