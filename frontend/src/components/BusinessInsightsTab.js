import React, { useState, useEffect } from 'react';
import { TrendingUp, DollarSign, Users, BarChart3, Activity, Target, Gauge } from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, ScatterChart, Scatter, AreaChart, Area,
  Legend, ComposedChart, Treemap, RadialBarChart, RadialBar, ReferenceLine
} from 'recharts';
import { getBusinessInsights, getDashboardKPIs, getDashboardCharts, getChartData } from '../services/api';
import toast from 'react-hot-toast';

const BusinessInsightsTab = ({ datasetId, analysisData }) => {
  const [insights, setInsights] = useState(null);
  const [kpis, setKpis] = useState([]);
  const [charts, setCharts] = useState([]);
  const [chartData, setChartData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadInsightsData = async () => {
      try {
        setLoading(true);
        const [insightsData, kpisData, chartsData] = await Promise.all([
          getBusinessInsights(datasetId),
          getDashboardKPIs(datasetId),
          getDashboardCharts(datasetId)
        ]);
        
        setInsights(insightsData);
        setKpis(kpisData.kpis || []);
        
        // Filter out KPI cards since they're already displayed in their own section
        const actualCharts = (chartsData.charts || []).filter(chart => chart.type !== 'kpi_cards');
        setCharts(actualCharts);
        
        // Load data for each chart (excluding KPI cards)
        const chartDataPromises = actualCharts?.map(async (chart) => {
          try {
            const data = await getChartData(datasetId, chart);
            return { chartId: chart.type + '_' + chart.title.replace(/\s+/g, '_'), data: data.chart_data };
          } catch (err) {
            console.warn(`Failed to load data for chart: ${chart.title}`);
            return { chartId: chart.type + '_' + chart.title.replace(/\s+/g, '_'), data: [] };
          }
        }) || [];
        
        const chartDataResults = await Promise.all(chartDataPromises);
        const chartDataMap = {};
        chartDataResults.forEach(({ chartId, data }) => {
          chartDataMap[chartId] = data;
        });
        
        setChartData(chartDataMap);
      } catch (err) {
        toast.error('Failed to load insights data');
      } finally {
        setLoading(false);
      }
    };

    if (datasetId) {
      loadInsightsData();
    }
  }, [datasetId]);

  // Helper function to format KPI values based on industry standards
  const formatKPIValue = (value, format, name) => {
    if (value === null || value === undefined) return 'N/A';
    
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return value;

    // Industry-specific formatting for transportation/ride-sharing
    if (name.toLowerCase().includes('cost') || name.toLowerCase().includes('value') || name.toLowerCase().includes('revenue')) {
      // Currency values - round to 2 decimal places or whole numbers if large
      if (numValue >= 1000) {
        return `$${Math.round(numValue).toLocaleString()}`;
      }
      return `$${numValue.toFixed(2)}`;
    }
    
    if (name.toLowerCase().includes('time') || name.toLowerCase().includes('vtat') || name.toLowerCase().includes('ctat')) {
      // Time values - round to 1 decimal place
      return numValue.toFixed(1);
    }
    
    if (name.toLowerCase().includes('count') || name.toLowerCase().includes('total') || name.toLowerCase().includes('records')) {
      // Count values - whole numbers
      return Math.round(numValue).toLocaleString();
    }
    
    if (name.toLowerCase().includes('rate') || name.toLowerCase().includes('percentage')) {
      // Percentage values
      return `${numValue.toFixed(1)}%`;
    }
    
        // Default formatting based on magnitude
    if (numValue >= 1000000) {
      return `${(numValue / 1000000).toFixed(1)}M`;
    } else if (numValue >= 1000) {
      return Math.round(numValue).toLocaleString();
    } else if (numValue >= 100) {
      return Math.round(numValue);
    } else {
      return numValue.toFixed(1);
    }
  };

  const getKPIIcon = (type) => {
    switch (type) {
      case 'revenue': return <DollarSign className="w-5 h-5" />;
      case 'users': return <Users className="w-5 h-5" />;
      case 'growth': return <TrendingUp className="w-5 h-5" />;
      case 'performance': return <Activity className="w-5 h-5" />;
      default: return <BarChart3 className="w-5 h-5" />;
    }
  };

  const renderChart = (chart, data) => {
    const chartId = chart.type + '_' + chart.title.replace(/\s+/g, '_');
    const chartDataForChart = data[chartId] || [];
    
    // Enhanced color palettes for professional appearance
    const colors = ['#2563EB', '#16A34A', '#DC2626', '#CA8A04', '#9333EA', '#C2410C', '#0891B2', '#BE185D'];
    const gradientColors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

    // Handle KPI Cards separately - they don't need chart data, they use KPI values
    if (chart.type === 'kpi_cards' || chart.type?.toLowerCase() === 'kpi_cards') {
      return (
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
          {chart.kpis?.map((kpiKey, index) => {
            const kpi = kpis.find(k => k.name?.toLowerCase().includes(kpiKey.replace(/_/g, ' ')) || 
                                        k.source_column === kpiKey);
            return (
              <div key={index} className="metric-card">
                <div className="flex items-center justify-between">
                  <div className="flex-grow">
                    <p className="text-sm font-medium text-gray-600">
                      {kpi?.name || kpiKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </p>
                    <p className="text-xl font-bold text-primary-600 mt-1">
                      {kpi?.formatted_value || kpi?.value || 'N/A'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {kpi?.description || 'Key metric'}
                    </p>
                  </div>
                  <div className="flex-shrink-0 text-primary-600">
                    {getKPIIcon(kpi?.type)}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      );
    }

    // Handle table charts
    if (chart.type === 'table') {
      if (!chartDataForChart || chartDataForChart.length === 0) {
        return (
          <div className="h-64 flex items-center justify-center text-gray-500">
            No data available for this table
          </div>
        );
      }
      
      const columns = Object.keys(chartDataForChart[0] || {});
      return (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {columns.map((col) => (
                  <th key={col} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {chartDataForChart.slice(0, 10).map((row, index) => (
                <tr key={index}>
                  {columns.map((col) => (
                    <td key={col} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {row[col]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    // For all other chart types, ensure we have data
    if (!chartDataForChart || chartDataForChart.length === 0) {
      return (
        <div className="h-64 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <BarChart3 className="w-12 h-12 mx-auto text-gray-300 mb-2" />
            <p className="text-sm">No data available for this chart</p>
            <p className="text-xs text-gray-400 mt-1">Chart Type: {chart.type}</p>
          </div>
        </div>
      );
    }

    // Intelligent chart type mapping with professional styling
    const normalizedType = chart.type.toLowerCase();

    // BAR CHART - Enhanced with legends and proper formatting
    if (normalizedType.includes('bar') || normalizedType === 'bar') {
      return (
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartDataForChart} margin={{ top: 20, right: 20, left: 20, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="x" 
              tick={{ fontSize: 10, fill: '#6B7280' }}
              axisLine={{ stroke: '#D1D5DB' }}
              interval={0}
              angle={-45}
              textAnchor="end"
              height={50}
              tickFormatter={(value) => {
                // Truncate long labels and make them more readable
                if (typeof value === 'string' && value.length > 12) {
                  return value.substring(0, 10) + '...';
                }
                return value;
              }}
            />
            <YAxis 
              tick={{ fontSize: 10, fill: '#6B7280' }}
              axisLine={{ stroke: '#D1D5DB' }}
              tickFormatter={(value) => {
                // Format large numbers
                if (value >= 1000) {
                  return (value / 1000).toFixed(1) + 'K';
                }
                return value.toFixed(0);
              }}
              width={40}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#F9FAFB', 
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                fontSize: '11px'
              }}
              formatter={(value, name) => [value?.toLocaleString(), name]}
              labelFormatter={(label) => `Category: ${label}`}
            />
            <Legend wrapperStyle={{ fontSize: '11px' }} />
            <Bar dataKey="y" fill={colors[0]} name={chart.y_axis || 'Value'} radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      );
    }

    // DONUT CHART - Professional donut with center text
    if (normalizedType.includes('donut') || normalizedType === 'donut') {
      // Normalize data format for donut charts and limit to top 8 items
      let normalizedData = chartDataForChart.map(item => ({
        name: item.x || item.name || item.label || 'Unknown',
        value: item.y || item.value || 0
      }));
      
      // Sort by value and take top 8, aggregate the rest as "Others"
      normalizedData = normalizedData
        .filter(item => item.value > 0) // Remove zero values
        .sort((a, b) => b.value - a.value);
      
      if (normalizedData.length > 8) {
        const top7 = normalizedData.slice(0, 7);
        const others = normalizedData.slice(7);
        const othersSum = others.reduce((sum, item) => sum + item.value, 0);
        
        normalizedData = [...top7, { name: 'Others', value: othersSum }];
      }
      
      const total = normalizedData.reduce((sum, item) => sum + (item.value || 0), 0);
      
      return (
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={normalizedData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => 
                percent > 0.05 ? `${name}: ${(percent * 100).toFixed(1)}%` : null
              }
              outerRadius="80%"
              innerRadius="50%"
              fill="#8884d8"
              dataKey="value"
              paddingAngle={2}
            >
              {normalizedData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#F9FAFB', 
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                fontSize: '11px'
              }}
              formatter={(value, name) => [value?.toLocaleString(), 'Value']}
            />
            <Legend wrapperStyle={{ fontSize: '11px' }} />
          </PieChart>
        </ResponsiveContainer>
      );
    }

    // HISTOGRAM - Enhanced bar chart for distribution
    if (normalizedType.includes('histogram') || normalizedType === 'histogram') {
      return (
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartDataForChart} margin={{ top: 20, right: 20, left: 20, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="x" 
              tick={{ fontSize: 10, fill: '#6B7280' }}
              axisLine={{ stroke: '#D1D5DB' }}
              angle={-45}
              textAnchor="end"
              height={40}
            />
            <YAxis 
              tick={{ fontSize: 10, fill: '#6B7280' }}
              axisLine={{ stroke: '#D1D5DB' }}
              width={35}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#F9FAFB', 
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                fontSize: '11px'
              }}
            />
            <Legend wrapperStyle={{ fontSize: '11px' }} />
            <Bar dataKey="y" fill={colors[2]} name="Frequency" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      );
    }

    // BOX PLOT - Simulated using line chart with error bars
    if (normalizedType.includes('box') || normalizedType === 'box') {
      return (
        <ResponsiveContainer width="100%" height={350}>
          <ComposedChart data={chartDataForChart} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="x" 
              tick={{ fontSize: 12, fill: '#6B7280' }}
              axisLine={{ stroke: '#D1D5DB' }}
            />
            <YAxis 
              tick={{ fontSize: 12, fill: '#6B7280' }}
              axisLine={{ stroke: '#D1D5DB' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#F9FAFB', 
                border: '1px solid #E5E7EB',
                borderRadius: '8px'
              }}
            />
            <Legend />
            <Bar dataKey="y" fill={colors[3]} name="Quartile Range" fillOpacity={0.6} />
            <Line type="monotone" dataKey="y" stroke={colors[0]} strokeWidth={2} name="Median" />
          </ComposedChart>
        </ResponsiveContainer>
      );
    }

    // TREEMAP - Use actual Recharts Treemap component
    if (normalizedType.includes('treemap') || normalizedType === 'treemap') {
      // Transform data for treemap format
      const treemapData = {
        name: 'root',
        children: chartDataForChart.slice(0, 6).map((item, index) => ({
          name: item.x || item.name || `Item ${index + 1}`,
          size: item.y || item.value || 1,
          color: colors[index % colors.length]
        }))
      };

      return (
        <ResponsiveContainer width="100%" height={350}>
          <Treemap
            data={treemapData.children}
            dataKey="size"
            aspectRatio={4/3}
            stroke="#fff"
            strokeWidth={2}
            content={({ x, y, width, height, index, name, size }) => (
              <g>
                <rect
                  x={x}
                  y={y}
                  width={width}
                  height={height}
                  fill={colors[index % colors.length]}
                  opacity={0.8}
                />
                {width > 60 && height > 30 && (
                  <text
                    x={x + width / 2}
                    y={y + height / 2}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize="12"
                    fill="#fff"
                    fontWeight="bold"
                  >
                    {name}
                  </text>
                )}
                {width > 60 && height > 50 && (
                  <text
                    x={x + width / 2}
                    y={y + height / 2 + 15}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize="10"
                    fill="#fff"
                  >
                    {size?.toLocaleString()}
                  </text>
                )}
              </g>
            )}
          />
        </ResponsiveContainer>
      );
    }

    // GAUGE CHART - Simulated using radial bar
    if (normalizedType.includes('gauge') || normalizedType === 'gauge') {
      // Transform data for gauge representation
      const gaugeData = chartDataForChart.map(item => ({
        ...item,
        fullValue: 100,
        value: Math.min(item.y || item.value || 0, 100)
      }));

      return (
        <ResponsiveContainer width="100%" height={350}>
          <RadialBarChart 
            cx="50%" 
            cy="50%" 
            innerRadius="60%" 
            outerRadius="90%" 
            data={gaugeData.slice(0, 1)} // Show first metric as gauge
            startAngle={180} 
            endAngle={0}
          >
            <RadialBar 
              minAngle={15} 
              label={{ position: 'insideStart', fill: '#fff', fontSize: '14px' }} 
              background 
              clockWise 
              dataKey="value"
              fill={colors[5]}
            />
            <Legend 
              iconSize={18} 
              layout="horizontal" 
              verticalAlign="bottom" 
              align="center"
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#F9FAFB', 
                border: '1px solid #E5E7EB',
                borderRadius: '8px'
              }}
            />
          </RadialBarChart>
        </ResponsiveContainer>
      );
    }

    // LINE CHART - Enhanced with styling
    if (normalizedType.includes('line') || normalizedType === 'line' || 
        normalizedType === 'multi_line' || normalizedType.includes('trend')) {
      return (
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={chartDataForChart} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="x" 
              tick={{ fontSize: 12, fill: '#6B7280' }}
              axisLine={{ stroke: '#D1D5DB' }}
            />
            <YAxis 
              tick={{ fontSize: 12, fill: '#6B7280' }}
              axisLine={{ stroke: '#D1D5DB' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#F9FAFB', 
                border: '1px solid #E5E7EB',
                borderRadius: '8px'
              }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="y" 
              stroke={colors[0]} 
              strokeWidth={3}
              name={chart.y_axis || 'Value'}
              dot={{ r: 4, fill: colors[0] }}
              activeDot={{ r: 6, fill: colors[0] }}
            />
          </LineChart>
        </ResponsiveContainer>
      );
    }

    // PIE CHART - Enhanced with styling
    if (normalizedType.includes('pie') || normalizedType === 'pie') {
      return (
        <ResponsiveContainer width="100%" height={350}>
          <PieChart>
            <Pie
              data={chartDataForChart}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
              paddingAngle={1}
            >
              {chartDataForChart.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#F9FAFB', 
                border: '1px solid #E5E7EB',
                borderRadius: '8px'
              }}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      );
    }

    // SCATTER CHART - Enhanced with styling
    if (normalizedType.includes('scatter') || normalizedType === 'scatter' || 
        normalizedType.includes('relationship')) {
      return (
        <ResponsiveContainer width="100%" height={350}>
          <ScatterChart data={chartDataForChart} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="x" 
              tick={{ fontSize: 12, fill: '#6B7280' }}
              axisLine={{ stroke: '#D1D5DB' }}
              name={chart.x_axis || 'X Axis'}
            />
            <YAxis 
              dataKey="y" 
              tick={{ fontSize: 12, fill: '#6B7280' }}
              axisLine={{ stroke: '#D1D5DB' }}
              name={chart.y_axis || 'Y Axis'}
            />
            <Tooltip 
              cursor={{ strokeDasharray: '3 3' }}
              contentStyle={{ 
                backgroundColor: '#F9FAFB', 
                border: '1px solid #E5E7EB',
                borderRadius: '8px'
              }}
            />
            <Legend />
            <Scatter 
              dataKey="y" 
              fill={colors[0]} 
              name={chart.title || 'Data Points'}
            />
          </ScatterChart>
        </ResponsiveContainer>
      );
    }

    // AREA CHART - Enhanced with styling
    if (normalizedType.includes('area') || normalizedType === 'area') {
      return (
        <ResponsiveContainer width="100%" height={350}>
          <AreaChart data={chartDataForChart} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="x" 
              tick={{ fontSize: 12, fill: '#6B7280' }}
              axisLine={{ stroke: '#D1D5DB' }}
            />
            <YAxis 
              tick={{ fontSize: 12, fill: '#6B7280' }}
              axisLine={{ stroke: '#D1D5DB' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#F9FAFB', 
                border: '1px solid #E5E7EB',
                borderRadius: '8px'
              }}
            />
            <Legend />
            <Area 
              type="monotone" 
              dataKey="y" 
              stroke={colors[0]} 
              fill={colors[0]} 
              fillOpacity={0.3}
              strokeWidth={2}
              name={chart.y_axis || 'Value'}
            />
          </AreaChart>
        </ResponsiveContainer>
      );
    }

    // Fallback: Enhanced bar chart for any unknown type
    return (
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={chartDataForChart} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis 
            dataKey="x" 
            tick={{ fontSize: 12, fill: '#6B7280' }}
            axisLine={{ stroke: '#D1D5DB' }}
          />
          <YAxis 
            tick={{ fontSize: 12, fill: '#6B7280' }}
            axisLine={{ stroke: '#D1D5DB' }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#F9FAFB', 
              border: '1px solid #E5E7EB',
              borderRadius: '8px'
            }}
          />
          <Legend />
          <Bar dataKey="y" fill={colors[0]} name="Value" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="card bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
          <div className="flex items-center justify-center space-x-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                🧠 AI is analyzing your data...
              </h3>
              <p className="text-gray-600 text-sm">
                Creating intelligent business charts tailored to your dataset
              </p>
            </div>
          </div>
        </div>
        
        {[...Array(3)].map((_, i) => (
          <div key={i} className="card">
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
              <div className="h-64 bg-gray-200 rounded"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Domain Information */}
      {insights?.domain && (
        <div className="card bg-gradient-to-r from-primary-50 to-blue-50 border-primary-200">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-primary-600 rounded-lg flex items-center justify-center">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                Transportation & Logistics Analytics
              </h3>
              <p className="text-gray-600">
                Analysis optimized for ride-sharing and transportation data
              </p>
            </div>
          </div>
        </div>
      )}

      {/* KPI Cards */}
      {kpis.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Performance Indicators</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {kpis.map((kpi, index) => (
              <div key={index} className="metric-card">
                <div className="flex items-center justify-between">
                  <div className="flex-grow">
                    <p className="text-sm font-medium text-gray-600">{kpi.name}</p>
                    <p className="text-2xl font-bold text-primary-600 mt-1">
                      {formatKPIValue(kpi.value, kpi.format, kpi.name)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{kpi.description}</p>
                  </div>
                  <div className="flex-shrink-0 text-primary-600">
                    {getKPIIcon(kpi.type)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Charts */}
      {charts.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Business Intelligence Dashboard</h3>
          <div className="dashboard-grid grid grid-cols-1 xl:grid-cols-2 gap-4 sm:gap-6">
            {charts.filter(chart => {
              // Filter out charts that don't have data
              const chartId = chart.type + '_' + chart.title.replace(/\s+/g, '_');
              const chartDataForChart = chartData[chartId] || [];
              return chartDataForChart && chartDataForChart.length > 0;
            }).map((chart, index) => (
              <div 
                key={index} 
                className={`card ${
                  chart.type === 'table' ? 'xl:col-span-2' :
                  chart.type === 'multi_line' || chart.type === 'line' || chart.type === 'area' ? 'xl:col-span-2' :
                  'xl:col-span-1'
                }`}
              >
                {/* Chart Title and Description */}
                <div className="mb-3 pb-2 border-b border-gray-100">
                  <h4 className="chart-title text-sm sm:text-md font-semibold text-gray-900 mb-1">
                    {chart.title}
                  </h4>
                  {chart.description && (
                    <p className="chart-description text-xs sm:text-sm text-gray-600">
                      {chart.description}
                    </p>
                  )}
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full font-medium">
                      {chart.type?.toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-500">
                      {chartData[chart.type + '_' + chart.title.replace(/\s+/g, '_')]?.length || 0} data points
                    </span>
                  </div>
                </div>
                
                {/* Chart Content */}
                <div className={`${
                  chart.type === 'table' ? 'h-64 sm:h-80 lg:h-96' :
                  chart.type === 'multi_line' || chart.type === 'line' || chart.type === 'area' ? 'h-60 sm:h-72 lg:h-80' :
                  'h-56 sm:h-64 lg:h-72'
                }`}>
                  {renderChart(chart, chartData)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Insights Summary */}
      {insights?.summary && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">AI-Generated Insights</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">
                {insights.summary.total_kpis}
              </div>
              <div className="text-sm text-gray-600">Key Performance Indicators</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">
                {insights.summary.total_charts}
              </div>
              <div className="text-sm text-gray-600">Data Visualizations</div>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-100">
            <p className="text-sm text-gray-700">
              <span className="font-medium">Business Intelligence Summary:</span> {' '}
              Our AI analysis has identified key performance patterns in your transportation data, 
              providing actionable insights for operational efficiency, customer satisfaction, and revenue optimization. 
              The recommended KPIs and visualizations above are specifically tailored to help you make data-driven decisions 
              in ride-sharing and logistics operations.
            </p>
          </div>
        </div>
      )}

      {/* No Data Message */}
      {kpis.length === 0 && charts.length === 0 && (
        <div className="card text-center py-12">
          <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Business Insights Available</h3>
          <p className="text-gray-600">
            The analysis is still processing or there was an issue generating insights for your data.
          </p>
        </div>
      )}
    </div>
  );
};

export default BusinessInsightsTab;
