// src/layouts/AdminLayout.jsx
import { useState, useEffect } from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import {
  LayoutDashboard,
  FolderOpen,
  Building2,
  Users,
  ScrollText,
  Bell,
  LogOut,
  Menu,
  X,
  ChevronRight,
  Settings,
  Sun,
  Moon,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import logo from '@/assets/logo.jpg';

// Mock notifications pour le badge (attend DEV 1C — Maïmouna Sall)
// TODO: brancher API réelle GET /api/notifications/
const MOCK_NOTIFICATIONS = [
  { id: 1, title: "Nouveau dossier soumis", body: "TC-2026-089 — Acte de naissance", is_read: false, created_at: new Date().toISOString(), related_dossier_id: 89 },
  { id: 2, title: "Dossier approuvé", body: "TC-2026-045 approuvé par l'officier", is_read: true, created_at: new Date(Date.now() - 3600000).toISOString(), related_dossier_id: 45 },
  { id: 3, title: "Dossier rejeté", body: "TC-2026-031 — Documents insuffisants", is_read: false, created_at: new Date(Date.now() - 7200000).toISOString(), related_dossier_id: 31 },
];

const navigation = [
  { name: 'Tableau de bord', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Dossiers', href: '/dossiers', icon: FolderOpen },
  { name: 'Communes', href: '/communes', icon: Building2 },
  { name: 'Agents', href: '/agents', icon: Users },
  { name: 'Journal d\'audit', href: '/audit-logs', icon: ScrollText },
  { name: 'Notifications', href: '/notifications', icon: Bell },
  { name: 'Paramètres', href: '/settings', icon: Settings },
];

export function AdminLayout() {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    window.dispatchEvent(new Event('theme-change'));
  };

  useEffect(() => {
    const handleThemeChange = () => {
      setTheme(localStorage.getItem('theme') || 'light');
    };
    window.addEventListener('theme-change', handleThemeChange);
    return () => window.removeEventListener('theme-change', handleThemeChange);
  }, []);

  useEffect(() => {
    // TODO: brancher API réelle
    const count = MOCK_NOTIFICATIONS.filter((n) => !n.is_read).length;
    setUnreadCount(count);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Obtenir le titre de la page actuelle
  const getCurrentPageTitle = () => {
    const currentNav = navigation.find((nav) => location.pathname.startsWith(nav.href));
    if (location.pathname.startsWith('/dossiers/') && location.pathname !== '/dossiers') {
      return 'Détail du dossier';
    }
    return currentNav?.name || 'Dashboard';
  };

  // Libellé du rôle
  const getRoleLabel = (r) => {
    const labels = {
      super_admin: 'Super Administrateur',
      civil_admin: 'Administrateur Civil',
      agent: 'Agent',
    };
    return labels[r] || r;
  };

  return (
    <div className="h-screen bg-background flex overflow-hidden">
      {/* Overlay mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden backdrop-blur-sm"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-[260px] flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{ background: 'linear-gradient(180deg, #0D1F3C 0%, #162847 100%)' }}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <img src={logo} alt="TC Logo" className="w-9 h-9 rounded-lg object-contain bg-white shadow-lg" />
            <div>
              <h1 className="text-white font-bold text-lg tracking-tight leading-none">
                TERANGA
              </h1>
              <span className="text-primary/80 text-[10px] font-semibold tracking-[0.2em] uppercase">
                Civil
              </span>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-slate-400 hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href || 
              (item.href !== '/dashboard' && location.pathname.startsWith(item.href));
            
            return (
              <NavLink
                key={item.name}
                to={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`sidebar-link relative ${isActive ? 'active' : ''}`}
              >
                <item.icon className="h-5 w-5 flex-shrink-0" />
                <span className="flex-1">{item.name}</span>
                {item.href === '/notifications' && unreadCount > 0 && (
                  <span 
                    className="absolute right-3 top-1/2 -translate-y-1/2 min-w-[20px] h-5 flex items-center justify-center rounded-full bg-danger text-white text-[11px] font-bold px-1.5 shadow-lg shadow-danger/30 animate-pulse"
                    aria-label={`${unreadCount} notifications non lues`}
                  >
                    {unreadCount}
                  </span>
                )}
                {isActive && (
                  <ChevronRight className="h-4 w-4 text-primary" />
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* User info en bas du sidebar */}
        <div className="px-4 py-4 border-t border-white/10">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 rounded-full bg-accent/20 flex items-center justify-center">
              <span className="text-accent font-semibold text-sm">
                {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">
                {user?.full_name || user?.email || 'Utilisateur'}
              </p>
              <p className="text-xs text-slate-400 truncate">
                {getRoleLabel(role)}
              </p>
              <p className="text-[10px] text-slate-500 truncate mt-0.5" title="Dernière connexion">
                Connexion: {new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            className="w-full justify-start text-slate-400 hover:text-white hover:bg-white/10 h-9"
            onClick={handleLogout}
          >
            <LogOut className="h-4 w-4 mr-2" />
            Déconnexion
          </Button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col h-full overflow-hidden lg:pl-[260px]">
        {/* Header */}
        <header className="sticky top-0 z-30 h-16 bg-white dark:bg-slate-900 border-b border-slate-100 dark:border-slate-800 shadow-sm flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <Menu className="h-5 w-5" />
            </button>
            <div>
              <h2 className="text-lg font-semibold text-secondary dark:text-white">
                {getCurrentPageTitle()}
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Settings button */}
            <button
              onClick={() => navigate('/settings')}
              className="p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              title="Paramètres"
            >
              <Settings className="h-5 w-5" />
            </button>

            {/* Dark/Light mode toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              title={theme === 'dark' ? 'Mode Clair' : 'Mode Sombre'}
            >
              {theme === 'dark' ? (
                <Sun className="h-5 w-5 text-amber-500 animate-[spin_4s_linear_infinite]" />
              ) : (
                <Moon className="h-5 w-5 text-slate-600 dark:text-slate-300" />
              )}
            </button>

            {/* Notification bell */}
            <button
              onClick={() => navigate('/notifications')}
              className="relative p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              aria-label={unreadCount > 0 ? `${unreadCount} notifications non lues` : 'Notifications'}
            >
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] flex items-center justify-center rounded-full bg-danger text-white text-[10px] font-bold px-1 shadow-sm" aria-hidden="true">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* User info */}
            <div className="hidden sm:flex items-center gap-3 pl-4 border-l border-slate-100 dark:border-slate-800">
              <div className="text-right">
                <p className="text-sm font-medium text-secondary dark:text-slate-200">
                  {user?.full_name || 'Utilisateur'}
                </p>
                <p className="text-xs text-slate-400">
                  {getRoleLabel(role)}
                </p>
              </div>
              <div className="w-9 h-9 rounded-full gradient-primary flex items-center justify-center shadow-md">
                <span className="text-white font-semibold text-sm">
                  {user?.full_name?.charAt(0) || 'U'}
                </span>
              </div>
            </div>

            {/* Logout button */}
            <Button
              variant="ghost"
              size="icon"
              onClick={handleLogout}
              className="text-slate-400 hover:text-danger hover:bg-danger/10"
              title="Déconnexion"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6 overflow-y-auto animate-enter">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
