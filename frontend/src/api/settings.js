// src/api/settings.js
import axiosClient from './axiosClient';

export const getSystemSettings = async () => {
  const response = await axiosClient.get('/api/system/settings/');
  return response.data;
};

export const updateSystemSettings = async (settingsData) => {
  const response = await axiosClient.put('/api/system/settings/', settingsData);
  return response.data;
};
