from flask import request, jsonify
from app.api import api_bp
from app.services.analysis_service import AnalysisService
from app.utils.validators import validate_dataset_id, validate_chart_config
import structlog

logger = structlog.get_logger(__name__)


@api_bp.route('/dashboard/<dataset_id>', methods=['GET'])
def get_dashboard_structure(dataset_id):
    """Get the dashboard structure and layout for a dataset"""
    try:
        # Validate dataset ID
        validation = validate_dataset_id(dataset_id)
        if not validation['valid']:
            return jsonify({'error': validation['message']}), 400
        
        analysis_service = AnalysisService()
        analysis_result = analysis_service.get_dataset_analysis(dataset_id)
        
        if not analysis_result:
            return jsonify({'error': 'Dataset not found'}), 404
        
        dashboard_structure = analysis_result.get('dashboard_structure')
        
        if not dashboard_structure:
            return jsonify({'error': 'Dashboard not yet generated'}), 404
        
        return jsonify({
            'success': True,
            'dataset_id': dataset_id,
            'dashboard': dashboard_structure,
            'metadata': {
                'domain': analysis_result.get('domain_classification'),
                'last_updated': analysis_result.get('processing_completed_at'),
                'data_quality_score': analysis_result.get('data_quality_report', {}).get('quality_score')
            }
        }), 200
        
    except Exception as e:
        logger.error("Error getting dashboard structure", dataset_id=dataset_id, error=str(e))
        return jsonify({'error': 'Failed to get dashboard structure'}), 500


@api_bp.route('/dashboard/<dataset_id>/charts', methods=['GET'])
def get_dashboard_charts(dataset_id):
    """Get chart configurations for the dashboard"""
    try:
        # Validate dataset ID
        validation = validate_dataset_id(dataset_id)
        if not validation['valid']:
            return jsonify({'error': validation['message']}), 400
        
        analysis_service = AnalysisService()
        analysis_result = analysis_service.get_dataset_analysis(dataset_id)
        
        if not analysis_result:
            return jsonify({'error': 'Dataset not found'}), 404
        
        # Get charts from dashboard_structure.visualizations instead of recommended_charts
        dashboard_structure = analysis_result.get('dashboard_structure', {})
        charts = dashboard_structure.get('visualizations', [])
        
        return jsonify({
            'success': True,
            'dataset_id': dataset_id,
            'charts': charts,
            'total_charts': len(charts)
        }), 200
        
    except Exception as e:
        logger.error("Error getting dashboard charts", dataset_id=dataset_id, error=str(e))
        return jsonify({'error': 'Failed to get dashboard charts'}), 500


@api_bp.route('/dashboard/<dataset_id>/chart-data', methods=['POST'])
def get_chart_data(dataset_id):
    """Get data for a specific chart configuration"""
    try:
        # Validate dataset ID
        validation = validate_dataset_id(dataset_id)
        if not validation['valid']:
            return jsonify({'error': validation['message']}), 400
        
        # Validate chart configuration
        chart_config = request.json
        if not chart_config:
            return jsonify({'error': 'Chart configuration required'}), 400
        
        config_validation = validate_chart_config(chart_config)
        if not config_validation['valid']:
            return jsonify({'error': config_validation['message']}), 400
        
        # Get dataset data
        analysis_service = AnalysisService()
        data_result = analysis_service.get_dataset_data(dataset_id, page=1, per_page=10000)
        
        if not data_result['data']:
            return jsonify({'error': 'No data available'}), 404
        
        # Extract the nested data from each row
        raw_data = data_result['data']
        flattened_data = []
        for row in raw_data:
            if isinstance(row, dict) and 'data' in row:
                flattened_data.append(row['data'])
            else:
                flattened_data.append(row)
        
        # Process data for the specific chart
        chart_data = _process_chart_data(flattened_data, chart_config)
        
        return jsonify({
            'success': True,
            'dataset_id': dataset_id,
            'chart_config': chart_config,
            'chart_data': chart_data
        }), 200
        
    except Exception as e:
        logger.error("Error getting chart data", dataset_id=dataset_id, error=str(e))
        return jsonify({'error': 'Failed to get chart data'}), 500


