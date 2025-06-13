"""
SQLAlchemy models for Discourse forum data with vector database capabilities.
Optimized for PostgreSQL with pgvector extension.
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey,
    Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model for Discourse forum users."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    avatar_template = Column(Text, nullable=True)
    display_username = Column(String(255), nullable=True)
    user_title = Column(String(255), nullable=True)
    title_is_group = Column(Boolean, default=False)
    user_cakedate = Column(DateTime, nullable=True)
    user_birthdate = Column(DateTime, nullable=True)
    
    # User permissions and status
    moderator = Column(Boolean, default=False, index=True)
    admin = Column(Boolean, default=False, index=True)
    staff = Column(Boolean, default=False, index=True)
    group_moderator = Column(Boolean, default=False)
    trust_level = Column(Integer, default=1, index=True)
    hidden = Column(Boolean, default=False)
    user_deleted = Column(Boolean, default=False)
    
    # Group information
    primary_group_name = Column(String(100), nullable=True, index=True)
    flair_name = Column(String(100), nullable=True)
    flair_url = Column(String(255), nullable=True)
    flair_bg_color = Column(String(20), nullable=True)
    flair_color = Column(String(20), nullable=True)
    flair_group_id = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    posts = relationship("Post", back_populates="user", foreign_keys="Post.user_id")
    topics = relationship("Topic", back_populates="user")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_status', 'moderator', 'admin', 'staff'),
        Index('idx_user_group', 'primary_group_name', 'flair_group_id'),
        Index('idx_user_trust_level', 'trust_level', 'user_deleted'),
    )

class Category(Base):
    """Category model for forum categories."""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    parent_category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    
    # Category settings
    color = Column(String(20), nullable=True)
    text_color = Column(String(20), nullable=True)
    topic_count = Column(Integer, default=0)
    post_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_category = relationship("Category", remote_side=[id])
    subcategories = relationship("Category", back_populates="parent_category")
    topics = relationship("Topic", back_populates="category")

class Topic(Base):
    """Topic model for forum topics/threads."""
    __tablename__ = 'topics'
    
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False, index=True)
    html_title = Column(Text, nullable=True)
    slug = Column(String(255), nullable=False, index=True)
    
    # Foreign keys
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Topic statistics
    posts_count = Column(Integer, default=0, index=True)
    reply_count = Column(Integer, default=0)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    
    # Topic status
    closed = Column(Boolean, default=False, index=True)
    archived = Column(Boolean, default=False)
    pinned = Column(Boolean, default=False, index=True)
    visible = Column(Boolean, default=True, index=True)
    
    # Answer tracking
    has_accepted_answer = Column(Boolean, default=False, index=True)
    accepted_answer_post_id = Column(Integer, ForeignKey('posts.id'), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, index=True)
    updated_at = Column(DateTime, nullable=False, index=True)
    bumped_at = Column(DateTime, nullable=True)
    last_posted_at = Column(DateTime, nullable=True, index=True)
    
    # Vector embeddings for semantic search
    title_embedding = Column(Vector(384), nullable=True)  # all-MiniLM-L6-v2 dimensions
    content_summary_embedding = Column(Vector(384), nullable=True)
    
    # Relationships
    category = relationship("Category", back_populates="topics")
    user = relationship("User", back_populates="topics")
    posts = relationship("Post", back_populates="topic", foreign_keys="[Post.topic_id]")
    accepted_answer = relationship("Post", foreign_keys=[accepted_answer_post_id], post_update=True)
    
    # Indexes for vector similarity search
    __table_args__ = (
        Index('idx_topic_category_date', 'category_id', 'created_at'),
        Index('idx_topic_status', 'visible', 'closed', 'archived'),
        Index('idx_topic_stats', 'posts_count', 'views', 'likes'),
        Index('idx_topic_answers', 'has_accepted_answer', 'accepted_answer_post_id'),
        Index('idx_title_embedding_cosine', 'title_embedding', postgresql_using='ivfflat', postgresql_ops={'title_embedding': 'vector_cosine_ops'}),
        Index('idx_topic_content_embedding_cosine', 'content_summary_embedding', postgresql_using='ivfflat', postgresql_ops={'content_summary_embedding': 'vector_cosine_ops'}),
    )

class Post(Base):
    """Post model for forum posts."""
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    
    # Foreign keys
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    reply_to_post_id = Column(Integer, ForeignKey('posts.id'), nullable=True, index=True)
    reply_to_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Post content
    raw = Column(Text, nullable=False)  # Original markdown content
    cooked = Column(Text, nullable=False)  # Rendered HTML content
    excerpt = Column(Text, nullable=True)
    
    # Post metadata
    post_number = Column(Integer, nullable=False, index=True)
    post_type = Column(Integer, default=1, index=True)  # 1=regular, 2=moderator, etc.
    version = Column(Integer, default=1)
    
    # Post statistics
    reads = Column(Integer, default=0, index=True)
    readers_count = Column(Integer, default=0)
    score = Column(Float, default=0.0, index=True)
    reply_count = Column(Integer, default=0)
    quote_count = Column(Integer, default=0)
    incoming_link_count = Column(Integer, default=0)
    
    # Post status and permissions
    hidden = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    edit_reason = Column(Text, nullable=True)
    wiki = Column(Boolean, default=False)
    bookmarked = Column(Boolean, default=False)
    
    # Answer status
    accepted_answer = Column(Boolean, default=False, index=True)
    can_accept_answer = Column(Boolean, default=False)
    can_unaccept_answer = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, index=True)
    updated_at = Column(DateTime, nullable=False, index=True)
    
    # Vector embeddings for semantic search
    content_embedding = Column(Vector(384), nullable=True)  # all-MiniLM-L6-v2 dimensions
    
    # Additional metadata
    actions_summary = Column(JSON, nullable=True)
    user_actions = Column(JSON, nullable=True)
    
    # Relationships
    topic = relationship("Topic", back_populates="posts", foreign_keys=[topic_id])
    user = relationship("User", back_populates="posts", foreign_keys=[user_id])
    reply_to_post = relationship("Post", remote_side=[id])
    reply_to_user = relationship("User", foreign_keys=[reply_to_user_id])
    reactions = relationship("PostReaction", back_populates="post")
    
    # Full-text search
    search_vector = Column(Text, nullable=True)  # Will be populated with tsvector
    
    # Indexes
    __table_args__ = (
        Index('idx_post_topic_number', 'topic_id', 'post_number'),
        Index('idx_post_user_date', 'user_id', 'created_at'),
        Index('idx_post_replies', 'reply_to_post_id', 'reply_count'),
        Index('idx_post_status', 'hidden', 'deleted_at', 'accepted_answer'),
        Index('idx_post_stats', 'score', 'reads', 'readers_count'),
        Index('idx_post_content_embedding_cosine', 'content_embedding', postgresql_using='ivfflat', postgresql_ops={'content_embedding': 'vector_cosine_ops'}),
        Index('idx_post_search', 'search_vector', postgresql_using='gin'),
        CheckConstraint('score >= 0', name='ck_post_score_positive'),
        CheckConstraint('reads >= 0', name='ck_post_reads_positive'),
        UniqueConstraint('topic_id', 'post_number', name='uq_topic_post_number'),
    )

class PostReaction(Base):
    """Model for post reactions (likes, hearts, etc.)."""
    __tablename__ = 'post_reactions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Reaction details
    reaction_type = Column(String(50), nullable=False, index=True)  # 'heart', 'like', 'laughing', etc.
    emoji_id = Column(String(100), nullable=True)
    count = Column(Integer, default=1)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    post = relationship("Post", back_populates="reactions")
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_reaction_post_type', 'post_id', 'reaction_type'),
        Index('idx_reaction_user_post', 'user_id', 'post_id'),
        UniqueConstraint('post_id', 'user_id', 'reaction_type', name='uq_post_user_reaction'),
    )

class Badge(Base):
    """Model for user badges."""
    __tablename__ = 'badges'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    badge_type = Column(String(50), nullable=False, index=True)
    icon = Column(String(100), nullable=True)
    image_url = Column(String(500), nullable=True)
    
    # Badge settings
    enabled = Column(Boolean, default=True)
    allow_title = Column(Boolean, default=False)
    multiple_grant = Column(Boolean, default=False)
    listable = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserBadge(Base):
    """Association table for user badges."""
    __tablename__ = 'user_badges'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    badge_id = Column(Integer, ForeignKey('badges.id'), nullable=False, index=True)
    
    # Badge grant details
    granted_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    granted_at = Column(DateTime, default=datetime.utcnow, index=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=True)  # Badge earned for specific post
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    badge = relationship("Badge")
    granted_by = relationship("User", foreign_keys=[granted_by_id])
    post = relationship("Post")
    
    __table_args__ = (
        Index('idx_user_badge_grant', 'user_id', 'granted_at'),
        Index('idx_badge_users', 'badge_id', 'granted_at'),
    )

class SearchQuery(Base):
    """Model to track search queries for analytics and caching."""
    __tablename__ = 'search_queries'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_text = Column(Text, nullable=False, index=True)
    query_type = Column(String(50), nullable=False, index=True)  # 'full_text', 'semantic', 'similarity'
    
    # Search parameters
    filters = Column(JSON, nullable=True)  # Category, user, date filters
    limit_results = Column(Integer, default=20)
    
    # Results metadata
    results_count = Column(Integer, default=0)
    execution_time_ms = Column(Float, nullable=True)
    
    # User tracking (optional, for analytics)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_search_query_type_date', 'query_type', 'created_at'),
        Index('idx_search_user_date', 'user_id', 'created_at'),
        Index('idx_search_performance', 'execution_time_ms', 'results_count'),
    )

class EmbeddingCache(Base):
    """Cache table for computed embeddings to avoid recomputation."""
    __tablename__ = 'embedding_cache'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_hash = Column(String(64), nullable=False, unique=True, index=True)  # SHA-256 hash
    content_type = Column(String(50), nullable=False, index=True)  # 'post', 'topic_title', 'summary'
    
    # Embedding details
    model_name = Column(String(100), nullable=False, index=True)  # 'text-embedding-ada-002', etc.
    embedding = Column(Vector(1536), nullable=False)
    token_count = Column(Integer, nullable=True)
    
    # Usage tracking
    hit_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_embedding_model_type', 'model_name', 'content_type'),
        Index('idx_embedding_usage', 'hit_count', 'last_accessed'),
        Index('idx_embedding_vector_cosine', 'embedding', postgresql_using='ivfflat', postgresql_ops={'embedding': 'vector_cosine_ops'}),
    )
