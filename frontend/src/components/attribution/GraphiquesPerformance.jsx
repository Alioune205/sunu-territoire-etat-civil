import React from 'react';

const GraphiquesPerformance = ({ agents }) => {
  if (!agents || agents.length === 0) return null;

  // Mock data generation for the charts if no real historical data is passed
  const maxScore = Math.max(...agents.map(a => a.score_performance_global || 0), 100);

  return (
    <div className="bg-[#1E293B] border border-slate-700/50 rounded-3xl p-6 h-full">
      <h3 className="text-white font-bold text-lg mb-6 flex items-center gap-2">
        <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
        </svg>
        Performance Globale
      </h3>

      <div className="space-y-4">
        {agents.map((agent) => {
          const score = agent.score_performance_global || 0;
          const percentage = (score / maxScore) * 100;
          
          return (
            <div key={agent.id} className="relative">
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300 font-medium truncate w-32">{agent.user_name}</span>
                <span className="text-indigo-400 font-bold">{score} pts</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden border border-white/5">
                <div 
                  className="bg-gradient-to-r from-indigo-500 to-purple-500 h-2 rounded-full transition-all duration-1000 ease-out relative"
                  style={{ width: `${percentage}%` }}
                >
                  <div className="absolute top-0 right-0 bottom-0 w-10 bg-white/20 blur-sm"></div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-6 pt-4 border-t border-slate-700/50">
        <p className="text-xs text-slate-500 italic text-center">
          Basé sur la vélocité de résolution, le respect du SLA et l'assiduité de l'agent.
        </p>
      </div>
    </div>
  );
};

export default GraphiquesPerformance;