@api_bp.route('/dashboard/<dataset_id>/kpis', methods=['GET'])
def get_dashboard_kpis(dataset_id):
    """Get KPI values for the dashboard"""
    try:
        # Validate dataset ID
        validation = validate_dataset_id(dataset_id)
        if not validation['valid']:
            return jsonify({'error': validation['message']}), 400
        
        analysis_service = AnalysisService()
        analysis_result = analysis_service.get_dataset_analysis(dataset_id)
        
        if not analysis_result:
            return jsonify({'error': 'Dataset not found'}), 404
        
        # Get KPIs from kpi_analysis.identified_kpis instead of recommended_kpis
        kpi_analysis = analysis_result.get('kpi_analysis', {})
        identified_kpis = kpi_analysis.get('identified_kpis', {})
        
        # Convert to list format expected by frontend
        kpi_values = list(identified_kpis.values())
        
        return jsonify({
            'success': True,
            'dataset_id': dataset_id,
            'kpis': kpi_values,
            'domain': analysis_result.get('domain_analysis', {}).get('domain_classification')
        }), 200
        
    except Exception as e:
        logger.error("Error getting dashboard KPIs", dataset_id=dataset_id, error=str(e))
        return jsonify({'error': 'Failed to get dashboard KPIs'}), 500


@api_bp.route('/dashboard/<dataset_id>/filters', methods=['GET'])
def get_dashboard_filters(dataset_id):
    """Get available filters for the dashboard"""
    try:
        # Validate dataset ID
        validation = validate_dataset_id(dataset_id)
        if not validation['valid']:
            return jsonify({'error': validation['message']}), 400
        
        analysis_service = AnalysisService()
        analysis_result = analysis_service.get_dataset_analysis(dataset_id)
        
        if not analysis_result:
            return jsonify({'error': 'Dataset not found'}), 404
        
        # Generate filter options based on column analysis
        column_analysis = analysis_result.get('column_analysis', {})
        filters = _generate_filter_options(column_analysis)
        
        return jsonify({
            'success': True,
            'dataset_id': dataset_id,
            'filters': filters
        }), 200
        
    except Exception as e:
        logger.error("Error getting dashboard filters", dataset_id=dataset_id, error=str(e))
        return jsonify({'error': 'Failed to get dashboard filters'}), 500


def _process_chart_data(data, chart_config):
    """Process raw data for specific chart type based on AI-generated configuration"""
    try:
        chart_type = chart_config.get('type')
        
        if chart_type == 'kpi_cards':
            return _process_kpi_cards_data(data, chart_config)
        elif chart_type == 'bar':
            return _process_ai_bar_chart_data(data, chart_config)
        elif chart_type in ['pie', 'donut']:
            return _process_ai_pie_chart_data(data, chart_config)
        elif chart_type == 'scatter':
            return _process_ai_scatter_chart_data(data, chart_config)
        elif chart_type == 'heatmap':
            return _process_heatmap_data(data, chart_config)
        elif chart_type in ['multi_line', 'line', 'trend']:
            return _process_line_chart_data(data, chart_config)
        elif chart_type in ['histogram', 'box', 'treemap', 'gauge']:
            return _process_advanced_chart_data(data, chart_config)
        elif chart_type == 'table':
            return _process_table_data(data, chart_config)
        else:
            # Intelligent fallback - try to determine best chart type from data
            return _process_intelligent_fallback(data, chart_config)
            
    except Exception as e:
        logger.error("Error processing chart data", error=str(e), chart_type=chart_type)
        return []


