"""
Dashboard Designer Agent for AutomatedBI
Responsible for creating dashboard layouts and visualization recommendations.
"""

from crewai import Agent
from typing import Dict, Any, List
import pandas as pd


class DashboardDesigner:
    """Agent responsible for dashboard design and visualization strategy"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        self.llm_config = llm_config
        
        # Chart type recommendations based on data characteristics
        self.chart_recommendations = {
            'time_series': ['line', 'area'],
            'categorical': ['bar', 'column', 'pie'],
            'comparison': ['bar', 'column', 'radar'],
            'distribution': ['histogram', 'box', 'violin'],
            'correlation': ['scatter', 'bubble', 'heatmap'],
            'composition': ['pie', 'donut', 'stacked_bar', 'treemap'],
            'relationship': ['scatter', 'bubble', 'network'],
            'geographic': ['map', 'choropleth']
        }
        
        # Color schemes for different contexts
        self.color_schemes = {
            'financial': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
            'sales': ['#2E8B57', '#FF6347', '#4682B4', '#32CD32', '#FF4500'],
            'marketing': ['#FF69B4', '#00CED1', '#FFD700', '#9370DB', '#FF1493'],
            'operations': ['#808080', '#A52A2A', '#006400', '#FF8C00', '#4B0082'],
            'default': ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
        }
        
    def create_agent(self) -> Agent:
        """Create the Dashboard Designer agent"""
        return Agent(
            role='Dashboard Designer',
            goal='Design business-intelligent dashboards with appropriate chart types that provide actionable insights',
            backstory="""You are an expert business intelligence dashboard designer with deep knowledge of:
            
            CHART SELECTION EXPERTISE:
            - Line Charts: Use for time series data, trends, forecasting (revenue over time, performance trends)
            - Bar Charts: Use for categorical comparisons (sales by region, performance by department)  
            - Pie/Donut Charts: Use for part-to-whole relationships (market share, budget allocation)
            - Scatter Plots: Use ONLY for correlation analysis between continuous variables
            - Histograms: Use for distribution analysis (age distribution, salary ranges)
            - Box Plots: Use for statistical analysis (outliers, quartiles, variance)
            - Heatmaps: Use for correlation matrices or intensity mapping
            - Tree Maps: Use for hierarchical data with size and color dimensions
            - Area Charts: Use for cumulative data or stacked trends
            - Gauge Charts: Use for KPI performance against targets
            
            BUSINESS INTELLIGENCE PRINCIPLES:
            - Transportation/Logistics: Focus on route efficiency, driver performance, cost analysis
            - Financial: Emphasize P&L, cash flow, ratios, budget vs actual  
            - HR: Highlight performance, demographics, retention, satisfaction
            - Sales: Show pipeline, conversion rates, territory performance
            - Operations: Display efficiency metrics, capacity utilization, quality
            
            You analyze data characteristics and business context to select the most meaningful 
            chart types that executives and business users can immediately understand and act upon.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm_config.get('model'),
            max_iter=3,
            memory=True
        )
    
    def design_dashboard(self, df: pd.DataFrame, kpis: Dict[str, Any], 
                        domain: str, user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Design a comprehensive dashboard layout
        
        Args:
            df: DataFrame with the data
            kpis: Identified KPIs and their configurations
            domain: Business domain
            user_preferences: Optional user preferences for design
            
        Returns:
            Dictionary containing complete dashboard design
        """
        try:
            # Analyze data for visualization opportunities
            data_analysis = self._analyze_data_for_visualization(df)
            
            # Create visualization recommendations
            visualizations = self._recommend_visualizations(df, kpis, domain, data_analysis)
            
            # Design dashboard layout
            layout = self._design_layout(visualizations, kpis)
            
            # Create dashboard sections
            sections = self._create_dashboard_sections(visualizations, kpis, domain)
            
            # Generate filter recommendations
            filters = self._recommend_filters(df, domain)
            
            # Create color scheme
            colors = self._get_color_scheme(domain, user_preferences)
            
            # Generate dashboard metadata
            metadata = self._generate_dashboard_metadata(df, kpis, domain)
            
            return {
                'layout': layout,
                'sections': sections,
                'visualizations': visualizations,
                'filters': filters,
                'colors': colors,
                'metadata': metadata,
                'recommendations': self._generate_design_recommendations(visualizations, domain)
            }
            
        except Exception as e:
            return {
                'layout': {},
                'sections': [],
                'visualizations': [],
                'filters': [],
                'colors': self.color_schemes['default'],
                'metadata': {},
                'error': f"Dashboard design failed: {str(e)}"
            }
    
    def _analyze_data_for_visualization(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data characteristics for visualization planning"""
        analysis = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': [],
            'categorical_columns': [],
            'date_columns': [],
            'temporal_data': False,
            'geographic_data': False,
            'hierarchical_data': False
        }
        
        # Analyze each column
        for column in df.columns:
            dtype = df[column].dtype
            
            if pd.api.types.is_numeric_dtype(dtype):
                analysis['numeric_columns'].append({
                    'name': column,
                    'min': float(df[column].min()) if pd.notna(df[column].min()) else 0,
                    'max': float(df[column].max()) if pd.notna(df[column].max()) else 0,
                    'mean': float(df[column].mean()) if pd.notna(df[column].mean()) else 0,
                    'distribution': 'normal'  # Simplified
                })
            
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                analysis['date_columns'].append(column)
                analysis['temporal_data'] = True
            
            else:
                unique_count = df[column].nunique()
                analysis['categorical_columns'].append({
                    'name': column,
                    'unique_count': unique_count,
                    'is_high_cardinality': unique_count > 20,
                    'top_values': df[column].value_counts().head(5).to_dict()
                })
                
                # Check for geographic indicators
                if any(geo_term in column.lower() for geo_term in ['country', 'state', 'city', 'region', 'location']):
                    analysis['geographic_data'] = True
                
                # Check for hierarchical indicators
                if any(hier_term in column.lower() for hier_term in ['category', 'department', 'division', 'level']):
                    analysis['hierarchical_data'] = True
        
        return analysis
    
    def _recommend_visualizations(self, df: pd.DataFrame, kpis: Dict[str, Any], 
                                 domain: str, data_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Intelligently recommend business-appropriate visualizations based on data characteristics and domain"""
        visualizations = []
        column_count = len(df.columns)
        
        # Determine target chart count based on data richness
        if column_count >= 20:
            target_charts = 8  # Rich datasets get more charts
        elif column_count >= 15:
            target_charts = 7
        elif column_count >= 10:
            target_charts = 6
        else:
            target_charts = 5  # Minimum for any dataset
        
        # 1. KPI Summary Cards (Always first priority)
        if kpis and isinstance(kpis, dict):
            kpi_list = list(kpis.keys())[:6] if hasattr(kpis, 'keys') else []
            visualizations.append({
                'type': 'kpi_cards',
                'title': 'Key Performance Indicators',
                'description': 'Executive summary of critical business metrics',
                'data_source': 'kpis',
                'priority': 1,
                'size': 'full-width',
                'kpis': kpi_list,
                'style': {
                    'show_trend': True,
                    'show_comparison': True,
                    'color_coding': True
                }
            })
        
        # 2. TIME SERIES ANALYSIS - Line Charts for temporal data
        if data_analysis['temporal_data'] and data_analysis['numeric_columns']:
            date_columns = data_analysis['date_columns']
            numeric_cols = data_analysis['numeric_columns']
            
            # Primary time series - most important metric over time
            primary_metric = self._select_primary_metric(numeric_cols, domain)
            visualizations.append({
                'type': 'line',
                'title': f'{primary_metric["name"].replace("_", " ").title()} Trend Analysis',
                'description': f'Time series showing {primary_metric["name"]} performance over time',
                'x_axis': date_columns[0],
                'y_axis': primary_metric['name'],
                'priority': 2,
                'size': 'full-width',
                'features': {
                    'trend_line': True,
                    'moving_average': True,
                    'annotations': True,
                    'zoom': True
                }
            })
            
            # Secondary time series if we have multiple important metrics
            if len(numeric_cols) >= 2 and len(visualizations) < target_charts:
                secondary_metric = self._select_secondary_metric(numeric_cols, domain, primary_metric)
                visualizations.append({
                    'type': 'area',
                    'title': f'{secondary_metric["name"].replace("_", " ").title()} Cumulative Trend',
                    'description': f'Cumulative analysis of {secondary_metric["name"]} over time',
                    'x_axis': date_columns[0],
                    'y_axis': secondary_metric['name'],
                    'priority': 3,
                    'size': 'half-width',
                    'features': {
                        'stacked': False,
                        'fill_opacity': 0.3,
                        'tooltips': True
                    }
                })
        
        # 3. CATEGORICAL ANALYSIS - Bar Charts and Pie Charts
        if data_analysis['categorical_columns'] and data_analysis['numeric_columns']:
            cat_cols = data_analysis['categorical_columns']
            numeric_cols = data_analysis['numeric_columns']
            
            # Find best categorical breakdown
            best_cat_col = self._select_best_categorical_column(cat_cols, domain)
            primary_metric = self._select_primary_metric(numeric_cols, domain)
            
            if not best_cat_col['is_high_cardinality']:
                # Bar chart for categorical comparison
                visualizations.append({
                    'type': 'bar',
                    'title': f'{primary_metric["name"].replace("_", " ").title()} by {best_cat_col["name"].replace("_", " ").title()}',
                    'description': f'Comparative analysis across {best_cat_col["name"]} categories',
                    'x_axis': best_cat_col['name'],
                    'y_axis': primary_metric['name'],
                    'priority': 3,
                    'size': 'half-width',
                    'features': {
                        'sort_options': True,
                        'color_gradient': True,
                        'data_labels': True,
                        'horizontal': False
                    }
                })
                
                # Pie chart for composition analysis (if appropriate)
                if self._is_suitable_for_pie_chart(best_cat_col, df) and len(visualizations) < target_charts:
                    visualizations.append({
                        'type': 'donut',
                        'title': f'{primary_metric["name"].replace("_", " ").title()} Distribution',
                        'description': f'Composition breakdown showing share by {best_cat_col["name"]}',
                        'category_column': best_cat_col['name'],
                        'value_column': primary_metric['name'],
                        'priority': 3,
                        'size': 'half-width',
                        'features': {
                            'show_percentages': True,
                            'interactive_legend': True,
                            'center_total': True
                        }
                    })
        
        # 4. DISTRIBUTION ANALYSIS - Histograms and Box Plots
        if len(data_analysis['numeric_columns']) >= 1 and len(visualizations) < target_charts:
            # Key metric distribution
            primary_metric = self._select_primary_metric(data_analysis['numeric_columns'], domain)
            visualizations.append({
                'type': 'histogram',
                'title': f'{primary_metric["name"].replace("_", " ").title()} Distribution Analysis',
                'description': f'Statistical distribution showing patterns and outliers in {primary_metric["name"]}',
                'data_column': primary_metric['name'],
                'priority': 4,
                'size': 'half-width',
                'features': {
                    'bins': 'auto',
                    'statistics': True,
                    'normal_curve': True,
                    'percentiles': True
                }
            })
            
            # Box plot for outlier analysis (if we have multiple metrics)
            if len(data_analysis['numeric_columns']) >= 3 and len(visualizations) < target_charts:
                metrics_for_box = [col['name'] for col in data_analysis['numeric_columns'][:4]]
                visualizations.append({
                    'type': 'box',
                    'title': 'Performance Metrics Distribution',
                    'description': 'Box plot analysis showing quartiles, outliers, and variance',
                    'metrics': metrics_for_box,
                    'priority': 4,
                    'size': 'half-width',
                    'features': {
                        'show_outliers': True,
                        'show_mean': True,
                        'notched': True
                    }
                })
        
        # 5. CORRELATION ANALYSIS - Only when business-relevant
        if len(data_analysis['numeric_columns']) >= 2 and len(visualizations) < target_charts:
            # Only create scatter plot if there's a meaningful business relationship
            corr_pairs = self._find_meaningful_correlations(data_analysis['numeric_columns'], domain)
            if corr_pairs:
                col1, col2 = corr_pairs[0]
                visualizations.append({
                    'type': 'scatter',
                    'title': f'{col1.replace("_", " ").title()} vs {col2.replace("_", " ").title()} Correlation',
                    'description': f'Correlation analysis to identify relationship patterns',
                    'x_axis': col1,
                    'y_axis': col2,
                    'priority': 5,
                    'size': 'half-width',
                    'features': {
                        'trend_line': True,
                        'r_squared': True,
                        'confidence_interval': True
                    }
                })
        
        # 6. HIERARCHICAL ANALYSIS - Tree Maps for rich datasets
        if column_count >= 15 and len(data_analysis['categorical_columns']) >= 2 and len(visualizations) < target_charts:
            cat_cols = data_analysis['categorical_columns']
            numeric_col = self._select_primary_metric(data_analysis['numeric_columns'], domain)
            
            # Tree map for hierarchical data
            primary_cat = self._select_best_categorical_column(cat_cols, domain)
            secondary_cat = next((col for col in cat_cols if col['name'] != primary_cat['name']), None)
            
            if secondary_cat and not primary_cat['is_high_cardinality']:
                visualizations.append({
                    'type': 'treemap',
                    'title': f'{numeric_col["name"].replace("_", " ").title()} by {primary_cat["name"].replace("_", " ").title()}',
                    'description': f'Hierarchical view showing size and performance relationships',
                    'size_column': numeric_col['name'],
                    'group_column': primary_cat['name'],
                    'color_column': secondary_cat['name'] if len(data_analysis['numeric_columns']) >= 2 else None,
                    'priority': 5,
                    'size': 'half-width',
                    'features': {
                        'tooltips': True,
                        'drill_down': True,
                        'color_scale': True
                    }
                })
        
        # 7. PERFORMANCE GAUGES - For KPI visualization
        if len(data_analysis['numeric_columns']) >= 1 and len(visualizations) < target_charts:
            primary_metric = self._select_primary_metric(data_analysis['numeric_columns'], domain)
            current_value = df[primary_metric['name']].mean()
            
            visualizations.append({
                'type': 'gauge',
                'title': f'{primary_metric["name"].replace("_", " ").title()} Performance Gauge',
                'description': f'Current performance level with target benchmarking',
                'metric': primary_metric['name'],
                'current_value': current_value,
                'target_value': current_value * 1.2,  # 20% improvement target
                'priority': 5,
                'size': 'half-width',
                'features': {
                    'color_zones': True,
                    'trend_indicator': True,
                    'percentage_display': True
                }
            })
        
        # 8. COMPARATIVE ANALYSIS - Multi-metric charts for rich datasets
        if len(data_analysis['numeric_columns']) >= 3 and len(visualizations) < target_charts:
            top_metrics = [col['name'] for col in data_analysis['numeric_columns'][:4]]
            visualizations.append({
                'type': 'radar',
                'title': 'Multi-Metric Performance Radar',
                'description': 'Comparative analysis across multiple performance dimensions',
                'metrics': top_metrics,
                'priority': 6,
                'size': 'half-width',
                'features': {
                    'normalize_scales': True,
                    'fill_opacity': 0.2,
                    'point_labels': True
                }
            })
        
        # 9. DETAILED DATA TABLE (Always last)
        if len(visualizations) < target_charts:
            top_columns = []
            if data_analysis['categorical_columns']:
                top_columns.append(data_analysis['categorical_columns'][0]['name'])
            if data_analysis['temporal_data']:
                top_columns.append(data_analysis['date_columns'][0])
            top_columns.extend([col['name'] for col in data_analysis['numeric_columns'][:4]])
            
            visualizations.append({
                'type': 'table',
                'title': 'Detailed Data Analysis',
                'description': 'Comprehensive data table with filtering and sorting capabilities',
                'columns': top_columns[:8],  # Limit to 8 columns for readability
                'sort_by': data_analysis['numeric_columns'][0]['name'] if data_analysis['numeric_columns'] else top_columns[0],
                'limit': 50,
                'priority': 7,
                'size': 'full-width',
                'features': {
                    'search': True,
                    'pagination': True,
                    'export': True,
                    'conditional_formatting': True,
                    'column_filters': True
                }
            })
        
        # Sort by priority and return target number of charts
        sorted_viz = sorted(visualizations, key=lambda x: x['priority'])
        return sorted_viz[:target_charts]
    
    def _select_primary_metric(self, numeric_columns: List[Dict], domain: str) -> Dict:
        """Select the most important numeric metric based on business domain"""
        if not numeric_columns:
            return None
            
        # Domain-specific metric prioritization
        priority_keywords = {
            'financial': ['revenue', 'profit', 'cost', 'price', 'amount', 'value', 'fee', 'fare'],
            'transportation': ['fare', 'distance', 'duration', 'rating', 'cost', 'efficiency'],
            'hr': ['salary', 'performance', 'rating', 'score', 'experience'],
            'sales': ['revenue', 'amount', 'quantity', 'volume', 'conversion'],
            'operations': ['efficiency', 'utilization', 'throughput', 'capacity']
        }
        
        keywords = priority_keywords.get(domain, priority_keywords['financial'])
        
        # Score each column based on keyword matching and data characteristics
        scored_columns = []
        for col in numeric_columns:
            score = 0
            col_name_lower = col['name'].lower()
            
            # Keyword matching
            for keyword in keywords:
                if keyword in col_name_lower:
                    score += 10
            
            # Variance-based scoring (more varied data is often more interesting)
            if 'variance' in col:
                score += min(col['variance'] / 1000, 5)  # Cap at 5 points
                
            scored_columns.append((score, col))
        
        # Return highest scoring column, or first if no scores
        if scored_columns:
            scored_columns.sort(key=lambda x: x[0], reverse=True)
            return scored_columns[0][1]
        return numeric_columns[0]
    
    def _select_secondary_metric(self, numeric_columns: List[Dict], domain: str, primary_metric: Dict) -> Dict:
        """Select a complementary secondary metric"""
        available_columns = [col for col in numeric_columns if col['name'] != primary_metric['name']]
        if not available_columns:
            return primary_metric
            
        # Look for metrics that complement the primary
        complementary_keywords = {
            'fare': ['distance', 'duration', 'rating'],
            'revenue': ['cost', 'quantity', 'volume'],
            'rating': ['count', 'volume', 'frequency'],
            'amount': ['quantity', 'rate', 'percentage']
        }
        
        primary_name = primary_metric['name'].lower()
        for keyword, complements in complementary_keywords.items():
            if keyword in primary_name:
                for col in available_columns:
                    for complement in complements:
                        if complement in col['name'].lower():
                            return col
        
        return available_columns[0]
    
    def _select_best_categorical_column(self, categorical_columns: List[Dict], domain: str) -> Dict:
        """Select the most business-relevant categorical column"""
        if not categorical_columns:
            return None
            
        # Domain-specific categorical priorities
        priority_keywords = {
            'financial': ['type', 'category', 'department', 'region', 'status'],
            'transportation': ['vehicle', 'location', 'route', 'driver', 'payment', 'status'],
            'hr': ['department', 'role', 'level', 'location', 'team'],
            'sales': ['region', 'product', 'channel', 'segment', 'status']
        }
        
        keywords = priority_keywords.get(domain, priority_keywords['financial'])
        
        # Score columns by business relevance and cardinality
        scored_columns = []
        for col in categorical_columns:
            if col['is_high_cardinality']:
                continue  # Skip high cardinality columns
                
            score = 0
            col_name_lower = col['name'].lower()
            
            # Keyword matching
            for keyword in keywords:
                if keyword in col_name_lower:
                    score += 10
            
            # Prefer moderate cardinality (2-10 categories)
            unique_count = col.get('unique_count', 0)
            if 2 <= unique_count <= 10:
                score += 5
            elif unique_count <= 15:
                score += 2
                
            scored_columns.append((score, col))
        
        if scored_columns:
            scored_columns.sort(key=lambda x: x[0], reverse=True)
            return scored_columns[0][1]
        return categorical_columns[0]
    
    def _is_suitable_for_pie_chart(self, categorical_column: Dict, df: pd.DataFrame) -> bool:
        """Determine if a categorical column is suitable for pie chart visualization"""
        unique_count = categorical_column.get('unique_count', 0)
        
        # Pie charts work best with 2-8 categories
        if not (2 <= unique_count <= 8):
            return False
            
        # Check if the distribution is not too skewed
        col_name = categorical_column['name']
        if col_name in df.columns:
            value_counts = df[col_name].value_counts()
            if len(value_counts) > 0:
                # Avoid pie charts if one category dominates (>80%)
                max_percentage = value_counts.iloc[0] / len(df)
                if max_percentage > 0.8:
                    return False
        
        return True
    
    def _find_meaningful_correlations(self, numeric_columns: List[Dict], domain: str) -> List[tuple]:
        """Find pairs of numeric columns that have meaningful business relationships"""
        meaningful_pairs = []
        
        # Domain-specific meaningful correlations
        correlation_patterns = {
            'financial': [
                ('revenue', 'cost'), ('price', 'volume'), ('fee', 'service'),
                ('amount', 'quantity'), ('rate', 'duration')
            ],
            'transportation': [
                ('fare', 'distance'), ('rating', 'performance'), ('duration', 'distance'),
                ('cost', 'distance'), ('efficiency', 'fuel')
            ],
            'hr': [
                ('salary', 'experience'), ('performance', 'rating'), ('age', 'experience'),
                ('satisfaction', 'performance')
            ]
        }
        
        patterns = correlation_patterns.get(domain, correlation_patterns['financial'])
        column_names = [col['name'].lower() for col in numeric_columns]
        
        # Find matching patterns
        for pattern1, pattern2 in patterns:
            col1_matches = [name for name in column_names if pattern1 in name]
            col2_matches = [name for name in column_names if pattern2 in name]
            
            for col1 in col1_matches:
                for col2 in col2_matches:
                    if col1 != col2:
                        meaningful_pairs.append((col1, col2))
        
        # If no meaningful patterns found, use first two columns
        if not meaningful_pairs and len(numeric_columns) >= 2:
            meaningful_pairs.append((numeric_columns[0]['name'], numeric_columns[1]['name']))
        
        return meaningful_pairs[:2]  # Limit to 2 correlation pairs
    
    def _design_layout(self, visualizations: List[Dict[str, Any]], kpis: Dict[str, Any]) -> Dict[str, Any]:
        """Design the overall dashboard layout with support for 5-8 charts"""
        
        # Calculate grid layout with intelligent row arrangement
        grid_rows = []
        current_row = []
        current_row_width = 0
        
        for viz in visualizations:
            viz_width = 2 if viz['size'] == 'full-width' else 1
            
            if current_row_width + viz_width > 2:
                # Start new row
                if current_row:
                    grid_rows.append(current_row)
                current_row = [viz]
                current_row_width = viz_width
            else:
                current_row.append(viz)
                current_row_width += viz_width
        
        if current_row:
            grid_rows.append(current_row)
        
        return {
            'title': f'{kpis.get("dashboard_title", "Business Intelligence Dashboard")}',
            'description': f'Comprehensive analysis dashboard with {len(visualizations)} key visualizations',
            'grid_layout': {
                'rows': len(grid_rows),
                'columns': 2,
                'responsive': True,
                'row_data': grid_rows
            },
            'style': {
                'theme': 'professional',
                'color_scheme': 'business',
                'spacing': 'comfortable',
                'chart_height': 'adaptive'  # Adjust height based on number of charts
            },
            'interactivity': {
                'cross_filtering': True,
                'drill_down': True,
                'export_options': True,
                'refresh_data': True
            },
            'performance': {
                'lazy_loading': len(visualizations) > 6,  # Enable lazy loading for rich dashboards
                'chart_caching': True,
                'progressive_rendering': True
            }
        }
        
        return {
            'type': 'grid',
            'columns': 2,
            'rows': grid_rows,
            'responsive': True,
            'spacing': 'medium',
            'header': {
                'title': 'Business Intelligence Dashboard',
                'subtitle': f'Key insights and performance metrics',
                'show_filters': True,
                'show_refresh': True
            },
            'footer': {
                'show_timestamp': True,
                'show_data_source': True
            }
        }
    
    def _create_dashboard_sections(self, visualizations: List[Dict[str, Any]], 
                                  kpis: Dict[str, Any], domain: str) -> List[Dict[str, Any]]:
        """Create logical sections for the dashboard"""
        sections = []
        
        # Overview section (KPIs and key metrics)
        overview_viz = [v for v in visualizations if v['type'] in ['kpi_cards', 'line'] and v['priority'] <= 2]
        if overview_viz:
            sections.append({
                'name': 'overview',
                'title': 'Executive Overview',
                'description': 'High-level performance indicators and trends',
                'visualizations': overview_viz,
                'default_expanded': True
            })
        
        # Performance section (detailed metrics)
        performance_viz = [v for v in visualizations if v['type'] in ['bar', 'pie', 'scatter'] and v['priority'] <= 3]
        if performance_viz:
            sections.append({
                'name': 'performance',
                'title': 'Performance Analysis',
                'description': 'Detailed breakdown and analysis of key metrics',
                'visualizations': performance_viz,
                'default_expanded': True
            })
        
        # Insights section (correlations and patterns)
        insights_viz = [v for v in visualizations if v['priority'] >= 4]
        if insights_viz:
            sections.append({
                'name': 'insights',
                'title': 'Business Insights',
                'description': 'Data-driven insights and detailed analysis',
                'visualizations': insights_viz,
                'default_expanded': False
            })
        
        return sections
    
    def _recommend_filters(self, df: pd.DataFrame, domain: str) -> List[Dict[str, Any]]:
        """Recommend filters for the dashboard"""
        filters = []
        
        # Date range filter (if temporal data exists)
        date_columns = df.select_dtypes(include=['datetime']).columns
        if len(date_columns) > 0:
            filters.append({
                'type': 'date_range',
                'column': date_columns[0],
                'label': 'Date Range',
                'default': 'last_30_days',
                'position': 'top'
            })
        
        # Categorical filters (for low-cardinality categories)
        categorical_columns = df.select_dtypes(include=['object']).columns
        for column in categorical_columns:
            unique_count = df[column].nunique()
            if 2 <= unique_count <= 20:  # Good filter range
                filters.append({
                    'type': 'multi_select',
                    'column': column,
                    'label': column.replace('_', ' ').title(),
                    'options': df[column].unique().tolist(),
                    'default': 'all',
                    'position': 'sidebar'
                })
        
        # Numeric range filters (for key metrics)
        numeric_columns = df.select_dtypes(include=['number']).columns
        for column in numeric_columns[:2]:  # Only first 2 numeric columns
            if df[column].nunique() > 10:  # Only if there's variation
                filters.append({
                    'type': 'range',
                    'column': column,
                    'label': f'{column.replace("_", " ").title()} Range',
                    'min': float(df[column].min()),
                    'max': float(df[column].max()),
                    'default': [float(df[column].min()), float(df[column].max())],
                    'position': 'sidebar'
                })
        
        return filters
    
    def _get_color_scheme(self, domain: str, user_preferences: Dict[str, Any] = None) -> List[str]:
        """Get appropriate color scheme for the domain"""
        if user_preferences and 'colors' in user_preferences:
            return user_preferences['colors']
        
        return self.color_schemes.get(domain, self.color_schemes['default'])
    
    def _generate_dashboard_metadata(self, df: pd.DataFrame, kpis: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """Generate metadata for the dashboard"""
        return {
            'created_at': pd.Timestamp.now().isoformat(),
            'data_source': 'uploaded_csv',
            'total_records': len(df),
            'data_columns': len(df.columns),
            'domain': domain,
            'kpi_count': len(kpis),
            'visualization_count': 0,  # Will be updated by calling function
            'refresh_interval': 'manual',
            'version': '1.0'
        }
    
    def _generate_design_recommendations(self, visualizations: List[Dict[str, Any]], domain: str) -> List[str]:
        """Generate design and usage recommendations"""
        recommendations = []
        
        # Layout recommendations
        if len(visualizations) > 8:
            recommendations.append("Consider using tabs or accordion sections to organize visualizations for better user experience.")
        
        # Visualization type recommendations
        chart_types = [v['type'] for v in visualizations]
        if 'line' not in chart_types and any('trend' in v.get('title', '').lower() for v in visualizations):
            recommendations.append("Add line charts to better show trends over time.")
        
        # Interactivity recommendations
        recommendations.append("Enable drill-down capabilities on summary charts for deeper analysis.")
        recommendations.append("Add hover tooltips to charts for detailed information display.")
        
        # Performance recommendations
        if len(visualizations) > 6:
            recommendations.append("Implement lazy loading for better dashboard performance with many visualizations.")
        
        # Domain-specific recommendations
        if domain == 'financial':
            recommendations.append("Include variance analysis charts to compare actual vs. budget/forecast.")
        elif domain == 'sales':
            recommendations.append("Add funnel charts to visualize the sales pipeline conversion process.")
        elif domain == 'marketing':
            recommendations.append("Include attribution analysis to understand campaign effectiveness.")
        
        # User experience recommendations
        recommendations.append("Implement auto-refresh functionality for real-time data updates.")
        recommendations.append("Add export capabilities for charts and data tables.")
        recommendations.append("Include contextual help tooltips for business users.")
        
        return recommendations
