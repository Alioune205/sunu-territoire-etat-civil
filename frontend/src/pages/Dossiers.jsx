// src/pages/Dossiers.jsx
import { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useDossiers } from '@/hooks/useDossiers';
import { getDossiers, patchDossier, assignDossier, approveDossier, rejectDossier } from '@/api/dossiers';
import { getCommuneList } from '@/api/communes';
import { getUserList } from '@/api/users';
import { attributionApi } from '@/services/attributionApi';
import { TYPE_DOSSIER_LABELS, STATUT_LABELS } from '@/utils/labels';
import { StatusBadge } from '@/components/StatusBadge';
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
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
} from '@tanstack/react-table';
import {
  Search,
  RotateCcw,
  MoreHorizontal,
  Eye,
  UserPlus,
  CheckCircle,
  XCircle,
  FileDown,
  ChevronLeft,
  ChevronRight,
  Loader2,
} from 'lucide-react';

const STATUS_OPTIONS = [
  { value: '', label: 'Tous les statuts' },
  { value: 'submitted', label: 'Soumis' },
  { value: 'in_review', label: 'En vérification' },
  { value: 'approved', label: 'Approuvé' },
  { value: 'rejected', label: 'Rejeté' },
  { value: 'completed', label: 'Terminé' },
];

const TYPE_OPTIONS = [
  { value: '', label: 'Tous les types' },
  { value: 'birth_certificate', label: 'Acte de naissance' },
  { value: 'marriage_certificate', label: 'Acte de mariage' },
  { value: 'death_certificate', label: 'Acte de décès' },
  { value: 'residence_certificate', label: 'Certificat de résidence' },
  { value: 'other', label: 'Autre' },
];

