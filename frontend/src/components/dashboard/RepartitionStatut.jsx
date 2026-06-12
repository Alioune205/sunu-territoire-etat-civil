// src/components/dashboard/RepartitionStatut.jsx
import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { PieChart, Pie, Cell, Legend, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';
import { EmptyState } from './EmptyState';

const STATUS_COLORS = {
  submitted: '#F59E0B',
  in_review: '#1D4ED8',
  validated: '#10B981',
  rejected: '#EF4444',
  draft: '#64748B',
  approved: '#10B981',
  completed: '#10B981',
  delivered: '#10B981',
};

const STATUS_LABELS = {
  draft: 'Brouillon',
  submitted: 'Soumis',
  in_review: 'En vérification',
  approved: 'Approuvés',
  validated: 'Validés',
  rejected: 'Rejetés',
  completed: 'Terminés',
  delivered: 'Délivrés',
};

function CustomPieTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null;
  const item = payload[0];
  const pct = item?.payload?.total ? ((item.value / item.payload.total) * 100).toFixed(1) : 0;
  const fillColor = item?.payload?.fill || '#94A3B8';
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-lg shadow-xl p-3">
      <p className="text-sm font-medium text-slate-700 dark:text-slate-200">{item?.name || '—'}</p>
      <p className="text-sm font-bold mt-1" style={{ color: fillColor }}>
        {item?.value || 0} demandes ({pct}%)
      </p>
    </div>
  );
}

export function RepartitionStatut({ loading, stats }) {
  const pieData = useMemo(() => {
    if (!stats?.status_counts) return [];
    const total = Object.values(stats.status_counts).reduce((a, b) => a + b, 0);
    if (total === 0) return [];
    return Object.entries(stats.status_counts).map(([key, value]) => ({
      name: STATUS_LABELS[key] || key,
      value,
      fill: STATUS_COLORS[key] || '#94A3B8',
      total,
    }));
  }, [stats]);

  const renderPieLegend = (props) => {
    const payload = props?.payload || [];
    if (!payload || payload.length === 0) return null;
    return (
      <div className="flex flex-col gap-2.5 mt-2">
        {payload.map((entry, index) => {
          const item = pieData[index];
          const pct = item ? ((item.value / item.total) * 100).toFixed(1) : 0;
          return (
            <div key={`item-${index}`} className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: entry.color }} />
                <span className="text-secondary dark:text-slate-300 font-medium">{entry.value}</span>
              </div>
              <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                <span>{item ? item.value : 0} demandes</span>
                <span className="bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded text-xs">{pct}%</span>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <Card className="lg:col-span-2 lg:row-span-1 border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm p-4 overflow-hidden h-full flex flex-col">
      <CardHeader className="p-0 pb-4 flex-shrink-0">
        <CardTitle className="text-base font-semibold text-secondary dark:text-white">
          Répartition par statut
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0 flex-1 min-h-0">
        {loading ? (
          <Skeleton className="h-full w-full rounded-xl" />
        ) : pieData.length === 0 ? (
          <EmptyState
            variant="no-data"
            title="Aucune donnée de répartition disponible"
            description="Aucune demande n'a été enregistrée pour le moment."
          />
        ) : (
          <div className="relative flex flex-col sm:flex-row items-center justify-around h-full gap-4">
            <div className="relative w-[150px] h-[150px] flex-shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={70} paddingAngle={3} dataKey="value" stroke="none">
                    {pieData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.fill} />)}
                  </Pie>
                  <RechartsTooltip content={<CustomPieTooltip />} />
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="text-2xl font-bold text-secondary dark:text-white">{stats?.total_dossiers ?? 0}</span>
                <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold mt-0.5">Demandes</span>
              </div>
            </div>
            <div className="flex-1 max-w-[200px] overflow-y-auto pr-2">
              <Legend layout="vertical" verticalAlign="middle" align="right" content={renderPieLegend} />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
