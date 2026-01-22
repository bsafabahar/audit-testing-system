"""
Database connection and session management module.
Handles SQLAlchemy engine creation and session lifecycle.
"""
from typing import Any, Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import NullPool
from config import Config

# Create the declarative base for model definitions
Base = declarative_base()


class ReadOnlySession:
    """
    Read-only session wrapper that prevents write operations.
    Only SELECT queries are allowed.
    """
    def __init__(self, session: Session) -> None:
        """
        Initialize read-only session wrapper
        
        Args:
            session: SQLAlchemy session to wrap
        """
        self._session = session
        # Disable autoflush to prevent automatic writes
        self._session.autoflush = False
    
    def query(self, *args: Any, **kwargs: Any) -> Any:
        """
        Allow SELECT queries
        
        Returns:
            Query object
        """
        return self._session.query(*args, **kwargs)
    
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Allow execute for SELECT queries
        
        Returns:
            Result object
        """
        return self._session.execute(*args, **kwargs)
    
    def get(self, *args: Any, **kwargs: Any) -> Any:
        """
        Allow get operations
        
        Returns:
            Entity instance or None
        """
        return self._session.get(*args, **kwargs)
    
    def close(self) -> None:
        """Close the underlying session"""
        self._session.close()
    
    def rollback(self) -> None:
        """Allow rollback"""
        self._session.rollback()
    
    # Block write operations
    def add(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("Write operations are not allowed. Session is read-only.")
    
    def add_all(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("Write operations are not allowed. Session is read-only.")
    
    def delete(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("Write operations are not allowed. Session is read-only.")
    
    def commit(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("Write operations are not allowed. Session is read-only.")
    
    def flush(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("Write operations are not allowed. Session is read-only.")
    
    def merge(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("Write operations are not allowed. Session is read-only.")
    
    def bulk_save_objects(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("Write operations are not allowed. Session is read-only.")
    
    def bulk_insert_mappings(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("Write operations are not allowed. Session is read-only.")
    
    def bulk_update_mappings(self, *args: Any, **kwargs: Any) -> None:
        raise PermissionError("Write operations are not allowed. Session is read-only.")


class Database:
    """Database connection manager"""
    
    def __init__(self) -> None:
        """Initialize database engine and session factory"""
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self._initialized: bool = False
    
    def _initialize(self) -> None:
        """Create database engine and session factory (lazy initialization)"""
        if self._initialized:
            return
            
        try:
            connection_string = Config.get_connection_string()
            
            # Create engine with connection pooling disabled for SQL Server
            self.engine = create_engine(
                connection_string,
                poolclass=NullPool,
                echo=False,  # Set to True to see SQL queries in console
                future=True
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self._initialized = True
            
        except Exception as e:
            print(f"✗ Error initializing database connection: {e}")
            raise
    
    def get_session(self) -> ReadOnlySession:
        """
        Create and return a new read-only database session
        
        Returns:
            ReadOnlySession: Read-only SQLAlchemy session wrapper
            
        Raises:
            Exception: If database is not initialized
        """
        if not self._initialized:
            self._initialize()
        if self.SessionLocal is None:
            raise Exception("Database not initialized")
        session = self.SessionLocal()
        return ReadOnlySession(session)
    
    def test_connection(self) -> bool:
        """
        Test the database connection
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            if not self._initialized:
                self._initialize()
            from sqlalchemy import text
            if self.engine is None:
                return False
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"✗ Database connection test failed: {e}")
            return False

# Global database instance
db = Database()

def get_db() -> ReadOnlySession:
    """
    Dependency function to get database session.
    Use this in your queries to get a session.
    
    Usage:
        session = get_db()
        try:
            # Your query operations
            result = session.query(YourModel).all()
        finally:
            session.close()
    
    Returns:
        ReadOnlySession: Read-only SQLAlchemy session wrapper
    """
    return db.get_session()
