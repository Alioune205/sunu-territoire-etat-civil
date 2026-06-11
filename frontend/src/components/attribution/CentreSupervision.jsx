import React from 'react';
import GraphiquesPerformance from './GraphiquesPerformance';
import JournalAudit from './JournalAudit';
import CarteAttribution from './CarteAttribution';

const CentreSupervision = ({ agents }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
      <div className="lg:col-span-1">
        <GraphiquesPerformance agents={agents} />
      </div>
      
      <div className="lg:col-span-1">
        <JournalAudit />
      </div>
      
      <div className="lg:col-span-1">
        <div className="bg-[#0F172A] border border-slate-700/50 rounded-3xl p-6 h-full flex flex-col">
          <h3 className="text-white font-bold text-lg mb-6 flex items-center gap-2">
            <svg className="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            Dossier en Focus
          </h3>
          <div className="flex-1 flex items-center justify-center">
            {/* Simulation of a currently assigned folder */}
            <CarteAttribution 
              attribution={{
                dossier_reference: 'NAISS-2026-X89',
                agent_name: agents.length > 0 ? agents[0].user_name : 'Agent Intelligent',
                niveau_priorite: 3,
                score_adequation: 94,
                justification_ia: 'Expertise historique sur les extraits de naissance de la commune.'
              }} 
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default CentreSupervision;
