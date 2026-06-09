// src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import { PrivateRoute } from '@/components/PrivateRoute';
import { AdminLayout } from '@/layouts/AdminLayout';
import { Toaster } from '@/components/ui/toaster';

// Pages
import Login from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import Dossiers from '@/pages/Dossiers';
import DossierDetail from '@/pages/DossierDetail';
import Communes from '@/pages/Communes';
import Agents from '@/pages/Agents';
import AuditLogs from '@/pages/AuditLogs';
import Notifications from '@/pages/Notifications';
import Settings from '@/pages/Settings';
import Transactions from '@/pages/Transactions';

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
              <Route path="/communes" element={<Communes />} />
              <Route path="/agents" element={<Agents />} />
              <Route path="/audit-logs" element={<AuditLogs />} />
              <Route path="/admin/transactions" element={<Transactions />} />
              <Route path="/notifications" element={<Notifications />} />
              <Route path="/settings" element={<Settings />} />
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
