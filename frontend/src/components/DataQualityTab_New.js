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

  return (
    <div className="space-y-6">
      {/* ML Engineer Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-100">
        <div className="flex items-center space-x-3 mb-4">
          <Brain className="w-8 h-8 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">ML Engineering Dashboard</h2>
        </div>
        <p className="text-gray-600">
          Comprehensive data quality analysis designed for machine learning practitioners. 
          Understand data readiness, preprocessing requirements, and modeling considerations.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-2 p-1 bg-gray-100 rounded-lg">
        <TabButton 
          id="overview" 
          icon={Target} 
          label="ML Readiness" 
          active={activeTab === 'overview'} 
          onClick={setActiveTab} 
        />
        <TabButton 
          id="preprocessing" 
          icon={Settings} 
          label="Preprocessing" 
          active={activeTab === 'preprocessing'} 
          onClick={setActiveTab} 
        />
        <TabButton 
          id="modeling" 
          icon={Code} 
          label="Modeling" 
          active={activeTab === 'modeling'} 
          onClick={setActiveTab} 
        />
        <TabButton 
          id="features" 
          icon={Zap} 
          label="Feature Engineering" 
          active={activeTab === 'features'} 
          onClick={setActiveTab} 
        />
        <TabButton 
          id="data" 
          icon={Database} 
          label="Data Profile" 
          active={activeTab === 'data'} 
          onClick={setActiveTab} 
        />
      </div>

      {/* ML Readiness Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* ML Readiness Score */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <div className="card">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold text-gray-900">ML Readiness Score</h3>
                  <span 
                    className="px-3 py-1 rounded-full text-sm font-medium"
                    style={{ 
                      backgroundColor: getMLReadinessColor(qualityData.data_quality_score?.ml_readiness_level) + '20',
                      color: getMLReadinessColor(qualityData.data_quality_score?.ml_readiness_level)
                    }}
                  >
                    {qualityData.data_quality_score?.ml_readiness_level || 'Unknown'}
                  </span>
                </div>
                
                <div className="flex items-center justify-center mb-6">
                  <div className="relative w-40 h-40">
                    <svg className="w-40 h-40 -rotate-90" viewBox="0 0 200 200">
                      <circle
                        cx="100"
                        cy="100"
                        r="80"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="transparent"
                        className="text-gray-200"
                      />
                      <circle
                        cx="100"
                        cy="100"
                        r="80"
                        stroke={getMLReadinessColor(qualityData.data_quality_score?.ml_readiness_level)}
                        strokeWidth="8"
                        fill="transparent"
                        strokeDasharray={`${2 * Math.PI * 80}`}
                        strokeDashoffset={`${2 * Math.PI * 80 * (1 - (qualityData.data_quality_score?.overall_score || 0) / 100)}`}
                        className="transition-all duration-1000 ease-out"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-gray-900">
                          {qualityData.data_quality_score?.overall_score?.toFixed(0) || '0'}
                        </div>
                        <div className="text-sm text-gray-500">/ 100</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Score Breakdown */}
                <div className="grid grid-cols-5 gap-4">
                  {Object.entries(qualityData.data_quality_score?.component_scores || {}).map(([component, score]) => (
                    <div key={component} className="text-center">
                      <div className="text-lg font-semibold text-gray-900">{score}</div>
                      <div className="text-xs text-gray-500 capitalize">{component.replace('_', ' ')}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {/* Critical Issues */}
              <div className="card">
                <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
                  <AlertTriangle className="w-5 h-5 text-orange-500 mr-2" />
                  Critical Issues
                </h4>
                <div className="space-y-2">
                  {(qualityData.data_quality_score?.critical_issues || []).map((issue, idx) => (
                    <div key={idx} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-sm text-red-800">{issue}</p>
                    </div>
                  ))}
                  {(!qualityData.data_quality_score?.critical_issues || qualityData.data_quality_score.critical_issues.length === 0) && (
                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                      <p className="text-sm text-green-800">No critical issues detected</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Quick Stats */}
              <div className="card">
                <h4 className="text-md font-semibold text-gray-900 mb-3">Dataset Overview</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Rows:</span>
                    <span className="text-sm font-medium">{qualityData.basic_info?.total_rows?.toLocaleString() || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Features:</span>
                    <span className="text-sm font-medium">{qualityData.basic_info?.total_columns || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Missing Data:</span>
                    <span className="text-sm font-medium text-red-600">
                      {((Object.values(qualityData.missing_values || {}).reduce((sum, col) => sum + (col.missing_percentage || 0), 0) / Object.keys(qualityData.missing_values || {}).length) || 0).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Memory:</span>
                    <span className="text-sm font-medium">{(qualityData.basic_info?.memory_usage_mb || 0).toFixed(2)} MB</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* ML Recommendations */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <FileText className="w-5 h-5 text-blue-600 mr-2" />
              ML Engineer Recommendations
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {(qualityData.recommendations || []).map((rec, idx) => (
                <div key={idx} className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">{rec}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Preprocessing Tab */}
      {activeTab === 'preprocessing' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Missing Value Strategy */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Missing Value Strategy</h3>
              {Object.keys(qualityData.data_preprocessing_requirements?.missing_value_strategy || {}).length > 0 ? (
                <div className="space-y-3">
                  {Object.entries(qualityData.data_preprocessing_requirements.missing_value_strategy).map(([col, strategy]) => (
                    <div key={col} className="border border-gray-200 rounded-lg p-3">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-gray-900">{col}</span>
                        <span className="text-sm text-red-600">{strategy.missing_percentage}% missing</span>
                      </div>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {strategy.recommended_strategy.replace('_', ' ')}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 italic">No missing values detected</p>
              )}
            </div>

            {/* Outlier Treatment */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Outlier Treatment</h3>
              {Object.keys(qualityData.data_preprocessing_requirements?.outlier_treatment || {}).length > 0 ? (
                <div className="space-y-3">
                  {Object.entries(qualityData.data_preprocessing_requirements.outlier_treatment).map(([col, treatment]) => (
                    <div key={col} className="border border-gray-200 rounded-lg p-3">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-gray-900">{col}</span>
                        <span className="text-sm text-orange-600">{treatment.outlier_percentage}% outliers</span>
                      </div>
                      <div className="space-x-2">
                        {treatment.treatment_options.map((option, idx) => (
                          <span key={idx} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                            {option.replace('_', ' ')}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 italic">No significant outliers detected</p>
              )}
            </div>
          </div>

          {/* Transformation Pipeline */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Preprocessing Pipeline</h3>
            <div className="space-y-3">
              {(qualityData.data_preprocessing_requirements?.transformation_pipeline || []).map((step, idx) => (
                <div key={idx} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                    {idx + 1}
                  </div>
                  <span className="text-gray-900">{step}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Modeling Tab */}
      {activeTab === 'modeling' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Model Recommendations */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommended Models</h3>
              <div className="space-y-2">
                {(qualityData.modeling_considerations?.model_recommendations || []).map((model, idx) => (
                  <div key={idx} className="p-3 bg-green-50 border border-green-200 rounded-lg">
                    <span className="text-green-800 font-medium">{model}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Validation Strategy */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Validation Strategy</h3>
              {qualityData.modeling_considerations?.validation_strategy && (
                <div className="space-y-3">
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2">
                      {qualityData.modeling_considerations.validation_strategy.method}
                    </h4>
                    <p className="text-sm text-blue-800">
                      {qualityData.modeling_considerations.validation_strategy.reason}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Performance Considerations */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Considerations</h3>
            <div className="space-y-2">
              {(qualityData.modeling_considerations?.performance_considerations || []).map((consideration, idx) => (
                <div key={idx} className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <span className="text-yellow-800">{consideration}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Target Variable Analysis */}
          {qualityData.ml_readiness?.target_variable_analysis && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Potential Target Variables</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {qualityData.ml_readiness.target_variable_analysis.binary_targets?.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Binary Classification</h4>
                    {qualityData.ml_readiness.target_variable_analysis.binary_targets.map((target, idx) => (
                      <div key={idx} className="p-2 bg-purple-50 border border-purple-200 rounded text-sm">
                        {target.column}
                      </div>
                    ))}
                  </div>
                )}
                {qualityData.ml_readiness.target_variable_analysis.categorical_targets?.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Multi-class Classification</h4>
                    {qualityData.ml_readiness.target_variable_analysis.categorical_targets.map((target, idx) => (
                      <div key={idx} className="p-2 bg-indigo-50 border border-indigo-200 rounded text-sm">
                        {target.column} ({target.classes} classes)
                      </div>
                    ))}
                  </div>
                )}
                {qualityData.ml_readiness.target_variable_analysis.continuous_targets?.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Regression</h4>
                    {qualityData.ml_readiness.target_variable_analysis.continuous_targets.map((target, idx) => (
                      <div key={idx} className="p-2 bg-green-50 border border-green-200 rounded text-sm">
                        {target.column}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Feature Engineering Tab */}
      {activeTab === 'features' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Encoding Requirements */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Categorical Encoding</h3>
              {qualityData.ml_readiness?.encoding_requirements?.categorical_features?.length > 0 ? (
                <div className="space-y-3">
                  {qualityData.ml_readiness.encoding_requirements.categorical_features.map((feature, idx) => (
                    <div key={idx} className="border border-gray-200 rounded-lg p-3">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-gray-900">{feature.column}</span>
                        <span className="text-sm text-gray-600">{feature.unique_values} unique values</span>
                      </div>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {feature.recommended_encoding}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 italic">No categorical features requiring encoding</p>
              )}
            </div>

            {/* Scaling Requirements */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Feature Scaling</h3>
              {qualityData.ml_readiness?.scaling_requirements?.features_needing_scaling?.length > 0 ? (
                <div className="space-y-3">
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2">Features Requiring Scaling:</h4>
                    <div className="space-x-2 mb-3">
                      {qualityData.ml_readiness.scaling_requirements.features_needing_scaling.map((feature, idx) => (
                        <span key={idx} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {feature}
                        </span>
                      ))}
                    </div>
                    <div className="space-y-1">
                      {Object.entries(qualityData.ml_readiness.scaling_requirements.scaling_methods || {}).map(([method, description]) => (
                        <div key={method} className="text-sm">
                          <span className="font-medium">{method.replace('_', ' ')}:</span> {description}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500 italic">No scaling required</p>
              )}
            </div>
          </div>

          {/* Feature Engineering Opportunities */}
          {qualityData.feature_engineering_opportunities && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Feature Engineering Opportunities</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {qualityData.feature_engineering_opportunities.datetime_features?.length > 0 && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                    <h4 className="font-medium text-green-900 mb-2">Datetime Features</h4>
                    {qualityData.feature_engineering_opportunities.datetime_features.map((dt, idx) => (
                      <div key={idx} className="text-sm text-green-800">{dt.column}</div>
                    ))}
                  </div>
                )}
                {qualityData.feature_engineering_opportunities.text_features?.length > 0 && (
                  <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                    <h4 className="font-medium text-purple-900 mb-2">Text Features</h4>
                    {qualityData.feature_engineering_opportunities.text_features.map((txt, idx) => (
                      <div key={idx} className="text-sm text-purple-800">{txt.column}</div>
                    ))}
                  </div>
                )}
                {qualityData.feature_engineering_opportunities.interaction_features?.length > 0 && (
                  <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                    <h4 className="font-medium text-orange-900 mb-2">Interaction Features</h4>
                    {qualityData.feature_engineering_opportunities.interaction_features.slice(0, 3).map((interaction, idx) => (
                      <div key={idx} className="text-sm text-orange-800">{interaction}</div>
                    ))}
                  </div>
                )}
                {qualityData.feature_engineering_opportunities.binning_opportunities?.length > 0 && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <h4 className="font-medium text-red-900 mb-2">Binning Opportunities</h4>
                    {qualityData.feature_engineering_opportunities.binning_opportunities.slice(0, 3).map((bin, idx) => (
                      <div key={idx} className="text-sm text-red-800">{bin.column}</div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Data Profile Tab */}
      {activeTab === 'data' && (
        <div className="space-y-6">
          {/* Basic Data Info */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Profile</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Column</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Missing %</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unique Values</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {Object.entries(qualityData.data_types || {}).map(([columnName, typeInfo]) => (
                    <tr key={columnName}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{columnName}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {typeInfo.current_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {qualityData.missing_values?.[columnName]?.missing_percentage?.toFixed(1) || '0'}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {/* We'll need to calculate this from the sample data */}
                        N/A
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Sample Data Preview */}
          {qualityData.basic_info?.sample_data && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Sample Data (First 3 Rows)</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {Object.keys(qualityData.basic_info.sample_data[0] || {}).map((header) => (
                        <th key={header} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          {header}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {qualityData.basic_info.sample_data.map((row, index) => (
                      <tr key={index}>
                        {Object.values(row).map((value, colIndex) => (
                          <td key={colIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
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
      )}
    </div>
  );
};

export default DataQualityTab;
