import React from 'react';
import BadgePriorite from './BadgePriorite';
import ScoreBar from './ScoreBar';

const CarteAttribution = ({ attribution }) => {
  if (!attribution) return null;

  return (
    <div className="bg-[#1E293B] border border-slate-700/50 rounded-2xl p-5 hover:border-indigo-500/30 transition-all group">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h4 className="text-white font-bold text-lg">{attribution.dossier_reference || 'Dossier INCONNU'}</h4>
          <p className="text-slate-400 text-sm flex items-center gap-2 mt-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            Agent: {attribution.agent_name || 'Non assigné'}
          </p>
        </div>
        <BadgePriorite niveau={attribution.niveau_priorite || 1} />
      </div>

      <div className="space-y-4">
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-400">Score d'Adéquation IA</span>
            <span className="text-indigo-400 font-bold">{attribution.score_adequation}%</span>
          </div>
          <ScoreBar score={attribution.score_adequation} color="indigo" />
        </div>

        <div className="bg-[#0F172A] rounded-xl p-3 border border-white/5 text-xs text-slate-300">
          <span className="font-semibold text-slate-100 block mb-1">Raison de l'attribution :</span>
          {attribution.justification_ia || "Attribution standard selon le SLA et la charge de l'agent."}
        </div>
      </div>
    </div>
  );
};

export default CarteAttribution;
