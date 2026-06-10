// src/api/dossiers.js
import axiosClient from './axiosClient';

export const getDossiers = async (params = {}) => {
  const response = await axiosClient.get('/api/dossiers/', { params });
  return response.data; // { count, next, previous, results }
};

export const getDossier = async (id) => {
  const response = await axiosClient.get(`/api/dossiers/${id}/`);
  return response.data;
};

export const patchDossier = async (id, data) => {
  const response = await axiosClient.patch(`/api/dossiers/${id}/`, data);
  return response.data;
};

export const takeDossier = async (id) => {
  const response = await axiosClient.post(`/api/dossiers/${id}/take/`);
  return response.data;
};

export const getDossierComments = async (id) => {
  const response = await axiosClient.get(`/api/dossiers/${id}/comments/`);
  return response.data;
};

export const addDossierComment = async (id, text) => {
  const response = await axiosClient.post(`/api/dossiers/${id}/comments/`, { text });
  return response.data;
};

export const reviewDossier = async (id) => {
  const response = await axiosClient.post(`/api/dossiers/${id}/review/`);
  return response.data;
};

export const approveDossier = async (id) => {
  const response = await axiosClient.post(`/api/dossiers/${id}/approve/`);
  return response.data;
};

export const rejectDossier = async (id, rejectionReason) => {
  const response = await axiosClient.post(`/api/dossiers/${id}/reject/`, { rejection_reason: rejectionReason });
  return response.data;
};

export const submitDossier = async (id) => {
  const response = await axiosClient.post(`/api/dossiers/${id}/submit/`);
  return response.data;
};

export const completeDossier = async (id) => {
  const response = await axiosClient.post(`/api/dossiers/${id}/complete/`);
  return response.data;
};


