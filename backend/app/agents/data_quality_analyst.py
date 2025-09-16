"""
Data Quality Analyst Agent for AutomatedBI
Responsible for analyzing data quality, identifying issues, and providing recommendations.
"""

from crewai import Agent
from typing import Dict, Any, List
import pandas as pd
import numpy as np


class DataQualityAnalyst:
    """Agent responsible for comprehensive data quality analysis"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        self.llm_config = llm_config
        
    def create_agent(self) -> Agent:
        """Create the Data Quality Analyst agent"""
        return Agent(
            role='Data Quality Analyst',
            goal='Analyze data quality, identify issues, anomalies, and provide actionable recommendations for data improvement',
            backstory="""You are an expert data quality analyst with years of experience in identifying 
            data issues, anomalies, and quality problems. You have a keen eye for spotting inconsistencies, 
            missing values, outliers, and data integrity issues. Your expertise helps organizations 
            improve their data quality and make better decisions.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm_config.get('model'),
            max_iter=3,
            memory=True
        )
    
    def analyze_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive ML-focused data quality analysis
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary containing ML-focused quality metrics and recommendations
        """
        try:
            quality_report = {
                'basic_info': self._get_basic_info(df),
                'missing_values': self._analyze_missing_values(df),
                'duplicates': self._analyze_duplicates(df),
                'data_types': self._analyze_data_types(df),
                'outliers': self._detect_outliers(df),
                'consistency': self._check_consistency(df),
                'ml_readiness': self._assess_ml_readiness(df),
                'feature_engineering_opportunities': self._identify_feature_opportunities(df),
                'data_preprocessing_requirements': self._identify_preprocessing_needs(df),
                'modeling_considerations': self._provide_modeling_insights(df),
                'data_quality_score': self._calculate_quality_score(df),
                'recommendations': self._generate_ml_recommendations(df)
            }
            
            return quality_report
            
        except Exception as e:
            return {
                'error': f'Error analyzing data quality: {str(e)}',
                'basic_info': self._get_basic_info(df) if not df.empty else {}
            }
    
    def _get_basic_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic information about the dataset"""
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'columns': list(df.columns),
            'sample_data': df.head(3).to_dict('records') if len(df) > 0 else []
        }
    
    def _analyze_missing_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze missing values in the dataset"""
        missing_info = {}
        total_rows = len(df)
        
        for column in df.columns:
            missing_count = df[column].isnull().sum()
            missing_percentage = (missing_count / total_rows) * 100
            
            missing_info[column] = {
                'missing_count': int(missing_count),
                'missing_percentage': round(missing_percentage, 2),
                'severity': self._get_missing_severity(missing_percentage)
            }
        
        return missing_info
    
    def _get_missing_severity(self, percentage: float) -> str:
        """Determine severity of missing data"""
        if percentage == 0:
            return 'none'
        elif percentage < 5:
            return 'low'
        elif percentage < 20:
            return 'medium'
        elif percentage < 50:
            return 'high'
        else:
            return 'critical'
    
    def _analyze_duplicates(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze duplicate records"""
        duplicate_rows = df.duplicated().sum()
        total_rows = len(df)
        duplicate_percentage = (duplicate_rows / total_rows) * 100 if total_rows > 0 else 0
        
        return {
            'duplicate_count': int(duplicate_rows),
            'duplicate_percentage': round(duplicate_percentage, 2),
            'severity': 'high' if duplicate_percentage > 10 else 'medium' if duplicate_percentage > 5 else 'low'
        }
    
    def _analyze_data_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data types and suggest improvements"""
        type_info = {}
        
        for column in df.columns:
            dtype = str(df[column].dtype)
            sample_values = df[column].dropna().head(5).tolist()
            
            # Check if numeric columns are stored as object
            suggestions = []
            if dtype == 'object':
                # Try to convert to numeric
                try:
                    pd.to_numeric(df[column], errors='raise')
                    suggestions.append('Consider converting to numeric type')
                except:
                    # Check for date patterns - suppress warnings with explicit format checking
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        try:
                            date_converted = pd.to_datetime(df[column], errors='coerce')
                            # Only suggest datetime if more than 50% of values were successfully converted
                            if date_converted.notna().sum() > len(df[column]) * 0.5:
                                suggestions.append('Consider converting to datetime type')
                        except:
                            pass
            
            type_info[column] = {
                'current_type': dtype,
                'sample_values': sample_values,
                'suggestions': suggestions
            }
        
        return type_info
    
    def _detect_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect outliers in numeric columns"""
        outlier_info = {}
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            if df[column].notna().sum() > 0:
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
                outlier_count = len(outliers)
                
                outlier_info[column] = {
                    'outlier_count': outlier_count,
                    'outlier_percentage': round((outlier_count / len(df)) * 100, 2),
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound,
                    'severity': 'high' if outlier_count > len(df) * 0.1 else 'medium' if outlier_count > len(df) * 0.05 else 'low'
                }
        
        return outlier_info
    
    def _check_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check data consistency across columns"""
        consistency_issues = []
        
        # Check for inconsistent text casing
        text_columns = df.select_dtypes(include=['object']).columns
        for column in text_columns:
            if df[column].dtype == 'object':
                unique_values = df[column].dropna().unique()
                if len(unique_values) > 1:
                    # Check for case inconsistencies
                    lower_values = [str(v).lower() for v in unique_values]
                    if len(set(lower_values)) < len(unique_values):
                        consistency_issues.append(f"Inconsistent casing in column '{column}'")
        
        # Check for date format consistency
        for column in df.columns:
            if 'date' in column.lower() or 'time' in column.lower():
                try:
                    sample_dates = df[column].dropna().head(10).astype(str)
                    date_formats = set()
                    for date_str in sample_dates:
                        if '/' in date_str:
                            date_formats.add('slash_format')
                        elif '-' in date_str:
                            date_formats.add('dash_format')
                    
                    if len(date_formats) > 1:
                        consistency_issues.append(f"Inconsistent date formats in column '{column}'")
                except:
                    pass
        
        return {
            'issues': consistency_issues,
            'severity': 'high' if len(consistency_issues) > 3 else 'medium' if len(consistency_issues) > 1 else 'low'
        }
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate overall data quality score and ML readiness metrics
        """
        scores = {}
        total_score = 0
        max_score = 0
        
        # Missing data score (0-25 points)
        missing_percentage = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        if missing_percentage <= 5:
            missing_score = 25
        elif missing_percentage <= 15:
            missing_score = 20
        elif missing_percentage <= 30:
            missing_score = 15
        elif missing_percentage <= 50:
            missing_score = 10
        else:
            missing_score = 5
        
        scores['missing_data'] = missing_score
        total_score += missing_score
        max_score += 25
        
        # Duplicate score (0-20 points)
        duplicate_percentage = (df.duplicated().sum() / len(df)) * 100
        if duplicate_percentage == 0:
            duplicate_score = 20
        elif duplicate_percentage <= 5:
            duplicate_score = 15
        elif duplicate_percentage <= 10:
            duplicate_score = 10
        else:
            duplicate_score = 5
        
        scores['duplicates'] = duplicate_score
        total_score += duplicate_score
        max_score += 20
        
        # Data type consistency (0-20 points)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        consistent_types = 0
        total_cols = len(df.columns)
        
        for col in df.columns:
            if col in numeric_cols:
                # Check if numeric columns have consistent values
                if not df[col].isnull().all():
                    try:
                        pd.to_numeric(df[col], errors='raise')
                        consistent_types += 1
                    except:
                        pass
            else:
                # For non-numeric, check if values are reasonable
                if df[col].dtype == 'object':
                    unique_ratio = df[col].nunique() / len(df)
                    if 0.01 <= unique_ratio <= 0.8:  # Reasonable diversity
                        consistent_types += 1
        
        type_score = int((consistent_types / total_cols) * 20) if total_cols > 0 else 0
        scores['data_types'] = type_score
        total_score += type_score
        max_score += 20
        
        # Outlier impact (0-15 points)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_impact = 0
        
        for col in numeric_cols:
            if not df[col].isnull().all():
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
                outlier_percentage = len(outliers) / len(df) * 100
                if outlier_percentage <= 5:
                    outlier_impact += 1
        
        outlier_score = int((outlier_impact / len(numeric_cols)) * 15) if len(numeric_cols) > 0 else 15
        scores['outliers'] = outlier_score
        total_score += outlier_score
        max_score += 15
        
        # Sample size adequacy (0-20 points)
        sample_score = 20 if len(df) >= 1000 else int((len(df) / 1000) * 20)
        scores['sample_size'] = sample_score
        total_score += sample_score
        max_score += 20
        
        # Overall score
        overall_score = (total_score / max_score) * 100 if max_score > 0 else 0
        
        return {
            'overall_score': round(overall_score, 2),
            'component_scores': scores,
            'ml_readiness_level': self._get_ml_readiness_level(overall_score),
            'critical_issues': self._identify_critical_issues(df, scores)
        }
    
    def _get_ml_readiness_level(self, score: float) -> str:
        """Determine ML readiness level based on quality score"""
        if score >= 85:
            return "Production Ready"
        elif score >= 70:
            return "Model Development Ready"
        elif score >= 55:
            return "Requires Preprocessing"
        elif score >= 40:
            return "Significant Cleaning Needed"
        else:
            return "Not Suitable for ML Without Major Preprocessing"
    
    def _identify_critical_issues(self, df: pd.DataFrame, scores: Dict) -> List[str]:
        """Identify critical issues that block ML development"""
        issues = []
        
        if scores.get('missing_data', 0) < 15:
            issues.append("High missing data rate - consider imputation strategies")
        
        if scores.get('duplicates', 0) < 15:
            issues.append("Significant duplicate records detected")
        
        if scores.get('sample_size', 0) < 10:
            issues.append("Insufficient sample size for reliable ML models")
        
        if scores.get('data_types', 0) < 10:
            issues.append("Data type inconsistencies require attention")
        
        # Check for high cardinality categorical variables
        for col in df.select_dtypes(include=['object']).columns:
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio > 0.8:
                issues.append(f"High cardinality in '{col}' - may need encoding strategies")
        
        return issues

    def _assess_ml_readiness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Assess how ready the data is for machine learning
        """
        readiness = {
            'target_variable_analysis': self._analyze_potential_targets(df),
            'feature_distribution': self._analyze_feature_distributions(df),
            'correlation_analysis': self._analyze_correlations(df),
            'class_balance': self._check_class_balance(df),
            'scaling_requirements': self._assess_scaling_needs(df),
            'encoding_requirements': self._assess_encoding_needs(df)
        }
        
        return readiness
    
    def _analyze_potential_targets(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify potential target variables for ML"""
        targets = {
            'binary_targets': [],
            'categorical_targets': [],
            'continuous_targets': [],
            'recommendations': []
        }
        
        for col in df.columns:
            if df[col].dtype in ['object', 'category']:
                unique_count = df[col].nunique()
                if unique_count == 2:
                    targets['binary_targets'].append({
                        'column': col,
                        'values': df[col].unique().tolist(),
                        'distribution': df[col].value_counts().to_dict()
                    })
                elif 2 < unique_count <= 10:
                    targets['categorical_targets'].append({
                        'column': col,
                        'classes': unique_count,
                        'distribution': df[col].value_counts().to_dict()
                    })
            else:
                # Check if numeric column could be a target
                if df[col].nunique() > 10:  # Continuous target
                    targets['continuous_targets'].append({
                        'column': col,
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'mean': float(df[col].mean()),
                        'std': float(df[col].std())
                    })
        
        # Generate recommendations
        if targets['binary_targets']:
            targets['recommendations'].append("Binary classification tasks available")
        if targets['categorical_targets']:
            targets['recommendations'].append("Multi-class classification tasks available")
        if targets['continuous_targets']:
            targets['recommendations'].append("Regression tasks available")
        
        return targets
    
    def _analyze_feature_distributions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze feature distributions for ML insights"""
        distributions = {
            'skewed_features': [],
            'normal_distributions': [],
            'uniform_distributions': [],
            'recommendations': []
        }
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if not df[col].isnull().all():
                skewness = abs(df[col].skew())
                if skewness > 1:
                    distributions['skewed_features'].append({
                        'column': col,
                        'skewness': round(skewness, 3),
                        'transformation_needed': True
                    })
                elif skewness < 0.5:
                    distributions['normal_distributions'].append({
                        'column': col,
                        'skewness': round(skewness, 3)
                    })
        
        if distributions['skewed_features']:
            distributions['recommendations'].append("Consider log/sqrt transformation for skewed features")
        
        return distributions
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze feature correlations"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.shape[1] < 2:
            return {'message': 'Insufficient numeric features for correlation analysis'}
        
        corr_matrix = numeric_df.corr()
        
        # Find highly correlated pairs
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.8:
                    high_corr_pairs.append({
                        'feature1': corr_matrix.columns[i],
                        'feature2': corr_matrix.columns[j],
                        'correlation': round(corr_value, 3)
                    })
        
        return {
            'high_correlations': high_corr_pairs,
            'multicollinearity_risk': len(high_corr_pairs) > 0,
            'recommendations': ['Consider removing highly correlated features'] if high_corr_pairs else []
        }
    
    def _check_class_balance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check class balance for potential target variables"""
        balance_analysis = {}
        
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_cols:
            unique_count = df[col].nunique()
            if 2 <= unique_count <= 10:  # Potential classification target
                value_counts = df[col].value_counts()
                balance_ratio = value_counts.min() / value_counts.max()
                
                balance_analysis[col] = {
                    'class_distribution': value_counts.to_dict(),
                    'balance_ratio': round(balance_ratio, 3),
                    'is_balanced': balance_ratio > 0.3,
                    'imbalance_severity': 'Low' if balance_ratio > 0.7 else 'Medium' if balance_ratio > 0.3 else 'High'
                }
        
        return balance_analysis
    
    def _assess_scaling_needs(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess which features need scaling"""
        scaling_needs = {
            'features_needing_scaling': [],
            'scaling_methods': {},
            'recommendations': []
        }
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        scales = {}
        for col in numeric_cols:
            if not df[col].isnull().all():
                col_range = df[col].max() - df[col].min()
                col_std = df[col].std()
                scales[col] = {'range': col_range, 'std': col_std}
        
        # Check if features have very different scales
        if len(scales) > 1:
            ranges = [v['range'] for v in scales.values() if v['range'] > 0]
            if ranges and max(ranges) / min(ranges) > 100:
                scaling_needs['features_needing_scaling'] = list(scales.keys())
                scaling_needs['scaling_methods'] = {
                    'standard_scaler': 'For normally distributed features',
                    'min_max_scaler': 'For features with known bounds',
                    'robust_scaler': 'For features with outliers'
                }
                scaling_needs['recommendations'].append('Feature scaling required due to different scales')
        
        return scaling_needs
    
    def _assess_encoding_needs(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess categorical encoding requirements"""
        encoding_needs = {
            'categorical_features': [],
            'encoding_strategies': {},
            'recommendations': []
        }
        
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_cols:
            unique_count = df[col].nunique()
            
            feature_info = {
                'column': col,
                'unique_values': unique_count,
                'sample_values': df[col].dropna().unique()[:5].tolist()
            }
            
            # Recommend encoding strategy
            if unique_count == 2:
                feature_info['recommended_encoding'] = 'Label Encoding or Binary Encoding'
            elif unique_count <= 10:
                feature_info['recommended_encoding'] = 'One-Hot Encoding'
            elif unique_count <= 50:
                feature_info['recommended_encoding'] = 'Target Encoding or Binary Encoding'
            else:
                feature_info['recommended_encoding'] = 'Target Encoding or Feature Hashing'
            
            encoding_needs['categorical_features'].append(feature_info)
        
        if categorical_cols.any():
            encoding_needs['recommendations'].append('Categorical encoding required for ML algorithms')
        
        return encoding_needs

    def _identify_feature_opportunities(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify feature engineering opportunities"""
        opportunities = {
            'datetime_features': [],
            'text_features': [],
            'interaction_features': [],
            'binning_opportunities': [],
            'recommendations': []
        }
        
        # Check for datetime columns
        for col in df.columns:
            if df[col].dtype == 'object':
                sample_values = df[col].dropna().head(10)
                # Simple check for date-like strings
                for val in sample_values:
                    if isinstance(val, str) and any(char in val for char in ['-', '/', ':']):
                        try:
                            pd.to_datetime(val)
                            opportunities['datetime_features'].append({
                                'column': col,
                                'potential_features': ['year', 'month', 'day', 'hour', 'weekday']
                            })
                            break
                        except:
                            continue
        
        # Check for text features
        text_cols = df.select_dtypes(include=['object']).columns
        for col in text_cols:
            avg_length = df[col].dropna().astype(str).str.len().mean()
            if avg_length > 20:  # Likely text data
                opportunities['text_features'].append({
                    'column': col,
                    'avg_length': round(avg_length, 2),
                    'potential_features': ['text_length', 'word_count', 'sentiment', 'TF-IDF']
                })
        
        # Check for binning opportunities
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].nunique() > 20:
                opportunities['binning_opportunities'].append({
                    'column': col,
                    'unique_values': df[col].nunique(),
                    'binning_methods': ['equal_width', 'equal_frequency', 'k_means']
                })
        
        # Suggest interaction features for numeric columns
        if len(numeric_cols) > 1:
            opportunities['interaction_features'] = [
                f"{col1} * {col2}" for i, col1 in enumerate(numeric_cols) 
                for col2 in numeric_cols[i+1:] if col1 != col2
            ][:5]  # Limit to 5 suggestions
        
        # Generate recommendations
        if opportunities['datetime_features']:
            opportunities['recommendations'].append('Extract temporal features from datetime columns')
        if opportunities['text_features']:
            opportunities['recommendations'].append('Apply NLP techniques to text features')
        if opportunities['binning_opportunities']:
            opportunities['recommendations'].append('Consider binning continuous features for non-linear relationships')
        if opportunities['interaction_features']:
            opportunities['recommendations'].append('Create interaction features between numeric variables')
        
        return opportunities

    def _identify_preprocessing_needs(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify specific preprocessing requirements"""
        preprocessing = {
            'missing_value_strategy': {},
            'outlier_treatment': {},
            'data_cleaning': [],
            'transformation_pipeline': [],
            'recommendations': []
        }
        
        # Missing value strategies
        for col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 0:
                if df[col].dtype in ['object', 'category']:
                    strategy = 'mode_imputation' if missing_pct < 50 else 'create_missing_category'
                else:
                    strategy = 'mean_imputation' if missing_pct < 30 else 'median_imputation' if missing_pct < 50 else 'drop_column'
                
                preprocessing['missing_value_strategy'][col] = {
                    'missing_percentage': round(missing_pct, 2),
                    'recommended_strategy': strategy
                }
        
        # Outlier treatment
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if not df[col].isnull().all():
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
                outlier_pct = (len(outliers) / len(df)) * 100
                
                if outlier_pct > 5:
                    preprocessing['outlier_treatment'][col] = {
                        'outlier_percentage': round(outlier_pct, 2),
                        'treatment_options': ['cap_outliers', 'log_transform', 'remove_outliers']
                    }
        
        # Data cleaning needs
        if df.duplicated().sum() > 0:
            preprocessing['data_cleaning'].append('Remove duplicate records')
        
        # Build transformation pipeline
        pipeline_steps = []
        if preprocessing['missing_value_strategy']:
            pipeline_steps.append('1. Handle missing values')
        if preprocessing['outlier_treatment']:
            pipeline_steps.append('2. Treat outliers')
        if any(df.select_dtypes(include=['object']).columns):
            pipeline_steps.append('3. Encode categorical variables')
        if len(df.select_dtypes(include=[np.number]).columns) > 1:
            pipeline_steps.append('4. Scale numerical features')
        
        preprocessing['transformation_pipeline'] = pipeline_steps
        
        # Generate recommendations
        if len(preprocessing['missing_value_strategy']) > 0:
            preprocessing['recommendations'].append('Implement missing value imputation strategy')
        if len(preprocessing['outlier_treatment']) > 0:
            preprocessing['recommendations'].append('Address outliers before model training')
        if pipeline_steps:
            preprocessing['recommendations'].append('Follow systematic preprocessing pipeline')
        
        return preprocessing

    def _provide_modeling_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Provide insights for model selection and training"""
        insights = {
            'dataset_characteristics': {},
            'model_recommendations': [],
            'validation_strategy': {},
            'performance_considerations': [],
            'feature_importance_analysis': {}
        }
        
        # Dataset characteristics
        insights['dataset_characteristics'] = {
            'sample_size': len(df),
            'feature_count': len(df.columns),
            'numeric_features': len(df.select_dtypes(include=[np.number]).columns),
            'categorical_features': len(df.select_dtypes(include=['object', 'category']).columns),
            'missing_data_percentage': round((df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100, 2)
        }
        
        # Model recommendations based on data characteristics
        sample_size = len(df)
        feature_count = len(df.columns)
        
        if sample_size < 1000:
            insights['model_recommendations'].extend([
                'Simple models (Linear/Logistic Regression)',
                'Decision Trees',
                'Naive Bayes'
            ])
            insights['performance_considerations'].append('Small dataset - risk of overfitting')
        elif sample_size < 10000:
            insights['model_recommendations'].extend([
                'Random Forest',
                'Support Vector Machines',
                'Gradient Boosting'
            ])
        else:
            insights['model_recommendations'].extend([
                'Deep Learning models',
                'Ensemble methods',
                'XGBoost/LightGBM'
            ])
        
        # Validation strategy
        if sample_size < 1000:
            insights['validation_strategy'] = {
                'method': 'Leave-One-Out or K-Fold (k=5)',
                'reason': 'Small dataset requires careful validation'
            }
        else:
            insights['validation_strategy'] = {
                'method': 'Train-Validation-Test split (60-20-20)',
                'reason': 'Sufficient data for proper holdout validation'
            }
        
        # Performance considerations
        if feature_count > sample_size:
            insights['performance_considerations'].append('High dimensional data - consider dimensionality reduction')
        
        if insights['dataset_characteristics']['missing_data_percentage'] > 30:
            insights['performance_considerations'].append('High missing data rate may impact model performance')
        
        return insights

    def _generate_ml_recommendations(self, df: pd.DataFrame) -> List[str]:
        """
        Generate ML-focused recommendations for data scientists
        """
        recommendations = []
        
        # Data quality recommendations
        missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        if missing_pct > 20:
            recommendations.append("🚨 High missing data rate (>20%) - implement robust imputation strategy")
        
        duplicate_pct = (df.duplicated().sum() / len(df)) * 100
        if duplicate_pct > 5:
            recommendations.append("🔄 Significant duplicates detected - clean before modeling")
        
        # Sample size recommendations
        if len(df) < 500:
            recommendations.append("📊 Small dataset (<500 rows) - consider data augmentation or simple models")
        elif len(df) > 100000:
            recommendations.append("⚡ Large dataset - consider sampling strategies for faster iteration")
        
        # Feature engineering recommendations
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        if len(categorical_cols) > len(numeric_cols):
            recommendations.append("🏷️ Many categorical features - plan encoding strategy carefully")
        
        # Check for high cardinality categoricals
        high_cardinality = []
        for col in categorical_cols:
            if df[col].nunique() > len(df) * 0.5:
                high_cardinality.append(col)
        
        if high_cardinality:
            recommendations.append(f"🔢 High cardinality features detected: {high_cardinality[:3]} - consider target encoding")
        
        # Skewness recommendations
        skewed_features = []
        for col in numeric_cols:
            if not df[col].isnull().all() and abs(df[col].skew()) > 2:
                skewed_features.append(col)
        
        if skewed_features:
            recommendations.append(f"📈 Highly skewed features: {skewed_features[:3]} - consider transformation")
        
        # Correlation recommendations
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            high_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if abs(corr_matrix.iloc[i, j]) > 0.9:
                        high_corr.append((corr_matrix.columns[i], corr_matrix.columns[j]))
            
            if high_corr:
                recommendations.append("🔗 Highly correlated features detected - consider dimensionality reduction")
        
        # Model selection recommendations
        if len(df) < 1000 and len(df.columns) > 50:
            recommendations.append("⚠️ High dimensionality vs sample size - risk of overfitting")
        
        # Add general ML workflow recommendations
        recommendations.extend([
            "✅ Start with simple baseline models before complex ones",
            "🎯 Define clear success metrics before modeling",
            "🔄 Plan for iterative feature engineering and model improvement",
            "📋 Document all preprocessing steps for reproducibility"
        ])
        
        return recommendations
    
    def _generate_recommendations(self, quality_report: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on quality analysis"""
        recommendations = []
        
        # Get ML-focused recommendations from the DataFrame
        # We need to reconstruct the DataFrame context here, but for now use traditional approach
        
        # Missing values recommendations
        for column, info in quality_report['missing_values'].items():
            if info['severity'] in ['high', 'critical']:
                recommendations.append(f"Address missing values in '{column}' ({info['missing_percentage']}% missing)")
        
        # Duplicate recommendations
        if quality_report['duplicates']['severity'] in ['medium', 'high']:
            recommendations.append(f"Remove duplicate records ({quality_report['duplicates']['duplicate_count']} duplicates found)")
        
        # Data type recommendations
        for column, info in quality_report['data_types'].items():
            if info['suggestions']:
                recommendations.extend([f"{column}: {suggestion}" for suggestion in info['suggestions']])
        
        # Outlier recommendations
        for column, info in quality_report['outliers'].items():
            if info['severity'] == 'high':
                recommendations.append(f"Investigate outliers in '{column}' ({info['outlier_count']} outliers)")
        
        # Consistency recommendations
        if quality_report['consistency']['severity'] in ['medium', 'high']:
            recommendations.extend(quality_report['consistency']['issues'])
        
        # Add ML readiness info if available
        if 'data_quality_score' in quality_report:
            score_info = quality_report['data_quality_score']
            recommendations.append(f"🎯 ML Readiness: {score_info.get('ml_readiness_level', 'Unknown')} (Score: {score_info.get('overall_score', 0):.1f}/100)")
            
            # Add critical issues
            critical_issues = score_info.get('critical_issues', [])
            for issue in critical_issues[:3]:  # Limit to top 3
                recommendations.append(f"⚠️ {issue}")
        
        # General recommendations
        if len(recommendations) == 0:
            recommendations.append("Data quality looks good! No major issues detected.")
        else:
            recommendations.insert(0, f"Found {len([r for r in recommendations if not r.startswith('🎯') and not r.startswith('⚠️')])} data quality issues that need attention.")
        
        return recommendations
