# main.py
import asyncio
import json
import uuid
import time
import traceback
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, Request, Form, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from core.database import DatabaseManager, get_db
from core.llm_manager import LLMManager
from core.representations import RepresentationEngine
from core.auth import AuthManager
from models.schemas import (
    QueryRequest, RepresentationResponse, UserSession, 
    ConversationLog, AdminRequest
)
from config.settings import Settings

# Initialize FastAPI app
app = FastAPI(
    title="Knowledge Representation Engine",
    description="Dynamic AI-powered knowledge representation system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize core components
settings = Settings()
db_manager = DatabaseManager()
llm_manager = LLMManager()
representation_engine = RepresentationEngine()
auth_manager = AuthManager()

# main.py - Add this helper function after imports
def representation_result_to_dict(result) -> Dict[str, Any]:
    """Convert RepresentationResult dataclass to dictionary"""
    return {
        "mode": result.mode,
        "content": result.content,
        "metadata": result.metadata,
        "css_classes": result.css_classes,
        "javascript_code": result.javascript_code
    }

@app.on_event("startup")
async def startup_event():
    """Initialize database and core components"""
    try:
        print("🔧 Initializing database...")
        await db_manager.initialize()
        print("✅ Database initialized successfully!")
        
        print("🤖 Initializing LLM Manager...")
        await llm_manager.initialize()
        print("✅ LLM Manager initialized successfully!")
        
        print("🚀 Knowledge Representation Engine started successfully!")
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        print(f"Error details: {traceback.format_exc()}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources"""
    await db_manager.close()
    print("👋 Application shutdown complete")

# Main Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main application interface"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "representation_modes": representation_engine.get_available_modes()
    })

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """Admin panel interface"""
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "app_title": "Knowledge Representation Admin"
    })

# API Routes
@app.post("/api/process", response_model=RepresentationResponse)
async def process_query(
    request: QueryRequest,
    db = Depends(get_db)
):
    """Process user query and generate representation"""
    try:
        print(f"🔍 Processing query: {request.query[:50]}...")
        print(f"📊 Representation mode: {request.representation_mode}")
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Log the incoming request
        conversation_log = ConversationLog(
            session_id=session_id,
            user_query=request.query,
            context=request.context,
            representation_mode=request.representation_mode,
            user_preferences=request.user_preferences,
            timestamp=datetime.now()
        )
        
        # Generate LLM response if not provided
        print("🤖 Generating LLM response...")
        if not request.response:
            try:
                llm_response = await llm_manager.generate_response(
                    query=request.query,
                    context=request.context,
                    representation_mode=request.representation_mode
                )
                response_text = llm_response.content
                token_usage = llm_response.usage
                print(f"✅ LLM response generated: {len(response_text)} characters")
            except Exception as e:
                print(f"❌ LLM generation failed: {e}")
                print(f"LLM Error details: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"LLM generation error: {str(e)}")
        else:
            response_text = request.response
            token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        # Generate representation
        print("🎨 Generating representation...")
        try:
            representation_result = await representation_engine.generate_representation(
                content=response_text,
                mode=request.representation_mode,
                user_preferences=request.user_preferences
            )
            print(f"✅ Representation generated: {representation_result.mode}")
        except Exception as e:
            print(f"❌ Representation generation failed: {e}")
            print(f"Representation Error details: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Representation generation error: {str(e)}")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Convert RepresentationResult to dict for database and response
        representation_dict = {
            "mode": representation_result.mode,
            "content": representation_result.content,
            "metadata": representation_result.metadata,
            "css_classes": representation_result.css_classes,
            "javascript_code": representation_result.javascript_code
        }
        
        # Update conversation log
        conversation_log.llm_response = response_text
        conversation_log.representation_output = representation_dict  # Use dict instead of object
        conversation_log.token_usage = token_usage
        conversation_log.processing_time = round(processing_time, 3)
        conversation_log.llm_config = llm_manager.get_current_config()
        
        # Save to database
        print("💾 Saving to database...")
        try:
            await db_manager.save_conversation(conversation_log)
            print("✅ Conversation saved to database")
        except Exception as e:
            print(f"⚠️ Database save failed: {e}")
            # Don't fail the request if database save fails
        
        response_data = RepresentationResponse(
            session_id=session_id,
            original_query=request.query,
            llm_response=response_text,
            representation=representation_dict,  # Use dict instead of object
            mode=request.representation_mode,
            token_usage=token_usage,
            processing_time=round(processing_time, 3),
            timestamp=datetime.now()
        )
        
        print(f"🎉 Request processed successfully in {processing_time:.2f}s")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 Unexpected error in process_query: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Add a simple health check endpoint that tests each component
@app.get("/api/health-detailed")
async def detailed_health_check():
    """Detailed health check endpoint"""
    health_status = {
        "status": "unknown",
        "timestamp": datetime.now(),
        "components": {}
    }
    
    try:
        # Test database
        try:
            db_healthy = await db_manager.health_check()
            health_status["components"]["database"] = "✅ healthy" if db_healthy else "❌ unhealthy"
        except Exception as e:
            health_status["components"]["database"] = f"❌ error: {str(e)}"
        
        # Test LLM
        try:
            llm_healthy = await llm_manager.health_check()
            health_status["components"]["llm"] = "✅ healthy" if llm_healthy else "❌ unhealthy"
        except Exception as e:
            health_status["components"]["llm"] = f"❌ error: {str(e)}"
        
        # Test representations
        try:
            repr_healthy = representation_engine.health_check()
            health_status["components"]["representations"] = "✅ healthy" if repr_healthy else "❌ unhealthy"
        except Exception as e:
            health_status["components"]["representations"] = f"❌ error: {str(e)}"
        
        # Overall status
        all_healthy = all("✅" in str(status) for status in health_status["components"].values())
        health_status["status"] = "healthy" if all_healthy else "unhealthy"
        
        return health_status
        
    except Exception as e:
        health_status["status"] = "error"
        health_status["error"] = str(e)
        return health_status

@app.get("/api/representations")
async def get_representations():
    """Get available representation modes"""
    return {"modes": representation_engine.get_available_modes()}

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str, db = Depends(get_db)):
    """Retrieve session data"""
    session_data = await db_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_data

