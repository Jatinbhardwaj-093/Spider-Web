#!/usr/bin/env python3
# filepath: /Users/jatinbhardwaj/Documents/TDS-Project1/Backend/scripts/setup_database.py
"""
Database setup script for the Discourse Forum backend.
This script will:
1. Create the database if it doesn't exist
2. Install required PostgreSQL extensions
3. Run Alembic migrations
4. Optionally load sample data
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from database.connection import get_database_url, initialize_database
from database.models import Base

def check_postgresql_connection():
    """Check if PostgreSQL is running and accessible"""
    try:
        # Try to connect to PostgreSQL (without specifying a database)
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        username = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "password")
        
        engine = create_engine(f"postgresql://{username}:{password}@{host}:{port}/postgres")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ PostgreSQL connection successful")
        return True
    except Exception as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        print("\nPlease ensure PostgreSQL is running and the connection details are correct.")
        print("Check your .env file or environment variables:")
        print(f"  POSTGRES_HOST: {os.getenv('POSTGRES_HOST', 'localhost')}")
        print(f"  POSTGRES_PORT: {os.getenv('POSTGRES_PORT', '5432')}")
        print(f"  POSTGRES_USER: {os.getenv('POSTGRES_USER', 'postgres')}")
        print(f"  POSTGRES_DB: {os.getenv('POSTGRES_DB', 'discourse_forum')}")
        return False

def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    try:
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        username = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "password")
        database = os.getenv("POSTGRES_DB", "discourse_forum")
        
        # Connect to PostgreSQL without specifying a database
        engine = create_engine(f"postgresql://{username}:{password}@{host}:{port}/postgres")
        
        with engine.connect() as conn:
            conn.execute(text("COMMIT"))  # End any existing transaction
            
            # Check if database exists
            result = conn.execute(text(
                "SELECT 1 FROM pg_database WHERE datname = :db_name"
            ), {"db_name": database})
            
            if result.fetchone() is None:
                print(f"Creating database '{database}'...")
                conn.execute(text(f'CREATE DATABASE "{database}"'))
                print(f"✓ Database '{database}' created successfully")
            else:
                print(f"✓ Database '{database}' already exists")
                
    except Exception as e:
        print(f"✗ Failed to create database: {e}")
        return False
    
    return True

def run_alembic_migration():
    """Run Alembic migrations"""
    try:
        print("Running Alembic migrations...")
        
        # First, initialize Alembic if not already done
        result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if "No current revision" in result.stdout or result.returncode != 0:
            print("Initializing Alembic...")
            subprocess.run(
                ["alembic", "stamp", "head"],
                check=True,
                cwd=Path(__file__).parent.parent
            )
        
        # Generate initial migration if no migrations exist
        versions_dir = Path(__file__).parent.parent / "alembic" / "versions"
        if not any(versions_dir.glob("*.py")):
            print("Generating initial migration...")
            subprocess.run(
                ["alembic", "revision", "--autogenerate", "-m", "Initial migration"],
                check=True,
                cwd=Path(__file__).parent.parent
            )
        
        # Run migrations
        subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True,
            cwd=Path(__file__).parent.parent
        )
        
        print("✓ Alembic migrations completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Alembic migration failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during migration: {e}")
        return False

def create_vector_indexes():
    """Create vector indexes after data is loaded"""
    try:
        engine = create_engine(get_database_url())
        with engine.connect() as conn:
            print("Creating vector indexes...")
            
            # Create IVFFlat index for post embeddings
            conn.execute(text("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_posts_embedding_ivfflat 
                ON posts USING ivfflat (content_embedding vector_cosine_ops) 
                WITH (lists = 100)
            """))
            
            print("✓ Vector indexes created successfully")
            
    except Exception as e:
        print(f"✗ Failed to create vector indexes: {e}")
        return False
    
    return True

def main():
    """Main setup function"""
    print("=== Discourse Forum Database Setup ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Check PostgreSQL connection
    if not check_postgresql_connection():
        return False
    
    # Create database
    if not create_database_if_not_exists():
        return False
    
    # Initialize database (create extensions, etc.)
    try:
        print("Initializing database extensions...")
        initialize_database()
        print("✓ Database extensions initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False
    
    # Run migrations
    if not run_alembic_migration():
        return False
    
    print("\n=== Database Setup Complete ===")
    print("\nNext steps:")
    print("1. Load data using: python scripts/load_data.py")
    print("2. Create vector indexes: python scripts/setup_database.py --create-indexes")
    print("3. Start the API server: uvicorn main:app --reload")
    
    return True

if __name__ == "__main__":
    if "--create-indexes" in sys.argv:
        load_dotenv()
        if create_vector_indexes():
            print("✓ Vector indexes created successfully")
        else:
            print("✗ Failed to create vector indexes")
            sys.exit(1)
    else:
        if not main():
            sys.exit(1)
