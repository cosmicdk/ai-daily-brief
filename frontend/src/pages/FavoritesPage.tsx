import { useEffect, useState } from 'react';
import { DailyReport } from '../types';
import { fetchReports } from '../hooks/api';
import ReportCard from '../components/ReportCard';
import { Heart } from 'lucide-react';

export default function FavoritesPage() {
  const [favIds, setFavIds] = useState<number[]>(() => {
    try {
      return JSON.parse(localStorage.getItem('fav_reports') || '[]');
    } catch {
      return [];
    }
  });

  const [reports, setReports] = useState<DailyReport[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (favIds.length === 0) {
      setReports([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    // 获取所有报告然后过滤
    fetchReports({ limit: 100 })
      .then((data) => {
        setReports(data.items.filter((r) => favIds.includes(r.id)));
      })
      .finally(() => setLoading(false));
  }, [favIds]);

  function clearFavorites() {
    localStorage.removeItem('fav_reports');
    setFavIds([]);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <Heart size={20} className="text-red-400" />
          收藏的报告
        </h1>
        {favIds.length > 0 && (
          <button
            onClick={clearFavorites}
            className="text-sm text-gray-500 hover:text-red-400 transition-colors"
          >
            清空收藏
          </button>
        )}
      </div>

      {loading ? (
        <div className="text-center py-20 text-gray-500">加载中...</div>
      ) : favIds.length === 0 ? (
        <div className="text-center py-20 text-gray-500">
          还没有收藏任何报告。在日报列表中可以收藏。
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map((r) => (
            <ReportCard key={r.id} report={r} />
          ))}
        </div>
      )}
    </div>
  );
}
