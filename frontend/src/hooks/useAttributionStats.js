import { useState, useEffect } from 'react';
import { attributionApi } from '../services/attributionApi';

export const useAttributionStats = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const data = await attributionApi.getMonitoringAgents();
      setAgents(data.agents_metrics);
      setError(null);
    } catch (err) {
      setError(err.message || 'Erreur lors de la récupération des données');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    // Rafraîchissement toutes les 30s
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  return { agents, loading, error, refetch: fetchStats };
};
