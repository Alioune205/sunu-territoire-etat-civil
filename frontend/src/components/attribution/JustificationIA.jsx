import React from 'react';

const JustificationIA = ({ msg }) => {
  return (
    <div className="mt-3 p-3 rounded-xl bg-slate-900/50 border border-indigo-500/20 backdrop-blur-md">
      <div className="flex items-center gap-2 mb-2">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
        </span>
        <span className="text-xs font-mono text-indigo-400 uppercase tracking-widest">Analyse Heuristique IA</span>
      </div>
      
      <div className="space-y-2">
        <div className="flex justify-between items-center text-xs">
          <span className="text-slate-400">Match Compétence</span>
          <span className="text-emerald-400 font-bold">98%</span>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-1">
          <div className="bg-gradient-to-r from-emerald-500 to-emerald-300 h-1 rounded-full w-[98%]"></div>
        </div>

        <div className="flex justify-between items-center text-xs">
          <span className="text-slate-400">Disponibilité (Bande Passante)</span>
          <span className="text-blue-400 font-bold">85%</span>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-1">
          <div className="bg-gradient-to-r from-blue-500 to-blue-300 h-1 rounded-full w-[85%]"></div>
        </div>
      </div>
      
      <div className="mt-3 text-[10px] text-slate-500 font-mono leading-tight">
        &gt; DÉCISION: {msg.agent_nom || "Agent assigné"} sélectionné pour le dossier {msg.dossier_reference}. SLA garanti.
      </div>
    </div>
  );
};

export default JustificationIA;
