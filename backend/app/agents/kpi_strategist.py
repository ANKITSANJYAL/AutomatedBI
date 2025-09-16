"""
KPI Strategist Agent for AutomatedBI
Responsible for identifying relevant KPIs and creating strategic measurements.
"""

from crewai import Agent
from typing import Dict, Any, List
import pandas as pd


class KPIStrategist:
    """Agent responsible for KPI identification and strategic measurement design"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        self.llm_config = llm_config
        
        # KPI categories and formulas
        self.kpi_categories = {
            'financial': {
                'revenue_metrics': ['total_revenue', 'revenue_growth', 'recurring_revenue'],
                'profitability': ['gross_margin', 'net_margin', 'ebitda_margin'],
                'efficiency': ['revenue_per_employee', 'cost_per_acquisition', 'roi'],
                'liquidity': ['current_ratio', 'cash_flow', 'working_capital']
            },
            'sales': {
                'performance': ['sales_revenue', 'sales_growth', 'quota_attainment'],
                'efficiency': ['conversion_rate', 'average_deal_size', 'sales_cycle_length'],
                'pipeline': ['pipeline_value', 'pipeline_velocity', 'win_rate'],
                'customer': ['customer_acquisition_cost', 'customer_lifetime_value', 'churn_rate']
            },
            'marketing': {
                'acquisition': ['cost_per_lead', 'cost_per_acquisition', 'lead_conversion_rate'],
                'engagement': ['click_through_rate', 'engagement_rate', 'bounce_rate'],
                'roi': ['return_on_ad_spend', 'marketing_roi', 'customer_lifetime_value'],
                'brand': ['brand_awareness', 'share_of_voice', 'net_promoter_score']
            },
            'operations': {
                'efficiency': ['operational_efficiency', 'capacity_utilization', 'productivity_rate'],
                'quality': ['quality_score', 'defect_rate', 'first_pass_yield'],
                'delivery': ['on_time_delivery', 'cycle_time', 'throughput'],
                'cost': ['cost_per_unit', 'cost_reduction', 'waste_percentage']
            }
        }
        
    def create_agent(self) -> Agent:
        """Create the KPI Strategist agent"""
        return Agent(
            role='KPI Strategist',
            goal='Identify relevant KPIs, design strategic measurements, and create actionable metrics that drive business decisions',
            backstory="""You are a strategic business analyst with expertise in KPI design and 
            performance measurement. You understand how to translate business objectives into 
            measurable metrics and create dashboards that drive action. Your experience spans 
            multiple industries and you know which metrics matter most for different business contexts.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm_config.get('model'),
            max_iter=3,
            memory=True
        )
    
    def identify_kpis(self, df: pd.DataFrame, domain: str, business_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Identify relevant KPIs based on data and domain
        
        Args:
            df: DataFrame to analyze
            domain: Business domain
            business_context: Additional context about the business
            
        Returns:
            Dictionary containing identified KPIs and their configurations
        """
        try:
            # Analyze available data columns
            available_metrics = self._analyze_available_metrics(df)
            
            # Get domain-specific KPI suggestions
            domain_kpis = self._get_domain_kpis(domain)
            
            # Match available data with potential KPIs
            matched_kpis = self._match_kpis_to_data(available_metrics, domain_kpis)
            
            # Calculate KPI values
            calculated_kpis = self._calculate_kpis(df, matched_kpis)
            
            # Generate KPI recommendations
            recommendations = self._generate_kpi_recommendations(calculated_kpis, domain)
            
            return {
                'identified_kpis': calculated_kpis,
                'recommended_kpis': calculated_kpis,  # For compatibility
                'available_metrics': available_metrics,
                'domain_suggestions': domain_kpis,
                'recommendations': recommendations,
                'kpi_hierarchy': self._create_kpi_hierarchy(calculated_kpis, domain)
            }
            
        except Exception as e:
            return {
                'identified_kpis': {},
                'recommended_kpis': {},
                'available_metrics': [],
                'domain_suggestions': {},
                'recommendations': [],
                'error': str(e)
            }
    
    def _analyze_available_metrics(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze available metrics in the dataset"""
        metrics = []
        
        for column in df.columns:
            dtype = df[column].dtype
            metric_info = {
                'name': column,
                'data_type': str(dtype),
                'non_null_count': df[column].count(),
                'null_percentage': (df[column].isnull().sum() / len(df)) * 100,
                'unique_count': df[column].nunique()
            }
            
            # Categorize metric type
            if pd.api.types.is_numeric_dtype(dtype):
                metric_info['metric_type'] = 'numeric'
                metric_info['min'] = float(df[column].min())
                metric_info['max'] = float(df[column].max())
                metric_info['mean'] = float(df[column].mean())
                
                # Determine likely metric category based on name
                column_lower = column.lower()
                if any(keyword in column_lower for keyword in ['revenue', 'sales', 'income', 'profit']):
                    metric_info['category'] = 'revenue'
                elif any(keyword in column_lower for keyword in ['cost', 'expense', 'spend']):
                    metric_info['category'] = 'cost'
                elif any(keyword in column_lower for keyword in ['rate', 'ratio', 'percent']):
                    metric_info['category'] = 'rate'
                else:
                    metric_info['category'] = 'general'
                    
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                metric_info['metric_type'] = 'temporal'
                metric_info['category'] = 'time'
            else:
                metric_info['metric_type'] = 'categorical'
                metric_info['category'] = 'dimension'
            
            metrics.append(metric_info)
        
        return metrics
    
    def _get_domain_kpis(self, domain: str) -> Dict[str, List[str]]:
        """Get KPI suggestions for a specific domain"""
        return self.kpi_categories.get(domain, {
            'performance': ['total_volume', 'growth_rate', 'efficiency_ratio'],
            'quality': ['accuracy_rate', 'completion_rate', 'satisfaction_score'],
            'volume': ['total_count', 'average_volume', 'throughput']
        })
    
    def _match_kpis_to_data(self, available_metrics: List[Dict[str, Any]], 
                           domain_kpis: Dict[str, List[str]]) -> Dict[str, Dict[str, Any]]:
        """Match available data columns to potential KPIs"""
        matched_kpis = {}
        
        # Create a lookup of available columns by type
        numeric_columns = [m for m in available_metrics if m['metric_type'] == 'numeric']
        
        # Try to match domain KPIs with available data
        for category, kpis in domain_kpis.items():
            for kpi in kpis:
                # Find potential columns for this KPI
                potential_columns = []
                
                # Direct name matching
                for metric in numeric_columns:
                    if any(keyword in metric['name'].lower() for keyword in kpi.split('_')):
                        potential_columns.append(metric['name'])
                
                # If no direct match, use category-based matching
                if not potential_columns:
                    category_matches = {
                        'revenue': ['revenue', 'sales', 'income'],
                        'cost': ['cost', 'expense', 'spend'],
                        'efficiency': ['rate', 'ratio', 'percent']
                    }
                    
                    if kpi in category_matches:
                        for metric in numeric_columns:
                            if any(cat in metric['name'].lower() for cat in category_matches[kpi]):
                                potential_columns.append(metric['name'])
                
                if potential_columns:
                    matched_kpis[kpi] = {
                        'category': category,
                        'potential_columns': potential_columns[:3],  # Top 3 matches
                        'calculation_type': self._get_calculation_type(kpi),
                        'priority': self._get_kpi_priority(kpi, category)
                    }
        
        return matched_kpis
    
    def _get_calculation_type(self, kpi: str) -> str:
        """Determine how to calculate the KPI"""
        if 'rate' in kpi or 'ratio' in kpi or 'percentage' in kpi:
            return 'ratio'
        elif 'growth' in kpi:
            return 'growth'
        elif 'average' in kpi or 'mean' in kpi:
            return 'average'
        elif 'total' in kpi or 'sum' in kpi:
            return 'sum'
        elif 'count' in kpi:
            return 'count'
        else:
            return 'direct'
    
    def _get_kpi_priority(self, kpi: str, category: str) -> int:
        """Assign priority to KPI (1=highest, 5=lowest)"""
        high_priority_kpis = [
            'revenue', 'sales', 'profit', 'growth', 'conversion_rate',
            'customer_acquisition_cost', 'roi', 'margin'
        ]
        
        for keyword in high_priority_kpis:
            if keyword in kpi:
                return 1
        
        if category in ['financial', 'sales']:
            return 2
        else:
            return 3
    
    def _calculate_kpis(self, df: pd.DataFrame, matched_kpis: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate actual KPI values from the data"""
        calculated_kpis = {}
        
        for kpi_name, kpi_config in matched_kpis.items():
            try:
                columns = kpi_config['potential_columns']
                calculation_type = kpi_config['calculation_type']
                category = kpi_config['category']
                
                if not columns or columns[0] not in df.columns:
                    continue
                
                primary_column = columns[0]
                column_data = df[primary_column].dropna()
                
                if len(column_data) == 0:
                    continue
                
                # Calculate KPI value based on type
                if calculation_type == 'sum':
                    value = float(column_data.sum())
                    format_type = 'currency' if any(keyword in primary_column.lower() for keyword in ['revenue', 'sales', 'cost']) else 'number'
                elif calculation_type == 'average':
                    value = float(column_data.mean())
                    format_type = 'currency' if any(keyword in primary_column.lower() for keyword in ['revenue', 'sales', 'cost']) else 'number'
                elif calculation_type == 'count':
                    value = int(len(column_data))
                    format_type = 'integer'
                elif calculation_type == 'growth' and len(column_data) > 1:
                    first_val = float(column_data.iloc[0])
                    last_val = float(column_data.iloc[-1])
                    if first_val != 0:
                        value = ((last_val - first_val) / first_val) * 100
                    else:
                        value = 0
                    format_type = 'percentage'
                else:
                    value = float(column_data.mean())
                    format_type = 'number'
                
                calculated_kpis[kpi_name] = {
                    'name': kpi_name.replace('_', ' ').title(),
                    'value': value,
                    'format': format_type,
                    'trend': self._calculate_trend(df, primary_column),
                    'category': category,
                    'priority': kpi_config['priority'],
                    'source_column': primary_column,
                    'description': f"Calculated {kpi_name.replace('_', ' ')} from {primary_column}"
                }
                
            except Exception as e:
                continue
        
        # Add fallback KPIs if not enough were calculated
        if len(calculated_kpis) < 4:
            calculated_kpis.update(self._generate_fallback_kpis(df))
        
        return calculated_kpis
    
    def _calculate_trend(self, df: pd.DataFrame, column: str) -> str:
        """Calculate trend for a column"""
        try:
            data = df[column].dropna()
            if len(data) < 2:
                return 'neutral'
            
            # Simple trend analysis
            first_half = data.iloc[:len(data)//2].mean()
            second_half = data.iloc[len(data)//2:].mean()
            
            if second_half > first_half * 1.05:
                return 'positive'
            elif second_half < first_half * 0.95:
                return 'negative'
            else:
                return 'neutral'
        except:
            return 'neutral'
    
    def _generate_fallback_kpis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate basic KPIs when domain-specific ones aren't available"""
        fallback_kpis = {}
        
        numeric_columns = df.select_dtypes(include=['number']).columns
        
        if len(numeric_columns) > 0:
            primary_metric = numeric_columns[0]
            
            fallback_kpis['total_volume'] = {
                'name': f'Total {primary_metric.replace("_", " ").title()}',
                'value': float(df[primary_metric].sum()),
                'format': 'number',
                'trend': 'neutral',
                'category': 'general',
                'priority': 2,
                'source_column': primary_metric,
                'description': f'Total sum of {primary_metric}'
            }
            
            fallback_kpis['average_value'] = {
                'name': f'Average {primary_metric.replace("_", " ").title()}',
                'value': float(df[primary_metric].mean()),
                'format': 'number',
                'trend': 'neutral',
                'category': 'general',
                'priority': 2,
                'source_column': primary_metric,
                'description': f'Average value of {primary_metric}'
            }
        
        fallback_kpis['total_records'] = {
            'name': 'Total Records',
            'value': len(df),
            'format': 'integer',
            'trend': 'neutral',
            'category': 'general',
            'priority': 3,
            'source_column': 'count',
            'description': 'Total number of data records'
        }
        
        return fallback_kpis
    
    def _generate_kpi_recommendations(self, calculated_kpis: Dict[str, Any], domain: str) -> List[str]:
        """Generate recommendations based on calculated KPIs"""
        recommendations = []
        
        if domain == 'sales':
            recommendations.extend([
                "Monitor conversion rates to identify optimization opportunities",
                "Track average deal size trends for revenue forecasting"
            ])
        elif domain == 'marketing':
            recommendations.extend([
                "Focus on cost per acquisition optimization",
                "Measure campaign ROI across different channels"
            ])
        else:
            recommendations.extend([
                "Establish baseline measurements for all KPIs",
                "Set up regular monitoring and alerting"
            ])
        
        return recommendations
    
    def _create_kpi_hierarchy(self, calculated_kpis: Dict[str, Any], domain: str) -> Dict[str, List[str]]:
        """Create a hierarchical structure for KPIs"""
        hierarchy = {
            'primary': [],
            'secondary': [],
            'operational': []
        }
        
        for kpi_name, kpi_data in calculated_kpis.items():
            priority = kpi_data.get('priority', 3)
            
            if priority == 1:
                hierarchy['primary'].append(kpi_name)
            elif priority == 2:
                hierarchy['secondary'].append(kpi_name)
            else:
                hierarchy['operational'].append(kpi_name)
        
        return hierarchy