import { DailyReport } from '../types';
import RepoCard from './RepoCard';
import { Calendar, Clock, Database } from 'lucide-react';

export default function ReportCard({
  report,
  defaultExpanded = false,
}: {
  report: DailyReport;
  defaultExpanded?: boolean;
}) {
  return (
    <details
      open={defaultExpanded}
      className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden group"
    >
      <summary className="p-4 cursor-pointer hover:bg-gray-800/50 transition-colors list-none flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <h3 className="text-base font-semibold text-white truncate">
            {report.title}
          </h3>
          <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Calendar size={12} /> {report.date}
            </span>
            <span className="flex items-center gap-1">
              <Database size={12} /> {report.items.length} 个项目
            </span>
            <span className="flex items-center gap-1">
              <Clock size={12} />
              {new Date(report.created_at).toLocaleString('zh-CN')}
            </span>
          </div>
        </div>
        <div className="flex flex-wrap gap-1 ml-4">
          {report.sources.map((s) => (
            <span
              key={s}
              className="text-xs px-2 py-0.5 rounded-full bg-blue-600/20 text-blue-400"
            >
              {s}
            </span>
          ))}
        </div>
      </summary>

      {/* 内容 */}
      <div className="px-4 pb-4 space-y-4">
        {report.summary && (
          <div className="bg-gray-800/50 rounded-lg p-3 text-sm text-gray-300 leading-relaxed">
            {report.summary}
          </div>
        )}
        <div className="grid gap-3">
          {report.items.map((item, i) => (
            <RepoCard key={`${item.name}-${i}`} item={item} />
          ))}
        </div>
      </div>
    </details>
  );
}
