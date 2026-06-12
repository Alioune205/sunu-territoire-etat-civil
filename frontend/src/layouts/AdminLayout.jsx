// src/layouts/AdminLayout.jsx
import { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { ShieldAlert } from 'lucide-react';
import { getNotifications } from '@/api/notifications';

import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';

export function AdminLayout() {
  const { role } = useAuth();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const fetchNotifs = async () => {
      try {
        const data = await getNotifications();
        const results = data.results || data;
        const count = results.filter((n) => !n.is_read).length;
        setUnreadCount(count);
      } catch (err) {
        console.error("Erreur chargement notifications (AdminLayout):", err);
      }
    };
    
    fetchNotifs();
    const interval = setInterval(fetchNotifs, 120000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-screen bg-layer-0 flex overflow-hidden">
      <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} unreadCount={unreadCount} />

      {/* Main content */}
      <div className="flex-1 flex flex-col h-full overflow-hidden lg:pl-[260px]">
        <Header setSidebarOpen={setSidebarOpen} unreadCount={unreadCount} />

        {/* Page content */}
        <main className="flex-1 min-h-0 overflow-hidden p-6">
          {role === 'super_admin' && location.pathname.includes('/admin/transactions') && (
            <div className="mb-6 flex items-center justify-between p-3 bg-[#FFFBEB] dark:bg-[#F59E0B]/5 border-l-4 border-l-[#F59E0B] border-y border-r border-[#F59E0B]/20 rounded-r-lg shadow-sm animate-enter">
              <div className="flex items-center gap-3">
                <ShieldAlert className="h-[18px] w-[18px] text-[#F59E0B] flex-shrink-0" />
                <span className="text-[#B45309] dark:text-[#D97706] text-sm font-medium">
                  Mode lecture seule — Règles de la Trésorerie Publique
                </span>
              </div>
              <a href="#" className="text-xs text-[#D97706] hover:text-[#B45309] underline underline-offset-2 transition-colors">
                En savoir plus
              </a>
            </div>
          )}
          <Outlet />
        </main>
      </div>
    </div>
  );
}
