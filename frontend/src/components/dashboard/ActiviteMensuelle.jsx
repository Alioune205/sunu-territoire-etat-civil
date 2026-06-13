// src/components/dashboard/ActiviteMensuelle.jsx
import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';
import { EmptyState } from './EmptyState';

function CustomAreaTooltip({ active, payload, label, monthlyData = [] }) {
  if (!active || !payload || !payload.length) return null;
  const currentVal = payload[0].value;
  const index = payload[0].payload?.index;

  let diffText = '';
  let isPositive = true;
  if (typeof index === 'number' && index > 0 && monthlyData[index - 1]) {
    const prevVal = monthlyData[index - 1].value;
    if (prevVal > 0) {
      const pctDiff = ((currentVal - prevVal) / prevVal) * 100;
      isPositive = pctDiff >= 0;
      diffText = `${isPositive ? '+' : ''}${pctDiff.toFixed(1)}% vs mois préc.`;
    } else if (currentVal > 0) {
      diffText = `+100% vs mois préc.`;
    } else {
      diffText = `0% vs mois préc.`;
    }
  } else {
    diffText = 'Premier mois';
  }

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-lg shadow-xl p-3">
      <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">{label}</p>
      <p className="text-lg font-bold text-blue-700 dark:text-blue-400 mt-1">{currentVal} demandes</p>
      <p className={`text-xs font-medium mt-1 ${isPositive ? 'text-emerald-500' : 'text-rose-500'}`}>
        {diffText}
      </p>
    </div>
  );
}

export function ActiviteMensuelle({ loading, activity }) {
  const navigate = useNavigate();

  const monthlyData = useMemo(() => {
    if (!activity?.monthly) return [];
    return [...activity.monthly].reverse().map((item, index) => {
      const date = new Date(item.date);
      return {
        name: date.toLocaleDateString('fr-FR', { month: 'short', year: '2-digit' }),
        value: item.count,
        index,
      };
    });
  }, [activity]);

  return (
    <Card className="lg:col-span-3 lg:row-span-1 border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm p-4 overflow-hidden h-full flex flex-col">
      <CardHeader className="p-0 pb-4 flex-shrink-0">
        <CardTitle className="text-base font-semibold text-secondary dark:text-white">
          Activité mensuelle
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0 flex-1 min-h-0">
        {loading ? (
          <Skeleton className="h-full w-full rounded-xl" />
        ) : monthlyData.length === 0 ? (
          <EmptyState
            variant="no-data"
            title="Aucune activité ce mois"
            description="Créez votre première demande pour générer des statistiques détaillées."
            actionLabel="Nouvelle demande"
            onAction={() => navigate('/dossiers')}
          />
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={monthlyData} margin={{ top: 20, right: 20, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#1D4ED8" stopOpacity={0.08} />
                  <stop offset="95%" stopColor="#1D4ED8" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#94A3B8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12, fill: '#94A3B8' }} axisLine={false} tickLine={false} />
              <RechartsTooltip content={<CustomAreaTooltip monthlyData={monthlyData} />} />
              <Area type="monotone" dataKey="value" stroke="#1D4ED8" strokeWidth={3} fillOpacity={1} fill="url(#colorValue)" dot={{ r: 5, fill: '#1D4ED8', strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 7, fill: '#1D4ED8', strokeWidth: 3, stroke: '#fff' }} />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
