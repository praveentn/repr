# core/database.py
import sqlite3
import aiosqlite
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path: str = "data/knowledge_repr.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(exist_ok=True)
    
    async def initialize(self):
        """Initialize database with required tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_query TEXT NOT NULL,
                    context TEXT,
                    llm_response TEXT,
                    representation_mode TEXT NOT NULL,
                    representation_output TEXT,
                    user_preferences TEXT,
                    token_usage TEXT,
                    processing_time REAL,
                    llm_config TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    user_id TEXT,
                    preferences TEXT,
                    conversation_count INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    total_processing_time REAL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS representation_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    session_id TEXT,
                    rating INTEGER,
                    feedback_text TEXT,
                    representation_mode TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_key TEXT UNIQUE NOT NULL,
                    config_value TEXT NOT NULL,
                    config_type TEXT DEFAULT 'string',
                    description TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS llm_usage_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    total_tokens INTEGER,
                    cost_estimate REAL,
                    response_time REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            await db.execute("CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_sessions_activity ON user_sessions(last_activity)")
            
            await db.commit()
    
    async def save_conversation(self, conversation_log):
        """Save conversation log to database"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO conversations (
                    session_id, user_query, context, llm_response, 
                    representation_mode, representation_output, user_preferences,
                    token_usage, processing_time, llm_config, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation_log.session_id,
                conversation_log.user_query,
                json.dumps(conversation_log.context) if conversation_log.context else None,
                conversation_log.llm_response,
                conversation_log.representation_mode,
                json.dumps(conversation_log.representation_output),
                json.dumps(conversation_log.user_preferences) if conversation_log.user_preferences else None,
                json.dumps(conversation_log.token_usage),
                round(conversation_log.processing_time, 3),
                json.dumps(conversation_log.llm_config),
                conversation_log.timestamp
            ))
            
            conversation_id = cursor.lastrowid
            
            # Update or create session
            await self.update_session(conversation_log.session_id, conversation_log.token_usage, conversation_log.processing_time)
            
            # Log LLM usage
            await self.log_llm_usage(conversation_log)
            
            await db.commit()
            return conversation_id
    
    async def update_session(self, session_id: str, token_usage: Dict, processing_time: float):
        """Update session statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            # Check if session exists
            cursor = await db.execute("SELECT id FROM user_sessions WHERE session_id = ?", (session_id,))
            session_exists = await cursor.fetchone()
            
            if session_exists:
                # Update existing session
                await db.execute("""
                    UPDATE user_sessions 
                    SET conversation_count = conversation_count + 1,
                        total_tokens = total_tokens + ?,
                        total_processing_time = total_processing_time + ?,
                        last_activity = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                """, (token_usage.get('total_tokens', 0), round(processing_time, 3), session_id))
            else:
                # Create new session
                await db.execute("""
                    INSERT INTO user_sessions (
                        session_id, conversation_count, total_tokens, total_processing_time
                    ) VALUES (?, 1, ?, ?)
                """, (session_id, token_usage.get('total_tokens', 0), round(processing_time, 3)))
            
            await db.commit()
    
    async def log_llm_usage(self, conversation_log):
        """Log LLM usage for cost tracking"""
        async with aiosqlite.connect(self.db_path) as db:
            model_name = conversation_log.llm_config.get('model', 'unknown')
            tokens = conversation_log.token_usage
            
            # Rough cost estimation (would need actual pricing)
            cost_estimate = (tokens.get('prompt_tokens', 0) * 0.00001) + (tokens.get('completion_tokens', 0) * 0.00002)
            
            await db.execute("""
                INSERT INTO llm_usage_logs (
                    session_id, model_name, prompt_tokens, completion_tokens,
                    total_tokens, cost_estimate, response_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation_log.session_id,
                model_name,
                tokens.get('prompt_tokens', 0),
                tokens.get('completion_tokens', 0),
                tokens.get('total_tokens', 0),
                round(cost_estimate, 4),
                round(conversation_log.processing_time, 3)
            ))
            
            await db.commit()
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve session data"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Get session info
            cursor = await db.execute("""
                SELECT * FROM user_sessions WHERE session_id = ?
            """, (session_id,))
            session = await cursor.fetchone()
            
            if not session:
                return None
            
            # Get conversations for this session
            cursor = await db.execute("""
                SELECT * FROM conversations 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 10
            """, (session_id,))
            conversations = await cursor.fetchall()
            
            return {
                "session": dict(session),
                "conversations": [dict(conv) for conv in conversations]
            }
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics for admin dashboard"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            stats = {}
            
            # Total conversations
            cursor = await db.execute("SELECT COUNT(*) as count FROM conversations")
            stats['total_conversations'] = (await cursor.fetchone())['count']
            
            # Total sessions
            cursor = await db.execute("SELECT COUNT(*) as count FROM user_sessions")
            stats['total_sessions'] = (await cursor.fetchone())['count']
            
            # Today's conversations
            cursor = await db.execute("""
                SELECT COUNT(*) as count FROM conversations 
                WHERE date(timestamp) = date('now')
            """)
            stats['todays_conversations'] = (await cursor.fetchone())['count']
            
            # Token usage summary
            cursor = await db.execute("""
                SELECT 
                    SUM(total_tokens) as total_tokens,
                    AVG(total_tokens) as avg_tokens,
                    SUM(cost_estimate) as total_cost
                FROM llm_usage_logs
            """)
            usage = await cursor.fetchone()
            stats['token_usage'] = dict(usage) if usage else {}
            
            # Popular representation modes
            cursor = await db.execute("""
                SELECT representation_mode, COUNT(*) as count 
                FROM conversations 
                GROUP BY representation_mode 
                ORDER BY count DESC 
                LIMIT 5
            """)
            popular_modes = await cursor.fetchall()
            stats['popular_modes'] = [dict(mode) for mode in popular_modes]
            
            # Recent activity (last 7 days)
            cursor = await db.execute("""
                SELECT date(timestamp) as date, COUNT(*) as conversations
                FROM conversations 
                WHERE timestamp >= datetime('now', '-7 days')
                GROUP BY date(timestamp)
                ORDER BY date DESC
            """)
            recent_activity = await cursor.fetchall()
            stats['recent_activity'] = [dict(activity) for activity in recent_activity]
            
            return stats
    
    async def get_table_list(self) -> List[str]:
        """Get list of all tables in database"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = await cursor.fetchall()
            return [table[0] for table in tables]
    
    async def get_table_data(self, table_name: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Get paginated table data"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Get total count
            cursor = await db.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            total_count = (await cursor.fetchone())['count']
            
            # Calculate offset
            offset = (page - 1) * limit
            
            # Get paginated data
            cursor = await db.execute(f"""
                SELECT * FROM {table_name} 
                ORDER BY rowid DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            rows = await cursor.fetchall()
            data = [dict(row) for row in rows]
            
            # Get column info
            cursor = await db.execute(f"PRAGMA table_info({table_name})")
            columns = await cursor.fetchall()
            column_info = [{"name": col[1], "type": col[2]} for col in columns]
            
            return {
                "data": data,
                "columns": column_info,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "pages": (total_count + limit - 1) // limit
                }
            }
    
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute raw SQL query (SELECT only for security)"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_conversations(self, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Get conversation logs with pagination"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Get total count
            cursor = await db.execute("SELECT COUNT(*) as count FROM conversations")
            total_count = (await cursor.fetchone())['count']
            
            # Calculate offset
            offset = (page - 1) * limit
            
            # Get conversations
            cursor = await db.execute("""
                SELECT 
                    id, session_id, user_query, representation_mode,
                    processing_time, timestamp,
                    json_extract(token_usage, '$.total_tokens') as tokens
                FROM conversations 
                ORDER BY timestamp DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            conversations = await cursor.fetchall()
            
            return {
                "conversations": [dict(conv) for conv in conversations],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "pages": (total_count + limit - 1) // limit
                }
            }
    
    async def health_check(self) -> bool:
        """Check database health"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("SELECT 1")
                return True
        except Exception:
            return False
    
    async def close(self):
        """Cleanup database connections"""
        # In this implementation, connections are opened/closed per request
        # No persistent connections to close
        pass

# Dependency to get database instance
async def get_db():
    db_manager = DatabaseManager()
    try:
        yield db_manager
    finally:
        await db_manager.close()
