import os
import logging
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Set up logging for easier debugging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the Base class
db = SQLAlchemy(model_class=Base)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "inventory_management_secret")

# Configure the database - use SQLite for offline use in Termux
# If DATABASE_URL is provided, use that (PostgreSQL on server), otherwise use SQLite
db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres"):
    # Use PostgreSQL if configured
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.logger.info("Using PostgreSQL database")
else:
    # Use SQLite for offline mode (perfect for Termux)
    sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory.db')
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_path}"
    app.logger.info(f"Using SQLite database at: {sqlite_path}")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database with the app
db.init_app(app)

with app.app_context():
    # Import routes after app and db are initialized to avoid circular imports
    from routes import *
    # Import models to ensure tables are created
    import models
    
    # Create all database tables
    db.create_all()
    
    # Log successful initialization
    app.logger.info("App initialized successfully.")
