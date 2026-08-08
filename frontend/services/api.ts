/**
 * Axios API service configuration for PneumoVision AI frontend.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import Cookies from 'js-cookie';
import toast from 'react-hot-toast';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create Axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor - adds auth token
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handles errors and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;

    // Handle 401 Unauthorized - try refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = Cookies.get('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token: newRefreshToken } = response.data;
          Cookies.set('access_token', access_token, { expires: 7 });
          Cookies.set('refresh_token', newRefreshToken, { expires: 7 });

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed - redirect to login
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

// Handle other errors
    const detail = (error.response?.data as any)?.detail;
    let message =
      error.message || 'An unexpected error occurred';

    // FastAPI returns `detail` as either a string or an array of
    // validation error objects (e.g. 422). react-hot-toast requires a
    // string, so coerce the array into a readable message.
    if (typeof detail === 'string') {
      message = detail;
    } else if (Array.isArray(detail)) {
      message = detail
        .map((d: any) => d?.msg)
        .filter(Boolean)
        .join(', ') || message;
    }

    if (error.response?.status !== 401) {
      toast.error(message);
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data: { name: string; email: string; password: string; role?: string }) =>
    api.post('/auth/register', data),
  
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  
  refresh: (refreshToken: string) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }),
  
  getProfile: () => api.get('/auth/profile'),
  
  changePassword: (data: { current_password: string; new_password: string }) =>
    api.put('/auth/password', data),
  
  logout: () => api.post('/auth/logout'),
};

// User API
export const userAPI = {
  getFullProfile: () => api.get('/users/profile'),
  
  updateProfile: (data: any) => api.put('/users/profile', data),
  
  updateName: (name: string) => api.put('/users/name', { name }),
  
  deleteAccount: () => api.delete('/users/account'),
};

// Prediction API
export const predictionAPI = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/predict/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  analyze: (imagePath: string, patientId?: string, doctorNotes?: string) =>
    api.post('/predict/analyze', {
      image_path: imagePath,
      patient_id: patientId,
      doctor_notes: doctorNotes,
    }),
  
  getHistory: (page: number = 1, pageSize: number = 10) =>
    api.get(`/predict/history?page=${page}&page_size=${pageSize}`),
  
  getStats: () => api.get('/predict/stats'),
  
  getPrediction: (id: string) => api.get(`/predict/${id}`),
  
  deletePrediction: (id: string) => api.delete(`/predict/${id}`),
};

// Report API
export const reportAPI = {
  download: (id: string) => api.get(`/reports/${id}`, { responseType: 'blob' }),
  view: (id: string) => api.get(`/reports/${id}/view`, { responseType: 'blob' }),
};

// Admin API
export const adminAPI = {
  getStats: () => api.get('/admin/stats'),
  getUsers: (page: number = 1, pageSize: number = 20, role?: string, search?: string) => {
    let url = `/admin/users?page=${page}&page_size=${pageSize}`;
    if (role) url += `&role=${role}`;
    if (search) url += `&search=${search}`;
    return api.get(url);
  },
  toggleUserStatus: (userId: string) => api.put(`/admin/users/${userId}/status`),
  deleteUser: (userId: string) => api.delete(`/admin/users/${userId}`),
  getRecentPredictions: (limit: number = 10) =>
    api.get(`/admin/predictions/recent?limit=${limit}`),
  getAuditLogs: (limit: number = 50, action?: string) => {
    let url = `/admin/audit-logs?limit=${limit}`;
    if (action) url += `&action=${action}`;
    return api.get(url);
  },
  getHealth: () => api.get('/admin/health'),
  getTotalUsers: () => api.get('/admin/users/total'),
};

export default api;

