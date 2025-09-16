from flask import Blueprint

# Create the API blueprint
api_bp = Blueprint('api', __name__)

# Import routes to register them
from . import upload, analysis, dashboard
