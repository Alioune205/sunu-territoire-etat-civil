// src/pages/Dashboard.jsx
import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDashboard } from '@/hooks/useDashboard';
import { KPICard } from '@/components/KPICard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from '@/components/ui/use-toast';
import {
  FileText,
  Clock,
  Eye,
  CheckCircle,
  XCircle,
  TrendingUp,
  RefreshCw,
  Download,
  LineChart as LineChartIcon,
  MapPin,
  Database,
  BarChart2,
  AlertCircle
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  BarChart,
  Bar,
  LabelList,
} from 'recharts';

// Mock données par type (triées) — attend DEV 1C (Maïmouna Sall)
const MOCK_BY_TYPE = [
  { type: 'birth_certificate', type_display: 'Acte de naissance', count: 520 },
  { type: 'residence_certificate', type_display: 'Certificat de résidence', count: 310 },
  { type: 'marriage_certificate', type_display: 'Acte de mariage', count: 180 },
  { type: 'other', type_display: 'Autre', count: 135 },
  { type: 'death_certificate', type_display: 'Acte de décès', count: 95 },
];

const STATUS_COLORS = {
  draft: '#EF9F27',
  submitted: '#F59E0B',
  in_review: '#378ADD',
  approved: '#10B981',
  validated: '#10B981',
  rejected: '#EF4444',
  completed: '#1D9E75',
  delivered: '#1D9E75',
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

// Custom EmptyState component unifié
function EmptyState({ variant = 'no-data', title, description, actionLabel, onAction }) {
  let Icon = Database;
  let iconColor = 'text-slate-400 dark:text-slate-500';
  
  if (variant === 'insufficient') {
    Icon = BarChart2;
    iconColor = 'text-amber-500';
    description = description || "Pas assez de données pour le moment.";
  } else if (variant === 'error') {
    Icon = AlertCircle;
    iconColor = 'text-red-500';
  }

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center select-none animate-enter">
      <div className="relative mb-5">
        <div className="absolute inset-0 bg-slate-100 dark:bg-slate-800 rounded-full blur-xl scale-125"></div>
        <div className={`relative bg-white dark:bg-slate-800 p-4 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 ${iconColor}`}>
          <Icon className="h-10 w-10" strokeWidth={1.5} />
        </div>
      </div>
      <h3 className="text-[15px] font-semibold text-secondary dark:text-slate-200">{title}</h3>
      <p className="text-[13px] text-slate-500 dark:text-slate-400 mt-1.5 max-w-sm leading-relaxed">{description}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} className="mt-5 h-9 bg-blue-700 hover:bg-blue-800 text-white" size="sm">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

// Custom tooltip pour le graphique ligne / area
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
    <div className="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-lg shadow-xl p-3 border-none ring-1 ring-black/5 dark:ring-white/10">
      <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">{label}</p>
      <p className="text-lg font-bold text-primary dark:text-blue-400 mt-1">{currentVal} demandes</p>
      <p className={`text-xs font-medium mt-1 ${isPositive ? 'text-emerald-500' : 'text-rose-500'}`}>
        {diffText}
      </p>
    </div>
  );
}

// Custom tooltip pour le camembert
function CustomPieTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null;
  const item = payload[0];
  const pct = item?.payload?.total ? ((item.value / item.payload.total) * 100).toFixed(1) : 0;
  const fillColor = item?.payload?.fill || '#94A3B8';
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-lg shadow-xl p-3 border-none ring-1 ring-black/5 dark:ring-white/10">
      <p className="text-sm font-medium text-slate-700 dark:text-slate-200">{item?.name || '—'}</p>
      <p className="text-sm font-bold mt-1" style={{ color: fillColor }}>
        {item?.value || 0} demandes ({pct}%)
      </p>
    </div>
  );
}

