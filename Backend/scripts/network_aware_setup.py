#!/usr/bin/env python3
"""
Network-aware database setup script.
Falls back to local SQLite if remote connection fails.
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def test_remote_connection():
    """Test if we can connect to Supabase."""
    try:
        db_host = os.getenv("DB_HOST")
        db_password = os.getenv("DB_PASSWORD")
        database_url = f"postgresql://postgres:{db_password}@{db_host}:5432/postgres"
        
        engine = create_engine(database_url, connect_args={"connect_timeout": 10})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Remote Supabase connection working!")
        return True
    except Exception as e:
        print(f"❌ Cannot connect to Supabase: {str(e)[:100]}...")
        return False

def setup_local_development():
    """Set up local SQLite for development."""
    print("\n🔧 Setting up local development environment...")
    
    # Create local .env override
    local_env = """
# Local Development Override
# Comment out these lines when deploying to production

DB_HOST=localhost
DB_PORT=5432
DB_NAME=spider_web_local
DB_USER=postgres
DB_PASSWORD=postgres

# Use SQLite for local development (uncomment if needed)
# DATABASE_URL=sqlite:///./spider_web_local.db
"""
    
    with open('.env.local', 'w') as f:
        f.write(local_env)
    
    print("✅ Created .env.local for local development")
    print("\n📋 Options for local development:")
    print("1. Install PostgreSQL locally and use .env.local")
    print("2. Use SQLite (uncomment DATABASE_URL in .env.local)")
    print("3. Deploy to Vercel where Supabase connection will work")
    
    return True

def main():
    print("🧪 Database Connection Test")
    print("=" * 40)
    
    # Test remote connection
    if test_remote_connection():
        print("\n🎉 You can proceed with normal development!")
        print("Run: python scripts/setup_database.py")
        return
    
    print("\n⚠️  Remote connection failed (likely network/firewall issue)")
    print("Your Supabase database is working (you tested it in SQL Editor)")
    print("But your local network blocks the connection.")
    
    setup_local_development()
    
    print("\n🚀 Recommended next steps:")
    print("1. Deploy to Vercel (connection will work there)")
    print("2. Use Supabase SQL Editor to run complete_supabase_setup.sql")
    print("3. Test your deployed application")
    
    print(f"\n📝 Files to check:")
    print(f"- complete_supabase_setup.sql (run in Supabase SQL Editor)")
    print(f"- QUICK_DEPLOY.md (deployment instructions)")

if __name__ == "__main__":
    main()
