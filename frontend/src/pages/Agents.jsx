// src/pages/Agents.jsx
import { useState, useEffect, useMemo } from 'react';
import { getUserList, createUser } from '@/api/users';
import { getCommuneList } from '@/api/communes';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
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
import { Search, Plus, Loader2, Users as UsersIcon } from 'lucide-react';

const ROLE_BADGES = {
  reception_agent: { label: 'Agent Réception', className: 'bg-[#1D4ED8] text-white border-[#1D4ED8]' },
  verification_agent: { label: 'Agent Vérification', className: 'bg-[#059669] text-white border-[#059669]' },
  civil_admin: { label: 'Admin Civil', className: 'bg-[#EA580C] text-white border-[#EA580C]' },
  super_admin: { label: 'Super Admin', className: 'bg-secondary text-white border-secondary' },
};

const ROLE_OPTIONS = [
  { value: '', label: 'Tous les rôles' },
  { value: 'reception_agent', label: 'Agent Réception' },
  { value: 'verification_agent', label: 'Agent Vérification' },
  { value: 'civil_admin', label: 'Admin Civil' },
];

const STATUS_OPTIONS = [
  { value: '', label: 'Tous les statuts' },
  { value: 'true', label: 'Actif' },
  { value: 'false', label: 'Inactif' },
];

const EMPTY_FORM = {
  full_name: '',
  email: '',
  phone: '',
  role: 'reception_agent',
  commune: '',
  password: '',
};

