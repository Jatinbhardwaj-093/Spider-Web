"""
Search service for Discourse forum data with vector similarity search capabilities.
Provides full-text search, semantic search, and vector similarity search.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import text, func, desc
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from database.models import Post, User, Topic, Category, PostReaction

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching forum data with various methods."""
    
    def __init__(self, session: Session, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize search service with database session and embedding model."""
        self.session = session
        self.model = SentenceTransformer(model_name)
        logger.info(f"Initialized SearchService with model: {model_name}")
    
    def full_text_search(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        category_id: Optional[int] = None,
        topic_id: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Perform full-text search on post content and titles.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            offset: Offset for pagination
            category_id: Optional category filter
            topic_id: Optional topic filter
            
        Returns:
            Tuple of (search results, total count)
        """
        # Build the search query
        search_conditions = []
        params = {"query": f"%{query}%"}
        
        # Base search condition
        search_conditions.append(
            "(posts.content ILIKE :query OR topics.title ILIKE :query)"
        )
        
        # Add filters
        if category_id:
            search_conditions.append("topics.category_id = :category_id")
            params["category_id"] = category_id
            
        if topic_id:
            search_conditions.append("posts.topic_id = :topic_id")
            params["topic_id"] = topic_id
        
        where_clause = " AND ".join(search_conditions)
        
        # Count query
        count_query = f"""
            SELECT COUNT(DISTINCT posts.id)
            FROM posts
            JOIN topics ON posts.topic_id = topics.id
            WHERE {where_clause}
        """
        
        # Main search query with joins
        search_query = f"""
            SELECT DISTINCT 
                posts.id,
                posts.content,
                posts.created_at,
                posts.like_count,
                posts.reply_count,
                posts.trust_level,
                topics.id as topic_id,
                topics.title as topic_title,
                topics.slug as topic_slug,
                categories.id as category_id,
                categories.name as category_name,
                users.id as user_id,
                users.username,
                users.name as user_name,
                users.avatar_template
            FROM posts
            JOIN topics ON posts.topic_id = topics.id
            JOIN categories ON topics.category_id = categories.id
            LEFT JOIN users ON posts.user_id = users.id
            WHERE {where_clause}
            ORDER BY posts.created_at DESC
            LIMIT :limit OFFSET :offset
        """
        
        # Execute count query
        count_result = self.session.execute(text(count_query), params)
        total_count = count_result.scalar()
        
        # Execute search query
        params.update({"limit": limit, "offset": offset})
        result = self.session.execute(text(search_query), params)
        rows = result.fetchall()
        
        # Format results
        results = []
        for row in rows:
            results.append({
                "post_id": row.id,
                "content": row.content[:500] + "..." if len(row.content) > 500 else row.content,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "like_count": row.like_count,
                "reply_count": row.reply_count,
                "trust_level": row.trust_level,
                "topic": {
                    "id": row.topic_id,
                    "title": row.topic_title,
                    "slug": row.topic_slug
                },
                "category": {
                    "id": row.category_id,
                    "name": row.category_name
                },
                "user": {
                    "id": row.user_id,
                    "username": row.username,
                    "name": row.user_name,
                    "avatar_template": row.avatar_template
                } if row.user_id else None,
                "search_type": "full_text"
            })
        
        logger.info(f"Full-text search for '{query}' returned {len(results)} results")
        return results, total_count

    def semantic_search(
        self,
        query: str,
        limit: int = 20,
        similarity_threshold: float = 0.3,
        category_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using vector embeddings.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            category_id: Optional category filter
            
        Returns:
            List of search results with similarity scores
        """
        # Generate embedding for query
        query_embedding = self.model.encode([query])[0]
        
        # Build query with optional category filter
        filter_clause = ""
        params = {"limit": limit, "threshold": similarity_threshold}
        
        if category_id:
            filter_clause = "AND topics.category_id = :category_id"
            params["category_id"] = category_id
        
        # Use pgvector cosine distance for similarity search
        search_query = f"""
            SELECT 
                posts.id,
                posts.content,
                posts.content_embedding,
                posts.created_at,
                posts.like_count,
                posts.reply_count,
                topics.id as topic_id,
                topics.title as topic_title,
                categories.id as category_id,
                categories.name as category_name,
                users.username,
                users.name as user_name,
                (1 - (posts.content_embedding <=> :query_embedding::vector)) as similarity_score
            FROM posts
            JOIN topics ON posts.topic_id = topics.id
            JOIN categories ON topics.category_id = categories.id
            LEFT JOIN users ON posts.user_id = users.id
            WHERE posts.content_embedding IS NOT NULL
            {filter_clause}
            AND (1 - (posts.content_embedding <=> :query_embedding::vector)) >= :threshold
            ORDER BY similarity_score DESC
            LIMIT :limit
        """
        
        params["query_embedding"] = query_embedding.tolist()
        
        result = self.session.execute(text(search_query), params)
        rows = result.fetchall()
        
        # Format results
        results = []
        for row in rows:
            results.append({
                "post_id": row.id,
                "content": row.content[:500] + "..." if len(row.content) > 500 else row.content,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "like_count": row.like_count,
                "reply_count": row.reply_count,
                "similarity_score": float(row.similarity_score),
                "topic": {
                    "id": row.topic_id,
                    "title": row.topic_title
                },
                "category": {
                    "id": row.category_id,
                    "name": row.category_name
                },
                "user": {
                    "username": row.username,
                    "name": row.user_name
                } if row.username else None,
                "search_type": "semantic"
            })
        
        logger.info(f"Semantic search for '{query}' returned {len(results)} results")
        return results

    def hybrid_search(
        self,
        query: str,
        limit: int = 20,
        semantic_weight: float = 0.6,
        text_weight: float = 0.4,
        category_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining full-text and semantic search.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            semantic_weight: Weight for semantic search results
            text_weight: Weight for full-text search results
            category_id: Optional category filter
            
        Returns:
            List of combined search results with hybrid scores
        """
        # Get results from both search methods
        text_results, _ = self.full_text_search(
            query, limit=limit*2, category_id=category_id
        )
        semantic_results = self.semantic_search(
            query, limit=limit*2, category_id=category_id
        )
        
        # Combine and score results
        combined_results = {}
        
        # Add full-text results with normalized scores
        for i, result in enumerate(text_results):
            post_id = result["post_id"]
            text_score = 1.0 - (i / len(text_results))  # Higher rank = higher score
            combined_results[post_id] = {
                **result,
                "text_score": text_score,
                "semantic_score": 0.0,
                "hybrid_score": text_score * text_weight
            }
        
        # Add semantic results and update scores
        for result in semantic_results:
            post_id = result["post_id"]
            semantic_score = result["similarity_score"]
            
            if post_id in combined_results:
                # Update existing result
                combined_results[post_id]["semantic_score"] = semantic_score
                combined_results[post_id]["hybrid_score"] = (
                    combined_results[post_id]["text_score"] * text_weight +
                    semantic_score * semantic_weight
                )
                combined_results[post_id]["search_type"] = "hybrid"
            else:
                # Add new result
                combined_results[post_id] = {
                    **result,
                    "text_score": 0.0,
                    "semantic_score": semantic_score,
                    "hybrid_score": semantic_score * semantic_weight,
                    "search_type": "hybrid"
                }
        
        # Sort by hybrid score and return top results
        sorted_results = sorted(
            combined_results.values(),
            key=lambda x: x["hybrid_score"],
            reverse=True
        )
        
        logger.info(f"Hybrid search for '{query}' returned {len(sorted_results[:limit])} results")
        return sorted_results[:limit]

    def find_similar_posts(
        self,
        post_id: int,
        limit: int = 10,
        similarity_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Find posts similar to a given post using vector similarity.
        
        Args:
            post_id: ID of the reference post
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar posts with similarity scores
        """
        # Get the reference post's embedding
        ref_query = """
            SELECT content_embedding 
            FROM posts 
            WHERE id = :post_id AND content_embedding IS NOT NULL
        """
        
        ref_result = self.session.execute(text(ref_query), {"post_id": post_id})
        ref_row = ref_result.fetchone()
        
        if not ref_row or not ref_row.content_embedding:
            logger.warning(f"No embedding found for post {post_id}")
            return []
        
        # Find similar posts
        similarity_query = """
            SELECT 
                posts.id,
                posts.content,
                posts.created_at,
                posts.like_count,
                topics.id as topic_id,
                topics.title as topic_title,
                categories.name as category_name,
                users.username,
                (1 - (posts.content_embedding <=> :ref_embedding::vector)) as similarity_score
            FROM posts
            JOIN topics ON posts.topic_id = topics.id
            JOIN categories ON topics.category_id = categories.id
            LEFT JOIN users ON posts.user_id = users.id
            WHERE posts.id != :post_id
            AND posts.content_embedding IS NOT NULL
            AND (1 - (posts.content_embedding <=> :ref_embedding::vector)) >= :threshold
            ORDER BY similarity_score DESC
            LIMIT :limit
        """
        
        params = {
            "post_id": post_id,
            "ref_embedding": ref_row.content_embedding,
            "threshold": similarity_threshold,
            "limit": limit
        }
        
        result = self.session.execute(text(similarity_query), params)
        rows = result.fetchall()
        
        # Format results
        results = []
        for row in rows:
            results.append({
                "post_id": row.id,
                "content": row.content[:300] + "..." if len(row.content) > 300 else row.content,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "like_count": row.like_count,
                "similarity_score": float(row.similarity_score),
                "topic": {
                    "id": row.topic_id,
                    "title": row.topic_title
                },
                "category_name": row.category_name,
                "username": row.username
            })
        
        logger.info(f"Found {len(results)} similar posts for post {post_id}")
        return results

    def get_trending_topics(
        self,
        days: int = 7,
        limit: int = 10,
        category_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get trending topics based on recent activity and engagement.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of results
            category_id: Optional category filter
            
        Returns:
            List of trending topics with engagement metrics
        """
        filter_clause = ""
        params = {"days": days, "limit": limit}
        
        if category_id:
            filter_clause = "AND topics.category_id = :category_id"
            params["category_id"] = category_id
        
        trending_query = f"""
            SELECT 
                topics.id,
                topics.title,
                topics.slug,
                categories.name as category_name,
                COUNT(posts.id) as recent_posts,
                SUM(posts.like_count) as total_likes,
                AVG(posts.like_count) as avg_likes,
                MAX(posts.created_at) as last_activity,
                COUNT(DISTINCT posts.user_id) as unique_participants
            FROM topics
            JOIN categories ON topics.category_id = categories.id
            LEFT JOIN posts ON topics.id = posts.topic_id 
                AND posts.created_at >= NOW() - INTERVAL '{days} days'
            WHERE topics.created_at >= NOW() - INTERVAL '{days*2} days'
            {filter_clause}
            GROUP BY topics.id, topics.title, topics.slug, categories.name
            HAVING COUNT(posts.id) > 0
            ORDER BY 
                COUNT(posts.id) DESC,
                SUM(posts.like_count) DESC,
                MAX(posts.created_at) DESC
            LIMIT :limit
        """
        
        result = self.session.execute(text(trending_query), params)
        rows = result.fetchall()
        
        # Format results
        results = []
        for row in rows:
            results.append({
                "topic_id": row.id,
                "title": row.title,
                "slug": row.slug,
                "category_name": row.category_name,
                "recent_posts": row.recent_posts,
                "total_likes": row.total_likes or 0,
                "avg_likes": float(row.avg_likes) if row.avg_likes else 0.0,
                "last_activity": row.last_activity.isoformat() if row.last_activity else None,
                "unique_participants": row.unique_participants
            })
        
        logger.info(f"Found {len(results)} trending topics for last {days} days")
        return results

    def search_users(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for users by username or name.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of matching users with their stats
        """
        search_query = """
            SELECT 
                users.id,
                users.username,
                users.name,
                users.avatar_template,
                users.title,
                COUNT(posts.id) as post_count,
                SUM(posts.like_count) as total_likes_received,
                MAX(posts.created_at) as last_post_date
            FROM users
            LEFT JOIN posts ON users.id = posts.user_id
            WHERE users.username ILIKE :query 
               OR users.name ILIKE :query
            GROUP BY users.id, users.username, users.name, 
                     users.avatar_template, users.title
            ORDER BY post_count DESC, total_likes_received DESC
            LIMIT :limit
        """
        
        params = {"query": f"%{query}%", "limit": limit}
        result = self.session.execute(text(search_query), params)
        rows = result.fetchall()
        
        # Format results
        results = []
        for row in rows:
            results.append({
                "user_id": row.id,
                "username": row.username,
                "name": row.name,
                "avatar_template": row.avatar_template,
                "title": row.title,
                "post_count": row.post_count,
                "total_likes_received": row.total_likes_received or 0,
                "last_post_date": row.last_post_date.isoformat() if row.last_post_date else None
            })
        
        logger.info(f"User search for '{query}' returned {len(results)} results")
        return results

    def simple_search(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Simple synchronous search method using the provided session.
        """
        try:
            # Simple text search in posts
            search_query = text("""
                SELECT DISTINCT 
                    posts.id,
                    posts.cooked,
                    posts.raw,
                    posts.created_at,
                    posts.reply_count,
                    posts.topic_id,
                    topics.title as topic_title,
                    topics.slug as topic_slug,
                    categories.id as category_id,
                    categories.name as category_name,
                    users.id as user_id,
                    users.username,
                    users.name as user_name
                FROM posts
                JOIN topics ON posts.topic_id = topics.id
                JOIN categories ON topics.category_id = categories.id
                LEFT JOIN users ON posts.user_id = users.id
                WHERE posts.cooked ILIKE :query OR posts.raw ILIKE :query OR topics.title ILIKE :query
                ORDER BY posts.created_at DESC
                LIMIT :limit
            """)
            
            params = {"query": f"%{query}%", "limit": limit}
            result = self.session.execute(search_query, params)
            rows = result.fetchall()
            
            # Format results
            results = []
            for row in rows:
                results.append({
                    "post_id": row.id,
                    "content": row.cooked,
                    "cooked": row.cooked,
                    "raw": row.raw,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "reply_count": row.reply_count or 0,
                    "topic_id": row.topic_id,
                    "topic_title": row.topic_title,
                    "topic_slug": row.topic_slug,
                    "category_id": row.category_id,
                    "category_name": row.category_name,
                    "user_id": row.user_id,
                    "username": row.username,
                    "user_name": row.user_name,
                    "search_type": "simple"
                })
            
            logger.info(f"Simple search for '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Simple search failed: {e}")
            return []

    def comprehensive_search(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Comprehensive search that combines multiple search strategies.
        """
        all_results = []
        
        try:
            # 1. Exact phrase search
            exact_results = self.simple_search(f'"{query}"', limit=limit//4)
            for result in exact_results:
                result['search_score'] = 1.0
                result['search_method'] = 'exact_phrase'
            all_results.extend(exact_results)
            
            # 2. Full-text search with all keywords
            keyword_results = self.simple_search(query, limit=limit//2)
            for result in keyword_results:
                result['search_score'] = 0.8
                result['search_method'] = 'keywords'
            all_results.extend(keyword_results)
            
            # 3. Individual keyword search for broader results
            keywords = self._extract_search_keywords(query)
            for keyword in keywords[:3]:  # Limit to top 3 keywords
                kw_results = self.simple_search(keyword, limit=limit//4)
                for result in kw_results:
                    result['search_score'] = 0.6
                    result['search_method'] = f'keyword_{keyword}'
                all_results.extend(kw_results)
            
            # 4. Topic title search
            topic_results = self._search_topics(query, limit=limit//4)
            for result in topic_results:
                result['search_score'] = 0.9
                result['search_method'] = 'topic_title'
            all_results.extend(topic_results)
            
            # Remove duplicates and sort by relevance
            unique_results = self._deduplicate_results(all_results)
            return sorted(unique_results, key=lambda x: x.get('search_score', 0), reverse=True)[:limit]
            
        except Exception as e:
            logger.error(f"Comprehensive search failed: {e}")
            # Fallback to simple search
            return self.simple_search(query, limit)
    
    def _extract_search_keywords(self, query: str) -> List[str]:
        """Extract important keywords for search."""
        import re
        
        # Remove common words and extract meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'how', 'what', 'when', 'where', 'why', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'can'}
        
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # Prioritize technical terms
        technical_terms = [word for word in keywords if any(term in word for term in ['gpt', 'api', 'model', 'docker', 'podman', 'ga', 'tds', 'exam', 'assignment'])]
        
        return technical_terms + [k for k in keywords if k not in technical_terms]
    
    def _search_topics(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search specifically in topic titles."""
        try:
            search_query = text("""
                SELECT DISTINCT 
                    posts.id,
                    posts.cooked,
                    posts.raw,
                    posts.created_at,
                    posts.reply_count,
                    posts.topic_id,
                    topics.title as topic_title,
                    topics.slug as topic_slug,
                    topics.created_at as topic_created_at,
                    categories.id as category_id,
                    categories.name as category_name,
                    users.id as user_id,
                    users.username,
                    users.name as user_name
                FROM topics
                JOIN posts ON posts.topic_id = topics.id
                JOIN categories ON topics.category_id = categories.id
                LEFT JOIN users ON posts.user_id = users.id
                WHERE topics.title ILIKE :query
                ORDER BY topics.created_at DESC, posts.id
                LIMIT :limit
            """)
            
            params = {"query": f"%{query}%", "limit": limit}
            result = self.session.execute(search_query, params)
            rows = result.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    "post_id": row.id,
                    "content": row.cooked,
                    "cooked": row.cooked,
                    "raw": row.raw,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "reply_count": row.reply_count or 0,
                    "topic_id": row.topic_id,
                    "topic_title": row.topic_title,
                    "topic_slug": row.topic_slug,
                    "category_id": row.category_id,
                    "category_name": row.category_name,
                    "user_id": row.user_id,
                    "username": row.username,
                    "user_name": row.user_name,
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Topic search failed: {e}")
            return []
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results while preserving the highest scored version."""
        seen_posts = {}
        
        for result in results:
            post_id = result.get('post_id') or result.get('id')
            if post_id:
                if post_id not in seen_posts or result.get('search_score', 0) > seen_posts[post_id].get('search_score', 0):
                    seen_posts[post_id] = result
        
        return list(seen_posts.values())

# Global search service instance
search_service = None

def get_search_service() -> SearchService:
    """Get or create global search service instance."""
    global search_service
    if search_service is None:
        search_service = SearchService()
    return search_service
