"""
Analysis Service for AutomatedBI
Orchestrates AI agents to analyze uploaded datasets
"""

import os
import logging
import warnings
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

# Suppress Google Cloud and gRPC warnings
import logging
logging.getLogger('google.auth').setLevel(logging.ERROR)
logging.getLogger('google.cloud').setLevel(logging.ERROR)
logging.getLogger('grpc').setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=UserWarning, module="google.*")

from app.models import DatasetAnalysis, DataPoint, ProcessingStatus
from app import db
from app.utils.json_serializer import prepare_for_jsonb
from app.agents.data_quality_analyst import DataQualityAnalyst
from app.agents.domain_expert import DomainExpert
from app.agents.kpi_strategist import KPIStrategist
from app.agents.dashboard_designer import DashboardDesigner

# Configure logging
logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for orchestrating dataset analysis using AI agents"""
    
    def __init__(self):
        """Initialize the analysis service with AI agents"""
        # Configure LLM for agents
        import google.generativeai as genai
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.warning("GEMINI_API_KEY not found, using placeholder analysis")
            self.llm = None
        else:
            genai.configure(api_key=api_key)
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.3,
                max_tokens=2048
            )
        
        # Initialize AI agents
        if self.llm:
            try:
                self.data_quality_analyst = DataQualityAnalyst({'model': self.llm})
                self.domain_expert = DomainExpert({'model': self.llm})
                self.kpi_strategist = KPIStrategist({'model': self.llm})
                self.dashboard_designer = DashboardDesigner({'model': self.llm})
                logger.info("AI agents initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize AI agents: {str(e)}")
                self.llm = None
        
        if not self.llm:
            logger.warning("Running without AI agents - using placeholder analysis")
        
    def analyze_dataset(self, analysis_id: str, file_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of uploaded dataset
        
        Args:
            analysis_id: ID of existing DatasetAnalysis record
            file_path: Path to the uploaded file
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Get existing analysis record
            analysis_record = DatasetAnalysis.query.get(analysis_id)
            if not analysis_record:
                raise ValueError(f"Analysis record {analysis_id} not found")
                
            logger.info(f"Starting analysis for file: {analysis_record.original_filename}")
            
            # Update status to processing
            analysis_record.status = ProcessingStatus.PROCESSING
            analysis_record.processing_started_at = datetime.utcnow()
            db.session.commit()
            
            # Load and validate data
            df = self._load_data(file_path)
            if df is None or df.empty:
                return self._handle_analysis_error(analysis_record, "Failed to load data or data is empty")
            
            # Store data points
            self._store_data_points(analysis_record.id, df)
            
            # Update basic info
            analysis_record.row_count = len(df)
            analysis_record.column_count = len(df.columns)
            
            # Run AI analysis
            analysis_results = self._run_ai_analysis(df, analysis_record.original_filename)
            
            # Update analysis record with results
            self._update_analysis_record(analysis_record, analysis_results)
            
            # Mark as completed
            analysis_record.status = ProcessingStatus.COMPLETED
            analysis_record.processing_completed_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Analysis completed successfully for file: {analysis_record.original_filename}")
            
            return {
                'success': True,
                'analysis_id': str(analysis_record.id),
                'results': analysis_results
            }
            
        except Exception as e:
            logger.error(f"Analysis failed for file {analysis_record.original_filename if 'analysis_record' in locals() else 'unknown'}: {str(e)}")
            if 'analysis_record' in locals():
                return self._handle_analysis_error(analysis_record, str(e))
            return {'success': False, 'error': str(e)}
    
    def _create_analysis_record(self, filename: str, original_filename: str, file_size: int) -> DatasetAnalysis:
        """Create initial analysis record in database"""
        try:
            analysis = DatasetAnalysis(
                filename=filename,
                original_filename=original_filename,
                file_size=file_size,
                status='pending'
            )
            db.session.add(analysis)
            db.session.commit()
            return analysis
        except SQLAlchemyError as e:
            logger.error(f"Failed to create analysis record: {str(e)}")
            db.session.rollback()
            raise
    
    def _load_data(self, file_path: str) -> Optional[pd.DataFrame]:
        """Load data from file into pandas DataFrame"""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                logger.error(f"Unsupported file format: {file_extension}")
                return None
            
            # Basic data cleaning
            df = df.dropna(how='all')  # Remove completely empty rows
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Remove unnamed columns
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to load data from {file_path}: {str(e)}")
            return None
    
    def _store_data_points(self, analysis_id: str, df: pd.DataFrame) -> None:
        """Store data points in database"""
        try:
            # Limit to first 1000 rows for performance
            sample_df = df.head(1000)
            
            data_points = []
            for idx, row in sample_df.iterrows():
                # Convert the row to dict and clean NaN values
                row_data = row.to_dict()
                cleaned_data = prepare_for_jsonb(row_data)
                
                data_point = DataPoint(
                    dataset_id=analysis_id,
                    row_index=int(idx),
                    data=cleaned_data
                )
                data_points.append(data_point)
            
            db.session.bulk_save_objects(data_points)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to store data points: {str(e)}")
            db.session.rollback()
    
    def _run_ai_analysis(self, df: pd.DataFrame, filename: str) -> Dict[str, Any]:
        """Run AI analysis using all agents"""
        results = {}
        
        try:
            if self.llm:
                # Data Quality Analysis using AI agent
                logger.info("Running AI-powered data quality analysis...")
                try:
                    quality_results = self.data_quality_analyst.analyze_data_quality(df)
                    results['data_quality'] = quality_results
                except Exception as e:
                    logger.error(f"Data quality analysis failed: {str(e)}")
                    quality_results = self._placeholder_data_quality_analysis(df)
                    results['data_quality'] = quality_results
                
                # Domain Expert Analysis using AI agent
                logger.info("Running AI-powered domain identification...")
                try:
                    domain_results = self.domain_expert.analyze_domain(df, filename)
                    results['domain_analysis'] = domain_results
                    domain = domain_results.get('primary_domain', 'general')
                except Exception as e:
                    logger.error(f"Domain analysis failed: {str(e)}")
                    domain_results = {'primary_domain': 'general', 'confidence': 0.0}
                    results['domain_analysis'] = domain_results
                    domain = 'general'
                
                # KPI Strategy Analysis using AI agent
                logger.info("Running AI-powered KPI identification...")
                try:
                    kpi_results = self.kpi_strategist.identify_kpis(df, domain, domain_results)
                    results['kpi_analysis'] = kpi_results
                except Exception as e:
                    logger.error(f"KPI analysis failed: {str(e)}")
                    kpi_results = {'recommended_kpis': {}}
                    results['kpi_analysis'] = kpi_results
                
                # Dashboard Design using AI agent
                logger.info("Creating AI-powered dashboard design...")
                try:
                    dashboard_results = self.dashboard_designer.design_dashboard(
                        df, kpi_results.get('recommended_kpis', {}), domain, quality_results
                    )
                    results['dashboard_design'] = dashboard_results
                except Exception as e:
                    logger.error(f"Dashboard design failed: {str(e)}")
                    dashboard_results = self._placeholder_dashboard_design(df)
                    results['dashboard_design'] = dashboard_results
                
                # Generate business insights using AI
                try:
                    results['business_insights'] = self._generate_ai_business_insights(
                        quality_results, domain_results, kpi_results, dashboard_results
                    )
                except Exception as e:
                    logger.error(f"Business insights generation failed: {str(e)}")
                    results['business_insights'] = self._placeholder_business_insights()
                
                logger.info("AI analysis completed successfully")
            else:
                # Fallback to placeholder analysis
                logger.warning("Using placeholder analysis - AI agents not available")
                quality_results = self._placeholder_data_quality_analysis(df)
                results['data_quality'] = quality_results
                
                domain_results = self._placeholder_domain_analysis(df, filename)
                results['domain_analysis'] = domain_results
                
                domain = domain_results.get('primary_domain', 'general')
                
                kpi_results = self._placeholder_kpi_analysis(df, domain)
                results['kpi_analysis'] = kpi_results
                
                dashboard_results = self._placeholder_dashboard_design(
                    df, kpi_results.get('identified_kpis', {}), domain
                )
                results['dashboard_design'] = dashboard_results
                
                results['business_insights'] = self._generate_business_insights(
                    quality_results, domain_results, kpi_results
                )
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            # Fallback to placeholder analysis on error
            quality_results = self._placeholder_data_quality_analysis(df)
            results['data_quality'] = quality_results
            
            domain_results = self._placeholder_domain_analysis(df, filename)
            results['domain_analysis'] = domain_results
            
            domain = domain_results.get('primary_domain', 'general')
            
            kpi_results = self._placeholder_kpi_analysis(df, domain)
            results['kpi_analysis'] = kpi_results
            
            dashboard_results = self._placeholder_dashboard_design(
                df, kpi_results.get('identified_kpis', {}), domain
            )
            results['dashboard_design'] = dashboard_results
            
            results['business_insights'] = self._generate_business_insights(
                quality_results, domain_results, kpi_results
            )
            results['error'] = str(e)
        
        return results
    
    def _generate_business_insights(self, quality_results: Dict, domain_results: Dict, kpi_results: Dict) -> Dict[str, Any]:
        """Generate high-level business insights"""
        insights = {
            'summary': [],
            'recommendations': [],
            'key_findings': []
        }
        
        try:
            # Data quality insights
            if quality_results.get('recommendations'):
                insights['summary'].append(f"Data quality analysis identified {len(quality_results['recommendations'])} areas for improvement")
                insights['recommendations'].extend(quality_results['recommendations'][:3])  # Top 3
            
            # Domain insights
            domain = domain_results.get('primary_domain', 'unknown')
            confidence = domain_results.get('confidence', 0)
            insights['key_findings'].append(f"Dataset identified as {domain.replace('_', ' ').title()} domain with {confidence:.1%} confidence")
            
            # KPI insights
            identified_kpis = kpi_results.get('identified_kpis', {})
            if identified_kpis:
                insights['key_findings'].append(f"Identified {len(identified_kpis)} relevant KPIs for analysis")
                insights['recommendations'].extend(kpi_results.get('recommendations', [])[:2])  # Top 2
            
            # Overall summary
            if not insights['summary']:
                insights['summary'].append("Analysis completed successfully with actionable insights generated")
                
        except Exception as e:
            logger.error(f"Failed to generate business insights: {str(e)}")
            insights['error'] = str(e)
        
        return insights
    
    def _generate_ai_business_insights(self, quality_results: Dict, domain_results: Dict, 
                                     kpi_results: Dict, dashboard_results: Dict) -> Dict[str, Any]:
        """Generate AI-powered business insights using Gemini"""
        insights = {
            'summary': [],
            'recommendations': [],
            'key_findings': [],
            'ai_generated': True
        }
        
        try:
            if not self.llm:
                return self._generate_business_insights(quality_results, domain_results, kpi_results)
            
            # Prepare context for AI
            context = f"""
            Data Quality Results: {quality_results}
            Domain Analysis: {domain_results}
            KPI Analysis: {kpi_results}
            Dashboard Design: {dashboard_results}
            """
            
            # Generate AI insights
            insight_prompt = f"""
            Based on the following data analysis results, provide comprehensive business insights:
            
            {context}
            
            Please provide:
            1. Executive Summary (2-3 key points)
            2. Strategic Recommendations (3-4 actionable items)
            3. Critical Findings (3-5 important discoveries)
            
            Format your response as JSON with keys: summary, recommendations, key_findings
            Each should be an array of strings.
            """
            
            response = self.llm.invoke(insight_prompt)
            
            # Parse AI response
            import json
            try:
                ai_insights = json.loads(response.content)
                insights.update(ai_insights)
            except json.JSONDecodeError:
                # Fallback to manual parsing if JSON fails
                insights['summary'] = [response.content[:500] + "..."]
                insights['recommendations'] = ["Review AI-generated insights for detailed recommendations"]
                insights['key_findings'] = ["AI analysis completed - check full response"]
                
        except Exception as e:
            logger.error(f"AI insight generation failed: {str(e)}")
            # Fallback to standard insights
            return self._generate_business_insights(quality_results, domain_results, kpi_results)
        
        return insights
    
    # Remove the old _make_json_serializable method since we're using prepare_for_jsonb now
    
    def _update_analysis_record(self, analysis_record: DatasetAnalysis, results: Dict[str, Any]) -> None:
        """Update analysis record with results"""
        try:
            # Extract and update individual fields
            domain_analysis = results.get('domain_analysis', {})
            
            analysis_record.domain_classification = domain_analysis.get('primary_domain')
            analysis_record.confidence_score = float(domain_analysis.get('confidence_score', 0.0))
            
            # Store analysis results as JSON (make sure they're serializable)
            analysis_record.data_quality_report = prepare_for_jsonb(results.get('data_quality', {}))
            analysis_record.domain_insights = prepare_for_jsonb(domain_analysis)
            analysis_record.recommended_kpis = prepare_for_jsonb(results.get('kpi_analysis', {}))
            analysis_record.dashboard_structure = prepare_for_jsonb(results.get('dashboard_design', {}))
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to update analysis record: {str(e)}")
            db.session.rollback()
    
    def _handle_analysis_error(self, analysis_record: DatasetAnalysis, error_message: str) -> Dict[str, Any]:
        """Handle analysis errors and update database"""
        try:
            analysis_record.status = ProcessingStatus.FAILED
            analysis_record.error_message = error_message
            analysis_record.processing_completed_at = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to update error status: {str(e)}")
            db.session.rollback()
        
        return {
            'success': False,
            'error': error_message,
            'analysis_id': str(analysis_record.id) if analysis_record else None
        }
    
    def get_analysis_results(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve analysis results by ID"""
        try:
            analysis = DatasetAnalysis.query.get(analysis_id)
            if not analysis:
                return None
            
            return {
                'id': str(analysis.id),
                'filename': analysis.original_filename,
                'status': analysis.status,
                'domain': analysis.domain_classification,
                'confidence': analysis.confidence_score,
                'row_count': analysis.row_count,
                'column_count': analysis.column_count,
                'data_quality': analysis.data_quality_report,
                'domain_insights': analysis.domain_insights,
                'kpis': analysis.recommended_kpis,
                'dashboard': analysis.dashboard_structure,
                'created_at': analysis.upload_timestamp.isoformat() if analysis.upload_timestamp else None,
                'completed_at': analysis.processing_completed_at.isoformat() if analysis.processing_completed_at else None
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve analysis results: {str(e)}")
            return None

    def _placeholder_data_quality_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Placeholder data quality analysis until agents are fixed"""
        return {
            'quality_score': 0.85,
            'total_rows': int(len(df)),
            'total_columns': int(len(df.columns)),
            'missing_values': {col: int(df[col].isnull().sum()) for col in df.columns},
            'duplicate_rows': int(df.duplicated().sum()),
            'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'issues': ['Some missing values detected'],
            'recommendations': ['Consider filling missing values']
        }
    
    def _placeholder_domain_analysis(self, df: pd.DataFrame, filename: str) -> Dict[str, Any]:
        """Placeholder domain analysis until agents are fixed"""
        return {
            'primary_domain': 'general',
            'confidence_score': 0.7,
            'domain_insights': 'General business data detected',
            'reasoning': 'Based on column structure and filename analysis'
        }
    
    def _placeholder_kpi_analysis(self, df: pd.DataFrame, domain: str) -> Dict[str, Any]:
        """Placeholder KPI analysis until agents are fixed"""
        numeric_cols = [col for col in df.select_dtypes(include=['number']).columns]
        return {
            'identified_kpis': {
                'revenue_metrics': numeric_cols[:3] if len(numeric_cols) >= 3 else numeric_cols,
                'performance_metrics': numeric_cols[3:6] if len(numeric_cols) >= 6 else [],
                'operational_metrics': numeric_cols[6:] if len(numeric_cols) >= 6 else []
            },
            'kpi_definitions': {},
            'recommended_targets': {}
        }
    
    def _placeholder_dashboard_design(self, df: pd.DataFrame, kpis: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """Placeholder dashboard design until agents are fixed"""
        numeric_cols = [col for col in df.select_dtypes(include=['number']).columns]
        object_cols = [col for col in df.select_dtypes(include=['object']).columns]
        
        return {
            'layout': 'grid',
            'charts': [
                {'type': 'line_chart', 'data_columns': numeric_cols[:2]},
                {'type': 'bar_chart', 'data_columns': numeric_cols[2:4]},
                {'type': 'pie_chart', 'data_columns': [df.columns[0]] if len(df.columns) > 0 else []}
            ],
            'filters': object_cols[:3],
            'color_scheme': 'blue'
        }

    def get_dataset_analysis(self, dataset_id: str) -> dict:
        """Get complete analysis results for a dataset"""
        try:
            analysis_record = DatasetAnalysis.query.get(dataset_id)
            if not analysis_record:
                return None
            
            return {
                'dataset_info': {
                    'id': str(analysis_record.id),
                    'filename': analysis_record.original_filename,
                    'file_size': analysis_record.file_size,
                    'upload_timestamp': analysis_record.upload_timestamp.isoformat() if analysis_record.upload_timestamp else None,
                    'row_count': analysis_record.row_count,
                    'column_count': analysis_record.column_count,
                    'status': analysis_record.status.value if analysis_record.status else None
                },
                'domain_analysis': {
                    'domain_classification': analysis_record.domain_classification,
                    'confidence_score': analysis_record.confidence_score,
                    'domain_insights': analysis_record.domain_insights
                },
                'data_quality': analysis_record.data_quality_report,
                'kpi_analysis': analysis_record.recommended_kpis,
                'dashboard_structure': analysis_record.dashboard_structure
            }
            
        except Exception as e:
            logger.error(f"Error getting dataset analysis: {str(e)}")
            return None

    def get_dataset_data(self, dataset_id: str, page: int = 1, per_page: int = 100) -> dict:
        """Get paginated dataset data points"""
        try:
            # Get the analysis record to verify it exists
            analysis_record = DatasetAnalysis.query.get(dataset_id)
            if not analysis_record:
                return None
            
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Get data points with pagination
            data_points = DataPoint.query.filter_by(dataset_id=dataset_id)\
                                        .offset(offset)\
                                        .limit(per_page)\
                                        .all()
            
            # Convert to list of dictionaries
            data_list = []
            for point in data_points:
                data_list.append({
                    'row_index': point.row_index,
                    'data': point.data
                })
            
            # Get total count for pagination info
            total_count = DataPoint.query.filter_by(dataset_id=dataset_id).count()
            
            return {
                'data': data_list,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_count,
                    'pages': (total_count + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting dataset data: {str(e)}")
            return None
