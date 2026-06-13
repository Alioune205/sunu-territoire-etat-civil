import React from 'react';

const ScoreBar = ({ score }) => {
  // Gradient dynamique et moderne basé sur la performance
  const getGradient = (s) => {
    if (s >= 80) return 'from-emerald-400 to-emerald-600 shadow-[0_0_10px_rgba(52,211,153,0.5)]';
    if (s >= 50) return 'from-amber-400 to-amber-600 shadow-[0_0_10px_rgba(251,191,36,0.5)]';
    return 'from-rose-500 to-rose-700 shadow-[0_0_10px_rgba(244,63,94,0.5)]';
  };

  return (
    <div className="flex items-center space-x-3">
      <div className="flex-1 w-full bg-gray-100/50 dark:bg-gray-800 rounded-full h-3 overflow-hidden backdrop-blur-sm border border-gray-200/50 dark:border-gray-700">
        <div 
          className={`h-full rounded-full bg-gradient-to-r transition-all duration-1000 ease-out ${getGradient(score)}`} 
          style={{ width: `${score}%` }}
        />
      </div>
      <span className="text-sm font-bold text-gray-700 dark:text-gray-300 w-8">{score}%</span>
    </div>
  );
};

export default ScoreBar;
