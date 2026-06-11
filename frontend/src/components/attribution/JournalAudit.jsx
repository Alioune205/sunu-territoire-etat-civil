import React, { useEffect, useState } from 'react';
import { attributionApi } from '../../services/attributionApi';

const JournalAudit = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await attributionApi.getHistory();
        // Assuming response.data contains the logs array
        setLogs(response.data.slice(0, 10) || []);
      } catch (error) {
        console.error('Erreur chargement journal', error);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  return (
    <div className="bg-[#1E293B] border border-slate-700/50 rounded-3xl p-6 h-full flex flex-col">
      <h3 className="text-white font-bold text-lg mb-6 flex items-center gap-2">
        <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Audit Trail Temps Réel
      </h3>

      <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
        {loading ? (
          <div className="text-slate-400 text-sm animate-pulse">Chargement des logs sécurisés...</div>
        ) : logs.length === 0 ? (
          <div className="text-slate-500 text-sm text-center italic py-4">Aucune trace d'attribution récente.</div>
        ) : (
          logs.map((log, idx) => (
            <div key={idx} className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/30 flex gap-3 text-sm">
              <div className="text-xs text-slate-500 font-mono whitespace-nowrap pt-0.5">
                {new Date(log.timestamp || Date.now()).toLocaleTimeString()}
              </div>
              <div>
                <span className="text-indigo-300 font-bold">{log.dossier_reference || 'Dossier'}</span>
                <span className="text-slate-300"> → assigné à </span>
                <span className="text-emerald-400 font-medium">{log.agent_name || 'Agent ID'}</span>
                <div className="text-xs text-slate-500 mt-1">{log.action || 'attribution'} - SLA : {log.respect_sla ? 'Respecté' : 'Hors Délai'}</div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default JournalAudit;
