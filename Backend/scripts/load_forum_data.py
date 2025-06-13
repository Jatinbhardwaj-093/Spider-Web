#!/usr/bin/env python3
"""
Script to load actual forum data from JSON files into the database.
This will replace the sample data with real forum content.
"""

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from database.connection import get_session
from datetime import datetime

def load_forum_data_from_json(json_file_path: str):
    """Load forum data from a JSON file into the database."""
    session = get_session()
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loading data from {json_file_path}")
        
        # Clear existing data
        print("Clearing existing data...")
        session.execute(text("DELETE FROM posts"))
        session.execute(text("DELETE FROM topics"))
        session.execute(text("DELETE FROM categories"))
        session.execute(text("DELETE FROM users"))
        session.commit()
        
        # Load users
        if 'users' in data:
            print(f"Loading {len(data['users'])} users...")
            for user in data['users']:
                session.execute(text("""
                    INSERT INTO users (id, username, name, trust_level, moderator, admin, staff, created_at)
                    VALUES (:id, :username, :name, :trust_level, :moderator, :admin, :staff, :created_at)
                """), {
                    'id': user.get('id'),
                    'username': user.get('username', ''),
                    'name': user.get('name', ''),
                    'trust_level': user.get('trust_level', 1),
                    'moderator': user.get('moderator', False),
                    'admin': user.get('admin', False),
                    'staff': user.get('staff', False),
                    'created_at': datetime.now()
                })
        
        # Load categories
        if 'categories' in data:
            print(f"Loading {len(data['categories'])} categories...")
            for category in data['categories']:
                session.execute(text("""
                    INSERT INTO categories (id, name, slug, color, description, topic_count, post_count)
                    VALUES (:id, :name, :slug, :color, :description, :topic_count, :post_count)
                """), {
                    'id': category.get('id'),
                    'name': category.get('name', ''),
                    'slug': category.get('slug', ''),
                    'color': category.get('color', '#0088CC'),
                    'description': category.get('description', ''),
                    'topic_count': category.get('topic_count', 0),
                    'post_count': category.get('post_count', 0)
                })
        
        # Load topics
        if 'topics' in data:
            print(f"Loading {len(data['topics'])} topics...")
            for topic in data['topics']:
                session.execute(text("""
                    INSERT INTO topics (id, title, slug, category_id, user_id, posts_count, reply_count, views, likes, created_at, updated_at, last_posted_at, pinned, closed, archived, visible)
                    VALUES (:id, :title, :slug, :category_id, :user_id, :posts_count, :reply_count, :views, :likes, :created_at, :updated_at, :last_posted_at, :pinned, :closed, :archived, :visible)
                """), {
                    'id': topic.get('id'),
                    'title': topic.get('title', ''),
                    'slug': topic.get('slug', ''),
                    'category_id': topic.get('category_id', 1),
                    'user_id': topic.get('user_id', 1),
                    'posts_count': topic.get('posts_count', 0),
                    'reply_count': topic.get('reply_count', 0),
                    'views': topic.get('views', 0),
                    'likes': topic.get('likes', 0),
                    'created_at': datetime.now(),
                    'updated_at': datetime.now(),
                    'last_posted_at': datetime.now(),
                    'pinned': topic.get('pinned', False),
                    'closed': topic.get('closed', False),
                    'archived': topic.get('archived', False),
                    'visible': topic.get('visible', True)
                })
        
        # Load posts
        if 'posts' in data:
            print(f"Loading {len(data['posts'])} posts...")
            for post in data['posts']:
                session.execute(text("""
                    INSERT INTO posts (id, post_number, topic_id, user_id, cooked, raw, reads, score, reply_count, quote_count, created_at, updated_at, hidden, deleted_at, accepted_answer)
                    VALUES (:id, :post_number, :topic_id, :user_id, :cooked, :raw, :reads, :score, :reply_count, :quote_count, :created_at, :updated_at, :hidden, :deleted_at, :accepted_answer)
                """), {
                    'id': post.get('id'),
                    'post_number': post.get('post_number', 1),
                    'topic_id': post.get('topic_id'),
                    'user_id': post.get('user_id', 1),
                    'cooked': post.get('cooked', ''),
                    'raw': post.get('raw', ''),
                    'reads': post.get('reads', 0),
                    'score': post.get('score', 0.0),
                    'reply_count': post.get('reply_count', 0),
                    'quote_count': post.get('quote_count', 0),
                    'created_at': datetime.now(),
                    'updated_at': datetime.now(),
                    'hidden': post.get('hidden', False),
                    'deleted_at': None,
                    'accepted_answer': post.get('accepted_answer', False)
                })
        
        session.commit()
        
        # Verify the data
        result = session.execute(text("SELECT COUNT(*) FROM posts"))
        post_count = result.scalar()
        
        result = session.execute(text("SELECT COUNT(*) FROM topics"))
        topic_count = result.scalar()
        
        result = session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        
        print(f"Successfully loaded: {user_count} users, {topic_count} topics, {post_count} posts")
        
    except Exception as e:
        session.rollback()
        print(f"Error loading forum data: {e}")
        raise
    finally:
        session.close()

def create_sample_json_format():
    """Create a sample JSON file showing the expected format."""
    sample_data = {
        "users": [
            {
                "id": 1,
                "username": "sample_user",
                "name": "Sample User",
                "trust_level": 1,
                "moderator": False,
                "admin": False,
                "staff": False
            }
        ],
        "categories": [
            {
                "id": 1,
                "name": "General Discussion",
                "slug": "general",
                "color": "#0088CC",
                "description": "General course discussions",
                "topic_count": 0,
                "post_count": 0
            }
        ],
        "topics": [
            {
                "id": 1,
                "title": "Sample Topic",
                "slug": "sample-topic",
                "category_id": 1,
                "user_id": 1,
                "posts_count": 1,
                "reply_count": 0,
                "views": 10,
                "likes": 0,
                "pinned": False,
                "closed": False,
                "archived": False,
                "visible": True
            }
        ],
        "posts": [
            {
                "id": 1,
                "post_number": 1,
                "topic_id": 1,
                "user_id": 1,
                "cooked": "<p>This is a sample post content in HTML format</p>",
                "raw": "This is a sample post content in markdown format",
                "reads": 5,
                "score": 0.5,
                "reply_count": 0,
                "quote_count": 0,
                "hidden": False,
                "accepted_answer": False
            }
        ]
    }
    
    with open('sample_forum_data.json', 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    print("Created sample_forum_data.json with expected format")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python load_forum_data.py <path_to_json_file>")
        print("       python load_forum_data.py --sample (to create sample format)")
        sys.exit(1)
    
    if sys.argv[1] == "--sample":
        create_sample_json_format()
    else:
        json_file = sys.argv[1]
        if not Path(json_file).exists():
            print(f"File not found: {json_file}")
            sys.exit(1)
        
        load_forum_data_from_json(json_file)
