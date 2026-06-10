// src/layouts/AdminLayout.jsx
import { useState, useEffect } from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useTheme } from '@/hooks/useTheme';
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
  CreditCard,
  ShieldAlert,
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
  const { isDark, toggle } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  const baseNavigation = [
    { name: 'Tableau de bord', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Dossiers', href: '/dossiers', icon: FolderOpen },
    { name: 'Communes', href: '/communes', icon: Building2 },
    { name: 'Agents', href: '/agents', icon: Users },
    { name: 'Journal d\'audit', href: '/audit-logs', icon: ScrollText },
  ];

  const filteredNavigation = [...baseNavigation];
  if (role === 'super_admin') {
    filteredNavigation.push({ name: 'Transactions', href: '/admin/transactions', icon: CreditCard });
  }
  filteredNavigation.push(
    { name: 'Notifications', href: '/notifications', icon: Bell },
    { name: 'Paramètres', href: '/settings', icon: Settings }
  );

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
    const currentNav = filteredNavigation.find((nav) => location.pathname.startsWith(nav.href));
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
    <div className="h-screen bg-layer-0 flex overflow-hidden">
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
        style={{
          backgroundImage: 'linear-gradient(180deg, #0D1F3C 0%, #080E1A 100%), url("data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.65%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22 opacity=%220.05%22/%3E%3C/svg%3E")',
          borderRight: '1px solid var(--border-subtle)',
        }}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <img src={logo} alt="TC Logo" className="w-9 h-9 rounded-lg object-contain bg-layer-0 shadow-lg" />
            <div>
              <h1 className="text-[#F0F4FF] font-bold text-lg tracking-tight leading-none">
                TERANGA
              </h1>
              <span className="text-amber/80 text-[10px] font-semibold tracking-[0.2em] uppercase">
                Civil
              </span>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-[#8B9FC2] hover:text-[#F0F4FF] transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {filteredNavigation.map((item) => {
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
                    className="absolute right-3 top-1/2 -translate-y-1/2 min-w-[20px] h-5 flex items-center justify-center rounded-full bg-error text-[#F0F4FF] text-[11px] font-bold px-1.5 shadow-[0_0_8px_rgba(248,113,113,0.5)] animate-pulse"
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
            <div className="w-9 h-9 rounded-full bg-amber-dim border-[1.5px] border-amber flex items-center justify-center">
              <span className="text-amber font-semibold text-sm">
                {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-[#F0F4FF] truncate">
                {user?.full_name || user?.email || 'Utilisateur'}
              </p>
              <p className="text-xs text-[#8B9FC2] truncate">
                {getRoleLabel(role)}
              </p>
              <p className="text-[10px] text-[#526080] truncate mt-0.5" title="Dernière connexion">
                Connexion: {new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            className="w-full justify-start text-[#8B9FC2] hover:text-[#F0F4FF] hover:bg-[rgba(255,255,255,0.1)] h-9 mb-4"
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
        <header className="sticky top-0 z-30 h-16 bg-layer-1 border-b border-border-strong flex items-center justify-between px-6" style={{ boxShadow: 'var(--shadow-card)' }}>
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg text-text-300 hover:bg-layer-2 transition-colors"
            >
              <Menu className="h-5 w-5" />
            </button>
            <Link
              to="/admin/audit-logs"
              className="hidden lg:flex items-center gap-3 rounded-lg px-3 py-2 text-slate-500 transition-all hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-50"
            >
              <Activity className="h-4 w-4" />
              Audit Logs
            </Link>
            <Link
              to="/admin/ai-logs"
              className="hidden lg:flex items-center gap-3 rounded-lg px-3 py-2 text-slate-500 transition-all hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-50"
            >
              <Bot className="h-4 w-4" />
              Supervision IA
            </Link>
            <div>
              <h2 className="text-lg font-semibold text-text-100">
                {getCurrentPageTitle()}
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Settings button */}
            <button
              onClick={() => navigate('/settings')}
              className="p-2 rounded-lg text-text-300 hover:bg-layer-2 hover:text-amber transition-colors focus-ring"
              title="Paramètres"
            >
              <Settings className="h-5 w-5" />
            </button>

            {/* Theme toggle */}
            <button
              onClick={toggle}
              className="theme-toggle"
              aria-label={isDark ? 'Passer en mode clair' : 'Passer en mode sombre'}
              title={isDark ? 'Mode clair' : 'Mode sombre'}
            >
              {isDark
                ? <Sun className="h-[18px] w-[18px]" />
                : <Moon className="h-[18px] w-[18px]" />
              }
            </button>

            {/* Notification bell */}
            <button
              onClick={() => navigate('/notifications')}
              className="relative p-2 rounded-lg text-text-300 hover:bg-layer-2 hover:text-amber transition-colors focus-ring"
              aria-label={unreadCount > 0 ? `${unreadCount} notifications non lues` : 'Notifications'}
            >
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] flex items-center justify-center rounded-full bg-error text-text-100 text-[10px] font-bold px-1 shadow-[0_0_8px_rgba(248,113,113,0.5)]" aria-hidden="true">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* User info */}
            <div className="hidden sm:flex items-center gap-3 pl-4 border-l border-border-strong">
              <div className="text-right">
                <p className="text-sm font-medium text-text-100">
                  {user?.full_name || 'Utilisateur'}
                </p>
                <p className="text-xs text-text-400">
                  {getRoleLabel(role)}
                </p>
              </div>
              <div className="w-9 h-9 rounded-full bg-amber-dim border-[1.5px] border-amber flex items-center justify-center shadow-md">
                <span className="text-amber font-semibold text-sm">
                  {user?.full_name?.charAt(0) || 'U'}
                </span>
              </div>
            </div>

            {/* Logout button */}
            <Button
              variant="ghost"
              size="icon"
              onClick={handleLogout}
              className="text-text-400 hover:text-error hover:bg-error-dim"
              title="Déconnexion"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6 overflow-y-auto animate-enter">
          {role === 'super_admin' && (
            <div className="mb-6 flex items-center gap-3 p-4 bg-[#F59E0B]/10 border border-[#F59E0B]/30 rounded-xl text-[#D97706] text-sm font-semibold shadow-sm animate-enter">
              <ShieldAlert className="h-5 w-5 flex-shrink-0" />
              <span>
                Mode lecture seule — Toute modification des transactions est désactivée conformément aux règles de la Trésorerie Publique.
              </span>
            </div>
          )}
          <Outlet />
        </main>
      </div>
    </div>
  );
}
