#!/usr/bin/env python3
"""
OpenAI integration for RAG system.
Provides LLM-powered answer generation using retrieved context.
"""

import os
import openai
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class OpenAIService:
    """Service for OpenAI LLM integration."""
    
    def __init__(self):
        """Initialize OpenAI service with API key."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        openai.api_key = self.api_key
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
    
    def generate_rag_answer(
        self, 
        question: str, 
        context_posts: List[Dict[str, Any]], 
        image_description: Optional[str] = None
    ) -> str:
        """
        Generate an answer using RAG approach with OpenAI.
        
        Args:
            question: User's question
            context_posts: Retrieved forum posts for context
            image_description: Optional description of uploaded image
            
        Returns:
            Generated answer based on context
        """
        # Prepare context from retrieved posts
        context_text = self._format_context(context_posts)
        
        # Build the prompt
        prompt = self._build_rag_prompt(question, context_text, image_description)
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._fallback_answer(question, context_posts)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the RAG assistant."""
        return """You are a helpful academic assistant for IIT Madras students. Your role is to answer questions based on forum discussions and course materials.

Guidelines:
1. Use ONLY the provided context from forum posts to answer questions
2. If the context doesn't contain enough information, clearly state this limitation
3. Be concise but informative
4. Maintain an academic and helpful tone
5. If multiple perspectives exist in the context, present them fairly
6. Always prioritize accuracy over completeness
7. For coding questions, provide practical examples when available in context
8. For course-related queries, refer to official information when mentioned in posts

Remember: You are answering based on student discussions and shared experiences in the forum."""
    
    def _build_rag_prompt(
        self, 
        question: str, 
        context: str, 
        image_description: Optional[str] = None
    ) -> str:
        """Build the RAG prompt with question and context."""
        prompt_parts = []
        
        # Add image context if available
        if image_description:
            prompt_parts.append(f"[Image Context: {image_description}]")
        
        # Add the main prompt structure
        prompt_parts.extend([
            "Question: " + question,
            "",
            "Relevant Forum Context:",
            "=" * 50,
            context,
            "=" * 50,
            "",
            "Based on the forum discussions above, please provide a helpful answer to the question. If the context doesn't contain sufficient information to answer the question, please state this clearly."
        ])
        
        return "\n".join(prompt_parts)
    
    def _format_context(self, context_posts: List[Dict[str, Any]]) -> str:
        """Format retrieved posts into context for the LLM."""
        if not context_posts:
            return "No relevant forum posts found."
        
        formatted_context = []
        
        for i, post in enumerate(context_posts[:5], 1):  # Limit to top 5 posts
            topic_title = post.get('topic_title', 'Unknown Topic')
            content = post.get('content', '') or post.get('cooked', '') or post.get('raw', '')
            username = post.get('username', 'Anonymous')
            
            # Clean and truncate content
            clean_content = self._clean_content(content)
            if len(clean_content) > 800:  # Limit content length
                clean_content = clean_content[:800] + "..."
            
            formatted_post = f"""
Post {i}: {topic_title}
Author: {username}
Content: {clean_content}
"""
            formatted_context.append(formatted_post.strip())
        
        return "\n\n".join(formatted_context)
    
    def _clean_content(self, content: str) -> str:
        """Clean HTML and format content for LLM consumption."""
        if not content:
            return ""
        
        import re
        import html
        
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', content)
        
        # Decode HTML entities
        clean = html.unescape(clean)
        
        # Clean up extra whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean
    
    def _fallback_answer(self, question: str, context_posts: List[Dict[str, Any]]) -> str:
        """Provide fallback answer when OpenAI is unavailable."""
        if not context_posts:
            return "I couldn't find relevant information in the forum to answer your question. Please try rephrasing or check if there are existing discussions on this topic."
        
        # Use the first post as basis for fallback
        first_post = context_posts[0]
        content = first_post.get('content', '') or first_post.get('cooked', '') or first_post.get('raw', '')
        clean_content = self._clean_content(content)
        
        if len(clean_content) > 300:
            clean_content = clean_content[:300] + "..."
        
        return f"Based on forum discussions: {clean_content}"
    
    def analyze_image(self, base64_image: str) -> Optional[str]:
        """
        Analyze uploaded image using OpenAI Vision API.
        
        Args:
            base64_image: Base64 encoded image
            
        Returns:
            Description of the image content
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe this image in the context of an academic/technical question. Focus on any text, diagrams, code, or technical content visible."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI Vision API error: {e}")
            return None

# Global instance
_openai_service = None

def get_openai_service() -> OpenAIService:
    """Get or create OpenAI service instance."""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