def _process_kpi_cards_data(data, chart_config):
    """Process data for KPI cards"""
    # KPI cards don't need chart data, they get values from the KPI analysis
    # Return the KPI configuration for rendering
    return {
        'type': 'kpi_cards',
        'kpis': chart_config.get('kpis', []),
        'style': chart_config.get('style', {}),
        'message': 'KPI data loaded from analysis'
    }


def _process_ai_bar_chart_data(data, chart_config):
    """Process data for AI-generated bar chart"""
    # Extract configuration from AI chart - handle both data_mapping format and direct fields
    data_mapping = chart_config.get('data_mapping', {})
    x_axis = data_mapping.get('x_axis') or chart_config.get('x_axis')
    y_axis = data_mapping.get('y_axis') or chart_config.get('y_axis')
    
    if not x_axis or not y_axis:
        # Fallback: use available numeric/categorical columns
        if len(data) > 0:
            columns = list(data[0].keys())
            categorical_cols = []
            numeric_cols = []
            
            for col in columns:
                sample_val = data[0].get(col)
                try:
                    float(sample_val)
                    numeric_cols.append(col)
                except:
                    categorical_cols.append(col)
            
            if not x_axis:
                x_axis = categorical_cols[0] if categorical_cols else columns[0]
            if not y_axis:
                y_axis = numeric_cols[0] if numeric_cols else columns[1] if len(columns) > 1 else columns[0]
    
    # Group by x_axis and aggregate y_axis
    chart_data = {}
    for row in data:
        x_val = str(row.get(x_axis, 'Unknown'))
        y_val = row.get(y_axis, 0)
        
        try:
            y_val = float(y_val) if y_val is not None else 0
        except (ValueError, TypeError):
            y_val = 1  # Count occurrences if not numeric
        
        chart_data[x_val] = chart_data.get(x_val, 0) + y_val
    
    return [{'x': k, 'y': v} for k, v in chart_data.items()]


def _process_ai_pie_chart_data(data, chart_config):
    """Process data for AI-generated pie/donut chart"""
    # Handle both direct fields and data_mapping
    data_mapping = chart_config.get('data_mapping', {})
    
    # Try multiple field name variations for category
    category_field = (data_mapping.get('category') or data_mapping.get('x_axis') or 
                     chart_config.get('category_column') or chart_config.get('category') or 
                     chart_config.get('x_axis'))
    
    # Try multiple field name variations for value  
    value_field = (data_mapping.get('value') or data_mapping.get('y_axis') or 
                  chart_config.get('value_column') or chart_config.get('value') or 
                  chart_config.get('y_axis'))
    
    if not category_field:
        # Use first categorical column
        if len(data) > 0:
            columns = list(data[0].keys())
            category_field = columns[0]
    
    # Group by category and sum/count values
    pie_data = {}
    for row in data:
        category = str(row.get(category_field, 'Unknown'))
        
        if value_field and value_field in row:
            try:
                value = float(row.get(value_field, 0))
            except (ValueError, TypeError):
                value = 1
        else:
            value = 1  # Count occurrences
        
        pie_data[category] = pie_data.get(category, 0) + value
    
    # Convert to chart format - using 'value' key for donut charts
    chart_data = []
    for category, total_value in pie_data.items():
        chart_data.append({
            'x': category,
            'name': category,  # For donut chart labels
            'value': total_value,  # For donut chart data
            'y': total_value  # For fallback compatibility
        })
    
    # Sort by value and limit to reasonable number for donut charts
    chart_data.sort(key=lambda x: x['value'], reverse=True)
    if chart_config.get('type') == 'donut' and len(chart_data) > 8:
        # Keep top 7 and group rest as "Others"
        top_items = chart_data[:7]
        others_total = sum(item['value'] for item in chart_data[7:])
        if others_total > 0:
            top_items.append({
                'x': 'Others',
                'name': 'Others',
                'value': others_total,
                'y': others_total
            })
        chart_data = top_items
    
    return chart_data


