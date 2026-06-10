// src/pages/AuditLogs.jsx
import { useState, useEffect } from 'react';
import { getAuditLogs } from '@/api/auditLogs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from '@/components/ui/use-toast';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Search, RotateCcw, ScrollText, ChevronLeft, ChevronRight } from 'lucide-react';

const ACTION_BADGES = {
  create: { label: 'Création', className: 'bg-[#10B981] text-white border-[#10B981]' },
  update: { label: 'Modification', className: 'bg-[#1D4ED8] text-white border-[#1D4ED8]' },
  delete: { label: 'Suppression', className: 'bg-[#EF4444] text-white border-[#EF4444]' },
  view: { label: 'Consultation', className: 'bg-[#94A3B8] text-white border-[#94A3B8]' },
};

const ACTION_OPTIONS = [
  { value: '', label: 'Toutes les actions' },
  { value: 'create', label: 'Création' },
  { value: 'update', label: 'Modification' },
  { value: 'delete', label: 'Suppression' },
  { value: 'view', label: 'Consultation' },
];

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [actionFilter, setActionFilter] = useState('');
  const [userSearch, setUserSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 20;

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = { page, page_size: pageSize };
      if (dateFrom) params.date_from = dateFrom;
      if (dateTo) params.date_to = dateTo;
      if (actionFilter) params.action = actionFilter;
      if (userSearch) params.search = userSearch;

      const data = await getAuditLogs(params);
      
      if (Array.isArray(data)) {
        setLogs(data);
        setTotalCount(data.length);
      } else {
        setLogs(data.results || []);
        setTotalCount(data.count || 0);
      }
    } catch (error) {
      toast({ title: 'Erreur', description: 'Impossible de charger les logs.', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page, dateFrom, dateTo, actionFilter, userSearch]);

  const handleReset = () => {
    setDateFrom('');
    setDateTo('');
    setActionFilter('');
    setUserSearch('');
    setPage(1);
  };

  const formatTimestamp = (ts) => {
    if (!ts) return '—';
    return new Date(ts).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-secondary">Journal d'audit</h1>
        <p className="text-sm text-slate-500 mt-1">
          Traçabilité de toutes les actions effectuées
        </p>
      </div>

      {/* Filtres */}
      <Card className="p-4 border-slate-100">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Rechercher par utilisateur..."
              value={userSearch}
              onChange={(e) => { setUserSearch(e.target.value); setPage(1); }}
              className="pl-9"
            />
          </div>
          <Select value={actionFilter} onValueChange={(val) => { setActionFilter(val === 'all' ? '' : val); setPage(1); }}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Toutes les actions" />
            </SelectTrigger>
            <SelectContent>
              {ACTION_OPTIONS.map((opt) => (
                <SelectItem key={opt.value || 'all-action'} value={opt.value || 'all'}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <div className="flex items-center gap-2">
            <Input
              type="date"
              value={dateFrom}
              onChange={(e) => { setDateFrom(e.target.value); setPage(1); }}
              className="w-[150px]"
              placeholder="Du"
            />
            <span className="text-slate-400 text-sm">au</span>
            <Input
              type="date"
              value={dateTo}
              onChange={(e) => { setDateTo(e.target.value); setPage(1); }}
              className="w-[150px]"
              placeholder="Au"
            />
          </div>
          <Button variant="outline" size="sm" onClick={handleReset} className="gap-2">
            <RotateCcw className="h-4 w-4" />
            Réinitialiser
          </Button>
        </div>
      </Card>

      {/* Table */}
      <Card className="table-container">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/50">
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Horodatage</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Utilisateur</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Action</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Ressource</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Détails</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">IP</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i} className="border-b border-slate-50">
                    {[...Array(6)].map((_, j) => (
                      <td key={j} className="px-4 py-3">
                        <Skeleton className="h-5 w-full" />
                      </td>
                    ))}
                  </tr>
                ))
              ) : logs.length > 0 ? (
                logs.map((log) => {
                  const actionBadge = ACTION_BADGES[log.action] || ACTION_BADGES.view;
                  return (
                    <tr key={log.id} className="border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
                      <td className="px-4 py-3">
                        <span className="text-sm text-slate-500 font-mono text-xs">
                          {formatTimestamp(log.created_at)}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center">
                            <span className="text-xs font-semibold text-primary">
                              {log.user_name?.charAt(0) || '?'}
                            </span>
                          </div>
                          <span className="text-sm font-medium text-secondary">{log.user_name || '—'}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <Badge className={`${actionBadge.className} text-xs`}>
                          {actionBadge.label}
                        </Badge>
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-sm">
                          <span className="text-slate-600">{log.resource_type}</span>
                          {log.resource_id && (
                            <span className="ml-1 text-primary font-mono text-xs">{log.resource_id}</span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <p className="text-sm text-slate-600 max-w-[300px] truncate" title={typeof log.details === 'object' && log.details !== null ? JSON.stringify(log.details) : log.details}>
                          {typeof log.details === 'object' && log.details !== null ? JSON.stringify(log.details) : log.details || '—'}
                        </p>
                      </td>
                      <td className="px-4 py-3">
                        <code className="text-xs bg-slate-100 px-2 py-1 rounded font-mono text-slate-500">
                          {log.ip_address || '—'}
                        </code>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={6} className="px-4 py-12 text-center text-slate-400">
                    Aucun log trouvé
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-slate-100">
            <p className="text-sm text-slate-500">
              Page {page} sur {totalPages}
            </p>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
