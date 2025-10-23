import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Agents } from './pages/Agents';
import { Workflows } from './pages/Workflows';
import { Tasks } from './pages/Tasks';
import { Monitoring } from './pages/Monitoring';
import { Settings } from './pages/Settings';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/agents" element={<Agents />} />
        <Route path="/workflows" element={<Workflows />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/monitoring" element={<Monitoring />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  );
}

export default App;
