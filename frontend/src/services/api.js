import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  return api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

export const queryRAG = async (question) => {
  return api.post('/query', { question });
};

export const getDocuments = async () => {
  return api.get('/documents');
};

export const getEvaluations = async () => {
  return api.get('/evaluations');
};

export const clearEvaluations = async () => {
  return api.post('/evaluations/clear');
};

export const getEvalDataset = async () => {
  return api.get('/eval-dataset');
};

export const healthCheck = async () => {
  return api.get('/health');
};