const AutoAssignButton = ({ dossier, onAssign }) => {
  const [loading, setLoading] = useState(false);

  const handleAutoAssign = async () => {
    setLoading(true);
    try {
      const recs = await attributionApi.getRecommandation(dossier.id);
      const topAgentId = recs?.recommandations?.[0]?.agent_id;
      if (!topAgentId) throw new Error("Aucune recommandation disponible");
      
      await attributionApi.reattribuerDossier(
        dossier.id, 
        topAgentId, 
        "Auto-assignation depuis la Banque des Demandes"
      );
      toast({ title: 'Succès', description: 'Agent assigné avec succès.', variant: 'success' });
      onAssign();
    } catch (error) {
      console.error(error);
      toast({ title: 'Erreur', description: 'Impossible d\'assigner automatiquement.', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button 
      size="sm" 
      onClick={handleAutoAssign} 
      disabled={loading}
      style={{ backgroundColor: '#1D4ED8', borderRadius: '0.375rem' }}
      className="text-white hover:bg-blue-800 h-7 text-xs px-3"
    >
      {loading ? <Loader2 className="h-3 w-3 animate-spin" /> : 'Assigner'}
    </Button>
  );
};

export default function Dossiers() {
  const navigate = useNavigate();
  const { role, user } = useAuth();
  const { data, loading, params, updateParams, setPage, refresh } = useDossiers();
  const [communes, setCommunes] = useState([]);
  const [agents, setAgents] = useState([]);
  const [searchValue, setSearchValue] = useState('');
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [rejectModalOpen, setRejectModalOpen] = useState(false);
  const [selectedDossier, setSelectedDossier] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [agentSearch, setAgentSearch] = useState('');

  // Charger les communes
  useEffect(() => {
    getCommuneList()
      .then((res) => setCommunes(Array.isArray(res) ? res : res.results || []))
      .catch((err) => console.error('Error loading communes:', err));
  }, []);

  // Charger les agents pour l'assignation
  useEffect(() => {
    const baseParams = {};
    const userCommuneId = typeof user?.commune === 'object' ? user.commune?.id : user?.commune;
    if (role === 'civil_admin' && userCommuneId) {
      baseParams.commune = userCommuneId;
    }
    
    Promise.all([
      getUserList({ ...baseParams, role: 'verification_agent' }),
      getUserList({ ...baseParams, role: 'reception_agent' })
    ])
      .then(([verifData, receptData]) => {
        const verifList = Array.isArray(verifData) ? verifData : verifData.results || [];
        const receptList = Array.isArray(receptData) ? receptData : receptData.results || [];
        setAgents([...verifList, ...receptList]);
      })
      .catch((err) => {
        console.error('Error loading agents:', err);
        setAgents([]);
      });
  }, [role, user]);

  // Debounce sur la recherche
  useEffect(() => {
    const timer = setTimeout(() => {
      updateParams({ search: searchValue });
    }, 400);
    return () => clearTimeout(timer);
  }, [searchValue, updateParams]);

  // Reset des filtres
  const handleReset = () => {
    setSearchValue('');
    updateParams({ status: '', type: '', commune: '', search: '', page: 1 });
  };

  // --- NOUVEAU : Connexion Temps Réel (WebSockets) ---
  useEffect(() => {
    // Construction de l'URL WebSocket à partir de l'URL de l'API
    const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';
    const wsUrl = baseUrl.replace('http', 'ws').replace('/api', '/ws/dashboard/');
      
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => console.log('🔗 Connecté au serveur Temps Réel (Banque des Demandes)');

    ws.onmessage = (event) => {
      const parsed = JSON.parse(event.data);
      if (parsed.message === 'new_dossier') {
        // Notification toast visuelle
        toast({
          title: 'Nouvelle demande ! 📄',
          description: `Une nouvelle demande (${parsed.data.reference}) vient d'être soumise.`,
          variant: 'default',
          className: 'bg-blue-50 border-blue-200 text-blue-900',
        });
        // Rafraîchir les données silencieusement
        refresh();
      }
    };

    ws.onclose = () => console.log('❌ Déconnecté du serveur Temps Réel');

    // Nettoyage à la fermeture de la page
    return () => ws.close();
  }, [refresh]);

  // Actions sur un dossier
  const handleApprove = async (dossier) => {
    setActionLoading(true);
    try {
      await approveDossier(dossier.id);
      toast({ title: 'Demande approuvée', description: `${dossier.reference} a été approuvée.`, variant: 'success' });
      refresh();
    } catch (error) {
      toast({ title: 'Erreur', description: 'Impossible d\'approuver la demande.', variant: 'destructive' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleAssign = async () => {
    if (!selectedAgent || !selectedDossier) return;
    setActionLoading(true);
    try {
      await assignDossier(selectedDossier.id, selectedAgent);
      toast({ title: 'Agent assigné', description: `Agent assigné à la demande ${selectedDossier.reference}.`, variant: 'success' });
      setAssignModalOpen(false);
      setSelectedAgent('');
      setSelectedDossier(null);
      refresh();
    } catch (error) {
      toast({ title: 'Erreur', description: 'Impossible d\'assigner l\'agent.', variant: 'destructive' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!rejectionReason || rejectionReason.length < 20 || !selectedDossier) return;
    setActionLoading(true);
    try {
      await rejectDossier(selectedDossier.id, rejectionReason);
      toast({ title: 'Demande rejetée', description: `${selectedDossier.reference} a été rejetée.`, variant: 'success' });
      setRejectModalOpen(false);
      setRejectionReason('');
      setSelectedDossier(null);
      refresh();
    } catch (error) {
      toast({ title: 'Erreur', description: 'Impossible de rejeter la demande.', variant: 'destructive' });
    } finally {
      setActionLoading(false);
    }
  };

  // Colonnes TanStack Table
  const columns = useMemo(
    () => [
      {
        accessorKey: 'reference',
        header: 'Référence',
        cell: ({ row }) => (
          <button
            onClick={() => navigate(`/dossiers/${row.original.id}`)}
            className="text-primary font-medium hover:underline"
          >
            {row.original.reference}
          </button>
        ),
      },
      {
        accessorKey: 'type_display',
        header: 'Type',
        cell: ({ row }) => (
          <span className="text-sm text-slate-600">{TYPE_DOSSIER_LABELS[row.original.type] || row.original.type_display}</span>
        ),
      },
      {
        accessorKey: 'status',
        header: 'Statut',
        cell: ({ row }) => (
          <span className="text-sm font-medium">
            {STATUT_LABELS[row.original.status] || <StatusBadge status={row.original.status} />}
          </span>
        ),
      },
      {
        accessorKey: 'citizen',
        header: 'Citoyen',
        cell: ({ row }) => (
          <span className="text-sm text-slate-700 font-medium">
            {row.original.citizen?.full_name || '—'}
          </span>
        ),
      },
      {
        accessorKey: 'commune',
        header: 'Commune',
        cell: ({ row }) => (
          <span className="text-sm text-slate-600">{row.original.commune?.name || '—'}</span>
        ),
      },
      {
        accessorKey: 'assigned_agent',
        header: 'Agent',
        cell: ({ row }) => {
          if (row.original.assigned_agent) {
            return (
              <span className="text-sm text-slate-600">
                {row.original.assigned_agent.full_name || row.original.assigned_agent.email}
              </span>
            );
          }
          return <AutoAssignButton dossier={row.original} onAssign={refresh} />;
        },
      },
      {
        accessorKey: 'created_at',
        header: 'Date',
        cell: ({ row }) => (
          <span className="text-sm text-slate-500">
            {row.original.created_at
              ? new Date(row.original.created_at).toLocaleDateString('fr-FR', {
                  day: '2-digit',
                  month: 'short',
                  year: 'numeric',
                })
              : '—'}
          </span>
        ),
      },
      {
        id: 'actions',
        header: '',
        cell: ({ row }) => {
          const dossier = row.original;
          return (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem onClick={() => navigate(`/dossiers/${dossier.id}`)}>
                  <Eye className="h-4 w-4 mr-2" /> Voir
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => {
                    setSelectedDossier(dossier);
                    setAssignModalOpen(true);
                  }}
                >
                  <UserPlus className="h-4 w-4 mr-2" /> Assigner agent
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                {dossier.status === 'in_review' && (
                  <DropdownMenuItem onClick={() => handleApprove(dossier)}>
                    <CheckCircle className="h-4 w-4 mr-2 text-success" /> Valider
                  </DropdownMenuItem>
                )}
                {(dossier.status === 'submitted' || dossier.status === 'in_review') && (
                  <DropdownMenuItem
                    onClick={() => {
                      setSelectedDossier(dossier);
                      setRejectModalOpen(true);
                    }}
                    className="text-danger"
                  >
                    <XCircle className="h-4 w-4 mr-2" /> Rejeter
                  </DropdownMenuItem>
                )}
                <DropdownMenuSeparator />
                <DropdownMenuItem disabled title="PDF disponible après livraison DEV 1B">
                  <FileDown className="h-4 w-4 mr-2" /> PDF (bientôt)
                </DropdownMenuItem>
                {/* TODO: brancher POST /api/dossiers/{id}/generer-pdf/ (DEV 1B) */}
              </DropdownMenuContent>
            </DropdownMenu>
          );
        },
      },
    ],
    [navigate, refresh]
  );

  const table = useReactTable({
    data: data.results || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
    manualPagination: true,
    pageCount: Math.ceil((data.count || 0) / 20),
  });

  const totalPages = Math.ceil((data.count || 0) / 20);
  const currentPage = params.page || 1;

  // Filtrer les agents pour le modal
  const filteredAgents = agents.filter(
    (a) =>
      a.full_name?.toLowerCase().includes(agentSearch.toLowerCase()) ||
      a.email?.toLowerCase().includes(agentSearch.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-secondary">Banque des Demandes</h1>
        <p className="text-sm text-slate-500 mt-1">
          {data.count || 0} demande{(data.count || 0) > 1 ? 's' : ''} enregistrée{(data.count || 0) > 1 ? 's' : ''}
        </p>
      </div>

      {/* Barre de filtres */}
      <Card className="p-4 border-slate-100">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Rechercher par référence..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              className="pl-9"
            />
          </div>
          <Select
            value={params.status || ''}
            onValueChange={(val) => updateParams({ status: val })}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Tous les statuts" />
            </SelectTrigger>
            <SelectContent>
              {STATUS_OPTIONS.map((opt) => (
                <SelectItem key={opt.value || 'all-status'} value={opt.value || 'all'}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select
            value={params.type || ''}
            onValueChange={(val) => updateParams({ type: val })}
          >
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Tous les types" />
            </SelectTrigger>
            <SelectContent>
              {TYPE_OPTIONS.map((opt) => (
                <SelectItem key={opt.value || 'all-type'} value={opt.value || 'all'}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {role !== 'civil_admin' && (
            <Select
              value={params.commune || ''}
              onValueChange={(val) => updateParams({ commune: val })}
            >
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Toutes communes" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Toutes communes</SelectItem>
                {communes.map((c) => (
                  <SelectItem key={c.id} value={String(c.id)}>
                    {c.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
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
                {table.getHeaderGroups().map((headerGroup) =>
                  headerGroup.headers.map((header) => (
                    <th
                      key={header.id}
                      className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider"
                    >
                      {header.isPlaceholder
                        ? null
                        : flexRender(header.column.columnDef.header, header.getContext())}
                    </th>
                  ))
                )}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i} className="border-b border-slate-50">
                    {columns.map((_, j) => (
                      <td key={j} className="px-4 py-3">
                        <Skeleton className="h-5 w-full" />
                      </td>
                    ))}
                  </tr>
                ))
              ) : table.getRowModel().rows.length > 0 ? (
                table.getRowModel().rows.map((row) => (
                  <tr
                    key={row.id}
                    className="border-b border-slate-50 hover:bg-slate-50/50 transition-colors"
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="px-4 py-3">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={columns.length} className="px-4 py-12 text-center text-slate-400">
                    Aucune demande trouvée
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
              Page {currentPage} sur {totalPages} — {data.count} résultat{data.count > 1 ? 's' : ''}
            </p>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage <= 1}
                onClick={() => setPage(currentPage - 1)}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              {[...Array(Math.min(totalPages, 5))].map((_, i) => {
                let pageNum;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (currentPage <= 3) {
                  pageNum = i + 1;
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = currentPage - 2 + i;
                }
                return (
                  <Button
                    key={pageNum}
                    variant={currentPage === pageNum ? 'default' : 'outline'}
                    size="sm"
                    className="w-9"
                    onClick={() => setPage(pageNum)}
                  >
                    {pageNum}
                  </Button>
                );
              })}
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage >= totalPages}
                onClick={() => setPage(currentPage + 1)}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </Card>

      {/* Modal Assignation */}
      <Dialog open={assignModalOpen} onOpenChange={setAssignModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Assigner un agent</DialogTitle>
            <DialogDescription>
              Sélectionnez l'agent à assigner à la demande {selectedDossier?.reference}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Input
              placeholder="Rechercher un agent..."
              value={agentSearch}
              onChange={(e) => setAgentSearch(e.target.value)}
            />
            <div className="max-h-[300px] overflow-y-auto space-y-1">
              {filteredAgents.length > 0 ? (
                filteredAgents.map((agent) => (
                  <button
                    key={agent.id}
                    onClick={() => setSelectedAgent(String(agent.id))}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      selectedAgent === String(agent.id)
                        ? 'bg-primary/10 border border-primary/30'
                        : 'hover:bg-slate-50 border border-transparent'
                    }`}
                  >
                    <p className="text-sm font-medium text-secondary">{agent.full_name}</p>
                    <p className="text-xs text-slate-400">{agent.email}</p>
                  </button>
                ))
              ) : (
                <p className="text-sm text-slate-400 text-center py-4">Aucun agent trouvé</p>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAssignModalOpen(false)}>
              Annuler
            </Button>
            <Button onClick={handleAssign} disabled={!selectedAgent || actionLoading}>
              {actionLoading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Confirmer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal Rejet */}
      <Dialog open={rejectModalOpen} onOpenChange={setRejectModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="text-danger">Rejeter la demande</DialogTitle>
            <DialogDescription>
              Indiquez le motif du rejet pour la demande {selectedDossier?.reference}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <textarea
              placeholder="Motif du rejet (minimum 20 caractères)..."
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              className="w-full min-h-[120px] p-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary resize-none"
            />
            <p className="text-xs text-slate-400">
              {rejectionReason.length}/20 caractères minimum
              {rejectionReason.length >= 20 && (
                <span className="text-success ml-2">✓</span>
              )}
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRejectModalOpen(false)}>
              Annuler
            </Button>
            <Button
              variant="destructive"
              onClick={handleReject}
              disabled={rejectionReason.length < 20 || actionLoading}
            >
              {actionLoading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Confirmer le rejet
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
