"""
Domain Expert Agent for AutomatedBI
Responsible for identifying business domain and providing domain-specific insights.
"""

from crewai import Agent
from typing import Dict, Any, List
import pandas as pd
import re


class DomainExpert:
    """Agent responsible for domain identification and business context analysis"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        self.llm_config = llm_config
        
        # Domain patterns for identification
        self.domain_patterns = {
            'financial': [
                'revenue', 'profit', 'cost', 'price', 'amount', 'balance', 'payment',
                'transaction', 'invoice', 'budget', 'expense', 'income', 'roi', 'margin',
                'cash', 'credit', 'debit', 'account', 'financial', 'money', 'currency'
            ],
            'sales': [
                'sales', 'customer', 'order', 'product', 'quantity', 'discount',
                'deal', 'lead', 'prospect', 'pipeline', 'conversion', 'campaign',
                'channel', 'territory', 'quota', 'commission', 'client'
            ],
            'hr': [
                'employee', 'salary', 'department', 'position', 'hire', 'training',
                'performance', 'review', 'benefit', 'attendance', 'leave', 'skill',
                'experience', 'manager', 'team', 'promotion', 'recruitment'
            ],
            'marketing': [
                'campaign', 'conversion', 'click', 'impression', 'reach', 'engagement',
                'acquisition', 'retention', 'segment', 'audience', 'channel', 'brand',
                'awareness', 'lead', 'funnel', 'attribution', 'social', 'digital'
            ],
            'operations': [
                'inventory', 'supply', 'logistics', 'delivery', 'warehouse', 'stock',
                'order', 'fulfillment', 'processing', 'quality', 'production',
                'efficiency', 'capacity', 'utilization', 'workflow', 'process'
            ],
            'customer_service': [
                'ticket', 'support', 'resolution', 'satisfaction', 'complaint',
                'feedback', 'rating', 'response', 'escalation', 'case', 'query',
                'help', 'issue', 'problem', 'service', 'customer_service'
            ],
            'healthcare': [
                'patient', 'diagnosis', 'treatment', 'medical', 'hospital', 'doctor',
                'nurse', 'medication', 'symptom', 'appointment', 'clinic', 'health',
                'care', 'therapy', 'surgery', 'insurance', 'billing'
            ],
            'education': [
                'student', 'grade', 'course', 'class', 'teacher', 'school', 'university',
                'enrollment', 'graduation', 'curriculum', 'exam', 'assignment',
                'learning', 'education', 'academic', 'semester', 'subject'
            ],
            'ecommerce': [
                'order', 'cart', 'checkout', 'shipping', 'return', 'refund',
                'product', 'category', 'browse', 'search', 'wishlist', 'rating',
                'review', 'recommendation', 'payment', 'delivery', 'website'
            ],
            'manufacturing': [
                'production', 'manufacturing', 'assembly', 'quality', 'defect',
                'batch', 'machine', 'equipment', 'maintenance', 'downtime',
                'efficiency', 'output', 'yield', 'scrap', 'rework', 'capacity'
            ]
        }
        
    def create_agent(self) -> Agent:
        """Create the Domain Expert agent"""
        return Agent(
            role='Domain Expert',
            goal='Identify business domain, understand industry context, and provide domain-specific insights and recommendations',
            backstory="""You are a seasoned business domain expert with deep knowledge across multiple 
            industries including finance, sales, marketing, operations, HR, healthcare, education, 
            and more. You can quickly identify the business context of data and provide valuable 
            insights specific to that domain. Your expertise helps translate raw data into 
            meaningful business intelligence.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm_config.get('model'),
            max_iter=3,
            memory=True
        )
    
    def analyze_domain(self, df: pd.DataFrame, filename: str = "") -> Dict[str, Any]:
        """
        Main analysis method that combines domain identification and storytelling insights.
        This method creates compelling business narratives from data.
        """
        # First identify the domain
        domain_results = self.identify_domain(df, filename)
        
        # Create data story and insights
        if domain_results.get('primary_domain') != 'general':
            domain = domain_results['primary_domain']
            story_insights = self.create_data_story(domain, df, filename)
            
            # Merge the results
            domain_results.update({
                'domain_insights': story_insights,
                'analysis_type': 'comprehensive_narrative'
            })
        else:
            # Even for general data, create a story
            story_insights = self.create_general_data_story(df, filename)
            domain_results.update({
                'domain_insights': story_insights,
                'analysis_type': 'narrative'
            })
        
        return domain_results
    
    def identify_domain(self, df: pd.DataFrame, filename: str = "") -> Dict[str, Any]:
        """
        Identify the business domain of the dataset
        
        Args:
            df: DataFrame to analyze
            filename: Optional filename for additional context
            
        Returns:
            Dictionary containing domain identification results
        """
        try:
            # Analyze column names
            column_analysis = self._analyze_columns(df.columns.tolist())
            
            # Analyze filename
            filename_analysis = self._analyze_filename(filename)
            
            # Analyze sample data
            data_analysis = self._analyze_sample_data(df)
            
            # Combine analyses to determine domain
            domain_scores = self._calculate_domain_scores(
                column_analysis, filename_analysis, data_analysis
            )
            
            # Get primary domain
            primary_domain = max(domain_scores.items(), key=lambda x: x[1])
            
            # Get secondary domains (confidence > 0.3)
            secondary_domains = [
                domain for domain, score in domain_scores.items() 
                if score > 0.3 and domain != primary_domain[0]
            ]
            
            return {
                'primary_domain': primary_domain[0],
                'confidence': primary_domain[1],
                'secondary_domains': secondary_domains,
                'domain_scores': domain_scores,
                'analysis_details': {
                    'column_analysis': column_analysis,
                    'filename_analysis': filename_analysis,
                    'data_analysis': data_analysis
                }
            }
            
        except Exception as e:
            return {
                'primary_domain': 'general',
                'confidence': 0.0,
                'secondary_domains': [],
                'domain_scores': {},
                'error': f"Domain identification failed: {str(e)}"
            }
    
    def get_domain_insights(self, domain: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get domain-specific insights and recommendations
        
        Args:
            domain: Identified business domain
            df: DataFrame to analyze
            
        Returns:
            Dictionary containing domain-specific insights
        """
        insights = {
            'domain': domain,
            'key_metrics': self._get_key_metrics(domain, df),
            'common_kpis': self._get_common_kpis(domain),
            'recommended_visualizations': self._get_recommended_visualizations(domain),
            'business_questions': self._get_business_questions(domain),
            'best_practices': self._get_best_practices(domain)
        }
        
        return insights
    
    def _analyze_columns(self, columns: List[str]) -> Dict[str, float]:
        """Analyze column names to identify domain patterns"""
        domain_scores = {domain: 0.0 for domain in self.domain_patterns.keys()}
        total_columns = len(columns)
        
        if total_columns == 0:
            return domain_scores
        
        for column in columns:
            column_lower = column.lower().replace('_', ' ').replace('-', ' ')
            
            for domain, keywords in self.domain_patterns.items():
                for keyword in keywords:
                    if keyword in column_lower:
                        domain_scores[domain] += 1.0 / total_columns
                        break
        
        return domain_scores
    
    def _analyze_filename(self, filename: str) -> Dict[str, float]:
        """Analyze filename for domain clues"""
        domain_scores = {domain: 0.0 for domain in self.domain_patterns.keys()}
        
        if not filename:
            return domain_scores
        
        filename_lower = filename.lower().replace('_', ' ').replace('-', ' ')
        
        for domain, keywords in self.domain_patterns.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    domain_scores[domain] += 0.5
                    break
        
        return domain_scores
    
    def _analyze_sample_data(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze sample data values for domain patterns"""
        domain_scores = {domain: 0.0 for domain in self.domain_patterns.keys()}
        
        # Sample a few rows to analyze content
        sample_size = min(5, len(df))
        if sample_size == 0:
            return domain_scores
        
        sample_df = df.head(sample_size)
        
        # Convert all values to strings and check for patterns
        for column in sample_df.columns:
            values = sample_df[column].astype(str).str.lower()
            
            for domain, keywords in self.domain_patterns.items():
                for keyword in keywords:
                    if values.str.contains(keyword, na=False).any():
                        domain_scores[domain] += 0.2
                        break
        
        return domain_scores
    
    def _calculate_domain_scores(self, column_analysis: Dict[str, float], 
                                filename_analysis: Dict[str, float],
                                data_analysis: Dict[str, float]) -> Dict[str, float]:
        """Combine different analyses to calculate final domain scores"""
        combined_scores = {}
        
        for domain in self.domain_patterns.keys():
            # Weighted combination of different analyses
            score = (
                column_analysis.get(domain, 0) * 0.5 +  # Columns are most important
                filename_analysis.get(domain, 0) * 0.3 +  # Filename is moderately important
                data_analysis.get(domain, 0) * 0.2  # Data content is least important
            )
            combined_scores[domain] = round(score, 3)
        
        return combined_scores
    
    def _get_key_metrics(self, domain: str, df: pd.DataFrame) -> List[str]:
        """Get key metrics typically tracked in this domain"""
        # Identify potential metrics in the data based on domain
        potential_metrics = []
        
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        
        domain_metric_mapping = {
            'financial': ['revenue', 'profit', 'cost', 'margin', 'roi'],
            'sales': ['sales_amount', 'quantity', 'conversion_rate', 'deal_size'],
            'marketing': ['conversion_rate', 'ctr', 'cost_per_acquisition', 'roas'],
            'hr': ['headcount', 'turnover_rate', 'satisfaction_score', 'productivity'],
            'operations': ['efficiency', 'utilization', 'downtime', 'quality_score'],
            'customer_service': ['resolution_time', 'satisfaction_rating', 'first_call_resolution'],
            'ecommerce': ['order_value', 'cart_abandonment', 'return_rate', 'customer_lifetime_value']
        }
        
        expected_metrics = domain_metric_mapping.get(domain, [])
        
        # Find matching columns
        for metric in expected_metrics:
            for column in df.columns:
                if metric.lower() in column.lower():
                    potential_metrics.append(column)
                    break
        
        # Add all numeric columns as potential metrics
        potential_metrics.extend(numeric_columns[:5])  # Limit to top 5
        
        return list(set(potential_metrics))
    
    def _get_common_kpis(self, domain: str) -> List[str]:
        """Get common KPIs for the identified domain"""
        kpi_mapping = {
            'financial': [
                'Revenue Growth Rate', 'Gross Profit Margin', 'Net Profit Margin',
                'Return on Investment (ROI)', 'Cash Flow', 'Debt-to-Equity Ratio'
            ],
            'sales': [
                'Sales Revenue', 'Conversion Rate', 'Average Deal Size',
                'Sales Cycle Length', 'Customer Acquisition Cost', 'Sales Growth Rate'
            ],
            'marketing': [
                'Cost Per Acquisition (CPA)', 'Return on Ad Spend (ROAS)',
                'Click-Through Rate (CTR)', 'Conversion Rate', 'Brand Awareness', 'Lead Quality Score'
            ],
            'hr': [
                'Employee Turnover Rate', 'Time to Hire', 'Employee Satisfaction Score',
                'Training Hours per Employee', 'Productivity Rate', 'Absenteeism Rate'
            ],
            'operations': [
                'Operational Efficiency', 'Capacity Utilization', 'Quality Score',
                'On-Time Delivery Rate', 'Inventory Turnover', 'Cost per Unit'
            ],
            'customer_service': [
                'Customer Satisfaction Score (CSAT)', 'First Call Resolution Rate',
                'Average Resolution Time', 'Net Promoter Score (NPS)', 'Ticket Volume', 'Agent Productivity'
            ]
        }
        
        return kpi_mapping.get(domain, ['Revenue', 'Growth Rate', 'Efficiency', 'Customer Satisfaction'])
    
    def _get_recommended_visualizations(self, domain: str) -> List[str]:
        """Get recommended visualization types for the domain"""
        viz_mapping = {
            'financial': ['Line Chart (Trends)', 'Waterfall Chart (P&L)', 'Pie Chart (Cost Breakdown)', 'Bar Chart (Comparisons)'],
            'sales': ['Funnel Chart (Pipeline)', 'Line Chart (Sales Trends)', 'Bar Chart (Performance)', 'Heat Map (Territory)'],
            'marketing': ['Funnel Chart (Conversion)', 'Line Chart (Campaign Performance)', 'Pie Chart (Channel Mix)', 'Scatter Plot (ROI)'],
            'hr': ['Bar Chart (Headcount)', 'Line Chart (Turnover)', 'Pie Chart (Department Distribution)', 'Gauge Chart (Satisfaction)'],
            'operations': ['Line Chart (Production)', 'Bar Chart (Efficiency)', 'Heat Map (Capacity)', 'Control Chart (Quality)'],
            'customer_service': ['Line Chart (Volume)', 'Bar Chart (Resolution Time)', 'Pie Chart (Issue Types)', 'Gauge Chart (Satisfaction)']
        }
        
        return viz_mapping.get(domain, ['Bar Chart', 'Line Chart', 'Pie Chart', 'Scatter Plot'])
    
    def _get_business_questions(self, domain: str) -> List[str]:
        """Get relevant business questions for the domain"""
        questions_mapping = {
            'financial': [
                'What are the main revenue drivers?',
                'How is profitability trending over time?',
                'Which cost categories need attention?',
                'What is the return on investment for key initiatives?'
            ],
            'sales': [
                'Which products/services generate the most revenue?',
                'How is the sales pipeline performing?',
                'What factors influence conversion rates?',
                'Which sales channels are most effective?'
            ],
            'marketing': [
                'Which campaigns deliver the best ROI?',
                'How effective are different marketing channels?',
                'What is the customer acquisition cost trend?',
                'Which audience segments respond best?'
            ],
            'hr': [
                'What is the employee turnover trend?',
                'Which departments have the highest satisfaction?',
                'How effective are training programs?',
                'What factors influence employee productivity?'
            ]
        }
        
        return questions_mapping.get(domain, [
            'What are the key trends in the data?',
            'Which factors drive performance?',
            'Where are the biggest opportunities?',
            'What patterns need attention?'
        ])
    
    def _get_best_practices(self, domain: str) -> List[str]:
        """Get domain-specific best practices for data analysis"""
        practices_mapping = {
            'financial': [
                'Compare metrics across time periods',
                'Calculate year-over-year growth rates',
                'Monitor cash flow trends',
                'Track profitability by business unit'
            ],
            'sales': [
                'Segment performance by product/region',
                'Track pipeline velocity',
                'Monitor customer lifetime value',
                'Analyze seasonal patterns'
            ],
            'marketing': [
                'Measure multi-touch attribution',
                'Track customer journey stages',
                'Monitor campaign performance by channel',
                'Calculate return on marketing investment'
            ]
        }
        
        return practices_mapping.get(domain, [
            'Focus on actionable insights',
            'Compare against benchmarks',
            'Track trends over time',
            'Segment data for deeper insights'
        ])
    
    def create_data_story(self, domain: str, df: pd.DataFrame, filename: str = "") -> Dict[str, Any]:
        """Create compelling business narrative from data"""
        
        # Analyze data characteristics
        total_records = len(df)
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Get key statistics
        key_insights = self._extract_key_insights(df, domain)
        trends = self._identify_trends(df, date_cols, numeric_cols)
        patterns = self._find_patterns(df, domain)
        
        # Create narrative structure
        story = {
            "executive_summary": self._create_executive_summary(domain, key_insights, filename),
            "key_findings": self._create_key_findings(key_insights, trends, patterns),
            "business_impact": self._assess_business_impact(domain, key_insights),
            "recommendations": self._generate_recommendations(domain, patterns, trends),
            "data_narrative": self._build_narrative(domain, df, key_insights),
            "performance_indicators": self._identify_performance_indicators(domain, numeric_cols),
            "visual_story": self._design_visual_story(domain, key_insights, trends),
            "next_steps": self._suggest_next_steps(domain, patterns)
        }
        
        return story
    
    def create_general_data_story(self, df: pd.DataFrame, filename: str = "") -> Dict[str, Any]:
        """Create story for general/unidentified domain data"""
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        return {
            "executive_summary": f"Analysis of {filename or 'uploaded dataset'} reveals {len(df)} records with {len(df.columns)} attributes spanning {len(categorical_cols)} categorical and {len(numeric_cols)} numerical dimensions.",
            "key_findings": [
                f"Dataset contains {len(df):,} total records",
                f"Primary dimensions: {', '.join(categorical_cols[:3]) if categorical_cols else 'Numerical data'}",
                f"Key metrics: {', '.join(numeric_cols[:3]) if numeric_cols else 'Categorical data'}"
            ],
            "data_narrative": "This dataset presents opportunities for comprehensive analysis across multiple dimensions, with potential for uncovering hidden patterns and relationships.",
            "recommendations": ["Explore correlations between key variables", "Identify outliers and anomalies", "Consider temporal analysis if dates are present"]
        }
    
    def _extract_key_insights(self, df: pd.DataFrame, domain: str) -> Dict[str, Any]:
        """Extract domain-specific key insights from data"""
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        insights = {}
        
        for col in numeric_cols[:5]:  # Top 5 numeric columns
            col_data = df[col].dropna()
            if len(col_data) > 0:
                insights[col] = {
                    'mean': col_data.mean(),
                    'median': col_data.median(),
                    'std': col_data.std(),
                    'min': col_data.min(),
                    'max': col_data.max(),
                    'trend': 'increasing' if col_data.iloc[-1] > col_data.iloc[0] else 'decreasing' if len(col_data) > 1 else 'stable'
                }
        
        return insights
    
    def _identify_trends(self, df: pd.DataFrame, date_cols: List[str], numeric_cols: List[str]) -> List[str]:
        """Identify trends in the data"""
        trends = []
        
        if date_cols and numeric_cols:
            for date_col in date_cols[:1]:  # First date column
                for num_col in numeric_cols[:3]:  # First 3 numeric columns
                    try:
                        df_sorted = df.sort_values(date_col)
                        values = df_sorted[num_col].dropna()
                        if len(values) > 5:
                            recent_avg = values.tail(len(values)//3).mean()
                            early_avg = values.head(len(values)//3).mean()
                            
                            if recent_avg > early_avg * 1.1:
                                trends.append(f"{num_col} shows strong upward trend over time")
                            elif recent_avg < early_avg * 0.9:
                                trends.append(f"{num_col} shows declining trend over time")
                            else:
                                trends.append(f"{num_col} remains relatively stable over time")
                    except:
                        continue
        
        return trends
    
    def _find_patterns(self, df: pd.DataFrame, domain: str) -> List[str]:
        """Find domain-specific patterns"""
        patterns = []
        
        # High-level pattern detection
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # Category distribution patterns
        for col in categorical_cols[:2]:
            value_counts = df[col].value_counts()
            if len(value_counts) > 1:
                top_category = value_counts.index[0]
                top_percentage = (value_counts.iloc[0] / len(df)) * 100
                patterns.append(f"{top_category} dominates {col} category with {top_percentage:.1f}% share")
        
        # Correlation patterns
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            strong_corrs = []
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        relationship = "strong positive" if corr_val > 0 else "strong negative"
                        strong_corrs.append(f"{relationship} correlation between {numeric_cols[i]} and {numeric_cols[j]}")
            patterns.extend(strong_corrs[:3])
        
        return patterns
    
    def _create_executive_summary(self, domain: str, insights: Dict[str, Any], filename: str) -> str:
        """Create executive summary"""
        
        domain_context = {
            'sales': f"Sales performance analysis of {filename or 'dataset'} reveals",
            'financial': f"Financial analysis of {filename or 'dataset'} indicates",
            'hr': f"Human resources analysis of {filename or 'dataset'} shows", 
            'marketing': f"Marketing performance analysis of {filename or 'dataset'} demonstrates",
            'operations': f"Operational analysis of {filename or 'dataset'} highlights"
        }
        
        prefix = domain_context.get(domain, f"Business analysis of {filename or 'dataset'} reveals")
        
        key_count = len(insights)
        summary = f"{prefix} {key_count} key performance indicators with varying patterns of growth and stability. "
        
        if insights:
            first_metric = list(insights.keys())[0]
            first_data = insights[first_metric]
            summary += f"Primary metric {first_metric} shows {first_data.get('trend', 'stable')} performance patterns."
        
        return summary
    
    def _create_key_findings(self, insights: Dict[str, Any], trends: List[str], patterns: List[str]) -> List[str]:
        """Create key findings list"""
        findings = []
        
        # From insights
        for metric, data in list(insights.items())[:3]:
            if data.get('trend') == 'increasing':
                findings.append(f"{metric} demonstrates positive growth trajectory")
            elif data.get('trend') == 'decreasing':
                findings.append(f"{metric} shows declining performance requiring attention")
            else:
                findings.append(f"{metric} maintains stable performance levels")
        
        # Add trend findings
        findings.extend(trends[:2])
        
        # Add pattern findings
        findings.extend(patterns[:2])
        
        return findings[:6]  # Limit to 6 key findings
    
    def _assess_business_impact(self, domain: str, insights: Dict[str, Any]) -> str:
        """Assess business impact based on domain"""
        
        impact_templates = {
            'sales': "Revenue performance and sales velocity metrics indicate {impact_level} business health with opportunities for {focus_area}",
            'financial': "Financial indicators suggest {impact_level} fiscal performance with emphasis needed on {focus_area}",
            'hr': "Workforce metrics demonstrate {impact_level} organizational health requiring attention to {focus_area}",
            'marketing': "Marketing performance metrics reveal {impact_level} campaign effectiveness with potential to optimize {focus_area}",
            'operations': "Operational indicators show {impact_level} efficiency levels with improvement opportunities in {focus_area}"
        }
        
        # Determine impact level based on trends
        positive_trends = sum(1 for data in insights.values() if data.get('trend') == 'increasing')
        total_metrics = len(insights)
        
        if total_metrics == 0:
            impact_level = "stable"
            focus_area = "data collection and monitoring"
        elif positive_trends / total_metrics > 0.6:
            impact_level = "strong"
            focus_area = "scaling successful initiatives"
        elif positive_trends / total_metrics > 0.3:
            impact_level = "moderate"
            focus_area = "optimizing underperforming areas"
        else:
            impact_level = "challenging"
            focus_area = "strategic intervention and improvement"
        
        template = impact_templates.get(domain, "Business metrics indicate {impact_level} performance with focus needed on {focus_area}")
        return template.format(impact_level=impact_level, focus_area=focus_area)
    
    def _generate_recommendations(self, domain: str, patterns: List[str], trends: List[str]) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        domain_recs = {
            'sales': [
                "Focus on high-performing channels and customer segments",
                "Implement pipeline optimization strategies",
                "Develop targeted retention programs for key accounts"
            ],
            'financial': [
                "Implement cost optimization initiatives in underperforming areas",
                "Enhance financial monitoring and forecasting capabilities",
                "Evaluate investment opportunities in growth areas"
            ],
            'hr': [
                "Develop talent retention strategies for critical roles",
                "Implement performance improvement programs",
                "Enhance employee engagement and satisfaction initiatives"
            ]
        }
        
        # Add domain-specific recommendations
        recommendations.extend(domain_recs.get(domain, [
            "Implement data-driven decision making processes",
            "Establish regular performance monitoring",
            "Develop targeted improvement strategies"
        ])[:2])
        
        # Add pattern-based recommendations
        if any("declining" in trend for trend in trends):
            recommendations.append("Prioritize intervention strategies for declining metrics")
        
        if any("correlation" in pattern for pattern in patterns):
            recommendations.append("Leverage identified correlations for predictive insights")
        
        return recommendations[:4]
    
    def _build_narrative(self, domain: str, df: pd.DataFrame, insights: Dict[str, Any]) -> str:
        """Build compelling data narrative"""
        
        total_records = len(df)
        time_span = "the analyzed period"
        
        # Try to identify time span
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if date_cols:
            try:
                dates = pd.to_datetime(df[date_cols[0]], errors='coerce').dropna()
                if len(dates) > 1:
                    span_days = (dates.max() - dates.min()).days
                    if span_days > 365:
                        time_span = f"over {span_days//365} years"
                    elif span_days > 30:
                        time_span = f"over {span_days//30} months"
                    else:
                        time_span = f"over {span_days} days"
            except:
                pass
        
        narrative = f"Our analysis of {total_records:,} records {time_span} reveals a complex business landscape with multiple performance indicators. "
        
        if insights:
            best_performing = max(insights.keys(), key=lambda k: insights[k].get('mean', 0))
            narrative += f"The standout performer is {best_performing}, which demonstrates strong operational significance. "
            
            trends_summary = [data.get('trend', 'stable') for data in insights.values()]
            positive_count = trends_summary.count('increasing')
            
            if positive_count > len(trends_summary) / 2:
                narrative += "Overall trends point toward positive momentum across key metrics, "
                narrative += "suggesting effective operational strategies and market positioning."
            else:
                narrative += "Mixed performance patterns indicate areas requiring strategic attention, "
                narrative += "with opportunities for optimization and improvement."
        
        return narrative
    
    def _identify_performance_indicators(self, domain: str, numeric_cols: List[str]) -> List[Dict[str, str]]:
        """Identify key performance indicators"""
        
        domain_kpis = {
            'sales': ['revenue', 'conversion', 'deal_size', 'pipeline', 'customer'],
            'financial': ['profit', 'margin', 'cost', 'revenue', 'cash'],
            'hr': ['satisfaction', 'turnover', 'productivity', 'training', 'performance'],
            'marketing': ['acquisition', 'engagement', 'conversion', 'reach', 'roi'],
            'operations': ['efficiency', 'quality', 'delivery', 'utilization', 'capacity']
        }
        
        relevant_kpis = domain_kpis.get(domain, ['performance', 'efficiency', 'quality'])
        
        indicators = []
        for col in numeric_cols[:6]:
            col_lower = col.lower()
            kpi_type = next((kpi for kpi in relevant_kpis if kpi in col_lower), 'operational')
            
            indicators.append({
                'name': col,
                'type': kpi_type,
                'importance': 'high' if any(kpi in col_lower for kpi in relevant_kpis[:3]) else 'medium'
            })
        
        return indicators
    
    def _design_visual_story(self, domain: str, insights: Dict[str, Any], trends: List[str]) -> Dict[str, Any]:
        """Design visual storytelling elements"""
        
        return {
            'color_theme': self._get_domain_colors(domain),
            'layout_priority': self._get_layout_priority(insights),
            'visual_hierarchy': self._define_visual_hierarchy(insights, trends),
            'storytelling_flow': self._create_storytelling_flow(domain)
        }
    
    def _get_domain_colors(self, domain: str) -> Dict[str, str]:
        """Get domain-appropriate color schemes"""
        
        color_schemes = {
            'financial': {'primary': '#2E8B57', 'secondary': '#32CD32', 'accent': '#228B22'},  # Green tones
            'sales': {'primary': '#4169E1', 'secondary': '#1E90FF', 'accent': '#0000FF'},     # Blue tones
            'hr': {'primary': '#FF6347', 'secondary': '#FF7F50', 'accent': '#FF4500'},        # Orange tones
            'marketing': {'primary': '#9932CC', 'secondary': '#BA55D3', 'accent': '#8A2BE2'}, # Purple tones
            'operations': {'primary': '#708090', 'secondary': '#778899', 'accent': '#696969'}  # Gray tones
        }
        
        return color_schemes.get(domain, {'primary': '#3B82F6', 'secondary': '#10B981', 'accent': '#F59E0B'})
    
    def _get_layout_priority(self, insights: Dict[str, Any]) -> List[str]:
        """Define layout priority based on data importance"""
        
        if not insights:
            return ['overview', 'trends', 'details']
        
        # Sort metrics by importance (using standard deviation as proxy for variability/interest)
        sorted_metrics = sorted(insights.items(), key=lambda x: x[1].get('std', 0), reverse=True)
        
        priority = ['executive_summary']
        priority.extend([metric for metric, _ in sorted_metrics[:3]])
        priority.extend(['patterns', 'recommendations'])
        
        return priority
    
    def _define_visual_hierarchy(self, insights: Dict[str, Any], trends: List[str]) -> Dict[str, str]:
        """Define visual hierarchy for dashboard elements"""
        
        return {
            'hero_metric': list(insights.keys())[0] if insights else 'primary_kpi',
            'supporting_metrics': list(insights.keys())[1:4] if len(insights) > 1 else [],
            'trend_indicators': 'prominent' if trends else 'subtle',
            'detail_level': 'high' if len(insights) > 3 else 'medium'
        }
    
    def _create_storytelling_flow(self, domain: str) -> List[str]:
        """Create narrative flow for dashboard"""
        
        flows = {
            'sales': ['performance_overview', 'pipeline_health', 'customer_insights', 'recommendations'],
            'financial': ['financial_summary', 'profitability_analysis', 'cost_patterns', 'strategic_outlook'],
            'hr': ['workforce_overview', 'performance_metrics', 'engagement_insights', 'development_opportunities'],
            'marketing': ['campaign_performance', 'audience_insights', 'conversion_analysis', 'optimization_opportunities'],
            'operations': ['operational_overview', 'efficiency_metrics', 'quality_indicators', 'improvement_areas']
        }
        
        return flows.get(domain, ['data_overview', 'key_insights', 'patterns_analysis', 'action_items'])
    
    def _suggest_next_steps(self, domain: str, patterns: List[str]) -> List[str]:
        """Suggest concrete next steps"""
        
        next_steps = []
        
        domain_steps = {
            'sales': [
                "Conduct deep-dive analysis of top-performing segments",
                "Implement A/B testing for underperforming channels",
                "Develop customer journey optimization strategy"
            ],
            'financial': [
                "Perform variance analysis against budget targets",
                "Implement cost center performance monitoring",
                "Develop financial forecasting models"
            ],
            'hr': [
                "Conduct employee satisfaction survey analysis",
                "Implement performance correlation studies",
                "Develop retention prediction models"
            ]
        }
        
        next_steps.extend(domain_steps.get(domain, [
            "Establish baseline metrics and KPI tracking",
            "Implement regular data quality monitoring",
            "Develop predictive analytics capabilities"
        ])[:2])
        
        # Add pattern-specific steps
        if any("correlation" in pattern for pattern in patterns):
            next_steps.append("Develop correlation-based predictive models")
        
        if any("dominates" in pattern for pattern in patterns):
            next_steps.append("Analyze concentration risk and diversification opportunities")
        
        return next_steps[:4]
