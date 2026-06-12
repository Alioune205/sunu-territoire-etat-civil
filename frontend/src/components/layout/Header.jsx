// src/components/layout/Header.jsx
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useTheme } from '@/hooks/useTheme';
import { Menu, Sun, Moon, Activity, Bot } from 'lucide-react';
import { ProfileDropdown } from './ProfileDropdown';

export function Header({ setSidebarOpen, unreadCount }) {
  const { role } = useAuth();
  const { isDark, toggle } = useTheme();
  const location = useLocation();

  const getCurrentPageTitle = () => {
    const path = location.pathname;
    if (path.startsWith('/dashboard')) return 'Tableau de bord';
    if (path.startsWith('/dossiers/') && path !== '/dossiers') return 'Détail de la demande';
    if (path.startsWith('/dossiers')) return 'Banque des Demandes';
    if (path.startsWith('/citoyens')) return 'Citoyens';
    if (path.startsWith('/agents')) return 'Agents';
    if (path.startsWith('/communes')) return 'Communes';
    if (path.startsWith('/dispatching')) return 'Dispatching IA';
    if (path.startsWith('/audit-logs')) return "Journal d'audit";
    if (path.startsWith('/admin/transactions')) return 'Transactions';
    if (path.startsWith('/notifications')) return 'Notifications';
    if (path.startsWith('/settings')) return 'Paramètres';
    return 'Dashboard';
  };

  return (
    <header className="sticky top-0 z-30 h-16 bg-layer-1 border-b border-border-strong flex items-center justify-between px-6 shrink-0" style={{ boxShadow: 'var(--shadow-card)' }}>
      <div className="flex items-center gap-4">
        <button
          onClick={() => setSidebarOpen(true)}
          className="lg:hidden p-2 rounded-lg text-text-300 hover:bg-layer-2 transition-colors"
        >
          <Menu className="h-5 w-5" />
        </button>
        {role === 'super_admin' && (
          <>
            <NavLink
              to="/audit-logs"
              className="hidden lg:flex items-center gap-3 rounded-lg px-3 py-2 text-slate-500 transition-all hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-50"
            >
              <Activity className="h-4 w-4" />
              Audit Logs
            </NavLink>
            <NavLink
              to="/supervision-ia"
              className="hidden lg:flex items-center gap-3 rounded-lg px-3 py-2 text-slate-500 transition-all hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-50"
            >
              <Bot className="h-4 w-4" />
              Supervision IA
            </NavLink>
          </>
        )}
        <div>
          <h2 className="text-lg font-semibold text-text-100">
            {getCurrentPageTitle()}
          </h2>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={toggle}
          className="theme-toggle"
          aria-label={isDark ? 'Passer en mode clair' : 'Passer en mode sombre'}
          title={isDark ? 'Mode clair' : 'Mode sombre'}
        >
          {isDark ? <Sun className="h-[18px] w-[18px]" /> : <Moon className="h-[18px] w-[18px]" />}
        </button>

        <ProfileDropdown unreadCount={unreadCount} />
      </div>
    </header>
  );
}
