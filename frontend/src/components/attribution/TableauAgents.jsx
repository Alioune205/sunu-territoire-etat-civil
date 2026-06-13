import React from 'react';
import BadgePriorite from './BadgePriorite';
import ScoreBar from './ScoreBar';

const TableauAgents = ({ agents }) => {
  return (
    <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl shadow-2xl overflow-hidden sm:rounded-2xl border border-gray-100 dark:border-gray-800 transition-all duration-300">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-800">
          <thead className="bg-gray-50/50 dark:bg-gray-800/50 backdrop-blur-sm">
            <tr>
              <th className="px-8 py-5 text-left text-xs font-black text-gray-500 dark:text-gray-400 uppercase tracking-widest">Agent Opérationnel</th>
              <th className="px-8 py-5 text-left text-xs font-black text-gray-500 dark:text-gray-400 uppercase tracking-widest">Statut Réseau</th>
              <th className="px-8 py-5 text-left text-xs font-black text-gray-500 dark:text-gray-400 uppercase tracking-widest">Bande Passante (Charge)</th>
              <th className="px-8 py-5 text-left text-xs font-black text-gray-500 dark:text-gray-400 uppercase tracking-widest">Score IA</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50 dark:divide-gray-800/50">
            {agents.map((agent) => (
              <tr 
                key={agent.agent_id} 
                className="group hover:bg-indigo-50/30 dark:hover:bg-indigo-900/20 transition-colors duration-200"
              >
                <td className="px-8 py-6 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold shadow-lg transform group-hover:scale-110 transition-transform duration-200">
                      {agent.nom_complet.charAt(0)}
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-bold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                        {agent.nom_complet}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">ID: {agent.agent_id.substring(0, 8)}</div>
                    </div>
                  </div>
                </td>
                <td className="px-8 py-6 whitespace-nowrap">
                  <div className="flex items-center space-x-2">
                    <span className={`h-2.5 w-2.5 rounded-full ${agent.est_disponible ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></span>
                    <BadgePriorite niveau={agent.est_disponible ? 'Normale' : 'Critique'} />
                  </div>
                </td>
                <td className="px-8 py-6 whitespace-nowrap">
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl font-black text-gray-700 dark:text-gray-200">{agent.charge_actuelle}</span>
                    <span className="text-sm text-gray-400 font-medium">/ {agent.capacite_maximale}</span>
                  </div>
                </td>
                <td className="px-8 py-6 whitespace-nowrap w-1/4">
                  <ScoreBar score={agent.score_performance} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TableauAgents;
