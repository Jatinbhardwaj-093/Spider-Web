#!/usr/bin/env python3
"""
RAG System Management Script
Provides utilities to manage the RAG system, test search functionality, and load data.
"""

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from database.connection import get_session
from services.search import SearchService
import argparse

def test_search(query: str, limit: int = 10):
    """Test the search functionality with a given query."""
    session = get_session()
    search_service = SearchService(session)
    
    print(f"\n🔍 Testing search for: '{query}'")
    print("=" * 50)
    
    try:
        # Test comprehensive search
        results = search_service.comprehensive_search(query, limit)
        
        if not results:
            print("❌ No results found")
            return
        
        print(f"✅ Found {len(results)} results:")
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Topic: {result.get('topic_title', 'N/A')}")
            print(f"   Score: {result.get('search_score', 0):.2f}")
            print(f"   Method: {result.get('search_method', 'N/A')}")
            
            content = result.get('content', '') or result.get('cooked', '') or result.get('raw', '')
            if content:
                preview = content[:150] + "..." if len(content) > 150 else content
                # Remove HTML tags for preview
                import re
                clean_preview = re.sub(r'<[^>]+>', '', preview)
                print(f"   Preview: {clean_preview}")
            
            url = f"https://discourse.onlinedegree.iitm.ac.in/t/{result.get('topic_id')}"
            if result.get('post_id', 0) > 1:
                url += f"/{result.get('post_id')}"
            print(f"   URL: {url}")
    
    except Exception as e:
        print(f"❌ Search failed: {e}")
    finally:
        session.close()

def show_database_stats():
    """Show database statistics."""
    session = get_session()
    
    try:
        print("\n📊 Database Statistics")
        print("=" * 30)
        
        # Count tables
        tables = ['users', 'categories', 'topics', 'posts']
        
        for table in tables:
            result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"{table.capitalize()}: {count}")
        
        # Show recent topics
        print("\n📋 Recent Topics:")
        result = session.execute(text("""
            SELECT title, created_at, posts_count 
            FROM topics 
            ORDER BY created_at DESC 
            LIMIT 5
        """))
        
        for row in result:
            print(f"  • {row.title} ({row.posts_count} posts)")
    
    except Exception as e:
        print(f"❌ Database query failed: {e}")
    finally:
        session.close()

def test_rag_endpoint(question: str, image: str = None):
    """Test the RAG endpoint with a question."""
    import requests
    
    print(f"\n🤖 Testing RAG endpoint")
    print("=" * 30)
    print(f"Question: {question}")
    
    payload = {"question": question}
    if image:
        payload["image"] = image
    
    try:
        response = requests.post(
            "http://localhost:8000/api/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Answer: {data.get('answer', 'No answer')}")
            
            links = data.get('links', [])
            if links:
                print(f"\n🔗 Found {len(links)} relevant links:")
                for i, link in enumerate(links, 1):
                    print(f"  {i}. {link.get('url', 'No URL')}")
                    print(f"     {link.get('text', 'No text')[:100]}...")
            else:
                print("\n🔗 No relevant links found")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Request failed: {e}")

def interactive_mode():
    """Start interactive testing mode."""
    print("\n🎯 Interactive RAG Testing Mode")
    print("Type 'quit' to exit, 'stats' for database stats")
    print("=" * 50)
    
    while True:
        try:
            question = input("\n💬 Enter your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif question.lower() == 'stats':
                show_database_stats()
                continue
            elif not question:
                continue
            
            # Test both search and RAG endpoint
            test_search(question, limit=5)
            test_rag_endpoint(question)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="RAG System Management")
    parser.add_argument('--search', '-s', help='Test search with a query')
    parser.add_argument('--question', '-q', help='Test RAG endpoint with a question')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    parser.add_argument('--interactive', '-i', action='store_true', help='Start interactive mode')
    parser.add_argument('--limit', '-l', type=int, default=10, help='Limit search results')
    
    args = parser.parse_args()
    
    if args.stats:
        show_database_stats()
    elif args.search:
        test_search(args.search, args.limit)
    elif args.question:
        test_rag_endpoint(args.question)
    elif args.interactive:
        interactive_mode()
    else:
        parser.print_help()
        print("\n💡 Quick start: python rag_manager.py --interactive")

if __name__ == "__main__":
    main()