// Export CSV côté client
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

  if (stats.dossiers_by_commune) {
    rows.push(['', '']);
    rows.push(['Commune', 'Nombre de demandes']);
    stats.dossiers_by_commune.forEach((c) => {
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

  toast({
    title: 'Export réussi',
    description: 'Le fichier CSV a été téléchargé.',
    variant: 'success',
  });
};

export default function Dashboard() {
  const navigate = useNavigate();
  const { stats, globalStats, performance, activity, loading, lastUpdated, refresh } = useDashboard();

  // Formater les données du graphique ligne (activité mensuelle)
  const monthlyData = useMemo(() => {
    if (!activity?.monthly) return [];
    return activity.monthly.map((item, index) => {
      const date = new Date(item.date);
      return {
        name: date.toLocaleDateString('fr-FR', { month: 'short', year: '2-digit' }),
        value: item.count,
        index,
      };
    });
  }, [activity]);

  // Données du camembert (statuts)
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

  // Temps écoulé depuis la dernière mise à jour
  const getTimeSinceUpdate = () => {
    if (!lastUpdated) return '';
    const diff = Math.floor((Date.now() - lastUpdated.getTime()) / 60000);
    if (diff < 1) return 'à l\'instant';
    if (diff === 1) return 'il y a 1 min';
    return `il y a ${diff} min`;
  };

  // Top communes
  const topCommunes = useMemo(() => {
    if (!stats?.dossiers_by_commune) return [];
    const sorted = [...stats.dossiers_by_commune].filter((c) => c.count > 0).sort((a, b) => b.count - a.count);
    const max = sorted[0]?.count || 1;
    return sorted.slice(0, 5).map((c) => ({ ...c, percentage: (c.count / max) * 100 }));
  }, [stats]);

  // Bar color selection for Top communes
  const getCommuneBarColor = (index) => {
    const colors = [
      'bg-primary',
      'bg-[#1D9E75]', // Teal
      'bg-[#EF9F27]', // Amber
      'bg-[#7C3AED]', // Purple
      'bg-[#64748B]', // Slate
    ];
    return colors[index] || 'bg-primary';
  };

  // Dynamic max for Horizontal Bar Chart (Math.ceil(maxValue * 1.15))
  const horizontalBarMax = useMemo(() => {
    const counts = MOCK_BY_TYPE.map((d) => d.count);
    const maxVal = Math.max(...counts, 1);
    return Math.ceil(maxVal / 50) * 50; // arrondi à la 50aine supérieure
  }, []);

  const totalMockDossiers = useMemo(() => {
    return MOCK_BY_TYPE.reduce((sum, item) => sum + item.count, 0);
  }, []);

  // Custom legend pour le camembert
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
                <span
                  className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: entry.color }}
                />
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

  // Taux d'approbation values and badges
  const isDossiersEmpty = !stats || stats.total_dossiers === 0;
  const approbationRateValue = useMemo(() => {
    if (isDossiersEmpty) return '–';
    return `${globalStats?.taux_approbation || 0}%`;
  }, [isDossiersEmpty, globalStats]);




  return (
    <div className="space-y-6">
      {/* Header avec Breadcrumb et Actions (titre H1 dupliqué supprimé) */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-100 dark:border-slate-800">
        <div className="space-y-1">
          <div className="text-sm font-medium text-slate-400 dark:text-slate-500">
            Accueil / <span className="text-slate-700 dark:text-slate-300">Tableau de bord</span>
          </div>
          <p className="text-[13px] text-slate-500 dark:text-slate-400 font-normal">
            Vue d'ensemble · Mis à jour {lastUpdated ? getTimeSinceUpdate() : "il y a 2 min"}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => exportCSV(stats, globalStats)}
            disabled={loading || !stats}
            className="gap-2 focus:ring-2 focus:ring-primary/20"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </Button>
          <div className="h-6 w-px bg-slate-200 dark:bg-slate-800 hidden sm:block" />
          <Button
            variant="outline"
            size="sm"
            onClick={refresh}
            disabled={loading}
            className="gap-2 focus:ring-2 focus:ring-primary/20"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Rafraîchir
          </Button>
        </div>
      </div>

      {/* Section A — 6 KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <KPICard
          title="Total demandes"
          value={stats?.total_dossiers ?? 0}
          icon={FileText}
          iconColorClass="text-blue-700 bg-blue-50 dark:bg-blue-900/20"
          trend={null}
          loading={loading}
          onClick={() => navigate('/dossiers')}
        />
        <KPICard
          title="En attente"
          value={stats?.status_counts?.submitted ?? 0}
          icon={Clock}
          iconColorClass="text-amber-500 bg-amber-50 dark:bg-amber-900/20"
          criticalStatus="warning"
          trend={null}
          loading={loading}
          onClick={() => navigate('/dossiers?status=submitted')}
        />
        <KPICard
          title="En vérification"
          value={stats?.status_counts?.in_review ?? 0}
          icon={Eye}
          iconColorClass="text-blue-500 bg-blue-50 dark:bg-blue-900/20"
          loading={loading}
          onClick={() => navigate('/dossiers?status=in_review')}
        />
        <KPICard
          title="Validés"
          value={stats?.status_counts?.validated ?? (stats?.status_counts?.approved ?? 0)}
          icon={CheckCircle}
          iconColorClass="text-emerald-500 bg-emerald-50 dark:bg-emerald-900/20"
          trend={null}
          loading={loading}
          onClick={() => navigate('/dossiers?status=validated')}
        />
        <KPICard
          title="Rejetés"
          value={stats?.status_counts?.rejected ?? 0}
          icon={XCircle}
          iconColorClass="text-red-500 bg-red-50 dark:bg-red-900/20"
          criticalStatus="error"
          trend={null}
          loading={loading}
          onClick={() => navigate('/dossiers?status=rejected')}
        />
        <KPICard
          title="Taux d'approbation"
          value={approbationRateValue}
          icon={TrendingUp}
          iconColorClass="text-blue-700 bg-blue-50 dark:bg-blue-900/20"
          loading={loading}
        />
      </div>

      {/* Section B & C — Graphiques ligne (Area) + Camembert (Donut) */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Section B — Graphique Area activité mensuelle */}
        <Card className="lg:col-span-3 border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm p-[20px] flex flex-col">
          <CardHeader className="p-0 pb-4">
            <CardTitle className="text-base font-semibold text-secondary dark:text-white">
              Activité mensuelle
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <Skeleton className="h-[300px] w-full rounded-xl" />
            ) : monthlyData.length < 2 ? (
              <EmptyState
                variant="no-data"
                title="Aucune activité ce mois"
                description="Créez votre première demande pour générer des statistiques détaillées et suivre l'évolution."
                actionLabel="Nouvelle demande"
                onAction={() => navigate('/dossiers')}
              />
            ) : (
              <div className="h-[300px]" aria-label="Graphique de l'activité mensuelle des demandes">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={monthlyData} margin={{ top: 20, right: 20, left: -20, bottom: 16 }}>
                    <defs>
                      <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#1D4ED8" stopOpacity={0.08} />
                        <stop offset="95%" stopColor="#1D4ED8" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                    <XAxis
                      dataKey="name"
                      tick={{ fontSize: 12, fill: '#94A3B8' }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fontSize: 12, fill: '#94A3B8' }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <RechartsTooltip content={<CustomAreaTooltip monthlyData={monthlyData} />} />
                    <Area
                      type="monotone"
                      dataKey="value"
                      stroke="#1D4ED8"
                      strokeWidth={3}
                      fillOpacity={1}
                      fill="url(#colorValue)"
                      dot={{ r: 5, fill: '#1D4ED8', strokeWidth: 2, stroke: '#fff' }}
                      activeDot={{ r: 7, fill: '#1D4ED8', strokeWidth: 3, stroke: '#fff' }}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Section C — Camembert Répartition par statut */}
        <Card className="lg:col-span-2 border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm p-[20px] flex flex-col">
          <CardHeader className="p-0 pb-4">
            <CardTitle className="text-base font-semibold text-secondary dark:text-white">
              Répartition par statut
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <Skeleton className="h-[300px] w-full rounded-xl" />
            ) : pieData.length === 0 ? (
              <EmptyState
                variant="no-data"
                title="Aucune donnée de répartition disponible"
                description="Aucune demande n'a été enregistrée pour le moment."
              />
            ) : (
              <div className="relative flex flex-col sm:flex-row items-center justify-around h-[300px] gap-4" aria-label="Graphique circulaire de répartition des demandes par statut">
                <div className="relative w-[200px] h-[200px] flex-shrink-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={65}
                        outerRadius={85}
                        paddingAngle={3}
                        dataKey="value"
                        stroke="none"
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Pie>
                      <RechartsTooltip content={<CustomPieTooltip />} />
                    </PieChart>
                  </ResponsiveContainer>
                  {/* Valeur centrale */}
                  <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <span className="text-2xl font-bold text-secondary dark:text-white">
                      {stats?.total_dossiers ?? 0}
                    </span>
                    <span className="text-[10px] uppercase tracking-wider text-slate-400 dark:text-slate-500 font-semibold mt-0.5">
                      Demandes
                    </span>
                  </div>
                </div>
                
                {/* Légende personnalisée */}
                <div className="flex-1 max-w-[200px]">
                  <Legend
                    layout="vertical"
                    verticalAlign="middle"
                    align="right"
                    content={renderPieLegend}
                  />
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Section D & E — Barres par type + Top communes */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Section D — Graphique barres par type */}
        <Card className="lg:col-span-3 border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm p-[20px] flex flex-col">
          <CardHeader className="p-0 pb-4">
            <CardTitle className="text-base font-semibold text-secondary dark:text-white">
              Demandes par type
            </CardTitle>
            <p className="text-[11px] text-muted-foreground mt-0.5">Données cumulées depuis l'ouverture du système</p>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <Skeleton className="h-[300px] w-full rounded-xl" />
            ) : (
              <div className="h-[300px]" aria-label="Graphique en barres des demandes par type administratif">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={MOCK_BY_TYPE}
                    layout="vertical"
                    margin={{ top: 20, right: 30, left: -20, bottom: 16 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" horizontal={false} />
                    <XAxis
                      type="number"
                      domain={[0, horizontalBarMax]}
                      tickCount={6}
                      allowDecimals={false}
                      tick={{ fontSize: 12, fill: '#94A3B8' }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      type="category"
                      dataKey="type_display"
                      tick={{ fontSize: 11, fill: '#64748B' }}
                      axisLine={false}
                      tickLine={false}
                      width={150}
                    />
                    <RechartsTooltip
                      formatter={(value) => {
                        const pct = totalMockDossiers > 0 ? ((value / totalMockDossiers) * 100).toFixed(1) : 0;
                        return [`${value} demandes (${pct}%)`, 'Proportion'];
                      }}
                      contentStyle={{
                        borderRadius: '8px',
                        border: 'none',
                        boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)',
                      }}
                      className="dark:bg-slate-900 dark:border-slate-800"
                    />
                    <Bar
                      dataKey="count"
                      fill="#1D4ED8"
                      radius={[0, 4, 4, 0]}
                      barSize={20}
                      isAnimationActive={true}
                    >
                      {MOCK_BY_TYPE.map((entry, index) => (
                        <Cell key={`cell-${index}`} fillOpacity={1 - (index * 0.15)} />
                      ))}
                      <LabelList
                        dataKey="count"
                        position="right"
                        fontSize={12}
                        fill="#64748B"
                        className="dark:fill-slate-400 font-semibold"
                        offset={8}
                      />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Section E — Top 5 Communes */}
        <Card className="lg:col-span-2 border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm p-[20px] flex flex-col">
          <CardHeader className="p-0 pb-4">
            <CardTitle className="text-base font-semibold text-secondary dark:text-white">
              Top 5 Communes
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full rounded-lg animate-pulse" />
                ))}
              </div>
            ) : topCommunes.length < 2 ? (
              <EmptyState
                variant="insufficient"
                title="Aucune donnée communale disponible pour cette période."
                description="Il n'y a pas assez d'activité dans les communes pour établir un classement."
              />
            ) : (
              <div className="space-y-4">
                {topCommunes.map((commune, index) => (
                  <div key={index} className="flex items-center gap-4 hover:bg-slate-50/50 dark:hover:bg-slate-800/30 p-2.5 rounded-lg transition-colors duration-150 group">
                    {/* Rang en monospace */}
                    <span className="font-mono text-sm font-semibold text-slate-400 dark:text-slate-600">
                      0{index + 1}
                    </span>
                    <div className="flex-1 space-y-1.5">
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium text-slate-700 dark:text-slate-300">
                          {commune.commune}
                        </span>
                        <span className="text-slate-500 dark:text-slate-400 font-semibold text-[13px]">
                          {commune.count} demandes
                        </span>
                      </div>
                      <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${getCommuneBarColor(index)}`}
                          style={{ width: `${commune.percentage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