# Admin API Routes
@app.get("/api/admin/stats")
async def get_admin_stats(db = Depends(get_db)):
    """Get system statistics for admin dashboard"""
    try:
        stats = await db_manager.get_system_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

@app.get("/api/admin/tables")
async def get_database_tables(db = Depends(get_db)):
    """Get list of database tables"""
    try:
        tables = await db_manager.get_table_list()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tables: {str(e)}")

@app.get("/api/admin/table/{table_name}")
async def get_table_data(
    table_name: str,
    page: int = 1,
    limit: int = 20,
    db = Depends(get_db)
):
    """Get paginated table data"""
    try:
        data = await db_manager.get_table_data(table_name, page, limit)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching table data: {str(e)}")

@app.post("/api/admin/query")
async def execute_sql_query(request: AdminRequest, db = Depends(get_db)):
    """Execute SQL query (admin only)"""
    try:
        # Security check - only allow SELECT statements for now
        if not request.query.strip().upper().startswith('SELECT'):
            raise HTTPException(status_code=403, detail="Only SELECT queries allowed")
        
        result = await db_manager.execute_query(request.query)
        return {"result": result, "query": request.query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution error: {str(e)}")

@app.get("/api/admin/conversations")
async def get_conversations(
    page: int = 1,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get conversation logs with pagination"""
    try:
        conversations = await db_manager.get_conversations(page, limit)
        return conversations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching conversations: {str(e)}")

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file uploads for context or queries"""
    try:
        content = await file.read()
        
        # Process based on file type
        if file.content_type == "application/json":
            data = json.loads(content.decode())
            return {"success": True, "data": data, "filename": file.filename}
        else:
            # Handle other file types (text, etc.)
            text_content = content.decode()
            return {"success": True, "content": text_content, "filename": file.filename}
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File upload error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "components": {
            "database": await db_manager.health_check(),
            "llm": await llm_manager.health_check(),
            "representations": representation_engine.health_check()
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
