// src/pages/DossierDetail.jsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getDossier, patchDossier, reviewDossier, approveDossier, rejectDossier, completeDossier, takeDossier, getDossierComments, addDossierComment } from '@/api/dossiers';
import { StatusBadge } from '@/components/StatusBadge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from '@/components/ui/use-toast';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  ArrowLeft,
  User,
  Building2,
  Calendar,
  FileText,
  Loader2,
  CheckCircle,
  XCircle,
  PlayCircle,
  FileDown,
  ExternalLink,
  Check,
  X,
  Clock,
  Flag,
  MessageSquare,
  Send
} from 'lucide-react';

const WORKFLOW_STEPS = [
  { key: 'draft', label: 'Brouillon', icon: FileText },
  { key: 'submitted', label: 'Soumis', icon: Clock },
  { key: 'in_review', label: 'En vérification', icon: PlayCircle },
  { key: 'approved_or_rejected', label: 'Approuvé/Rejeté', icon: CheckCircle },
  { key: 'completed', label: 'Terminé', icon: Flag },
];

const STATUS_ORDER = ['draft', 'submitted', 'in_review', 'approved', 'rejected', 'completed'];

function getStepStatus(stepKey, currentStatus) {
  const currentIndex = STATUS_ORDER.indexOf(currentStatus);
  
  if (stepKey === 'approved_or_rejected') {
    if (currentStatus === 'rejected') return 'rejected';
    if (currentStatus === 'approved' || currentStatus === 'completed') return 'passed';
    if (currentIndex >= STATUS_ORDER.indexOf('approved')) return 'passed';
    return 'future';
  }
  
  const stepMapping = {
    draft: 0,
    submitted: 1,
    in_review: 2,
    completed: 5,
  };
  
  const stepIndex = stepMapping[stepKey];
  if (stepIndex === undefined) return 'future';
  
  if (stepKey === 'completed') {
    return currentStatus === 'completed' ? 'passed' : 'future';
  }
  
  if (stepIndex < currentIndex) return 'passed';
  if (stepIndex === currentIndex) return 'active';
  return 'future';
}

