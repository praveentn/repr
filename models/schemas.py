# models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class RepresentationMode(str, Enum):
    PLAIN_TEXT = "plain_text"
    COLOR_CODED = "color_coded"
    COLLAPSIBLE_CONCEPTS = "collapsible_concepts"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    ANALOGICAL = "analogical"
    PERSONA_ELI5 = "persona_eli5"
    PERSONA_EXPERT = "persona_expert"
    PERSONA_LAYMAN = "persona_layman"
    CINEMATIC = "cinematic"
    INTERACTIVE = "interactive"
    TIMELINE = "timeline"
    COMPARISON = "comparison"
    SUMMARY = "summary"
    DETAILED = "detailed"

class QueryRequest(BaseModel):
    query: str = Field(..., description="User's main question or request")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context including chat history, metadata")
    response: Optional[str] = Field(None, description="Pre-generated response (optional)")
    representation_mode: RepresentationMode = Field(RepresentationMode.PLAIN_TEXT, description="Desired representation mode")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences and settings")
    session_id: Optional[str] = Field(None, description="Session identifier")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Explain quantum computing",
                "context": {
                    "chat_history": ["Previous conversation about classical computing"],
                    "user_profile": {"expertise_level": "intermediate"},
                    "metadata": {"source": "educational"}
                },
                "representation_mode": "knowledge_graph",
                "user_preferences": {
                    "visual_style": "modern",
                    "complexity_level": "medium"
                }
            }
        }

class RepresentationResponse(BaseModel):
    session_id: str
    original_query: str
    llm_response: str
    representation: Dict[str, Any]
    mode: RepresentationMode
    token_usage: Dict[str, int]
    processing_time: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "uuid-here",
                "original_query": "Explain quantum computing",
                "llm_response": "Quantum computing is...",
                "representation": {
                    "mode": "knowledge_graph",
                    "content": {},
                    "metadata": {}
                },
                "mode": "knowledge_graph",
                "token_usage": {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300},
                "processing_time": 2.5,
                "timestamp": "2025-01-01T00:00:00"
            }
        }

class UserSession(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    conversation_count: int = 0
    total_tokens: int = 0
    total_processing_time: float = 0
    created_at: datetime
    last_activity: datetime
    
class ConversationLog(BaseModel):
    session_id: str
    user_query: str
    context: Optional[Dict[str, Any]] = None
    llm_response: Optional[str] = None
    representation_mode: RepresentationMode
    representation_output: Optional[Dict[str, Any]] = None
    user_preferences: Optional[Dict[str, Any]] = None
    token_usage: Optional[Dict[str, int]] = None
    processing_time: Optional[float] = None
    llm_config: Optional[Dict[str, Any]] = None
    timestamp: datetime
    
class AdminRequest(BaseModel):
    query: str = Field(..., description="SQL query to execute")
    query_type: str = Field("SELECT", description="Type of SQL query")
    
class SystemStats(BaseModel):
    total_conversations: int
    total_sessions: int
    todays_conversations: int
    token_usage: Dict[str, Any]
    popular_modes: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    
class TableData(BaseModel):
    data: List[Dict[str, Any]]
    columns: List[Dict[str, str]]
    pagination: Dict[str, Any]
    
class LLMConfig(BaseModel):
    model: str = "gpt-4.1-nano"
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(2000, ge=1, le=4000)
    top_p: float = Field(1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(0.0, ge=-2.0, le=2.0)
    
class FeedbackRequest(BaseModel):
    conversation_id: int
    session_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = None
    representation_mode: RepresentationMode
    
class FileUploadResponse(BaseModel):
    success: bool
    filename: str
    content: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    components: Dict[str, bool]

# Additional utility models

class RepresentationModeInfo(BaseModel):
    name: str
    description: str
    icon: str
    category: str
    example_use_case: Optional[str] = None
    
class UserPreferences(BaseModel):
    preferred_mode: RepresentationMode = RepresentationMode.PLAIN_TEXT
    visual_style: str = "modern"
    complexity_level: str = "medium"  # basic, medium, advanced
    color_scheme: str = "light"  # light, dark, auto
    font_size: str = "medium"  # small, medium, large
    animation_enabled: bool = True
    auto_save: bool = True
    
class ConversationSummary(BaseModel):
    session_id: str
    conversation_count: int
    last_query: str
    last_mode: RepresentationMode
    total_tokens: int
    avg_processing_time: float
    last_activity: datetime
    
class ExportRequest(BaseModel):
    format: str = Field(..., pattern="^(json|csv|html|pdf)$")
    conversation_ids: Optional[List[int]] = None
    session_id: Optional[str] = None
    date_range: Optional[Dict[str, str]] = None
    
class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    sort_by: str = "timestamp"
    sort_order: str = Field("desc", pattern="^(asc|desc)$")

# Error response models

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.now)
    
class ValidationErrorResponse(BaseModel):
    error: str = "Validation Error"
    detail: List[Dict[str, Any]]
    status_code: int = 422
    timestamp: datetime = Field(default_factory=datetime.now)
