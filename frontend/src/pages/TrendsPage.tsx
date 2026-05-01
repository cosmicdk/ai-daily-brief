import { useEffect, useState } from 'react';
import { TrendPoint } from '../types';
import { fetchTrends } from '../hooks/api';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from 'recharts';
import { TrendingUp } from 'lucide-react';

const SOURCE_COLORS: Record<string, string> = {
  github: '#38bdf8',
  huggingface: '#f97316',
  arxiv: '#a78bfa',
  hackernews: '#22c55e',
};

export default function TrendsPage() {
  const [data, setData] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  useEffect(() => {
    setLoading(true);
    fetchTrends(days)
      .then(setData)
      .finally(() => setLoading(false));
  }, [days]);

  const sourceKeys = ['github', 'huggingface', 'arxiv', 'hackernews'].filter(
    (k) => data.some((d) => (d.sources as any)[k] > 0)
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <TrendingUp size={20} className="text-blue-400" />
          趋势分析
        </h1>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-300"
        >
          <option value={7}>7天</option>
          <option value={14}>14天</option>
          <option value={30}>30天</option>
          <option value={90}>90天</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-20 text-gray-500">加载中...</div>
      ) : data.length === 0 ? (
        <div className="text-center py-20 text-gray-500">暂无趋势数据</div>
      ) : (
        <>
          {/* 项目数量趋势 */}
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
            <h2 className="text-sm font-medium text-gray-400 mb-4">每日项目数</h2>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Legend />
                {sourceKeys.map((key) => (
                  <Bar
                    key={key}
                    dataKey={`sources.${key}`}
                    name={key}
                    stackId="a"
                    fill={SOURCE_COLORS[key]}
                    radius={[2, 2, 0, 0]}
                  />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 平均 Stars 趋势 */}
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
            <h2 className="text-sm font-medium text-gray-400 mb-4">平均 Stars</h2>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Line
                  type="monotone"
                  dataKey="avg_stars"
                  stroke="#38bdf8"
                  strokeWidth={2}
                  dot={{ fill: '#38bdf8', r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}
