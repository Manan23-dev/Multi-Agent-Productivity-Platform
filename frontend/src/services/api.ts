import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const api = {
  // System Status
  getSystemStatus: () => apiClient.get('/monitoring/status'),
  getHealthCheck: () => apiClient.get('/monitoring/health'),
  
  // Agents
  getAgentsStatus: () => apiClient.get('/monitoring/agents/status'),
  startAgent: (agentId: string) => apiClient.post(`/agents/${agentId}/start`),
  stopAgent: (agentId: string) => apiClient.post(`/agents/${agentId}/stop`),
  getAgentStatus: (agentId: string) => apiClient.get(`/agents/${agentId}/status`),
  
  // Workflows
  getWorkflows: () => apiClient.get('/workflows'),
  getWorkflow: (workflowId: string) => apiClient.get(`/workflows/${workflowId}`),
  createWorkflow: (workflowData: any) => apiClient.post('/workflows', workflowData),
  updateWorkflow: (workflowId: string, workflowData: any) => 
    apiClient.put(`/workflows/${workflowId}`, workflowData),
  deleteWorkflow: (workflowId: string) => apiClient.delete(`/workflows/${workflowId}`),
  startWorkflow: (workflowId: string) => apiClient.post(`/workflows/${workflowId}/start`),
  stopWorkflow: (workflowId: string) => apiClient.post(`/workflows/${workflowId}/stop`),
  getWorkflowStatus: (workflowId: string) => apiClient.get(`/workflows/${workflowId}/status`),
  
  // Tasks
  getTasks: () => apiClient.get('/tasks'),
  getTask: (taskId: string) => apiClient.get(`/tasks/${taskId}`),
  createTask: (taskData: any) => apiClient.post('/tasks', taskData),
  updateTask: (taskId: string, taskData: any) => apiClient.put(`/tasks/${taskId}`, taskData),
  deleteTask: (taskId: string) => apiClient.delete(`/tasks/${taskId}`),
  executeTask: (taskId: string) => apiClient.post(`/tasks/${taskId}/execute`),
  getTaskStatus: (taskId: string) => apiClient.get(`/tasks/${taskId}/status`),
  retryTask: (taskId: string) => apiClient.post(`/tasks/${taskId}/retry`),
  
  // Monitoring
  getMetrics: () => apiClient.get('/monitoring/metrics'),
  getExecutionLogs: (limit?: number) => 
    apiClient.get(`/monitoring/logs${limit ? `?limit=${limit}` : ''}`),
  getSystemMetrics: () => apiClient.get('/monitoring/metrics/system'),
  getAlerts: () => apiClient.get('/monitoring/alerts'),
  
  // Workflows Status
  getWorkflowsStatus: () => apiClient.get('/monitoring/workflows/status'),
};
