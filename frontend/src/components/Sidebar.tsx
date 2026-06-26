import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Home, Library as LibraryIcon, Settings, Activity } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

export function Sidebar() {
  const { t } = useTranslation();
  const location = useLocation();

  const navItems = [
    { name: t('queue') || 'Dashboard', path: '/', icon: Home },
    { name: t('library') || 'Library', path: '/library', icon: LibraryIcon },
    { name: t('settings') || 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <div className="w-64 bg-gray-900 border-r border-gray-800 text-white flex flex-col h-screen shadow-2xl">
      <div className="p-6 flex items-center space-x-3 border-b border-gray-800/50">
        <div className="p-2 bg-indigo-500/10 rounded-xl">
          <Activity className="w-6 h-6 text-indigo-500" />
        </div>
        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-500">DMS</span>
      </div>
      
      <nav className="flex-1 px-4 space-y-2 mt-6">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200",
                isActive 
                  ? "bg-indigo-500/10 text-indigo-400 font-medium shadow-sm ring-1 ring-indigo-500/20" 
                  : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
              )}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
