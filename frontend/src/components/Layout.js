import React from 'react';
import { Link } from 'react-router-dom';
import { BarChart3, Database, Zap } from 'lucide-react';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-primary-600 rounded-lg">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">AutomatedBI</h1>
                <p className="text-xs text-gray-500">Intelligent Dashboard Generator</p>
              </div>
            </Link>

            {/* Navigation */}
            <nav className="hidden md:flex items-center space-x-8">
              <Link
                to="/"
                className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors"
              >
                <Database className="w-4 h-4" />
                <span>Upload Data</span>
              </Link>
              <div className="flex items-center space-x-2 text-gray-400">
                <Zap className="w-4 h-4" />
                <span>AI-Powered Analytics</span>
              </div>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <p className="text-gray-500 text-sm">
              By Ankit
            </p>
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span>Production Ready</span>
              <span>•</span>
              <span>Professional Grade</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
