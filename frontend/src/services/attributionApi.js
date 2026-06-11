import api from './api';

export const attributionApi = {
  getMonitoringAgents: async () => {
    const response = await api.get('/api/attributions/monitoring-agents/');
    return response.data;
  },

  forcerAttribution: async (dossierId) => {
    const response = await api.post(`/api/attributions/forcer-attribution/${dossierId}/`);
    return response.data;
  }
};