export default function Agents() {
  const [users, setUsers] = useState([]);
  const [communes, setCommunes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterRole, setFilterRole] = useState('');
  const [filterCommune, setFilterCommune] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filterRole && filterRole !== 'all') params.role = filterRole;
      if (filterCommune && filterCommune !== 'all') params.commune = filterCommune;
      if (filterStatus && filterStatus !== 'all') params.is_active = filterStatus;
      
      const data = await getUserList(params);
      setUsers(Array.isArray(data) ? data : data.results || []);
    } catch (error) {
      if (error?.response?.status !== 401 && error?.status !== 401) {
        toast({ title: 'Erreur', description: 'Impossible de charger les agents.', variant: 'destructive' });
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [filterRole, filterCommune, filterStatus]);

  useEffect(() => {
    getCommuneList()
      .then((data) => setCommunes(Array.isArray(data) ? data : data.results || []))
      .catch(() => {});
  }, []);

  const filteredUsers = useMemo(() => {
    if (!search) return users;
    const lowerSearch = search.toLowerCase();
    return users.filter(
      (u) =>
        u.full_name?.toLowerCase().includes(lowerSearch) ||
        u.email?.toLowerCase().includes(lowerSearch)
    );
  }, [users, search]);

  const validateForm = () => {
    const newErrors = {};
    if (!form.full_name.trim()) newErrors.full_name = 'Le nom est obligatoire';
    if (!form.email.trim()) newErrors.email = 'L\'email est obligatoire';
    if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) newErrors.email = 'Email invalide';
    if (!form.role) newErrors.role = 'Le rôle est obligatoire';
    if (!form.commune) newErrors.commune = 'La commune est obligatoire';
    if (!form.password || form.password.length < 6) newErrors.password = 'Mot de passe min. 6 caractères';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;
    setSaving(true);
    try {
      await createUser({
        ...form,
        commune: parseInt(form.commune),
      });
      toast({ title: 'Agent créé', description: `${form.full_name} a été créé avec succès.`, variant: 'success' });
      setDialogOpen(false);
      setForm(EMPTY_FORM);
      fetchUsers();
    } catch (error) {
      toast({
        title: 'Erreur',
        description: error.response?.data?.detail || error.response?.data?.email?.[0] || 'Impossible de créer l\'agent.',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-secondary">Agents</h1>
          <p className="text-sm text-slate-500 mt-1">
            Gestion des utilisateurs et agents
          </p>
        </div>
        <Button onClick={() => { setForm(EMPTY_FORM); setErrors({}); setDialogOpen(true); }} className="gap-2">
          <Plus className="h-4 w-4" />
          Nouvel agent
        </Button>
      </div>

      {/* Filtres */}
      <Card className="p-4 border-slate-100">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Rechercher par nom ou email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
            />
          </div>
          <Select value={filterRole} onValueChange={setFilterRole}>
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="Tous les rôles" />
            </SelectTrigger>
            <SelectContent>
              {ROLE_OPTIONS.map((opt) => (
                <SelectItem key={opt.value || 'all-role'} value={opt.value || 'all'}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={filterCommune} onValueChange={setFilterCommune}>
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
          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Tous statuts" />
            </SelectTrigger>
            <SelectContent>
              {STATUS_OPTIONS.map((opt) => (
                <SelectItem key={opt.value || 'all-status'} value={opt.value || 'all'}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </Card>

      {/* Table */}
      <Card className="table-container">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/50">
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Nom</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Email</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Rôle</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Commune</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Statut</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Dernière connexion</th>
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
              ) : filteredUsers.length > 0 ? (
                filteredUsers.map((user) => {
                  const roleBadge = ROLE_BADGES[user.role] || ROLE_BADGES.reception_agent;
                  return (
                    <tr key={user.id} className="border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                            <span className="text-xs font-semibold text-primary">
                              {user.full_name?.charAt(0) || '?'}
                            </span>
                          </div>
                          <span className="text-sm font-medium text-secondary">{user.full_name}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-600">{user.email}</td>
                      <td className="px-4 py-3">
                        <Badge className={`${roleBadge.className} text-xs`}>
                          {roleBadge.label}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-600">{user.commune?.name || '—'}</td>
                      <td className="px-4 py-3">
                        <Badge className={user.is_active ? 'bg-success text-white border-success text-xs' : 'bg-slate-100 text-slate-500 border-slate-200 text-xs'}>
                          {user.is_active ? 'Actif' : 'Inactif'}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-500">{formatDate(user.last_login)}</td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={6} className="px-4 py-12 text-center text-slate-400">
                    Aucun agent trouvé
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Dialog Créer */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Nouvel agent</DialogTitle>
            <DialogDescription>Créer un nouveau compte utilisateur</DialogDescription>
          </DialogHeader>

          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2 space-y-2">
              <Label>Nom complet *</Label>
              <Input
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                placeholder="Ex: Awa Sall"
              />
              {errors.full_name && <p className="text-xs text-danger">{errors.full_name}</p>}
            </div>
            <div className="space-y-2">
              <Label>Email *</Label>
              <Input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="Ex: a.sall@tc.sn"
              />
              {errors.email && <p className="text-xs text-danger">{errors.email}</p>}
            </div>
            <div className="space-y-2">
              <Label>Téléphone</Label>
              <Input
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                placeholder="Ex: 771234567"
              />
            </div>
            <div className="space-y-2">
              <Label>Rôle *</Label>
              <Select value={form.role} onValueChange={(val) => setForm({ ...form, role: val })}>
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner un rôle" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="reception_agent">Agent de Réception</SelectItem>
                  <SelectItem value="verification_agent">Agent de Vérification</SelectItem>
                  <SelectItem value="civil_admin">Admin Civil</SelectItem>
                </SelectContent>
              </Select>
              {errors.role && <p className="text-xs text-danger">{errors.role}</p>}
            </div>
            <div className="space-y-2">
              <Label>Commune *</Label>
              <Select value={form.commune} onValueChange={(val) => setForm({ ...form, commune: val })}>
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner" />
                </SelectTrigger>
                <SelectContent>
                  {communes.map((c) => (
                    <SelectItem key={c.id} value={String(c.id)}>
                      {c.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.commune && <p className="text-xs text-danger">{errors.commune}</p>}
            </div>
            <div className="col-span-2 space-y-2">
              <Label>Mot de passe *</Label>
              <Input
                type="password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                placeholder="Minimum 6 caractères"
              />
              {errors.password && <p className="text-xs text-danger">{errors.password}</p>}
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Annuler
            </Button>
            <Button onClick={handleSubmit} disabled={saving}>
              {saving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Créer l'agent
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
