#!/usr/bin/env python3
"""
Alternative test for Supabase using direct DATABASE_URL.
This is useful when you have the complete connection string from Supabase.
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_with_database_url():
    """Test using DATABASE_URL environment variable."""
    
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        print("🔗 Testing with DATABASE_URL...")
        try:
            engine = create_engine(database_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"✅ Connected successfully using DATABASE_URL!")
                print(f"PostgreSQL Version: {version}")
                return True
        except Exception as e:
            print(f"❌ DATABASE_URL connection failed: {e}")
            return False
    else:
        print("⚠️  DATABASE_URL not set")
        return False

def test_with_components():
    """Test using individual components."""
    
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "postgres")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD")
    
    if not all([db_host, db_password]):
        print("❌ Missing DB_HOST or DB_PASSWORD")
        return False
    
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    print("🔗 Testing with individual components...")
    print(f"Host: {db_host}")
    print(f"Full URL: postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected successfully!")
            print(f"PostgreSQL Version: {version}")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def suggest_fixes():
    """Suggest fixes for common issues."""
    print("\n🔧 Troubleshooting Suggestions:")
    print()
    print("1. **Verify Supabase Project Status:**")
    print("   - Go to your Supabase dashboard")
    print("   - Check if your project is running (not paused)")
    print("   - Look for any maintenance notifications")
    print()
    print("2. **Check Connection Details:**")
    print("   - Go to Settings > Database in Supabase")
    print("   - Copy the exact connection string")
    print("   - The format should be: db.{project-ref}.supabase.co")
    print()
    print("3. **Alternative Connection Methods:**")
    print("   - Try using the connection pooler (pooler mode)")
    print("   - Use the direct DATABASE_URL instead of components")
    print()
    print("4. **Network Issues:**")
    print("   - Check your internet connection")
    print("   - Try from a different network")
    print("   - Some corporate networks block external databases")
    print()
    print("5. **Project Reference Format:**")
    print("   - Should be exactly as shown in Supabase dashboard")
    print("   - No extra characters or spaces")
    print("   - Case sensitive")

if __name__ == "__main__":
    print("🧪 Supabase Connection Diagnostic Tool")
    print("=" * 40)
    
    # Try DATABASE_URL first
    success1 = test_with_database_url()
    print()
    
    # Try with components
    success2 = test_with_components()
    
    if not (success1 or success2):
        suggest_fixes()
        sys.exit(1)
    else:
        print("\n🎉 Connection successful!")
        sys.exit(0)
