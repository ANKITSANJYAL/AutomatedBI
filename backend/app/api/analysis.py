from flask import request, jsonify
from app.api import api_bp
from app.services.analysis_service import AnalysisService
from app.utils.validators import validate_dataset_id
from app.utils.json_serializer import convert_numpy_types
import structlog

logger = structlog.get_logger(__name__)


@api_bp.route('/analysis/<dataset_id>', methods=['GET'])
def get_analysis_results(dataset_id):
    """Get complete analysis results for a dataset"""
    try:
        # Validate dataset ID
        validation = validate_dataset_id(dataset_id)
        if not validation['valid']:
            return jsonify({'error': validation['message']}), 400
        
        analysis_service = AnalysisService()
        analysis_result = analysis_service.get_dataset_analysis(dataset_id)
        
        if not analysis_result:
            return jsonify({'error': 'Dataset not found'}), 404
        
        return jsonify({
            'success': True,
            'dataset_id': dataset_id,
            'analysis': analysis_result
        }), 200
        
    except Exception as e:
        logger.error("Error getting analysis results", dataset_id=dataset_id, error=str(e))
        return jsonify({'error': 'Failed to get analysis results'}), 500


@api_bp.route('/analysis/<dataset_id>/data', methods=['GET'])
def get_dataset_data(dataset_id):
    """Get paginated dataset data"""
    try:
        # Validate dataset ID
        validation = validate_dataset_id(dataset_id)
        if not validation['valid']:
            return jsonify({'error': validation['message']}), 400
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 100, type=int), 1000)  # Max 1000 per page
        
        analysis_service = AnalysisService()
        data_result = analysis_service.get_dataset_data(dataset_id, page, per_page)
        
        # Clean any numpy types from the data result
        clean_data_result = convert_numpy_types(data_result)
        
        return jsonify({
            'success': True,
            'dataset_id': dataset_id,
            **clean_data_result
        }), 200
        
    except Exception as e:
        logger.error("Error getting dataset data", dataset_id=dataset_id, error=str(e))
        return jsonify({'error': 'Failed to get dataset data'}), 500


@api_bp.route('/analysis/<dataset_id>/quality', methods=['GET'])
def get_data_quality_report(dataset_id):
    """Get data quality report for a dataset"""
    try:
        # Validate dataset ID
        validation = validate_dataset_id(dataset_id)
        if not validation['valid']:
            return jsonify({'error': validation['message']}), 400
        
        analysis_service = AnalysisService()
        analysis_result = analysis_service.get_dataset_analysis(dataset_id)
        
        if not analysis_result:
            return jsonify({'error': 'Dataset not found'}), 404
        
        quality_report = analysis_result.get('data_quality')
        column_analysis = analysis_result.get('column_analysis')
        
        if not quality_report:
            return jsonify({'error': 'Quality analysis not yet completed'}), 404
        
        return jsonify({
            'success': True,
            'dataset_id': dataset_id,
            'quality_report': quality_report,
            'column_analysis': column_analysis,
            'summary': {
                'total_rows': analysis_result.get('dataset_info', {}).get('row_count'),
                'total_columns': analysis_result.get('dataset_info', {}).get('column_count'),
                'quality_score': quality_report.get('quality_score'),
                'domain': analysis_result.get('domain_analysis', {}).get('domain_classification'),
                'confidence': analysis_result.get('domain_analysis', {}).get('confidence_score')
            }
        }), 200
        
    except Exception as e:
        logger.error("Error getting quality report", dataset_id=dataset_id, error=str(e))
        return jsonify({'error': 'Failed to get quality report'}), 500


@api_bp.route('/analysis/<dataset_id>/insights', methods=['GET'])
def get_business_insights(dataset_id):
    """Get business insights and domain-specific analysis"""
    try:
        # Validate dataset ID
        validation = validate_dataset_id(dataset_id)
        if not validation['valid']:
            return jsonify({'error': validation['message']}), 400
        
        analysis_service = AnalysisService()
        analysis_result = analysis_service.get_dataset_analysis(dataset_id)
        
        if not analysis_result:
            return jsonify({'error': 'Dataset not found'}), 404
        
        domain_analysis = analysis_result.get('domain_analysis', {})
        kpi_analysis = analysis_result.get('kpi_analysis', {})
        dashboard_structure = analysis_result.get('dashboard_structure', {})
        
        if not domain_analysis:
            return jsonify({'error': 'Business analysis not yet completed'}), 404
        
        # Get charts from dashboard_structure.visualizations
        charts = dashboard_structure.get('visualizations', [])
        # Get KPIs from kpi_analysis.identified_kpis
        kpis = kpi_analysis.get('identified_kpis', {})
        
        return jsonify({
            'success': True,
            'dataset_id': dataset_id,
            'domain': {
                'classification': domain_analysis.get('domain_classification'),
                'confidence': domain_analysis.get('confidence_score'),
                'insights': domain_analysis.get('domain_insights')
            },
            'kpis': kpis,
            'charts': charts,
            'summary': {
                'domain': domain_analysis.get('domain_classification'),
                'total_kpis': len(kpis),
                'total_charts': len(charts)
            }
        }), 200
        
    except Exception as e:
        logger.error("Error getting business insights", dataset_id=dataset_id, error=str(e))
        return jsonify({'error': 'Failed to get business insights'}), 500


@api_bp.route('/analysis/<dataset_id>/export', methods=['POST'])
def export_analysis(dataset_id):
    """Export analysis results in various formats"""
    try:
        # Validate dataset ID
        validation = validate_dataset_id(dataset_id)
        if not validation['valid']:
            return jsonify({'error': validation['message']}), 400
        
        # Get export format
        export_format = request.json.get('format', 'json').lower()
        include_data = request.json.get('include_data', False)
        
        if export_format not in ['json', 'pdf', 'excel']:
            return jsonify({'error': 'Unsupported export format'}), 400
        
        analysis_service = AnalysisService()
        analysis_result = analysis_service.get_dataset_analysis(dataset_id)
        
        if not analysis_result:
            return jsonify({'error': 'Dataset not found'}), 404
        
        # For now, return JSON format
        # In production, you would implement PDF and Excel generation
        export_data = {
            'dataset_info': {
                'id': dataset_id,
                'filename': analysis_result.get('original_filename'),
                'upload_date': analysis_result.get('upload_timestamp'),
                'rows': analysis_result.get('row_count'),
                'columns': analysis_result.get('column_count')
            },
            'quality_analysis': analysis_result.get('data_quality_report'),
            'business_insights': {
                'domain': analysis_result.get('domain_classification'),
                'confidence': analysis_result.get('confidence_score'),
                'kpis': analysis_result.get('recommended_kpis'),
                'charts': analysis_result.get('recommended_charts')
            }
        }
        
        if include_data:
            data_result = analysis_service.get_dataset_data(dataset_id, page=1, per_page=10000)
            export_data['sample_data'] = data_result.get('data', [])[:1000]  # Limit to 1000 rows
        
        return jsonify({
            'success': True,
            'dataset_id': dataset_id,
            'format': export_format,
            'export_data': export_data
        }), 200
        
    except Exception as e:
        logger.error("Error exporting analysis", dataset_id=dataset_id, error=str(e))
        return jsonify({'error': 'Failed to export analysis'}), 500
