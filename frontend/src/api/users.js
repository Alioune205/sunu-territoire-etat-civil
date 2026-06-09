// src/api/users.js
import axiosClient from './axiosClient';

export const getUserList = async (params = {}) => {
  const response = await axiosClient.get('/api/users/', { params });
  return response.data;
};

export const createUser = async (data) => {
  const response = await axiosClient.post('/api/users/', data);
  return response.data;
};
