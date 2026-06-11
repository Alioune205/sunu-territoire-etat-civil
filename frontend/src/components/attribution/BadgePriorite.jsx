import React from 'react';

const BadgePriorite = ({ niveau }) => {
  const colors = {
    'Critique': 'bg-red-100 text-red-800',
    'Urgente': 'bg-orange-100 text-orange-800',
    'Haute': 'bg-yellow-100 text-yellow-800',
    'Normale': 'bg-green-100 text-green-800',
    'Basse': 'bg-gray-100 text-gray-800',
  };

  const badgeColor = colors[niveau] || colors['Normale'];

  return (
    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${badgeColor}`}>
      {niveau}
    </span>
  );
};

export default BadgePriorite;
