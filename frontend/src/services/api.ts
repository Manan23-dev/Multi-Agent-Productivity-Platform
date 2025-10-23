import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
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
    return Promise.reject(error);
  }
);

export const api = {
  // System Status
  getSystemStatus: () => apiClient.get('/api/status'),
  getHealthCheck: () => apiClient.get('/api/health'),
  
  // Agents
  getAgentsStatus: () => apiClient.get('/api/agents/status'),
  startAgent: (agentId: string) => apiClient.post(`/api/agents/${agentId}/start`),
  stopAgent: (agentId: string) => apiClient.post(`/api/agents/${agentId}/stop`),
  getAgentStatus: (agentId: string) => apiClient.get(`/api/agents/${agentId}/status`),
  
  // Workflows
  getWorkflows: () => apiClient.get('/api/workflows'),
  getWorkflow: (workflowId: string) => apiClient.get(`/api/workflows/${workflowId}`),
  createWorkflow: (workflowData: any) => apiClient.post('/api/workflows', workflowData),
  updateWorkflow: (workflowId: string, workflowData: any) => 
    apiClient.put(`/api/workflows/${workflowId}`, workflowData),
  deleteWorkflow: (workflowId: string) => apiClient.delete(`/api/workflows/${workflowId}`),
  startWorkflow: (workflowId: string) => apiClient.post(`/api/workflows/${workflowId}/start`),
  stopWorkflow: (workflowId: string) => apiClient.post(`/api/workflows/${workflowId}/stop`),
  getWorkflowStatus: (workflowId: string) => apiClient.get(`/api/workflows/${workflowId}/status`),
  
  // Tasks
  getTasks: () => apiClient.get('/api/tasks'),
  getTask: (taskId: string) => apiClient.get(`/api/tasks/${taskId}`),
  createTask: (taskData: any) => apiClient.post('/api/tasks', taskData),
  updateTask: (taskId: string, taskData: any) => apiClient.put(`/api/tasks/${taskId}`, taskData),
  deleteTask: (taskId: string) => apiClient.delete(`/api/tasks/${taskId}`),
  executeTask: (taskId: string) => apiClient.post(`/api/tasks/${taskId}/execute`),
  getTaskStatus: (taskId: string) => apiClient.get(`/api/tasks/${taskId}/status`),
  retryTask: (taskId: string) => apiClient.post(`/api/tasks/${taskId}/retry`),
  
  // Monitoring
  getMetrics: () => apiClient.get('/api/metrics'),
  getExecutionLogs: (limit?: number) => 
    apiClient.get(`/api/logs${limit ? `?limit=${limit}` : ''}`),
  getSystemMetrics: () => apiClient.get('/api/metrics/system'),
  getAlerts: () => apiClient.get('/api/alerts'),
  
  // Workflows Status
  getWorkflowsStatus: () => apiClient.get('/api/workflows/status'),
};
