import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from sentence_transformers import SentenceTransformer
import numpy as np
from database.connection import get_session
from database.models import Post, Topic
import re
from tqdm import tqdm

def clean_html_content(content: str) -> str:
    """Clean HTML content by removing tags and decoding entities."""
    if not content:
        return ""
    
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', content)
    
    # Decode HTML entities
    import html
    clean = html.unescape(clean)
    
    # Clean up extra whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    return clean

def generate_embeddings():
    """Generate and store embeddings for all posts."""
    print("🚀 Starting embedding generation process...")
    
    # Initialize the embedding model
    print("📦 Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print(f"✅ Model loaded with embedding dimension: {model.get_sentence_embedding_dimension()}")
    
    session = get_session()
    
    try:
        # Get all posts that don't have embeddings yet
        print("🔍 Fetching posts without embeddings...")
        posts = session.query(Post).filter(Post.content_embedding.is_(None)).all()
        
        if not posts:
            print("✅ All posts already have embeddings!")
            return
        
        print(f"📊 Found {len(posts)} posts to process...")
        
        # Process posts in batches for better performance
        batch_size = 10
        total_batches = (len(posts) + batch_size - 1) // batch_size
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min((batch_idx + 1) * batch_size, len(posts))
            batch_posts = posts[start_idx:end_idx]
            
            print(f"\n📦 Processing batch {batch_idx + 1}/{total_batches} ({len(batch_posts)} posts)...")
            
            # Prepare content for embedding
            contents = []
            valid_posts = []
            
            for post in batch_posts:
                # Combine raw and cooked content
                content = ""
                if post.raw:
                    content += clean_html_content(post.raw) + " "
                if post.cooked:
                    content += clean_html_content(post.cooked)
                
                content = content.strip()
                
                if len(content) > 10:  # Only process posts with meaningful content
                    contents.append(content)
                    valid_posts.append(post)
                else:
                    print(f"⚠️  Skipping post {post.id} - insufficient content")
            
            if not contents:
                print("⚠️  No valid content in this batch, skipping...")
                continue
            
            # Generate embeddings for the batch
            print(f"🧠 Generating embeddings for {len(contents)} posts...")
            embeddings = model.encode(contents, show_progress_bar=True)
            
            # Store embeddings in database
            print("💾 Storing embeddings in database...")
            for post, embedding in zip(valid_posts, embeddings):
                try:
                    # Convert numpy array to list for PostgreSQL
                    embedding_list = embedding.tolist()
                    
                    # Update the post with the embedding
                    session.execute(
                        text("UPDATE posts SET content_embedding = :embedding WHERE id = :post_id"),
                        {"embedding": embedding_list, "post_id": post.id}
                    )
                    
                    print(f"✅ Updated post {post.id}")
                    
                except Exception as e:
                    print(f"❌ Error updating post {post.id}: {e}")
            
            # Commit the batch
            session.commit()
            print(f"✅ Batch {batch_idx + 1} completed successfully!")
        
        # Generate topic title embeddings
        print("\n🏷️  Generating topic title embeddings...")
        topics = session.query(Topic).filter(Topic.title_embedding.is_(None)).all()
        
        if topics:
            topic_titles = [topic.title for topic in topics if topic.title]
            if topic_titles:
                title_embeddings = model.encode(topic_titles, show_progress_bar=True)
                
                for topic, embedding in zip(topics, title_embeddings):
                    embedding_list = embedding.tolist()
                    session.execute(
                        text("UPDATE topics SET title_embedding = :embedding WHERE id = :topic_id"),
                        {"embedding": embedding_list, "topic_id": topic.id}
                    )
                
                session.commit()
                print(f"✅ Updated {len(topics)} topic title embeddings")
        
        # Verify results
        print("\n📊 Verification:")
        result = session.execute(text("SELECT COUNT(*) as total, COUNT(content_embedding) as with_embeddings FROM posts"))
        row = result.fetchone()
        print(f"Total posts: {row.total}")
        print(f"Posts with embeddings: {row.with_embeddings}")
        print(f"Coverage: {(row.with_embeddings / row.total * 100):.1f}%")
        
        print("\n🎉 Embedding generation completed successfully!")
        print("🔍 Your RAG system now has semantic search capabilities!")
        
    except Exception as e:
        print(f"❌ Error during embedding generation: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("🤖 RAG System Embedding Generator")
    print("=" * 50)
    
    try:
        generate_embeddings()
        print("\n✅ Process completed successfully!")
        print("💡 You can now test semantic search with: python rag_manager.py --search 'your query'")
    except KeyboardInterrupt:
        print("\n⛔ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Process failed: {e}")
        sys.exit(1)