def _process_advanced_chart_data(data, chart_config):
    """Process data for advanced chart types (histogram, box, treemap, gauge)"""
    chart_type = chart_config.get('type')
    
    if chart_type == 'histogram':
        return _process_histogram_data(data, chart_config)
    elif chart_type == 'box':
        return _process_box_plot_data(data, chart_config)
    elif chart_type == 'treemap':
        return _process_treemap_data(data, chart_config)
    elif chart_type == 'gauge':
        return _process_gauge_data(data, chart_config)
    else:
        # Fallback to bar chart format
        return _process_ai_bar_chart_data(data, chart_config)


def _process_histogram_data(data, chart_config):
    """Process data for histogram chart"""
    data_column = chart_config.get('data_column') or chart_config.get('y_axis')
    
    if not data_column:
        # Find first numeric column
        if len(data) > 0:
            for col in data[0].keys():
                try:
                    float(data[0].get(col))
                    data_column = col
                    break
                except:
                    continue
    
    # Extract numeric values
    values = []
    for row in data:
        try:
            val = float(row.get(data_column, 0))
            values.append(val)
        except (ValueError, TypeError):
            continue
    
    if not values:
        return []
    
    # Create histogram bins
    import numpy as np
    hist, bin_edges = np.histogram(values, bins=10)
    
    chart_data = []
    for i in range(len(hist)):
        chart_data.append({
            'x': f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}",
            'y': int(hist[i])
        })
    
    return chart_data


def _process_box_plot_data(data, chart_config):
    """Process data for box plot (simulated as bar chart with quartiles)"""
    metrics = chart_config.get('metrics', [])
    
    if not metrics and len(data) > 0:
        # Find numeric columns
        for col in data[0].keys():
            try:
                float(data[0].get(col))
                metrics.append(col)
                if len(metrics) >= 4:  # Limit to 4 metrics
                    break
            except:
                continue
    
    chart_data = []
    for metric in metrics:
        values = []
        for row in data:
            try:
                val = float(row.get(metric, 0))
                values.append(val)
            except (ValueError, TypeError):
                continue
        
        if values:
            import numpy as np
            q75 = np.percentile(values, 75)
            chart_data.append({
                'x': metric.replace('_', ' ').title(),
                'y': float(q75)
            })
    
    return chart_data


def _process_treemap_data(data, chart_config):
    """Process data for treemap (simulated as grouped data)"""
    group_column = chart_config.get('group_column') or chart_config.get('category_column')
    size_column = chart_config.get('size_column') or chart_config.get('value_column')
    
    if not group_column or not size_column:
        return _process_ai_pie_chart_data(data, chart_config)
    
    # Group and aggregate data
    grouped_data = {}
    for row in data:
        category = str(row.get(group_column, 'Unknown'))
        try:
            value = float(row.get(size_column, 0))
            grouped_data[category] = grouped_data.get(category, 0) + value
        except (ValueError, TypeError):
            continue
    
    # Convert to chart format and limit to top 8
    chart_data = [{'x': k, 'y': v} for k, v in grouped_data.items()]
    chart_data.sort(key=lambda x: x['y'], reverse=True)
    
    return chart_data[:8]  # Limit for readability


def _process_gauge_data(data, chart_config):
    """Process data for gauge chart"""
    metric = chart_config.get('metric')
    current_value = chart_config.get('current_value')
    target_value = chart_config.get('target_value')
    
    if current_value is not None and target_value is not None:
        percentage = min((current_value / target_value) * 100, 100) if target_value > 0 else 0
        return [{
            'x': 'Performance',
            'y': percentage,
            'current': current_value,
            'target': target_value
        }]
    
    # Fallback: calculate from data
    if metric and len(data) > 0:
        values = []
        for row in data:
            try:
                val = float(row.get(metric, 0))
                values.append(val)
            except (ValueError, TypeError):
                continue
        
        if values:
            current = sum(values) / len(values)  # Average
            target = max(values) if values else current * 1.2
            percentage = min((current / target) * 100, 100) if target > 0 else 0
            
            return [{
                'x': metric.replace('_', ' ').title(),
                'y': percentage,
                'current': current,
                'target': target
            }]
    
    return []


