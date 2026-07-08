import axios from 'axios';

const api = axios.create();

// Her isteğe token ekle
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('dms_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 401 gelirse login'e yönlendir
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('dms_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
