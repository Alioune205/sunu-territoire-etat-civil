// src/pages/Dashboard.jsx
import { useNavigate } from 'react-router-dom';
import { useDashboard } from '@/hooks/useDashboard';
import { KPICard } from '@/components/KPICard';
import { Button } from '@/components/ui/button';
import { toast } from '@/components/ui/use-toast';
import { FileText, Clock, Eye, CheckCircle, XCircle, TrendingUp, RefreshCw, Download } from 'lucide-react';

import { ActiviteMensuelle } from '@/components/dashboard/ActiviteMensuelle';
import { RepartitionStatut } from '@/components/dashboard/RepartitionStatut';
import { Top5Communes } from '@/components/dashboard/Top5Communes';
import { DemandesParType } from '@/components/dashboard/DemandesParType';

const exportCSV = (stats, globalStats) => {
  if (!stats) return;
  const headers = ['Métrique', 'Valeur'];
  const rows = [
    ['Total Demandes', stats.total_dossiers],
    ['Soumis', stats.status_counts?.submitted || 0],
    ['En vérification', stats.status_counts?.in_review || 0],
    ['Approuvés/Validés', (stats.status_counts?.validated || stats.status_counts?.approved) || 0],
    ['Rejetés', stats.status_counts?.rejected || 0],
    ['Terminés/Délivrés', (stats.status_counts?.delivered || stats.status_counts?.completed) || 0],
    ['Taux d\'approbation', `${globalStats?.taux_approbation || 0}%`],
    ['Temps moyen de traitement', stats.average_review_time || 'N/A'],
  ];

  if (stats.dossiers_par_commune) {
    rows.push(['', '']);
    rows.push(['Commune', 'Nombre de demandes']);
    stats.dossiers_par_commune.forEach((c) => {
      rows.push([c.commune, c.count]);
    });
  }

  const csv = [headers, ...rows].map((r) => r.join(';')).join('\n');
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `export_dashboard_${new Date().toISOString().split('T')[0]}.csv`;
  a.click();
  URL.revokeObjectURL(a.href);

  toast({ title: 'Export réussi', description: 'Le fichier CSV a été téléchargé.', variant: 'success' });
};

export default function Dashboard() {
  const navigate = useNavigate();
  const { stats, globalStats, activity, loading, lastUpdated, refresh } = useDashboard();

  const getTimeSinceUpdate = () => {
    if (!lastUpdated) return '';
    const diff = Math.floor((Date.now() - lastUpdated.getTime()) / 60000);
    if (diff < 1) return 'à l\'instant';
    if (diff === 1) return 'il y a 1 min';
    return `il y a ${diff} min`;
  };

  const isDossiersEmpty = !stats || stats.total_dossiers === 0;
  const approbationRateValue = isDossiersEmpty ? '–' : `${globalStats?.taux_approbation || 0}%`;

  return (
    <div className="h-full flex flex-col overflow-hidden gap-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-100 dark:border-slate-800 shrink-0">
        <div className="space-y-1">
          <div className="text-sm font-medium text-slate-400 dark:text-slate-500">
            Accueil / <span className="text-slate-700 dark:text-slate-300">Tableau de bord</span>
          </div>
          <p className="text-[13px] text-slate-500 dark:text-slate-400 font-normal">
            Vue d'ensemble · Mis à jour {lastUpdated ? getTimeSinceUpdate() : "il y a 2 min"}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={() => exportCSV(stats, globalStats)} disabled={loading || !stats} className="gap-2">
            <Download className="h-4 w-4" /> Export CSV
          </Button>
          <div className="h-6 w-px bg-slate-200 dark:bg-slate-800 hidden sm:block" />
          <Button variant="outline" size="sm" onClick={refresh} disabled={loading} className="gap-2">
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} /> Rafraîchir
          </Button>
        </div>
      </div>

      {/* Section A — 6 KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-6 gap-4 shrink-0">
        <KPICard title="Total demandes" value={stats?.total_dossiers ?? 0} icon={FileText} iconColorClass="text-blue-700 bg-blue-50 dark:bg-blue-900/20" loading={loading} onClick={() => navigate('/dossiers')} />
        <KPICard title="En attente" value={stats?.status_counts?.submitted ?? 0} icon={Clock} iconColorClass="text-amber-500 bg-amber-50 dark:bg-amber-900/20" criticalStatus="warning" loading={loading} onClick={() => navigate('/dossiers?status=submitted')} />
        <KPICard title="En vérification" value={stats?.status_counts?.in_review ?? 0} icon={Eye} iconColorClass="text-blue-500 bg-blue-50 dark:bg-blue-900/20" loading={loading} onClick={() => navigate('/dossiers?status=in_review')} />
        <KPICard title="Validés" value={stats?.status_counts?.validated ?? (stats?.status_counts?.approved ?? 0)} icon={CheckCircle} iconColorClass="text-emerald-500 bg-emerald-50 dark:bg-emerald-900/20" loading={loading} onClick={() => navigate('/dossiers?status=validated')} />
        <KPICard title="Rejetés" value={stats?.status_counts?.rejected ?? 0} icon={XCircle} iconColorClass="text-red-500 bg-red-50 dark:bg-red-900/20" criticalStatus="error" loading={loading} onClick={() => navigate('/dossiers?status=rejected')} />
        <KPICard title="Taux d'approbation" value={approbationRateValue} icon={TrendingUp} iconColorClass="text-blue-700 bg-blue-50 dark:bg-blue-900/20" loading={loading} />
      </div>

      {/* Sections Graphiques */}
      <div className="grid grid-cols-1 lg:grid-cols-5 lg:grid-rows-2 gap-4 flex-1 min-h-0">
        <ActiviteMensuelle loading={loading} activity={activity} />
        <RepartitionStatut loading={loading} stats={stats} />
        <DemandesParType loading={loading} stats={stats} />
        <Top5Communes loading={loading} stats={stats} />
      </div>
    </div>
  );
}
