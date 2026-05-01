import { RepoItem } from '../types';
import { Star, GitFork, ChevronDown, ChevronRight, ExternalLink } from 'lucide-react';

function languageColor(lang?: string): string {
  const colors: Record<string, string> = {
    Python: 'bg-yellow-400',
    TypeScript: 'bg-blue-500',
    JavaScript: 'bg-yellow-300',
    Rust: 'bg-orange-600',
    Go: 'bg-cyan-500',
    'C++': 'bg-pink-500',
    'C#': 'bg-green-600',
    Java: 'bg-red-500',
    Shell: 'bg-gray-400',
    Jupyter: 'bg-orange-400',
    HTML: 'bg-red-400',
  };
  return lang ? colors[lang] || 'bg-gray-500' : 'bg-gray-600';
}

/** 趋势标签的颜色映射 */
function badgeStyle(badge: string): string {
  if (badge.includes('🔥')) return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
  if (badge.includes('⭐') || badge.includes('Star')) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
  if (badge.includes('🍴') || badge.includes('Fork')) return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
  if (badge.includes('📊')) return 'bg-green-500/20 text-green-400 border-green-500/30';
  return 'bg-gray-700/50 text-gray-400 border-gray-600/30';
}

export default function RepoCard({
  item,
  expanded,
  onToggle,
}: {
  item: RepoItem;
  expanded: boolean;
  onToggle: () => void;
}) {
  return (
    <div
      className={`bg-gray-900 border rounded-xl overflow-hidden transition-all duration-200 cursor-pointer ${
        expanded
          ? 'border-blue-600 shadow-lg shadow-blue-900/20'
          : 'border-gray-800 hover:border-gray-700'
      }`}
      onClick={onToggle}
    >
      {/* 紧凑头部 — 始终显示 */}
      <div className="flex items-center gap-2 px-3 py-2.5 min-h-0">
        <span className="shrink-0 text-gray-500">
          {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </span>
        <span className="text-[11px] font-medium text-gray-500 uppercase tracking-wider shrink-0">
          {item.source}
        </span>
        {item.trend_badge && (
          <span className={`text-[10px] px-1.5 py-0.5 rounded-full border shrink-0 ${badgeStyle(item.trend_badge)}`}>
            {item.trend_badge}
          </span>
        )}
        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-blue-400 hover:text-blue-300 font-medium truncate min-w-0"
          onClick={(e) => e.stopPropagation()}
        >
          {item.name}
        </a>
        <span className="text-xs text-gray-500 truncate flex-1 min-w-0 hidden sm:inline">
          {item.description ? item.description.slice(0, 80) + (item.description.length > 80 ? '…' : '') : ''}
        </span>
      </div>

      {/* 展开后的详情 */}
      {expanded && (
        <div className="px-3 pb-3 pt-0 border-t border-gray-800/50 animate-fadeIn">
          <p className="text-xs text-gray-400 mt-2 mb-2 leading-relaxed">
            {item.description || '暂无描述'}
          </p>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Star size={13} className="text-yellow-500" />
              <span className="font-medium text-yellow-400">{item.stars.toLocaleString()}</span>
            </span>
            {item.forks > 0 && (
              <span className="flex items-center gap-1">
                <GitFork size={13} className="text-purple-400" />
                <span>{item.forks.toLocaleString()}</span>
              </span>
            )}
            {item.stars > 0 && item.forks > 0 && (
              <span className="text-gray-600">
                Fork/Star: {(item.forks / item.stars).toFixed(2)}
              </span>
            )}
            {item.language && (
              <span className="flex items-center gap-1.5">
                <span className={`w-2 h-2 rounded-full ${languageColor(item.language)}`} />
                {item.language}
              </span>
            )}
            {item.updated_at && (
              <span className="text-gray-600">
                更新: {item.updated_at.slice(0, 10)}
              </span>
            )}
          </div>
          {item.extra_tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {item.extra_tags.map((tag) => (
                <span
                  key={tag}
                  className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-500"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 mt-2 text-xs text-blue-500 hover:text-blue-400"
            onClick={(e) => e.stopPropagation()}
          >
            <ExternalLink size={12} /> 查看详情
          </a>
        </div>
      )}
    </div>
  );
}
