// src/components/dashboard/Top5Communes.jsx
import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Cell, LabelList } from 'recharts';
import { EmptyState } from './EmptyState';

export function Top5Communes({ loading, stats }) {
  const topCommunes = useMemo(() => {
    if (!stats?.dossiers_par_commune) return [];
    const sorted = [...stats.dossiers_par_commune].filter((c) => c.count > 0).sort((a, b) => b.count - a.count);
    return sorted.slice(0, 5);
  }, [stats]);

  const maxVal = useMemo(() => {
    if (topCommunes.length === 0) return 0;
    return Math.max(...topCommunes.map(c => c.count));
  }, [topCommunes]);

  return (
    <Card className="lg:col-span-2 lg:row-span-1 border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm p-4 overflow-hidden h-full flex flex-col">
      <CardHeader className="p-0 pb-4 flex-shrink-0">
        <CardTitle className="text-base font-semibold text-secondary dark:text-white">
          Top 5 Communes
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0 flex-1 min-h-0">
        {loading ? (
          <Skeleton className="h-full w-full rounded-xl" />
        ) : topCommunes.length === 0 ? (
          <EmptyState
            variant="insufficient"
            title="Aucune donnée communale"
            description="Il n'y a pas assez d'activité dans les communes pour établir un classement."
          />
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={topCommunes} layout="vertical" margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" horizontal={false} />
              <XAxis type="number" domain={[0, Math.ceil(maxVal * 1.15)]} hide />
              <YAxis type="category" dataKey="commune" tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} width={80} />
              <RechartsTooltip cursor={{fill: 'transparent'}} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }} />
              <Bar dataKey="count" fill="#1D4ED8" radius={[0, 4, 4, 0]} barSize={20}>
                {topCommunes.map((entry, index) => (
                  <Cell key={`cell-${index}`} fillOpacity={1 - (index * 0.15)} />
                ))}
                <LabelList dataKey="count" position="right" fontSize={12} fill="#64748B" offset={8} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
