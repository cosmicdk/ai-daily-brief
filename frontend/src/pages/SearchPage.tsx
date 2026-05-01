import { useEffect, useState } from 'react';
import { DailyReport } from '../types';
import { fetchReports } from '../hooks/api';
import ReportCard from '../components/ReportCard';
import { Search, X } from 'lucide-react';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<DailyReport[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      setTotal(0);
      return;
    }
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await fetchReports({ q: query, limit: 50 });
        setResults(data.items);
        setTotal(data.total);
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    }, 400);
    return () => clearTimeout(timer);
  }, [query]);

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold text-white">搜索日报</h1>

      <div className="relative">
        <Search
          size={18}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500"
        />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="搜索项目名称、描述、标签..."
          className="w-full bg-gray-900 border border-gray-700 rounded-xl pl-10 pr-10 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 transition-colors"
        />
        {query && (
          <button
            onClick={() => setQuery('')}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
          >
            <X size={16} />
          </button>
        )}
      </div>

      {query && (
        <p className="text-sm text-gray-500">
          找到 {total} 条结果
        </p>
      )}

      {loading && (
        <div className="text-center py-20 text-gray-500">搜索中...</div>
      )}

      {!loading && query && results.length === 0 && (
        <div className="text-center py-20 text-gray-500">未找到相关内容</div>
      )}

      <div className="space-y-3">
        {results.map((r) => (
          <ReportCard key={r.id} report={r} />
        ))}
      </div>
    </div>
  );
}
