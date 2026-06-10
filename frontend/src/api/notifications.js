// src/api/notifications.js
import axiosClient from './axiosClient';

export const getNotifications = async () => {
  const response = await axiosClient.get('/api/notifications/');
  return response.data;
};

export const markNotificationRead = async (id) => {
  const response = await axiosClient.post(`/api/notifications/${id}/mark-read/`);
  return response.data;
};

export const markAllNotificationsRead = async () => {
  const response = await axiosClient.post('/api/notifications/mark-all-read/');
  return response.data;
};
