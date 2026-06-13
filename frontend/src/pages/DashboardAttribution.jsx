import React from 'react';
import { useAttributionStats } from '../hooks/useAttributionStats';
import { useWebSocket } from '../hooks/useWebSocket';
import StatsGlobales from '../components/attribution/StatsGlobales';
import TableauAgents from '../components/attribution/TableauAgents';
import JustificationIA from '../components/attribution/JustificationIA';
import CentreSupervision from '../components/attribution/CentreSupervision';

const DashboardAttribution = () => {
  const { agents, loading, error, refetch } = useAttributionStats();
  const { messages } = useWebSocket('ws://localhost:8000/ws/attributions/');

  if (loading && agents.length === 0) {
    return (
      <div className="flex justify-center items-center h-screen bg-slate-900">
        <div className="relative flex justify-center items-center">
          <div className="absolute animate-ping w-24 h-24 rounded-full bg-indigo-500 opacity-20"></div>
          <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin shadow-[0_0_15px_rgba(99,102,241,0.5)]"></div>
          <span className="absolute mt-32 text-indigo-400 font-bold tracking-widest text-sm uppercase">Initialisation du Moteur IA</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center p-6">
        <div className="bg-red-900/20 border border-red-500/50 p-8 rounded-3xl backdrop-blur-md max-w-lg text-center">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h2 className="text-red-400 text-xl font-bold mb-2">Défaillance Système</h2>
          <p className="text-red-300/80">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B1120] text-slate-200 p-8 relative overflow-hidden font-sans selection:bg-indigo-500/30">
      {/* Background Glow Effects (Mac OS style) */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-600/20 blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-purple-600/20 blur-[120px] pointer-events-none"></div>

      <div className="max-w-7xl mx-auto relative z-10">
        <header className="flex justify-between items-end mb-12 border-b border-white/5 pb-6">
          <div className="space-y-2">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-2">
              <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse"></span>
              <span>Teranga Civil v2.0</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-indigo-100 to-indigo-300 tracking-tight">
              Centre de Répartition IA
            </h1>
            <p className="text-slate-400 font-medium max-w-2xl">
              Supervision heuristique en temps réel. Le moteur de scoring optimise les charges selon 5 critères neuronaux.
            </p>
          </div>
          
          <button 
            onClick={refetch}
            className="group relative px-6 py-3 font-bold text-white rounded-xl overflow-hidden bg-indigo-600 hover:bg-indigo-500 transition-all shadow-[0_0_20px_rgba(79,70,229,0.3)] hover:shadow-[0_0_30px_rgba(79,70,229,0.5)] transform hover:-translate-y-0.5"
          >
            <div className="absolute inset-0 w-full h-full bg-gradient-to-br from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <span className="relative flex items-center gap-2">
              <svg className="w-4 h-4 group-hover:animate-spin-slow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Synchroniser
            </span>
          </button>
        </header>

        {/* Animations Toast pour les WebSockets */}
        <div className="fixed top-6 right-6 z-50 flex flex-col gap-4">
          {messages.slice(-2).map((msg, idx) => (
            <div 
              key={idx} 
              className="animate-slide-left bg-[#0B1120]/95 backdrop-blur-2xl border border-indigo-500/40 p-5 rounded-2xl shadow-[0_0_40px_rgba(79,70,229,0.2)] min-w-[340px] transform transition-all duration-500"
            >
              <div className="flex items-start gap-4">
                <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-2.5 rounded-xl text-white shadow-lg shadow-indigo-500/30">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h4 className="text-white font-black tracking-wide text-sm flex items-center gap-2">
                    ROUTAGE INTELLIGENT
                    <span className="px-2 py-0.5 rounded text-[10px] bg-red-500/20 text-red-400 border border-red-500/30">{msg.priorite || 'URGENT'}</span>
                  </h4>
                  <p className="text-slate-400 text-xs mt-1">Dossier <span className="text-indigo-300 font-mono font-bold">{msg.dossier_reference}</span> attribué</p>
                </div>
              </div>
              
              {/* Le "God Move" visuel : L'explication des calculs de l'IA */}
              <JustificationIA msg={msg} />
            </div>
          ))}
        </div>

        <section className="mb-12">
          <StatsGlobales agents={agents} />
        </section>

        <section className="relative">
          <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-3xl blur opacity-20 group-hover:opacity-30 transition duration-1000"></div>
          <div className="relative bg-[#0F172A] rounded-3xl p-1 shadow-2xl border border-white/5">
            <div className="p-6 border-b border-white/5 flex justify-between items-center">
              <h2 className="text-xl font-bold text-white flex items-center gap-3">
                <span className="w-2 h-8 rounded bg-gradient-to-b from-indigo-400 to-purple-600 inline-block"></span>
                État des Troupes Opérationnelles
              </h2>
            </div>
            <div className="p-2">
              <TableauAgents agents={agents} />
            </div>
          </div>
        </section>

        {/* Integration of the new components from Module 8 */}
        <section className="mt-12">
           <CentreSupervision agents={agents} />
        </section>
      </div>

      {/* Styles globaux pour les animations personnalisées */}
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes slide-left {
          0% { transform: translateX(100%); opacity: 0; }
          100% { transform: translateX(0); opacity: 1; }
        }
        .animate-slide-left {
          animation: slide-left 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        .animate-spin-slow {
          animation: spin 3s linear infinite;
        }
      `}} />
    </div>
  );
};

export default DashboardAttribution;
