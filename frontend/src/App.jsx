// src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext.jsx';
import { PrivateRoute } from '@/components/PrivateRoute.jsx';
import { RoleRoute } from '@/components/RoleRoute.jsx';
import { AdminLayout } from '@/layouts/AdminLayout.jsx';
import { Toaster } from '@/components/ui/toaster.jsx';

// Pages
import Login from '@/pages/Login.jsx';
import Dashboard from '@/pages/Dashboard.jsx';
import Dossiers from '@/pages/Dossiers.jsx';
import DossierDetail from '@/pages/DossierDetail.jsx';
import Communes from '@/pages/Communes.jsx';
import Agents from '@/pages/Agents.jsx';
import AuditLogs from '@/pages/AuditLogs.jsx';
import NdiogoyeLogs from '@/pages/NdiogoyeLogs.jsx';
import Notifications from '@/pages/Notifications.jsx';
import Settings from '@/pages/Settings.jsx';
import Transactions from '@/pages/Transactions.jsx';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Route publique */}
          <Route path="/login" element={<Login />} />

          {/* Redirect racine */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          {/* Routes protégées */}
          <Route element={<PrivateRoute />}>
            <Route element={<AdminLayout />}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/dossiers" element={<Dossiers />} />
              <Route path="/dossiers/:id" element={<DossierDetail />} />
              <Route path="/notifications" element={<Notifications />} />
              <Route path="/settings" element={<Settings />} />

              {/* Réservé Admin Civil et Super Admin */}
              <Route element={<RoleRoute allowedRoles={['civil_admin', 'super_admin']} />}>
                <Route path="/agents" element={<Agents />} />
              </Route>

              {/* Réservé Super Admin */}
              <Route element={<RoleRoute allowedRoles={['super_admin']} />}>
                <Route path="/communes" element={<Communes />} />
                <Route path="/audit-logs" element={<AuditLogs />} />
                <Route path="/ai-logs" element={<NdiogoyeLogs />} />
                <Route path="/admin/transactions" element={<Transactions />} />
              </Route>
            </Route>
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>

        {/* Toast global */}
        <Toaster />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
