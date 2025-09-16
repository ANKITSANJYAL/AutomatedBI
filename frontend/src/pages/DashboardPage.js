import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { BarChart3, Download, Filter, Info } from 'lucide-react';
import toast from 'react-hot-toast';
import DataQualityTab from '../components/DataQualityTab';
import BusinessInsightsTab from '../components/BusinessInsightsTab';
import { getAnalysisResults, getDashboardStructure } from '../services/api';

const DashboardPage = () => {
  const { datasetId } = useParams();
  const [activeTab, setActiveTab] = useState('data_quality');
  const [analysisData, setAnalysisData] = useState(null);
  const [dashboardStructure, setDashboardStructure] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        const [analysis, dashboard] = await Promise.all([
          getAnalysisResults(datasetId),
          getDashboardStructure(datasetId)
        ]);
        
        setAnalysisData(analysis);
        setDashboardStructure(dashboard);
      } catch (err) {
        setError(err.message);
        toast.error('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    if (datasetId) {
      loadDashboardData();
    }
  }, [datasetId]);

  const handleExport = async () => {
    try {
      // Implementation for export functionality
      toast.success('Export functionality coming soon!');
    } catch (err) {
      toast.error('Export failed');
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="animate-pulse">
          {/* Header Skeleton */}
          <div className="mb-8">
            <div className="h-8 bg-gray-300 rounded w-1/3 mb-2"></div>
            <div className="h-4 bg-gray-300 rounded w-1/2"></div>
          </div>
          
          {/* Tabs Skeleton */}
          <div className="flex space-x-4 mb-8">
            <div className="h-10 bg-gray-300 rounded w-32"></div>
            <div className="h-10 bg-gray-300 rounded w-32"></div>
          </div>
          
          {/* Content Skeleton */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="card h-64">
                <div className="h-full bg-gray-300 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto text-center">
        <div className="card">
          <Info className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Dashboard Not Ready</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="btn-primary"
          >
            Refresh Page
          </button>
        </div>
      </div>
    );
  }

  const tabs = dashboardStructure?.dashboard?.tabs || [
    { id: 'data_quality', name: 'Data Quality', description: 'Data profiling and quality analysis' },
    { id: 'business_insights', name: 'Business Insights', description: 'KPIs and intelligent insights' }
  ];

  return (
    <div className="max-w-7xl mx-auto">
      {/* Dashboard Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Dashboard Analytics
            </h1>
            <p className="text-gray-600">
              {analysisData?.analysis?.original_filename && 
                `Analysis for: ${analysisData.analysis.original_filename}`}
            </p>
            {analysisData?.analysis?.domain_classification && (
              <div className="mt-2">
                <span className="status-badge status-completed">
                  Domain: {analysisData.analysis.domain_classification}
                </span>
                {analysisData?.analysis?.confidence_score && (
                  <span className="ml-2 text-sm text-gray-500">
                    Confidence: {Math.round(analysisData.analysis.confidence_score * 100)}%
                  </span>
                )}
              </div>
            )}
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={handleExport}
              className="btn-secondary flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Export</span>
            </button>
            
            <button className="btn-secondary flex items-center space-x-2">
              <Filter className="w-4 h-4" />
              <span>Filters</span>
            </button>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="mb-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  py-2 px-1 border-b-2 font-medium text-sm transition-colors duration-200
                  ${activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <div className="flex items-center space-x-2">
                  <BarChart3 className="w-4 h-4" />
                  <span>{tab.name}</span>
                </div>
              </button>
            ))}
          </nav>
        </div>
        
        {/* Tab Description */}
        <div className="mt-4">
          {tabs.find(tab => tab.id === activeTab)?.description && (
            <p className="text-gray-600">
              {tabs.find(tab => tab.id === activeTab).description}
            </p>
          )}
        </div>
      </div>

      {/* Tab Content */}
      <div className="min-h-[500px]">
        {activeTab === 'data_quality' && (
          <DataQualityTab datasetId={datasetId} analysisData={analysisData} />
        )}
        
        {activeTab === 'business_insights' && (
          <BusinessInsightsTab datasetId={datasetId} analysisData={analysisData} />
        )}
      </div>

      {/* Footer Info */}
      <div className="mt-12 pt-8 border-t border-gray-200">
        <div className="grid md:grid-cols-3 gap-6 text-center">
          <div>
            <div className="text-2xl font-bold text-primary-600">
              {analysisData?.analysis?.dataset_info?.row_count?.toLocaleString() || '0'}
            </div>
            <div className="text-sm text-gray-600">Total Rows</div>
          </div>
          
          <div>
            <div className="text-2xl font-bold text-primary-600">
              {analysisData?.analysis?.dataset_info?.column_count || '0'}
            </div>
            <div className="text-sm text-gray-600">Columns Analyzed</div>
          </div>
          
          <div>
            <div className="text-2xl font-bold text-primary-600">
              {analysisData?.analysis?.data_quality?.data_quality_score?.overall_score?.toFixed(1) || 'N/A'}%
            </div>
            <div className="text-sm text-gray-600">Data Quality Score</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
