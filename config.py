"""
Database configuration module.
Loads database connection string from environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Database configuration class"""
    
    # SQL Server connection string
    # Get the full SQLAlchemy connection string directly from .env
    CONNECTION_STRING = os.getenv('CONNECTION_STRING', '')
    
    @classmethod
    def get_connection_string(cls):
        """
        Get SQLAlchemy connection string for SQL Server
        
        Returns:
            str: Connection string for SQLAlchemy
        """
        if not cls.CONNECTION_STRING:
            raise ValueError("CONNECTION_STRING not found in .env file. Please configure your database connection.")
        
        return cls.CONNECTION_STRING
