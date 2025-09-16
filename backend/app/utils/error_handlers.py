from flask import jsonify, request
import structlog

logger = structlog.get_logger(__name__)


def register_error_handlers(app):
    """Register global error handlers for the Flask application"""
    
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning("Bad request", error=str(error), url=request.url, method=request.method)
        return jsonify({
            'error': 'Bad request',
            'message': 'The request was invalid or cannot be served'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        logger.warning("Unauthorized access", error=str(error), url=request.url, method=request.method)
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        logger.warning("Forbidden access", error=str(error), url=request.url, method=request.method)
        return jsonify({
            'error': 'Forbidden',
            'message': 'Access denied'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        logger.warning("Resource not found", error=str(error), url=request.url, method=request.method)
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        logger.warning("Method not allowed", error=str(error), url=request.url, method=request.method)
        return jsonify({
            'error': 'Method not allowed',
            'message': f'The method {request.method} is not allowed for this endpoint'
        }), 405
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        logger.warning("File too large", error=str(error), url=request.url, method=request.method)
        return jsonify({
            'error': 'File too large',
            'message': 'The uploaded file exceeds the maximum allowed size'
        }), 413
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        logger.warning("Unprocessable entity", error=str(error), url=request.url, method=request.method)
        return jsonify({
            'error': 'Unprocessable entity',
            'message': 'The request was well-formed but contains semantic errors'
        }), 422
    
    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error("Internal server error", error=str(error), url=request.url, method=request.method)
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle unexpected exceptions"""
        logger.error("Unhandled exception", error=str(error), type=type(error).__name__, url=request.url, method=request.method)
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
