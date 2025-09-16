import os
import uuid
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
import pandas as pd
import structlog
from datetime import datetime

from app.api import api_bp
from app.models import DatasetAnalysis, ProcessingStatus
from app import db
from app.utils.file_handler import FileHandler
from app.utils.validators import validate_file
from app.services.analysis_service import AnalysisService
from app.utils.json_serializer import convert_numpy_types

logger = structlog.get_logger(__name__)


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'AutomatedBI Backend'}), 200


@api_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and initiate processing"""
    try:
        # Validate request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        validation_result = validate_file(file)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['message']}), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Save file
        file_handler = FileHandler(current_app.config['UPLOAD_FOLDER'])
        file_path = file_handler.save_file(file, unique_filename)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create database record
        dataset_analysis = DatasetAnalysis(
            filename=unique_filename,
            original_filename=original_filename,
            file_size=file_size,
            status=ProcessingStatus.PENDING
        )
        
        db.session.add(dataset_analysis)
        db.session.commit()
        
        # Process the dataset synchronously for now
        try:
            analysis_service = AnalysisService()
            result = analysis_service.analyze_dataset(
                analysis_id=str(dataset_analysis.id),
                file_path=file_path
            )
            
            logger.info(
                "File uploaded and processed successfully",
                dataset_id=str(dataset_analysis.id),
                filename=original_filename,
                file_size=file_size
            )
            
            # Clean results of any numpy types before returning
            clean_result = convert_numpy_types(result)
            
            return jsonify({
                'success': True,
                'dataset_id': str(dataset_analysis.id),
                'message': 'File uploaded and processed successfully.',
                'status': ProcessingStatus.COMPLETED.value,
                'results': clean_result
            }), 200
            
        except Exception as processing_error:
            logger.error(
                "Error processing uploaded file",
                dataset_id=str(dataset_analysis.id),
                error=str(processing_error)
            )
            
            # Update status to failed
            dataset_analysis.status = ProcessingStatus.FAILED
            dataset_analysis.error_message = str(processing_error)
            db.session.commit()
            
            return jsonify({
                'success': False,
                'dataset_id': str(dataset_analysis.id),
                'message': 'File uploaded but processing failed.',
                'status': ProcessingStatus.FAILED.value,
                'error': str(processing_error)
            }), 500
        
    except Exception as e:
        logger.error("Error uploading file", error=str(e))
        db.session.rollback()
        return jsonify({'error': 'Failed to upload file'}), 500


@api_bp.route('/upload/status/<dataset_id>', methods=['GET'])
def get_upload_status(dataset_id):
    """Get the processing status of an uploaded dataset"""
    try:
        dataset = DatasetAnalysis.query.get_or_404(dataset_id)
        
        response_data = {
            'dataset_id': str(dataset.id),
            'status': dataset.status.value,
            'original_filename': dataset.original_filename,
            'upload_timestamp': dataset.upload_timestamp.isoformat(),
            'processing_started_at': dataset.processing_started_at.isoformat() if dataset.processing_started_at else None,
            'processing_completed_at': dataset.processing_completed_at.isoformat() if dataset.processing_completed_at else None,
        }
        
        if dataset.status == ProcessingStatus.FAILED:
            response_data['error_message'] = dataset.error_message
        
        if dataset.status == ProcessingStatus.COMPLETED:
            response_data.update({
                'domain_classification': dataset.domain_classification,
                'confidence_score': dataset.confidence_score,
                'row_count': dataset.row_count,
                'column_count': dataset.column_count
            })
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error("Error getting upload status", dataset_id=dataset_id, error=str(e))
        return jsonify({'error': 'Failed to get status'}), 500


@api_bp.route('/upload/progress/<dataset_id>', methods=['GET'])
def get_processing_progress(dataset_id):
    """Get detailed processing progress including steps completed"""
    try:
        dataset = DatasetAnalysis.query.get_or_404(dataset_id)
        
        # Define processing steps
        steps = [
            {'id': 'upload', 'name': 'File Upload', 'status': 'completed'},
            {'id': 'validation', 'name': 'Data Validation', 'status': 'completed'},
            {'id': 'quality_analysis', 'name': 'Quality Analysis', 'status': 'pending'},
            {'id': 'domain_classification', 'name': 'Domain Classification', 'status': 'pending'},
            {'id': 'kpi_recommendation', 'name': 'KPI Recommendation', 'status': 'pending'},
            {'id': 'dashboard_design', 'name': 'Dashboard Design', 'status': 'pending'},
            {'id': 'completion', 'name': 'Analysis Complete', 'status': 'pending'}
        ]
        
        # Update step statuses based on current processing status
        if dataset.status == ProcessingStatus.PROCESSING:
            # Simulate progress - in production, you'd track this more granularly
            if dataset.data_quality_report:
                steps[2]['status'] = 'completed'
            if dataset.domain_classification:
                steps[3]['status'] = 'completed'
            if dataset.recommended_kpis:
                steps[4]['status'] = 'completed'
            if dataset.dashboard_structure:
                steps[5]['status'] = 'completed'
        
        elif dataset.status == ProcessingStatus.COMPLETED:
            for step in steps:
                step['status'] = 'completed'
        
        elif dataset.status == ProcessingStatus.FAILED:
            # Mark the step where failure occurred
            for i, step in enumerate(steps):
                if step['status'] == 'pending':
                    step['status'] = 'failed'
                    break
        
        return jsonify({
            'dataset_id': str(dataset.id),
            'overall_status': dataset.status.value,
            'steps': steps,
            'progress_percentage': _calculate_progress_percentage(steps),
            'current_step': _get_current_step(steps),
            'estimated_completion': _estimate_completion_time(dataset)
        }), 200
        
    except Exception as e:
        logger.error("Error getting processing progress", dataset_id=dataset_id, error=str(e))
        return jsonify({'error': 'Failed to get progress'}), 500


def _calculate_progress_percentage(steps):
    """Calculate the overall progress percentage"""
    completed_steps = sum(1 for step in steps if step['status'] == 'completed')
    return (completed_steps / len(steps)) * 100


def _get_current_step(steps):
    """Get the currently active step"""
    for step in steps:
        if step['status'] == 'pending':
            return step['name']
    return 'Completed'


def _estimate_completion_time(dataset):
    """Estimate completion time based on file size and processing status"""
    if dataset.status == ProcessingStatus.COMPLETED:
        return None
    
    # Simple estimation: ~1 minute per MB for processing
    estimated_minutes = dataset.file_size / (1024 * 1024)  # Convert to MB
    return max(1, int(estimated_minutes))  # At least 1 minute
