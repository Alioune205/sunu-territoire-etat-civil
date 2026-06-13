// src/components/dashboard/DemandesParType.jsx
import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Cell, LabelList } from 'recharts';
import { EmptyState } from './EmptyState';

const TYPE_LABELS = {
  birth_certificate: 'Acte de naissance',
  marriage_certificate: 'Acte de mariage',
  death_certificate: 'Acte de décès',
  residence_certificate: 'Certificat de résidence',
  other: 'Autre',
};

export function DemandesParType({ loading, stats }) {
  const dataByType = useMemo(() => {
    if (!stats?.dossiers_par_type) return [];
    return Object.entries(stats.dossiers_par_type)
      .filter(([_, count]) => count > 0)
      .map(([type, count]) => ({
        type,
        type_display: TYPE_LABELS[type] || type,
        count
      }))
      .sort((a, b) => b.count - a.count);
  }, [stats]);

  const totalDossiers = useMemo(() => {
    return dataByType.reduce((sum, item) => sum + item.count, 0);
  }, [dataByType]);

  const maxVal = useMemo(() => {
    if (dataByType.length === 0) return 0;
    return Math.max(...dataByType.map(d => d.count));
  }, [dataByType]);

  return (
    <Card className="lg:col-span-3 lg:row-span-1 border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm p-4 overflow-hidden h-full flex flex-col">
      <CardHeader className="p-0 pb-4 flex-shrink-0">
        <CardTitle className="text-base font-semibold text-secondary dark:text-white">
          Demandes par type
        </CardTitle>
        <p className="text-[11px] text-muted-foreground mt-0.5">Données cumulées depuis l'ouverture du système</p>
      </CardHeader>
      <CardContent className="p-0 flex-1 min-h-0">
        {loading ? (
          <Skeleton className="h-full w-full rounded-xl" />
        ) : dataByType.length === 0 ? (
          <EmptyState
            variant="no-data"
            title="Aucune demande par type"
            description="Les données n'ont pas encore été générées."
          />
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dataByType} layout="vertical" margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" horizontal={false} />
              <XAxis type="number" domain={[0, Math.ceil(maxVal * 1.15)]} hide />
              <YAxis type="category" dataKey="type_display" tick={{ fontSize: 11, fill: '#64748B' }} axisLine={false} tickLine={false} width={160} />
              <RechartsTooltip 
                cursor={{fill: 'transparent'}}
                formatter={(value) => {
                  const pct = totalDossiers > 0 ? ((value / totalDossiers) * 100).toFixed(1) : 0;
                  return [`${value} demandes (${pct}%)`, 'Proportion'];
                }}
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }} 
              />
              <Bar dataKey="count" fill="#1D4ED8" radius={[0, 4, 4, 0]} barSize={20}>
                {dataByType.map((entry, index) => (
                  <Cell key={`cell-${index}`} fillOpacity={1 - (index * 0.15)} />
                ))}
                <LabelList dataKey="count" position="right" fontSize={12} fill="#64748B" offset={12} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
