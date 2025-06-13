"""
Database configuration and connection management for PostgreSQL with pgvector.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import logging

from .models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration class."""
    
    def __init__(self):
        # Database connection parameters
        self.DB_HOST = os.getenv("DB_HOST", "localhost")
        self.DB_PORT = os.getenv("DB_PORT", "5432")
        self.DB_NAME = os.getenv("DB_NAME", "discourse_forum")
        self.DB_USER = os.getenv("DB_USER", "postgres")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
        
        # Connection pool settings
        self.POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
        self.MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        
        # Vector database settings
        self.VECTOR_DIMENSIONS = int(os.getenv("VECTOR_DIMENSIONS", "1536"))  # OpenAI ada-002
        self.IVFFLAT_LISTS = int(os.getenv("IVFFLAT_LISTS", "100"))  # For vector index
        
    @property
    def database_url(self) -> str:
        """Construct database URL."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

# Global configuration instance
config = DatabaseConfig()

class DatabaseManager:
    """Database manager for handling connections and operations."""
    
    def __init__(self):
        self.config = config
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize database engine with optimized settings."""
        self.engine = create_engine(
            self.config.database_url,
            poolclass=QueuePool,
            pool_size=self.config.POOL_SIZE,
            max_overflow=self.config.MAX_OVERFLOW,
            pool_timeout=self.config.POOL_TIMEOUT,
            pool_recycle=self.config.POOL_RECYCLE,
            pool_pre_ping=True,  # Validate connections before use
            echo=os.getenv("SQL_ECHO", "false").lower() == "true",  # SQL logging
            future=True,  # Use SQLAlchemy 2.0 style
        )
        
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
    
    def create_database(self):
        """Create database if it doesn't exist."""
        try:
            # Connect to postgres database to create our target database
            postgres_url = f"postgresql://{self.config.DB_USER}:{self.config.DB_PASSWORD}@{self.config.DB_HOST}:{self.config.DB_PORT}/postgres"
            temp_engine = create_engine(postgres_url, isolation_level="AUTOCOMMIT")
            
            with temp_engine.connect() as conn:
                # Check if database exists
                result = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                    {"db_name": self.config.DB_NAME}
                )
                
                if not result.fetchone():
                    logger.info(f"Creating database: {self.config.DB_NAME}")
                    conn.execute(text(f"CREATE DATABASE {self.config.DB_NAME}"))
                    logger.info("Database created successfully")
                else:
                    logger.info("Database already exists")
            
            temp_engine.dispose()
            
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            raise
    
    def setup_extensions(self):
        """Set up required PostgreSQL extensions."""
        try:
            with self.engine.connect() as conn:
                # Enable pgvector extension
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))  # For text similarity
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gin"))  # For GIN indexes
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_stat_statements"))  # For query statistics
                conn.commit()
                logger.info("PostgreSQL extensions enabled successfully")
                
        except Exception as e:
            logger.error(f"Error setting up extensions: {e}")
            raise
    
    def create_tables(self):
        """Create all database tables."""
        try:
            logger.info("Creating database tables...")
            Base.metadata.create_all(bind=self.engine)
            logger.info("Tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def setup_search_indexes(self):
        """Set up additional search and performance indexes."""
        try:
            with self.engine.connect() as conn:
                # Full-text search indexes
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_posts_fulltext_search 
                    ON posts USING gin(to_tsvector('english', cooked || ' ' || raw))
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_topics_fulltext_search 
                    ON topics USING gin(to_tsvector('english', title))
                """))
                
                # Partial indexes for performance
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_posts_visible_recent 
                    ON posts (created_at DESC) 
                    WHERE hidden = false AND deleted_at IS NULL
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_topics_active 
                    ON topics (last_posted_at DESC) 
                    WHERE visible = true AND closed = false
                """))
                
                # Composite indexes for common queries
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_posts_topic_user_date 
                    ON posts (topic_id, user_id, created_at)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_posts_score_reads 
                    ON posts (score DESC, reads DESC) 
                    WHERE hidden = false
                """))
                
                conn.commit()
                logger.info("Additional search indexes created successfully")
                
        except Exception as e:
            logger.error(f"Error creating search indexes: {e}")
            raise
    
    def setup_vector_indexes(self):
        """Set up vector similarity search indexes."""
        try:
            with self.engine.connect() as conn:
                # Set up ivfflat indexes for vector similarity search
                # These are created after data is loaded for better performance
                logger.info("Setting up vector similarity indexes...")
                
                # Posts content embeddings
                conn.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS idx_posts_embedding_ivfflat
                    ON posts USING ivfflat (content_embedding vector_cosine_ops)
                    WITH (lists = {self.config.IVFFLAT_LISTS})
                """))
                
                # Topic title embeddings
                conn.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS idx_topics_title_embedding_ivfflat
                    ON topics USING ivfflat (title_embedding vector_cosine_ops)
                    WITH (lists = {self.config.IVFFLAT_LISTS})
                """))
                
                # Topic content summary embeddings
                conn.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS idx_topics_content_embedding_ivfflat
                    ON topics USING ivfflat (content_summary_embedding vector_cosine_ops)
                    WITH (lists = {self.config.IVFFLAT_LISTS})
                """))
                
                # Embedding cache
                conn.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS idx_embedding_cache_ivfflat
                    ON embedding_cache USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = {self.config.IVFFLAT_LISTS})
                """))
                
                conn.commit()
                logger.info("Vector similarity indexes created successfully")
                
        except Exception as e:
            logger.error(f"Error creating vector indexes: {e}")
            raise
    
    def optimize_database(self):
        """Apply database optimizations."""
        try:
            with self.engine.connect() as conn:
                # Analyze tables for better query planning
                conn.execute(text("ANALYZE"))
                
                # Update table statistics
                conn.execute(text("SELECT pg_stat_reset()"))
                
                # Set optimized configuration for vector operations
                conn.execute(text("SET maintenance_work_mem = '256MB'"))
                conn.execute(text("SET max_parallel_workers_per_gather = 4"))
                conn.execute(text("SET random_page_cost = 1.0"))  # SSD optimized
                
                conn.commit()
                logger.info("Database optimization completed")
                
        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            raise
    
    def initialize_database(self):
        """Complete database initialization."""
        logger.info("Starting database initialization...")
        
        self.create_database()
        self.setup_extensions()
        self.create_tables()
        self.setup_search_indexes()
        self.optimize_database()
        
        logger.info("Database initialization completed successfully")
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with proper cleanup."""
        session = self.SessionLocal()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_session_sync(self) -> Session:
        """Get database session (sync version)."""
        return self.SessionLocal()
    
    def health_check(self) -> bool:
        """Check database connectivity and health."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return result.fetchone()[0] == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get database statistics."""
        try:
            with self.engine.connect() as conn:
                # Table sizes
                tables_query = text("""
                    SELECT 
                        schemaname,
                        tablename,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                        pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY size_bytes DESC
                """)
                
                tables_result = conn.execute(tables_query).fetchall()
                
                # Database size
                db_size_query = text("""
                    SELECT pg_size_pretty(pg_database_size(current_database())) as db_size
                """)
                
                db_size_result = conn.execute(db_size_query).fetchone()
                
                # Connection stats
                conn_stats_query = text("""
                    SELECT 
                        count(*) as total_connections,
                        count(*) FILTER (WHERE state = 'active') as active_connections,
                        count(*) FILTER (WHERE state = 'idle') as idle_connections
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                """)
                
                conn_stats_result = conn.execute(conn_stats_query).fetchone()
                
                return {
                    "database_size": db_size_result[0],
                    "tables": [
                        {
                            "schema": row[0],
                            "name": row[1],
                            "size": row[2],
                            "size_bytes": row[3]
                        }
                        for row in tables_result
                    ],
                    "connections": {
                        "total": conn_stats_result[0],
                        "active": conn_stats_result[1],
                        "idle": conn_stats_result[2]
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

# Global database manager instance
db = DatabaseManager()

# Convenience functions for compatibility
def test_connection() -> bool:
    """Test database connection."""
    return db.health_check()

def get_session() -> Session:
    """Get database session."""
    return db.get_session_sync()

def get_database_url() -> str:
    """Get database URL."""
    return config.database_url

def initialize_database():
    """Initialize database."""
    return db.initialize_database()

# Dependency for FastAPI
def get_database() -> Generator[Session, None, None]:
    """Dependency to get database session in FastAPI endpoints."""
    with db.get_session() as session:
        yield session
