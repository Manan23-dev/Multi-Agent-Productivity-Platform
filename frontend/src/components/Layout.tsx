import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  CpuChipIcon, 
  QueueListIcon, 
  CheckCircleIcon, 
  ChartBarIcon, 
  CogIcon 
} from '@heroicons/react/24/outline';

interface LayoutProps {
  children: React.ReactNode;
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Agents', href: '/agents', icon: CpuChipIcon },
  { name: 'Workflows', href: '/workflows', icon: QueueListIcon },
  { name: 'Tasks', href: '/tasks', icon: CheckCircleIcon },
  { name: 'Monitoring', href: '/monitoring', icon: ChartBarIcon },
  { name: 'Settings', href: '/settings', icon: CogIcon },
];

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center justify-center border-b border-gray-200">
            <h1 className="text-xl font-bold text-gray-900">FlowAgent</h1>
          </div>
          
          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-2 py-4">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors duration-200 ${
                    isActive
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <item.icon
                    className={`mr-3 h-5 w-5 flex-shrink-0 ${
                      isActive ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                    }`}
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>
          
          {/* Status */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex items-center">
              <div className="h-2 w-2 bg-green-400 rounded-full mr-2"></div>
              <span className="text-sm text-gray-600">System Online</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <main className="py-6">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