def _process_ai_scatter_chart_data(data, chart_config):
    """Process data for AI-generated scatter plot"""
    data_mapping = chart_config.get('data_mapping', {})
    x_axis = (data_mapping.get('x_axis') or chart_config.get('x_axis'))
    y_axis = (data_mapping.get('y_axis') or chart_config.get('y_axis'))
    
    if not x_axis or not y_axis:
        # Use first two numeric columns
        if len(data) > 0:
            columns = list(data[0].keys())
            numeric_cols = []
            
            for col in columns:
                try:
                    float(data[0].get(col))
                    numeric_cols.append(col)
                except:
                    pass
            
            x_axis = numeric_cols[0] if len(numeric_cols) > 0 else columns[0]
            y_axis = numeric_cols[1] if len(numeric_cols) > 1 else columns[1] if len(columns) > 1 else columns[0]
    
    chart_data = []
    for row in data:
        try:
            x_val = float(row.get(x_axis, 0))
            y_val = float(row.get(y_axis, 0))
            chart_data.append({'x': x_val, 'y': y_val})
        except (ValueError, TypeError):
            continue
    
    return chart_data


def _process_heatmap_data(data, chart_config):
    """Process data for heatmap"""
    data_mapping = chart_config.get('data_mapping', {})
    x_axis = data_mapping.get('x_axis')
    y_axis = data_mapping.get('y_axis')
    value_field = data_mapping.get('value')
    
    if not x_axis or not y_axis:
        if len(data) > 0:
            columns = list(data[0].keys())
            x_axis = columns[0] if len(columns) > 0 else 'x'
            y_axis = columns[1] if len(columns) > 1 else 'y'
    
    heatmap_data = []
    for i, row in enumerate(data):
        x_val = str(row.get(x_axis, f'Row {i}'))
        y_val = str(row.get(y_axis, f'Col {i}'))
        
        if value_field:
            try:
                value = float(row.get(value_field, 1))
            except:
                value = 1
        else:
            value = 1
        
        heatmap_data.append({'x': x_val, 'y': y_val, 'value': value})
    
    return heatmap_data


def _process_generic_ai_chart_data(data, chart_config):
    """Generic processor for unknown chart types"""
    if len(data) > 0:
        columns = list(data[0].keys())
        if len(columns) >= 2:
            return [{'x': row.get(columns[0]), 'y': row.get(columns[1])} for row in data[:20]]
    
    return []


def _process_line_chart_data(data, chart_config):
    """Process data for line/multi-line charts"""
    data_mapping = chart_config.get('data_mapping', {})
    x_axis = (data_mapping.get('x_axis') or chart_config.get('x_axis') or 
              chart_config.get('time_axis'))
    y_axis = (data_mapping.get('y_axis') or chart_config.get('y_axis') or 
              chart_config.get('value_axis'))
    
    if not x_axis or not y_axis:
        # Auto-detect: use first column as x, first numeric as y
        if len(data) > 0:
            columns = list(data[0].keys())
            x_axis = columns[0]
            
            # Find first numeric column for y
            for col in columns[1:]:
                try:
                    float(data[0].get(col))
                    y_axis = col
                    break
                except:
                    continue
            
            if not y_axis:
                y_axis = columns[1] if len(columns) > 1 else columns[0]
    
    chart_data = []
    for row in data:
        x_val = row.get(x_axis)
        y_val = row.get(y_axis)
        
        try:
            y_val = float(y_val) if y_val is not None else 0
        except (ValueError, TypeError):
            continue
        
        chart_data.append({'x': x_val, 'y': y_val})
    
    return sorted(chart_data, key=lambda x: str(x['x']))


