import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, Database, TrendingUp, Brain, Zap, Target, Code, Settings, FileText } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { getDataQualityReport, getDatasetData } from '../services/api';
import toast from 'react-hot-toast';

const DataQualityTab = ({ datasetId, analysisData }) => {
  const [qualityReport, setQualityReport] = useState(null);
  const [sampleData, setSampleData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const loadQualityData = async () => {
      try {
        setLoading(true);
        const [quality, sample] = await Promise.all([
          getDataQualityReport(datasetId),
          getDatasetData(datasetId, 1, 10) // Get first 10 rows for preview
        ]);
        
        setQualityReport(quality);
        setSampleData(sample);
      } catch (err) {
        toast.error('Failed to load quality data');
      } finally {
        setLoading(false);
      }
    };

    if (datasetId) {
      loadQualityData();
    }
  }, [datasetId]);

  if (loading) {
    return (
      <div className="space-y-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card h-64">
            <div className="skeleton h-full w-full"></div>
          </div>
        ))}
      </div>
    );
  }

  const qualityData = analysisData?.data_quality || qualityReport?.quality_report || {};
  const columnStats = qualityReport?.column_analysis?.column_stats || {};
  const summary = qualityReport?.summary || {};

  // Helper function to get ML readiness color
  const getMLReadinessColor = (level) => {
    const colors = {
      'Production Ready': '#10B981',
      'Model Development Ready': '#3B82F6', 
      'Requires Preprocessing': '#F59E0B',
      'Significant Cleaning Needed': '#EF4444',
      'Not Suitable for ML Without Major Preprocessing': '#DC2626'
    };
    return colors[level] || '#6B7280';
  };

  // ML readiness radar chart data
  const getRadarData = (scores) => {
    return [
      { subject: 'Missing Data', value: scores?.missing_data || 0, fullMark: 25 },
      { subject: 'Duplicates', value: scores?.duplicates || 0, fullMark: 20 },
      { subject: 'Data Types', value: scores?.data_types || 0, fullMark: 20 },
      { subject: 'Outliers', value: scores?.outliers || 0, fullMark: 15 },
      { subject: 'Sample Size', value: scores?.sample_size || 0, fullMark: 20 }
    ];
  };

  const TabButton = ({ id, icon: Icon, label, active, onClick }) => (
    <button
      onClick={() => onClick(id)}
      className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
        active 
          ? 'bg-blue-100 text-blue-700 border border-blue-200' 
          : 'text-gray-600 hover:bg-gray-100'
      }`}
    >
      <Icon size={18} />
      <span>{label}</span>
    </button>
  );

  // Prepare data for missing values chart
  const missingValuesData = Object.entries(qualityData.missing_values || {})
    .map(([col, data]) => ({
      column: col,
      missing: data.percentage,
      complete: 100 - data.percentage
    }))
    .slice(0, 10); // Show top 10 columns

  // Prepare data for data types pie chart
  const dataTypesCount = {};
  Object.entries(qualityData.data_types || {}).forEach(([col, type]) => {
    dataTypesCount[type] = (dataTypesCount[type] || 0) + 1;
  });
  
  const dataTypesData = Object.entries(dataTypesCount).map(([type, count]) => ({
    name: type,
    value: count
  }));

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#F97316'];

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="metric-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Quality Score</p>
              <p className="text-2xl font-bold text-primary-600">
                {qualityData.quality_score?.toFixed(1) || 'N/A'}%
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
        </div>
        
        <div className="metric-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Rows</p>
              <p className="text-2xl font-bold text-primary-600">
                {qualityData.total_rows?.toLocaleString() || '0'}
              </p>
            </div>
            <Database className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        
        <div className="metric-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Columns</p>
              <p className="text-2xl font-bold text-primary-600">
                {qualityData.total_columns || '0'}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-purple-500" />
          </div>
        </div>
        
        <div className="metric-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Duplicates</p>
              <p className="text-2xl font-bold text-primary-600">
                {qualityData.duplicates?.duplicate_rows || '0'}
              </p>
            </div>
            <AlertTriangle className="w-8 h-8 text-yellow-500" />
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Missing Values Chart */}
        <div className="chart-container">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Missing Values by Column</h3>
          {missingValuesData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={missingValuesData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="column" 
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis />
                <Tooltip 
                  formatter={(value) => [`${value.toFixed(1)}%`, 'Missing']}
                />
                <Bar dataKey="missing" fill="#EF4444" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-300 flex items-center justify-center text-gray-500">
              No missing values data available
            </div>
          )}
        </div>

        {/* Data Types Distribution */}
        <div className="chart-container">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Types Distribution</h3>
          {dataTypesData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={dataTypesData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {dataTypesData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-300 flex items-center justify-center text-gray-500">
              No data types information available
            </div>
          )}
        </div>
      </div>

      {/* Column Analysis Table */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Column Analysis</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Column
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Unique Values
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Missing %
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Most Frequent
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {Object.entries(columnStats).map(([columnName, stats]) => (
                <tr key={columnName}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {columnName}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {qualityData.data_types?.[columnName] || 'Unknown'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {stats.unique_values?.toLocaleString() || '0'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {qualityData.missing_values?.[columnName]?.percentage?.toFixed(1) || '0'}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {stats.most_frequent?.value || 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Sample Data Preview */}
      {sampleData?.data && sampleData.data.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Preview (First 10 Rows)</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {Object.keys(sampleData.data[0]).map((column) => (
                    <th
                      key={column}
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {column}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sampleData.data.map((row, index) => (
                  <tr key={index}>
                    {Object.values(row).map((value, colIndex) => (
                      <td
                        key={colIndex}
                        className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                      >
                        {value !== null && value !== undefined ? String(value) : (
                          <span className="text-gray-400 italic">null</span>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataQualityTab;
