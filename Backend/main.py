from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import JSONResponse
import os
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import re
import html

from database.connection import initialize_database, get_session
from api.routes import router as api_router


# Pydantic models
class FileAttachment(BaseModel):
    filename: str
    content: str  # base64 encoded file content
    content_type: Optional[str] = None

class StudentRequest(BaseModel):
    question: str
    image: Optional[str] = None  # base64 encoded image
    attachments: Optional[List[FileAttachment]] = None

class LinkResponse(BaseModel):
    url: str
    text: str

class RagResponse(BaseModel):
    answer: str
    links: List[LinkResponse]

class ApiResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    try:
        # Skip database initialization in serverless environment
        if os.getenv("VERCEL"):
            print("Running on Vercel - skipping database initialization")
        else:
            print("Initializing database...")
            initialize_database()
            print("Database initialization completed.")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        # Don't fail startup if database is not available
    yield

app = FastAPI(
    title="Discourse Forum API",
    description="API for searching and accessing Discourse forum data with vector search capabilities",
    version="1.0.0",
    lifespan=lifespan
)
# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include API routes
app.include_router(api_router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

@app.post("/api/", response_model=RagResponse)
async def handle_student_request(
    request: StudentRequest,
    session: Session = Depends(get_session)
):
    """
    Handle student questions with optional image attachments using RAG.
    
    Args:
        request: StudentRequest containing question and optional image
        session: Database session
        
    Returns:
        RagResponse with answer and relevant links
    """
    try:
        # Log the received request (for debugging)
        print(f"Received question: {request.question}")
        
        if request.image:
            print(f"Received base64 image (length: {len(request.image)})")
        
        # Import search service here to avoid circular imports
        from services.search import SearchService
        
        # Initialize search service with session
        search_service = SearchService(session)
        
        # Perform comprehensive search across multiple strategies
        search_results = search_service.comprehensive_search(
            query=request.question,
            limit=20  # Get more results for better context
        )
        
        # Generate answer based on search results and question context
        answer = _generate_answer_from_results(
            question=request.question, 
            search_results=search_results, 
            image=request.image,
            session=session
        )
        
        # Format links from relevant posts
        links = _format_links_from_results(search_results)
        
        return RagResponse(
            answer=answer,
            links=links
        )
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return RagResponse(
            answer="I apologize, but I encountered an error while processing your question. Please try again or rephrase your question.",
            links=[]
        )


def _clean_html_content(content: str) -> str:
    """Clean HTML content by removing tags and decoding entities."""
    if not content:
        return ""
    
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', content)
    
    # Decode HTML entities
    clean = html.unescape(clean)
    
    # Clean up extra whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    return clean


def _generate_answer_from_results(
    question: str, 
    search_results: List[dict], 
    image: Optional[str] = None,
    session: Session = None
) -> str:
    """
    Generate a comprehensive answer using OpenAI RAG approach.
    """
    try:
        # Try to use OpenAI service for proper RAG
        from services.openai_service import get_openai_service
        
        openai_service = get_openai_service()
        
        # Analyze image if provided
        image_description = None
        if image:
            image_description = openai_service.analyze_image(image)
        
        # Generate RAG answer using OpenAI
        answer = openai_service.generate_rag_answer(
            question=question,
            context_posts=search_results,
            image_description=image_description
        )
        
        return answer
        
    except Exception as e:
        print(f"OpenAI service error, falling back to rule-based: {e}")
        # Fallback to existing rule-based approach
        return _generate_fallback_answer(question, search_results, image, session)

def _generate_fallback_answer(
    question: str, 
    search_results: List[dict], 
    image: Optional[str] = None,
    session: Session = None
) -> str:
    """
    Generate a fallback answer using rule-based approach when OpenAI is unavailable.
    This processes the actual database content to provide contextual answers.
    """
    if not search_results:
        return "I couldn't find any relevant information in the forum to answer your question. Please try rephrasing your question or check if there are existing discussions on this topic."
    
    # Image context
    image_context = ""
    if image:
        image_context = "I can see you've included an image with your question. "
    
    # Analyze the question to determine intent and keywords
    question_lower = question.lower()
    question_keywords = _extract_keywords(question)
    
    # Categorize search results by relevance
    high_relevance_results = []
    medium_relevance_results = []
    
    for result in search_results:
        raw_content = result.get('content', '') or result.get('cooked', '') or result.get('raw', '')
        content = _clean_html_content(raw_content)
        title = result.get('topic_title', '')
        
        # Calculate relevance score
        relevance_score = _calculate_relevance_score(question_keywords, content, title)
        
        if relevance_score > 0.7:
            high_relevance_results.append((result, relevance_score))
        elif relevance_score > 0.3:
            medium_relevance_results.append((result, relevance_score))
    
    # Sort by relevance score
    high_relevance_results.sort(key=lambda x: x[1], reverse=True)
    medium_relevance_results.sort(key=lambda x: x[1], reverse=True)
    
    # Generate comprehensive answer
    if high_relevance_results:
        answer_parts = [image_context + "Based on the forum discussions, here's what I found:"]
        
        # Use top 3 high-relevance results
        for i, (result, score) in enumerate(high_relevance_results[:3]):
            raw_content = result.get('content', '') or result.get('cooked', '') or result.get('raw', '')
            content = _clean_html_content(raw_content)
            
            # Extract relevant excerpt
            excerpt = _extract_relevant_excerpt(content, question_keywords)
            
            if excerpt:
                if i == 0:
                    answer_parts.append(f"\n\n{excerpt}")
                else:
                    answer_parts.append(f"\n\nAdditionally, {excerpt}")
        
        # Add summary from medium relevance if needed
        if medium_relevance_results and len(answer_parts) == 1:
            for result, score in medium_relevance_results[:2]:
                raw_content = result.get('content', '') or result.get('cooked', '') or result.get('raw', '')
                content = _clean_html_content(raw_content)
                excerpt = _extract_relevant_excerpt(content, question_keywords)
                if excerpt:
                    answer_parts.append(f"\n\nAlso relevant: {excerpt}")
        
        return "".join(answer_parts)
    
    elif medium_relevance_results:
        # Use medium relevance results
        answer_parts = [image_context + "I found some related information:"]
        
        for i, (result, score) in enumerate(medium_relevance_results[:2]):
            raw_content = result.get('content', '') or result.get('cooked', '') or result.get('raw', '')
            content = _clean_html_content(raw_content)
            excerpt = _extract_relevant_excerpt(content, question_keywords)
            
            if excerpt:
                answer_parts.append(f"\n\n{excerpt}")
        
        return "".join(answer_parts)
    
    # Fallback to basic content
    if search_results:
        raw_content = search_results[0].get('content', '') or search_results[0].get('cooked', '') or search_results[0].get('raw', '')
        content = _clean_html_content(raw_content)
        if content:
            excerpt = content[:300] + "..." if len(content) > 300 else content
            return f"{image_context}I found this related discussion: {excerpt}"
    
    return f"{image_context}I found some discussions that might be related to your question, but I couldn't extract a specific answer. Please check the linked forum posts for more details."


def _extract_keywords(question: str) -> List[str]:
    """Extract important keywords from the question."""
    import re
    
    # Remove common stop words
    stop_words = {
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
        'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
        'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
        'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
        'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
        'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
        'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
        'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
        'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
        'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will',
        'just', 'don', 'should', 'now', 'use', 'get', 'would', 'could', 'should'
    }
    
    # Extract words and clean them
    words = re.findall(r'\b\w+\b', question.lower())
    keywords = [word for word in words if len(word) > 2 and word not in stop_words]
    
    # Also extract important phrases
    technical_phrases = re.findall(r'\b(?:gpt-[\w.-]+|docker|podman|ga\d+|tds|api|model|assignment|exam|dashboard)\b', question.lower())
    keywords.extend(technical_phrases)
    
    return list(set(keywords))


def _calculate_relevance_score(keywords: List[str], content: str, title: str) -> float:
    """Calculate relevance score based on keyword matches."""
    if not keywords:
        return 0.0
    
    content_lower = content.lower()
    title_lower = title.lower()
    
    # Count keyword matches
    content_matches = sum(1 for keyword in keywords if keyword in content_lower)
    title_matches = sum(1 for keyword in keywords if keyword in title_lower)
    
    # Weight title matches more heavily
    total_matches = content_matches + (title_matches * 2)
    max_possible_matches = len(keywords) * 3  # 1 for content + 2 for title
    
    return min(total_matches / max_possible_matches, 1.0) if max_possible_matches > 0 else 0.0


def _extract_relevant_excerpt(content: str, keywords: List[str], max_length: int = 1200) -> str:
    """Extract the most relevant excerpt from content based on keywords."""
    if not content or not keywords:
        return content[:max_length] + "..." if len(content) > max_length else content
    
    content_lower = content.lower()
    
    # Find sentences that contain keywords
    sentences = [s.strip() for s in content.split('.') if s.strip()]
    scored_sentences = []
    
    for i, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        keyword_count = sum(1 for keyword in keywords if keyword in sentence_lower)
        
        if keyword_count > 0:
            # Include context: previous and next sentence for better coherence
            context_sentences = []
            if i > 0:  # Add previous sentence for context
                context_sentences.append(sentences[i-1])
            context_sentences.append(sentence)
            if i < len(sentences) - 1:  # Add next sentence for context
                context_sentences.append(sentences[i+1])
            
            context_text = '. '.join(context_sentences) + '.'
            scored_sentences.append((context_text, keyword_count, i))
    
    if scored_sentences:
        # Sort by keyword count and take the best result
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Take the best matching excerpt and ensure it's complete
        best_excerpt = scored_sentences[0][0]
        
        # If it's still too long, try to find a good breaking point
        if len(best_excerpt) > max_length:
            # Try to break at sentence boundaries
            sentences_in_excerpt = best_excerpt.split('.')
            result = ""
            for sentence in sentences_in_excerpt:
                if len(result + sentence + '.') <= max_length:
                    result += sentence + '.'
                else:
                    break
            return result.strip() if result else best_excerpt[:max_length] + "..."
        
        return best_excerpt.strip()
    
    # Fallback to beginning of content
    return content[:max_length] + "..." if len(content) > max_length else content


def _format_links_from_results(search_results: List[dict]) -> List[LinkResponse]:
    """Format search results into link responses with smart deduplication."""
    links = []
    seen_urls = set()
    
    # Group results by topic to avoid duplicate topic links
    topic_groups = {}
    for result in search_results:
        topic_id = result.get('topic_id')
        if topic_id:
            if topic_id not in topic_groups:
                topic_groups[topic_id] = []
            topic_groups[topic_id].append(result)
    
    # Generate links with preference for high-scoring results
    for topic_id, topic_results in list(topic_groups.items())[:5]:  # Limit to top 5 topics
        # Sort by search score if available, otherwise by creation date
        topic_results.sort(key=lambda x: (
            x.get('search_score', 0.5),
            x.get('created_at', '1970-01-01')
        ), reverse=True)
        
        best_result = topic_results[0]
        
        # Get post details
        post_id = best_result.get('post_id') or best_result.get('id')
        topic_title = best_result.get('topic_title', 'Forum Discussion')
        content = best_result.get('content', '') or best_result.get('cooked', '') or best_result.get('raw', '')
        
        # Generate appropriate URL
        if post_id and post_id > 1:  # If it's not the first post in topic
            url = f"https://discourse.onlinedegree.iitm.ac.in/t/{topic_id}/{post_id}"
        else:
            url = f"https://discourse.onlinedegree.iitm.ac.in/t/{topic_id}"
        
        # Skip if we've already seen this URL
        if url in seen_urls:
            continue
        seen_urls.add(url)
        
        # Create descriptive text
        if content:
            # Clean HTML tags for text preview
            import re
            clean_content = re.sub(r'<[^>]+>', '', content)
            clean_content = clean_content.strip()
            
            if len(clean_content) > 100:
                text = clean_content[:97] + "..."
            else:
                text = clean_content or topic_title
        else:
            text = topic_title
        
        # Add search method context if available
        search_method = best_result.get('search_method', '')
        if search_method == 'exact_phrase':
            text = f"🎯 {text}"
        elif search_method == 'topic_title':
            text = f"📋 {text}"
        
        links.append(LinkResponse(url=url, text=text))
    
    return links