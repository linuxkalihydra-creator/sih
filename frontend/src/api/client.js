/**
 * API client for the Bitcoin Investigation Platform backend.
 * Provides centralized HTTP communication with error handling.
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

// The existing analysis endpoint is synchronous, so it must not be cut off while
// the backend is still processing a legitimate large upload. Axios treats 0 as no timeout.
const ANALYSIS_TIMEOUT_MS = 0;
const UPLOAD_TIMEOUT_MS = 300000;

export function apiErrorMessage(error, operation = 'Request') {
  if (error?.code === 'ECONNABORTED') return `${operation} timed out. Analysis may still be running; check the dataset status and retry if needed.`;
  if (!error?.response) return 'Backend unavailable. Check that the API is running and try again.';

  const status = error.response.status;
  const detail = error.response.data?.detail;
  if (status === 400) return typeof detail === 'string' ? detail : 'Dataset format invalid.';
  if (status === 404) return 'Dataset not found.';
  if (status === 409) return 'Dataset analysis is not complete yet.';
  if (status === 413) return 'Dataset is too large to upload.';
  if (status === 422) return 'The request data is invalid.';
  if (status === 502 || status === 503) return 'Neo4j or the backend is unavailable.';
  if (status >= 500) return 'Unknown server error. Please try again.';
  return `${operation} failed.`;
}

export const api = {
  health: async () => {
    return client.get('/health');
  },

  datasets: async (config = {}) => client.get('/datasets', config),
  stats: async (datasetId, config = {}) => {
    return client.get('/stats', { ...config, params: { ...config.params, ...(datasetId ? { dataset_id: datasetId } : {}) } });
  },

  analyze: async (path, outputDir = null, contamination = 0.05, randomState = 42, datasetId = null) => {
    const payload = {
      contamination,
      random_state: randomState,
      ...(datasetId ? { dataset_id: datasetId } : {}),
      ...(path ? { path } : {}),
      ...(outputDir ? { output_dir: outputDir } : {}),
    };
    return client.post('/analyze', payload, { timeout: ANALYSIS_TIMEOUT_MS });
  },

  uploadDataset: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return client.post('/datasets/upload', formData, { timeout: UPLOAD_TIMEOUT_MS });
  },

  alerts: async (datasetId, config = {}) => {
    return client.get('/alerts', { ...config, params: { ...config.params, ...(datasetId ? { dataset_id: datasetId } : {}) } });
  },

  alertForWallet: async (walletId, datasetId, config = {}) => {
    return client.get(`/alerts/${walletId}`, { ...config, params: { ...config.params, dataset_id: datasetId } });
  },

  entity: async (walletId, datasetId, config = {}) => {
    return client.get(`/entities/${walletId}`, { ...config, params: { ...config.params, dataset_id: datasetId } });
  },

  entityEvidence: async (walletId, datasetId, config = {}) => {
    return client.get(`/entities/${walletId}/evidence`, { ...config, params: { ...config.params, dataset_id: datasetId } });
  },

  entityGraph: async (walletId, datasetId, depth = 2, config = {}) => {
    return client.get(`/entities/${walletId}/graph`, { ...config, params: { ...config.params, dataset_id: datasetId, depth } });
  },

  entityTransactions: async (walletId, datasetId, config = {}) => {
    return client.get(`/entities/${walletId}/transactions`, { ...config, params: { ...config.params, dataset_id: datasetId } });
  },

  clusters: async (datasetId, config = {}) => {
    return client.get('/clusters', { ...config, params: { ...config.params, ...(datasetId ? { dataset_id: datasetId } : {}) } });
  },

  clusterGraph: async (datasetId, clusterId, config = {}) => client.get(`/datasets/${datasetId}/clusters/${clusterId}/graph`, config),

  ingest: async (path) => {
    return client.post('/ingest', { path });
  },
};

export default api;
