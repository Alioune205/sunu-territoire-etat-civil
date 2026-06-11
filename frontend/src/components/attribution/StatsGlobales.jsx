import React from 'react';

const StatsGlobales = ({ agents }) => {
  const totalAgents = agents.length;
  const agentsDispos = agents.filter(a => a.est_disponible).length;
  const chargeTotale = agents.reduce((acc, a) => acc + a.charge_actuelle, 0);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Carte 1 */}
      <div className="relative group rounded-3xl bg-gray-900/40 backdrop-blur-xl border border-white/10 p-8 overflow-hidden hover:border-indigo-500/50 transition-colors duration-300">
        <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/20 rounded-full blur-3xl transform group-hover:scale-150 transition-transform duration-700"></div>
        <div className="relative z-10">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/20 flex items-center justify-center mb-6 border border-indigo-500/30 text-indigo-400">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
          </div>
          <h3 className="text-slate-400 text-sm font-bold tracking-wider uppercase mb-1">Total Effectifs Connectés</h3>
          <p className="text-5xl font-black text-white">{totalAgents}</p>
        </div>
      </div>

      {/* Carte 2 */}
      <div className="relative group rounded-3xl bg-gray-900/40 backdrop-blur-xl border border-white/10 p-8 overflow-hidden hover:border-emerald-500/50 transition-colors duration-300">
        <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/20 rounded-full blur-3xl transform group-hover:scale-150 transition-transform duration-700"></div>
        <div className="relative z-10">
          <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 flex items-center justify-center mb-6 border border-emerald-500/30 text-emerald-400">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>
          <h3 className="text-slate-400 text-sm font-bold tracking-wider uppercase mb-1">Capacité Disponibilité</h3>
          <p className="text-5xl font-black text-white flex items-end gap-2">
            {agentsDispos} <span className="text-xl text-emerald-400 font-medium mb-1 border border-emerald-500/30 px-2 py-0.5 rounded-lg bg-emerald-500/10">Prêts</span>
          </p>
        </div>
      </div>

      {/* Carte 3 */}
      <div className="relative group rounded-3xl bg-gray-900/40 backdrop-blur-xl border border-white/10 p-8 overflow-hidden hover:border-rose-500/50 transition-colors duration-300">
        <div className="absolute top-0 right-0 w-32 h-32 bg-rose-500/20 rounded-full blur-3xl transform group-hover:scale-150 transition-transform duration-700"></div>
        <div className="relative z-10">
          <div className="w-12 h-12 rounded-2xl bg-rose-500/20 flex items-center justify-center mb-6 border border-rose-500/30 text-rose-400">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
          </div>
          <h3 className="text-slate-400 text-sm font-bold tracking-wider uppercase mb-1">Dossiers en Vol (Bande passante)</h3>
          <p className="text-5xl font-black text-white">{chargeTotale}</p>
        </div>
      </div>
    </div>
  );
};

export default StatsGlobales;
