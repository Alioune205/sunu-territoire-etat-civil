// src/components/StatusBadge.jsx
import { Badge } from '@/components/ui/badge';

const STATUS_CONFIG = {
  draft: {
    label: 'Brouillon',
    className: 'bg-[#94A3B8] text-white border-[#94A3B8]',
  },
  submitted: {
    label: 'Soumis',
    className: 'bg-[#F59E0B] text-white border-[#F59E0B]',
  },
  in_review: {
    label: 'En vérification',
    className: 'bg-[#1D4ED8] text-white border-[#1D4ED8]',
  },
  approved: {
    label: 'Approuvé',
    className: 'bg-[#10B981] text-white border-[#10B981]',
  },
  rejected: {
    label: 'Rejeté',
    className: 'bg-[#EF4444] text-white border-[#EF4444]',
  },
  completed: {
    label: 'Terminé',
    className: 'bg-[#0F172A] text-white border-[#0F172A]',
  },
};

export function StatusBadge({ status, className = '' }) {
  const config = STATUS_CONFIG[status] || {
    label: status,
    className: 'bg-slate-100 text-slate-700 border-slate-200',
  };

  return (
    <Badge className={`${config.className} ${className} text-xs font-medium px-2.5 py-1`}>
      {config.label}
    </Badge>
  );
}