def _process_table_data(data, chart_config):
    """Process data for table display"""
    # Return first 50 rows for table display
    return data[:50]


def _process_intelligent_fallback(data, chart_config):
    """Intelligent fallback that analyzes data to determine best representation"""
    if not data or len(data) == 0:
        return []
    
    columns = list(data[0].keys())
    
    # Analyze data types
    numeric_cols = []
    categorical_cols = []
    
    for col in columns:
        sample_vals = [row.get(col) for row in data[:5] if row.get(col) is not None]
        if sample_vals:
            try:
                [float(val) for val in sample_vals]
                numeric_cols.append(col)
            except:
                categorical_cols.append(col)
    
    # Intelligent decision making
    if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
        # Categorical + Numeric = Bar chart
        return _process_ai_bar_chart_data(data, {
            'x_axis': categorical_cols[0],
            'y_axis': numeric_cols[0]
        })
    elif len(numeric_cols) >= 2:
        # Two numeric = Scatter plot
        return _process_ai_scatter_chart_data(data, {
            'x_axis': numeric_cols[0],
            'y_axis': numeric_cols[1]
        })
    elif len(categorical_cols) >= 1:
        # Just categorical = Pie chart
        return _process_ai_pie_chart_data(data, {
            'category': categorical_cols[0]
        })
    else:
        # Fallback to simple table
        return data[:20]


def _calculate_kpi_values(data, recommended_kpis):
    """Calculate actual KPI values from the data"""
    kpi_values = []
    
    for kpi in recommended_kpis:
        kpi_name = kpi['name']
        kpi_type = kpi.get('type', 'metric')
        
        calculated_value = None
        
        if kpi_type == 'metric':
            # Find numeric columns and calculate sum/average
            numeric_values = []
            for row in data:
                for value in row.values():
                    try:
                        numeric_values.append(float(value))
                    except (ValueError, TypeError):
                        continue
            
            if numeric_values:
                calculated_value = sum(numeric_values) / len(numeric_values)
        
        elif kpi_type == 'percentage':
            # Calculate percentage based on some condition
            calculated_value = 75.5  # Placeholder
        
        elif kpi_type == 'ranking':
            # Get top items
            calculated_value = "Top Item"  # Placeholder
        
        kpi_values.append({
            'name': kpi_name,
            'description': kpi.get('description', ''),
            'type': kpi_type,
            'value': calculated_value,
            'formatted_value': _format_kpi_value(calculated_value, kpi_type)
        })
    
    return kpi_values


def _format_kpi_value(value, kpi_type):
    """Format KPI value for display"""
    if value is None:
        return "N/A"
    
    if kpi_type == 'percentage':
        return f"{value:.1f}%"
    elif kpi_type == 'metric' and isinstance(value, (int, float)):
        if value >= 1000000:
            return f"{value/1000000:.1f}M"
        elif value >= 1000:
            return f"{value/1000:.1f}K"
        else:
            return f"{value:.1f}"
    else:
        return str(value)


def _generate_filter_options(column_analysis):
    """Generate filter options based on column analysis"""
    filters = []
    
    column_stats = column_analysis.get('column_stats', {})
    data_types = column_analysis.get('data_types', {})
    
    for col_name, stats in column_stats.items():
        data_type = data_types.get(col_name, 'object')
        
        filter_config = {
            'column': col_name,
            'type': 'categorical' if data_type == 'object' else 'numeric',
            'unique_values': stats.get('unique_values', 0)
        }
        
        # Add specific options for categorical filters
        if filter_config['type'] == 'categorical' and stats.get('unique_values', 0) < 50:
            filter_config['options'] = ['All']  # Would be populated with actual unique values
        
        # Add range info for numeric filters
        if filter_config['type'] == 'numeric':
            filter_config['min'] = stats.get('min')
            filter_config['max'] = stats.get('max')
        
        filters.append(filter_config)
    
    return filters
