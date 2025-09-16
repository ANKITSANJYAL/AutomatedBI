from app import create_app, db
from app.models import DatasetAnalysis, DataPoint

# Create the Flask application
app = create_app()

@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized successfully!")

@app.cli.command()
def reset_db():
    """Reset the database"""
    db.drop_all()
    db.create_all()
    print("Database reset successfully!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
