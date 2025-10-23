import React from 'react';
import { useQuery } from 'react-query';
import { 
  CpuChipIcon, 
  QueueListIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';
import { api } from '../services/api';

export const Dashboard: React.FC = () => {
  const { data: systemStatus } = useQuery('system-status', api.getSystemStatus);
  const { data: agentsStatus } = useQuery('agents-status', api.getAgentsStatus);
  const { data: workflowsStatus } = useQuery('workflows-status', api.getWorkflowsStatus);

  const stats = [
    {
      name: 'Active Agents',
      value: agentsStatus?.agents?.filter((agent: any) => agent.status === 'active').length || 0,
      icon: CpuChipIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      name: 'Running Workflows',
      value: workflowsStatus?.workflows?.filter((wf: any) => wf.status === 'running').length || 0,
      icon: QueueListIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      name: 'Completed Tasks',
      value: workflowsStatus?.workflows?.reduce((acc: number, wf: any) => acc + (wf.tasks_completed || 0), 0) || 0,
      icon: CheckCircleIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      name: 'System Health',
      value: systemStatus?.system_status === 'operational' ? 'Healthy' : 'Issues',
      icon: ExclamationTriangleIcon,
      color: systemStatus?.system_status === 'operational' ? 'text-green-600' : 'text-red-600',
      bgColor: systemStatus?.system_status === 'operational' ? 'bg-green-100' : 'bg-red-100',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your FlowAgent multi-agent system
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center">
              <div className={`flex-shrink-0 rounded-md p-3 ${stat.bgColor}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">{stat.name}</p>
                <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Agents Status */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Agent Status</h3>
          <div className="space-y-3">
            {agentsStatus?.agents?.map((agent: any) => (
              <div key={agent.agent_id} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className={`h-2 w-2 rounded-full mr-3 ${
                    agent.status === 'active' ? 'bg-green-400' : 'bg-gray-400'
                  }`} />
                  <span className="text-sm font-medium text-gray-900 capitalize">
                    {agent.agent_id} Agent
                  </span>
                </div>
                <span className={`status-badge ${
                  agent.status === 'active' ? 'status-active' : 'status-inactive'
                }`}>
                  {agent.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Workflows Status */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Workflows</h3>
          <div className="space-y-3">
            {workflowsStatus?.workflows?.slice(0, 5).map((workflow: any) => (
              <div key={workflow.workflow_id} className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">{workflow.workflow_id}</p>
                  <p className="text-xs text-gray-500">
                    {workflow.tasks_completed}/{workflow.tasks_total} tasks
                  </p>
                </div>
                <div className="text-right">
                  <span className={`status-badge ${
                    workflow.status === 'running' ? 'status-active' : 
                    workflow.status === 'completed' ? 'status-active' : 'status-warning'
                  }`}>
                    {workflow.status}
                  </span>
                  <p className="text-xs text-gray-500 mt-1">
                    {workflow.progress}% complete
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* System Metrics */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">System Metrics</h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">
              {systemStatus?.cpu_usage || 0}%
            </p>
            <p className="text-sm text-gray-500">CPU Usage</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">
              {systemStatus?.memory_usage || 0}%
            </p>
            <p className="text-sm text-gray-500">Memory Usage</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-purple-600">
              {systemStatus?.uptime || '0h'}
            </p>
            <p className="text-sm text-gray-500">Uptime</p>
          </div>
        </div>
      </div>
    </div>
  );
};
