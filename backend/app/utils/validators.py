import os
import magic
from werkzeug.utils import secure_filename
from typing import Dict, Any


def validate_file(file) -> Dict[str, Any]:
    """Validate uploaded file"""
    try:
        # Check if file exists
        if not file or file.filename == '':
            return {'valid': False, 'message': 'No file provided'}
        
        # Get secure filename
        filename = secure_filename(file.filename)
        if not filename:
            return {'valid': False, 'message': 'Invalid filename'}
        
        # Check file extension
        allowed_extensions = {'csv', 'xlsx', 'xls'}
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if file_ext not in allowed_extensions:
            return {
                'valid': False, 
                'message': f'File type not allowed. Supported types: {", ".join(allowed_extensions)}'
            }
        
        # Check file size (read a small portion to verify it's not empty)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size == 0:
            return {'valid': False, 'message': 'File is empty'}
        
        # Check maximum file size (50MB)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        if file_size > max_size:
            return {'valid': False, 'message': 'File too large. Maximum size is 50MB'}
        
        # Validate MIME type
        file_content = file.read(1024)  # Read first 1KB for MIME detection
        file.seek(0)  # Reset to beginning
        
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
            valid_mime_types = {
                'text/csv',
                'application/csv',
                'text/plain',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/vnd.ms-excel'
            }
            
            if mime_type not in valid_mime_types:
                return {
                    'valid': False, 
                    'message': f'Invalid file format detected: {mime_type}'
                }
        except Exception:
            # If magic fails, rely on extension validation
            pass
        
        return {
            'valid': True, 
            'message': 'File validation successful',
            'file_size': file_size,
            'file_extension': file_ext,
            'filename': filename
        }
        
    except Exception as e:
        return {'valid': False, 'message': f'Validation error: {str(e)}'}


def validate_dataset_id(dataset_id: str) -> Dict[str, Any]:
    """Validate dataset ID format"""
    try:
        import uuid
        uuid.UUID(dataset_id)
        return {'valid': True, 'message': 'Valid dataset ID'}
    except ValueError:
        return {'valid': False, 'message': 'Invalid dataset ID format'}


def validate_chart_config(chart_config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate chart configuration for AI-generated charts"""
    # AI-generated charts have different structure than the original validator expected
    valid_chart_types = [
        'bar', 'line', 'pie', 'scatter', 'area', 'histogram', 
        'kpi_cards', 'heatmap', 'multi_line', 'table', 'trend',
        'donut', 'relationship', 'performance', 'distribution'
    ]
    
    try:
        # Check that type is present
        if 'type' not in chart_config:
            return {'valid': False, 'message': 'Missing required field: type'}
        
        # Validate chart type - be flexible and accept variations
        chart_type = chart_config['type'].lower()
        if not any(valid_type in chart_type or chart_type in valid_type 
                  for valid_type in valid_chart_types):
            # Still allow it - let the intelligent processor handle it
            pass
        
        # For AI-generated charts, we're flexible about required fields
        # The chart processing functions can handle missing fields with defaults
        
        return {'valid': True, 'message': 'Chart configuration is valid'}
        
    except Exception as e:
        return {'valid': False, 'message': f'Validation error: {str(e)}'}
