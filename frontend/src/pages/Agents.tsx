import React from 'react';
import { useQuery } from 'react-query';
import { PlayIcon, StopIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { api } from '../services/api';

export const Agents: React.FC = () => {
  const { data: agentsStatus, refetch } = useQuery('agents-status', api.getAgentsStatus);

  const handleStartAgent = async (agentId: string) => {
    try {
      await api.startAgent(agentId);
      refetch();
    } catch (error) {
      console.error('Failed to start agent:', error);
    }
  };

  const handleStopAgent = async (agentId: string) => {
    try {
      await api.stopAgent(agentId);
      refetch();
    } catch (error) {
      console.error('Failed to stop agent:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Agents</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your multi-agent system
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="btn-secondary flex items-center"
        >
          <ArrowPathIcon className="h-4 w-4 mr-2" />
          Refresh
        </button>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {agentsStatus?.agents?.map((agent: any) => (
          <div key={agent.agent_id} className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <div className={`h-3 w-3 rounded-full mr-3 ${
                  agent.status === 'active' ? 'bg-green-400' : 'bg-gray-400'
                }`} />
                <h3 className="text-lg font-medium text-gray-900 capitalize">
                  {agent.agent_id} Agent
                </h3>
              </div>
              <span className={`status-badge ${
                agent.status === 'active' ? 'status-active' : 'status-inactive'
              }`}>
                {agent.status}
              </span>
            </div>

            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Uptime:</span>
                <span className="text-gray-900">{agent.uptime}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Last Heartbeat:</span>
                <span className="text-gray-900">
                  {new Date(agent.last_heartbeat).toLocaleTimeString()}
                </span>
              </div>
            </div>

            <div className="flex space-x-2">
              {agent.status === 'active' ? (
                <button
                  onClick={() => handleStopAgent(agent.agent_id)}
                  className="btn-secondary flex items-center flex-1"
                >
                  <StopIcon className="h-4 w-4 mr-2" />
                  Stop
                </button>
              ) : (
                <button
                  onClick={() => handleStartAgent(agent.agent_id)}
                  className="btn-primary flex items-center flex-1"
                >
                  <PlayIcon className="h-4 w-4 mr-2" />
                  Start
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Agent Details */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Agent Details</h3>
        <div className="space-y-4">
          {agentsStatus?.agents?.map((agent: any) => (
            <div key={agent.agent_id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900 capitalize">
                  {agent.agent_id} Agent
                </h4>
                <span className={`status-badge ${
                  agent.status === 'active' ? 'status-active' : 'status-inactive'
                }`}>
                  {agent.status}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Uptime:</span>
                  <span className="ml-2 text-gray-900">{agent.uptime}</span>
                </div>
                <div>
                  <span className="text-gray-500">Last Heartbeat:</span>
                  <span className="ml-2 text-gray-900">
                    {new Date(agent.last_heartbeat).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
