import { DailyReport, RepoItem } from '../types';
import RepoCard from './RepoCard';
import { Calendar, Clock, Database, ChevronLeft, ChevronRight, ChevronDown, ChevronRight as ChevronRightIcon } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { useState } from 'react';

const PAGE_SIZE = 10;

export default function ReportCard({
  report,
  defaultExpanded = false,
}: {
  report: DailyReport;
  defaultExpanded?: boolean;
}) {
  const [page, setPage] = useState(0);
  const [selectedName, setSelectedName] = useState<string | null>(null);
  const totalPages = Math.ceil(report.items.length / PAGE_SIZE);
  const pagedItems = report.items.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  const handleToggle = (name: string) => {
    setSelectedName(selectedName === name ? null : name);
  };

  return (
    <details
      open={defaultExpanded}
      className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden group"
      onToggle={(e) => {
        if (!(e.target as HTMLDetailsElement).open) {
          setPage(0);
          setSelectedName(null);
        }
      }}
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

      {/* 内容：先项目列表，后摘要（可折叠） */}
      <div className="px-4 pb-4 space-y-4">
        <div className="space-y-1">
          {pagedItems.map((item, i) => (
            <RepoCard
              key={`${item.name}-${i}`}
              item={item}
              expanded={selectedName === item.name}
              onToggle={() => handleToggle(item.name)}
            />
          ))}
        </div>

        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-3 pt-2">
            <button
              onClick={() => {
                setPage(Math.max(0, page - 1));
                setSelectedName(null);
              }}
              disabled={page === 0}
              className="flex items-center gap-1 px-3 py-1.5 text-sm rounded-lg bg-gray-800/50 text-gray-400 hover:text-white hover:bg-gray-700/50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft size={14} /> 上一页
            </button>
            <span className="text-sm text-gray-500">
              {page + 1} / {totalPages}
            </span>
            <button
              onClick={() => {
                setPage(Math.min(totalPages - 1, page + 1));
                setSelectedName(null);
              }}
              disabled={page >= totalPages - 1}
              className="flex items-center gap-1 px-3 py-1.5 text-sm rounded-lg bg-gray-800/50 text-gray-400 hover:text-white hover:bg-gray-700/50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              下一页 <ChevronRight size={14} />
            </button>
          </div>
        )}

        {/* AI 摘要 — 折叠在下面 */}
        {report.summary && (
          <details className="group">
            <summary className="cursor-pointer hover:bg-gray-800/50 transition-colors list-none flex items-center gap-2 text-sm text-gray-500 py-2 px-1 -mx-1 rounded-lg">
              <ChevronRight size={14} className="group-open:rotate-90 transition-transform" />
              <span>📖 查看 AI 深度分析报告</span>
              <span className="text-xs text-gray-600">（{report.summary.length} 字）</span>
            </summary>
            <div className="bg-gray-800/50 rounded-lg p-4 mt-2 text-sm text-gray-300 leading-relaxed prose prose-invert max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>
                {report.summary}
              </ReactMarkdown>
            </div>
          </details>
        )}
      </div>
    </details>
  );
}
