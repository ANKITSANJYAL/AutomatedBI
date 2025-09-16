import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: (process.env.REACT_APP_API_URL || 'http://localhost:5001') + '/api',
  timeout: 120000, // Increased to 2 minutes for file processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth headers if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    const errorMessage = error.response?.data?.error || error.message || 'An unexpected error occurred';
    return Promise.reject(new Error(errorMessage));
  }
);

// Upload file
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response;
};

// Get upload status
export const getUploadStatus = async (datasetId) => {
  return await api.get(`/upload/status/${datasetId}`);
};

// Get processing progress
export const getProcessingProgress = async (datasetId) => {
  return await api.get(`/upload/progress/${datasetId}`);
};

// Get analysis results
export const getAnalysisResults = async (datasetId) => {
  return await api.get(`/analysis/${datasetId}`);
};

// Get dataset data
export const getDatasetData = async (datasetId, page = 1, perPage = 100) => {
  return await api.get(`/analysis/${datasetId}/data`, {
    params: { page, per_page: perPage }
  });
};

// Get data quality report
export const getDataQualityReport = async (datasetId) => {
  return await api.get(`/analysis/${datasetId}/quality`);
};

// Get business insights
export const getBusinessInsights = async (datasetId) => {
  return await api.get(`/analysis/${datasetId}/insights`);
};

// Get dashboard structure
export const getDashboardStructure = async (datasetId) => {
  return await api.get(`/dashboard/${datasetId}`);
};

// Get dashboard charts
export const getDashboardCharts = async (datasetId) => {
  return await api.get(`/dashboard/${datasetId}/charts`);
};

// Get chart data
export const getChartData = async (datasetId, chartConfig) => {
  return await api.post(`/dashboard/${datasetId}/chart-data`, chartConfig);
};

// Get dashboard KPIs
export const getDashboardKPIs = async (datasetId) => {
  return await api.get(`/dashboard/${datasetId}/kpis`);
};

// Get dashboard filters
export const getDashboardFilters = async (datasetId) => {
  return await api.get(`/dashboard/${datasetId}/filters`);
};

// Export analysis
export const exportAnalysis = async (datasetId, format = 'json', includeData = false) => {
  return await api.post(`/analysis/${datasetId}/export`, {
    format,
    include_data: includeData
  });
};

export default api;
