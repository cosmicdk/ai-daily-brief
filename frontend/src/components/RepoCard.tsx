import { RepoItem } from '../types';
import { Star, GitFork, Globe } from 'lucide-react';

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

export default function RepoCard({ item }: { item: RepoItem }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 hover:border-blue-700/50 transition-colors">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">
              {item.source}
            </span>
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 font-medium truncate block"
            >
              {item.name}
            </a>
          </div>
          <p className="text-sm text-gray-400 line-clamp-2 mb-3">
            {item.description || '暂无描述'}
          </p>
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Star size={14} className="text-yellow-500" />
              {item.stars.toLocaleString()}
            </span>
            {item.language && (
              <span className="flex items-center gap-1.5">
                <span className={`w-2.5 h-2.5 rounded-full ${languageColor(item.language)}`} />
                {item.language}
              </span>
            )}
          </div>
          {item.extra_tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-2">
              {item.extra_tags.map((tag) => (
                <span
                  key={tag}
                  className="text-xs px-2 py-0.5 rounded-full bg-gray-800 text-gray-400"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
