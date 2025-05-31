from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import JSONResponse


# Pydantic models
class FileAttachment(BaseModel):
    filename: str
    content: str  # base64 encoded file content
    content_type: Optional[str] = None

class StudentRequest(BaseModel):
    question: str
    attachments: Optional[List[FileAttachment]] = None

class ApiResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None

app = FastAPI()
# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

@app.post("/api/", response_model=ApiResponse)
async def handle_student_request(request: StudentRequest):
    """
    Handle student questions with optional file attachments.
    
    Args:
        request: StudentRequest containing question and optional attachments
        
    Returns:
        ApiResponse with status and message
    """
    try:
        # Log the received request (for debugging)
        print(f"Received question: {request.question}")
        
        if request.attachments:
            print(f"Number of attachments: {len(request.attachments)}")
            for i, attachment in enumerate(request.attachments):
                print(f"Attachment {i+1}: {attachment.filename} ({attachment.content_type})")
        
        # TODO: Process the question and attachments here
        # For now, just return a success response
        
        return ApiResponse(
            status="success",
            message="Request received successfully",
            data={
                "question_length": len(request.question),
                "attachments_count": len(request.attachments) if request.attachments else 0
            }
        )
        
    except Exception as e:
        return ApiResponse(
            status="error",
            message=f"Error processing request: {str(e)}"
        )