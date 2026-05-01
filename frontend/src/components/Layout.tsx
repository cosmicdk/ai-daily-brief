import { Link, useLocation } from 'react-router-dom';
import { Newspaper, TrendingUp, Search, Heart } from 'lucide-react';

const navItems = [
  { path: '/', label: '日报列表', icon: Newspaper },
  { path: '/trends', label: '趋势分析', icon: TrendingUp },
  { path: '/search', label: '搜索', icon: Search },
  { path: '/favorites', label: '收藏', icon: Heart },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  return (
    <div className="min-h-screen flex flex-col">
      {/* 导航栏 */}
      <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-xs font-bold">
              AI
            </div>
            <span className="text-lg font-semibold text-white hidden sm:inline">
              AI Daily Brief
            </span>
          </Link>
          <nav className="flex items-center gap-1">
            {navItems.map(({ path, label, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm transition-colors ${
                  location.pathname === path
                    ? 'bg-blue-600/20 text-blue-400'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
              >
                <Icon size={16} />
                <span className="hidden sm:inline">{label}</span>
              </Link>
            ))}
          </nav>
        </div>
      </header>

      {/* 内容 */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6">
        {children}
      </main>

      {/* 底部 */}
      <footer className="border-t border-gray-800 py-4 text-center text-xs text-gray-600">
        AI Daily Brief v0.3.0 · Built with Hermes Agent
      </footer>
    </div>
  );
}