export default function DossierDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [dossier, setDossier] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loadingComments, setLoadingComments] = useState(false);

  useEffect(() => {
    fetchDossier();
  }, [id]);

  const fetchDossier = async () => {
    setLoading(true);
    try {
      const data = await getDossier(id);
      setDossier(data);
    } catch (error) {
      toast({ title: 'Erreur', description: 'Impossible de charger le dossier.', variant: 'destructive' });
      navigate('/dossiers');
    } finally {
      setLoading(false);
    }
  };

  const fetchComments = async () => {
    try {
      const data = await getDossierComments(id);
      setComments(data.data || []);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    if (dossier) {
      fetchComments();
    }
  }, [dossier]);

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    setLoadingComments(true);
    try {
      await addDossierComment(id, newComment);
      setNewComment('');
      fetchComments();
    } catch (error) {
      toast({ title: 'Erreur', description: 'Impossible d\'ajouter le commentaire.', variant: 'destructive' });
    } finally {
      setLoadingComments(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    setActionLoading(true);
    try {
      if (newStatus === 'take') {
        await takeDossier(id);
      } else if (newStatus === 'in_review') {
        await reviewDossier(id);
      } else if (newStatus === 'approved') {
        await approveDossier(id);
      } else if (newStatus === 'completed') {
        await completeDossier(id);
      }
      toast({
        title: 'Statut mis à jour',
        description: `Le dossier a été mis à jour avec succès.`,
        variant: 'success',
      });
      fetchDossier();
    } catch (error) {
      toast({ title: 'Erreur', description: 'Impossible de mettre à jour le statut.', variant: 'destructive' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (rejectionReason.length < 20) return;
    setActionLoading(true);
    try {
      await rejectDossier(id, rejectionReason);
      toast({ title: 'Dossier rejeté', description: 'Le dossier a été rejeté.', variant: 'success' });
      setRejectDialogOpen(false);
      setRejectionReason('');
      fetchDossier();
    } catch (error) {
      toast({ title: 'Erreur', description: 'Impossible de rejeter le dossier.', variant: 'destructive' });
    } finally {
      setActionLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-enter">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-20 w-full" />
        <div className="grid grid-cols-2 gap-6">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      </div>
    );
  }

  if (!dossier) return null;

  return (
    <div className="space-y-6 animate-enter">
      {/* Breadcrumb + En-tête */}
      <div>
        <div className="flex items-center gap-2 text-sm text-slate-400 mb-4">
          <Link to="/dossiers" className="hover:text-primary transition-colors">
            Dossiers
          </Link>
          <span>/</span>
          <span className="text-secondary font-medium">{dossier.reference}</span>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-4">
            <Button variant="outline" size="icon" onClick={() => navigate('/dossiers')}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold text-secondary">{dossier.reference}</h1>
                <StatusBadge status={dossier.status} />
              </div>
              <p className="text-sm text-slate-500 mt-1">{dossier.type_display}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Timeline horizontale */}
      <Card className="border-slate-100 p-6">
        <div className="flex items-center justify-between">
          {WORKFLOW_STEPS.map((step, index) => {
            const stepStatus = getStepStatus(step.key, dossier.status);
            const StepIcon = step.icon;

            return (
              <div key={step.key} className="flex items-center flex-1">
                <div className="flex flex-col items-center gap-2 relative">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300 ${
                      stepStatus === 'active'
                        ? 'bg-primary border-primary text-white shadow-lg shadow-primary/30'
                        : stepStatus === 'passed'
                        ? 'bg-success border-success text-white'
                        : stepStatus === 'rejected'
                        ? 'bg-danger border-danger text-white'
                        : 'bg-white border-slate-200 text-slate-400'
                    }`}
                  >
                    {stepStatus === 'passed' ? (
                      <Check className="h-5 w-5" />
                    ) : stepStatus === 'rejected' ? (
                      <X className="h-5 w-5" />
                    ) : (
                      <StepIcon className="h-5 w-5" />
                    )}
                  </div>
                  <span
                    className={`text-xs font-medium text-center whitespace-nowrap ${
                      stepStatus === 'active'
                        ? 'text-primary'
                        : stepStatus === 'passed'
                        ? 'text-success'
                        : stepStatus === 'rejected'
                        ? 'text-danger'
                        : 'text-slate-400'
                    }`}
                  >
                    {step.label}
                  </span>
                </div>
                {index < WORKFLOW_STEPS.length - 1 && (
                  <div
                    className={`flex-1 h-0.5 mx-2 mt-[-20px] ${
                      stepStatus === 'passed' || stepStatus === 'active'
                        ? 'bg-success'
                        : stepStatus === 'rejected'
                        ? 'bg-danger'
                        : 'bg-slate-200'
                    }`}
                  />
                )}
              </div>
            );
          })}
        </div>
      </Card>

      {/* Deux colonnes d'infos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Colonne gauche */}
        <div className="space-y-6">
          {/* Citoyen */}
          <Card className="border-slate-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-semibold text-secondary flex items-center gap-2">
                <User className="h-4 w-4 text-primary" />
                Citoyen
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoRow label="Nom complet" value={dossier.citizen?.full_name} />
              <InfoRow label="Email" value={dossier.citizen?.email} />
              <InfoRow label="Téléphone" value={dossier.citizen?.phone} />
            </CardContent>
          </Card>

          {/* Commune */}
          <Card className="border-slate-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-semibold text-secondary flex items-center gap-2">
                <Building2 className="h-4 w-4 text-primary" />
                Commune
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoRow label="Commune" value={dossier.commune?.name} />
              <InfoRow label="Région" value={dossier.commune?.region} />
            </CardContent>
          </Card>

          {/* Agent assigné */}
          <Card className="border-slate-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-semibold text-secondary flex items-center gap-2">
                <User className="h-4 w-4 text-primary" />
                Agent assigné
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {dossier.assigned_agent ? (
                <>
                  <InfoRow label="Nom" value={dossier.assigned_agent.full_name} />
                  <InfoRow label="Email" value={dossier.assigned_agent.email} />
                </>
              ) : (
                <p className="text-sm text-slate-400 italic">Aucun agent assigné</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Colonne droite */}
        <div className="space-y-6">
          {/* Dates */}
          <Card className="border-slate-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-semibold text-secondary flex items-center gap-2">
                <Calendar className="h-4 w-4 text-primary" />
                Chronologie
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoRow label="Créé le" value={formatDate(dossier.created_at)} />
              <InfoRow label="Soumis le" value={formatDate(dossier.submitted_at)} />
              <InfoRow label="Terminé le" value={formatDate(dossier.completed_at)} />
            </CardContent>
          </Card>

          {/* Notes internes */}
          <Card className="border-slate-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-semibold text-secondary flex items-center gap-2">
                <FileText className="h-4 w-4 text-primary" />
                Notes internes
              </CardTitle>
            </CardHeader>
            <CardContent>
              {dossier.notes ? (
                <p className="text-sm text-slate-600 whitespace-pre-wrap">{dossier.notes}</p>
              ) : (
                <p className="text-sm text-slate-400 italic">Aucune note</p>
              )}
              {dossier.rejection_reason && (
                <div className="mt-4 p-3 bg-danger/5 border border-danger/20 rounded-lg">
                  <p className="text-xs font-semibold text-danger mb-1">Motif de rejet</p>
                  <p className="text-sm text-slate-700">{dossier.rejection_reason}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Documents joints */}
      {dossier.documents && dossier.documents.length > 0 && (
        <Card className="border-slate-100">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-semibold text-secondary">
              Documents joints ({dossier.documents.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {dossier.documents.map((doc) => (
                <div
                  key={doc.id}
                  className="border border-slate-100 rounded-lg p-4 hover:bg-slate-50 transition-colors group"
                >
                  {doc.file_type === 'image' && (
                    <div className="aspect-video bg-slate-100 rounded-md mb-3 overflow-hidden">
                      <img
                        src={`http://localhost:8000${doc.url}`}
                        alt={doc.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    </div>
                  )}
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-secondary">{doc.name}</p>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {doc.uploaded_at
                          ? new Date(doc.uploaded_at).toLocaleDateString('fr-FR')
                          : ''}
                      </p>
                    </div>
                    <a
                      href={`http://localhost:8000${doc.url}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2 rounded-lg text-primary hover:bg-primary/10 transition-colors"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Section Commentaires */}
      <Card className="border-slate-100 shadow-sm mt-6">
        <CardHeader className="pb-3 border-b border-slate-100">
          <CardTitle className="text-base font-semibold text-secondary flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-primary" />
            Commentaires internes
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="max-h-60 overflow-y-auto p-4 space-y-4 bg-slate-50">
            {comments.length === 0 ? (
              <p className="text-sm text-slate-400 text-center py-4 italic">Aucun commentaire pour le moment.</p>
            ) : (
              comments.map((c) => (
                <div key={c.id} className="bg-white p-3 rounded-lg border border-slate-100 shadow-sm">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-semibold text-secondary">{c.author_name || 'Agent'}</span>
                    <span className="text-xs text-slate-400">{formatDate(c.created_at)}</span>
                  </div>
                  <p className="text-sm text-slate-600 whitespace-pre-wrap">{c.text}</p>
                </div>
              ))
            )}
          </div>
          <form onSubmit={handleAddComment} className="p-4 border-t border-slate-100 bg-white flex gap-3">
            <input
              type="text"
              placeholder="Écrire un commentaire..."
              className="flex-1 px-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-primary"
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              disabled={loadingComments}
            />
            <Button type="submit" disabled={!newComment.trim() || loadingComments} className="px-4">
              {loadingComments ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Zone d'actions sticky en bas */}
      {(dossier.status === 'submitted' ||
        dossier.status === 'in_review' ||
        dossier.status === 'approved') && (
        <div className="sticky bottom-0 bg-white border-t border-slate-100 shadow-lg rounded-t-xl p-4 -mx-6 -mb-6">
          <div className="flex items-center justify-end gap-3 max-w-7xl mx-auto">
            {dossier.status === 'submitted' && (
              <>
                {!dossier.assigned_agent ? (
                  <Button
                    onClick={() => handleStatusChange('take')}
                    disabled={actionLoading}
                    className="gap-2"
                  >
                    {actionLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <PlayCircle className="h-4 w-4" />
                    )}
                    Prendre en charge
                  </Button>
                ) : (
                  <Button
                    onClick={() => handleStatusChange('in_review')}
                    disabled={actionLoading}
                    className="gap-2"
                  >
                    {actionLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <PlayCircle className="h-4 w-4" />
                    )}
                    Mettre en vérification
                  </Button>
                )}
                <Button
                  variant="destructive"
                  onClick={() => setRejectDialogOpen(true)}
                  disabled={actionLoading}
                  className="gap-2"
                >
                  <XCircle className="h-4 w-4" />
                  Rejeter
                </Button>
              </>
            )}

            {dossier.status === 'in_review' && (
              <>
                <Button
                  variant="success"
                  onClick={() => handleStatusChange('approved')}
                  disabled={actionLoading}
                  className="gap-2 bg-success hover:bg-success/90 text-white"
                >
                  {actionLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <CheckCircle className="h-4 w-4" />
                  )}
                  Approuver
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => setRejectDialogOpen(true)}
                  disabled={actionLoading}
                  className="gap-2"
                >
                  <XCircle className="h-4 w-4" />
                  Rejeter
                </Button>
              </>
            )}

            {dossier.status === 'approved' && (
              <>
                <Button
                  onClick={() => handleStatusChange('completed')}
                  disabled={actionLoading}
                  className="gap-2"
                >
                  {actionLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Flag className="h-4 w-4" />
                  )}
                  Marquer terminé
                </Button>
                {dossier.documents && dossier.documents.length > 0 && (
                  <Button variant="outline" className="gap-2" onClick={() => window.open(`http://localhost:8000${dossier.documents[0].url}`, '_blank')}>
                    <FileDown className="h-4 w-4" /> Télécharger l'acte ({dossier.documents[0].name})
                  </Button>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* Dialog de rejet */}
      <Dialog open={rejectDialogOpen} onOpenChange={setRejectDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="text-danger">Confirmer le rejet</DialogTitle>
            <DialogDescription>
              Cette action est irréversible. Veuillez indiquer le motif du rejet.
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
              {rejectionReason.length >= 20 && <span className="text-success ml-2">✓</span>}
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRejectDialogOpen(false)}>
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

// Composant utilitaire pour afficher une ligne d'information
function InfoRow({ label, value }) {
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-slate-50 last:border-0">
      <span className="text-sm text-slate-500">{label}</span>
      <span className="text-sm font-medium text-secondary">{value || '—'}</span>
    </div>
  );
}
