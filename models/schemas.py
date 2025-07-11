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
    PUZZLE_BASED = "puzzle_based"

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

class CacheInfo(BaseModel):
    """Cache information for responses"""
    is_cached: bool
    cache_age_hours: Optional[float] = None
    cache_usage_count: Optional[int] = None
    cache_last_used: Optional[datetime] = None
    query_hash: Optional[str] = None

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
                "timestamp": "2025-01-01T00:00:00",
                "metadata": {
                    "cache_info": {
                        "is_cached": True,
                        "cache_age_hours": 2.5,
                        "cache_usage_count": 3
                    }
                }
            }
        }

class UserSession(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    conversation_count: int = 0
    total_tokens: int = 0
    total_processing_time: float = 0
    cache_hits: int = 0
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
    query_hash: Optional[str] = None
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
    cache_stats: Optional[Dict[str, Any]] = None
    
class CacheStats(BaseModel):
    entries: int
    total_hits: int
    hit_rate: Optional[float] = None
    average_age_hours: Optional[float] = None
    most_popular_queries: Optional[List[Dict[str, Any]]] = None
    
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

# Enhanced representation-specific models

class KnowledgeGraphNode(BaseModel):
    id: str
    name: str
    type: str
    importance: int
    description: str
    color: str
    size: int

class KnowledgeGraphEdge(BaseModel):
    id: str
    from_node: str = Field(alias="from")
    to_node: str = Field(alias="to")
    label: str
    relationship: str
    strength: int
    color: str
    width: int

class KnowledgeGraphData(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

class TimelineEvent(BaseModel):
    id: str
    title: str
    description: str
    date_raw: str
    date_parsed: Dict[str, Any]
    period: float
    precision: str
    type: str
    importance: int
    icon: str

class ColorCodedSection(BaseModel):
    type: str  # facts, assumptions, examples, warnings
    content: List[str]
    legend: Dict[str, Any]

class ConceptNode(BaseModel):
    id: str
    title: str
    content: str
    level: int
    icon: str
    type: str
    expanded: bool = False
    children: List['ConceptNode'] = []

# Puzzle-Based Models
class PuzzleChallenge(BaseModel):
    type: str  # multiple_choice, fill_blank, true_false, concept_match
    question: str
    options: Optional[List[str]] = None
    correct_answer: Any
    difficulty: int = Field(ge=1, le=3)
    hint: Optional[str] = None
    case_sensitive: Optional[bool] = False

class PuzzleSegment(BaseModel):
    id: str
    content: str
    challenge: PuzzleChallenge
    unlocked: bool = False
    revealed: bool = False

class PuzzleCompletionStats(BaseModel):
    unlocked_count: int
    revealed_count: int
    solved_count: int

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
    cache_hit_rate: float
    last_activity: datetime
    
class ExportRequest(BaseModel):
    format: str = Field(..., pattern="^(json|csv|html|pdf)$")
    conversation_ids: Optional[List[int]] = None
    session_id: Optional[str] = None
    date_range: Optional[Dict[str, str]] = None
    include_cache_info: bool = False
    
class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    sort_by: str = "timestamp"
    sort_order: str = Field("desc", pattern="^(asc|desc)$")

class CacheRequest(BaseModel):
    action: str = Field(..., pattern="^(clear|stats|cleanup)$")
    parameters: Optional[Dict[str, Any]] = None

class RepresentationMetrics(BaseModel):
    mode: str
    total_uses: int
    average_processing_time: float
    average_user_rating: Optional[float] = None
    cache_hit_rate: float
    complexity_distribution: Dict[str, int]

class SystemPerformance(BaseModel):
    avg_response_time: float
    total_requests: int
    cache_efficiency: float
    popular_representations: List[RepresentationMetrics]
    error_rate: float
    uptime_hours: float

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

# Cache-specific models

class CacheEntry(BaseModel):
    query_hash: str
    query: str
    representation_mode: str
    created_at: datetime
    last_used: datetime
    usage_count: int
    processing_time: float
    token_usage: Dict[str, int]

class CacheCleanupResult(BaseModel):
    entries_removed: int
    space_freed_mb: float
    oldest_removed: Optional[datetime] = None
    newest_removed: Optional[datetime] = None

# Fix circular reference
ConceptNode.model_rebuild()
