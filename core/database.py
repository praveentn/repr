# core/database.py
import sqlite3
import aiosqlite
import json
import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "data/knowledge_repr.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(exist_ok=True)
        self._connection_pool = {}
        self._pool_size = 5
        self._timeout = 30.0
        self._retry_attempts = 3
        self._retry_delay = 0.5
        
    async def initialize(self):
        """Initialize database with required tables"""
        retries = 0
        while retries < self._retry_attempts:
            try:
                async with self._get_connection() as db:
                    await self._create_tables(db)
                    await db.commit()
                    logger.info("✅ Database initialized successfully")
                    return
            except Exception as e:
                retries += 1
                logger.warning(f"Database initialization attempt {retries} failed: {e}")
                if retries < self._retry_attempts:
                    await asyncio.sleep(self._retry_delay * retries)
                else:
                    logger.error("❌ Database initialization failed after all retries")
                    raise
    
    @asynccontextmanager
    async def _get_connection(self):
        """Get database connection with proper error handling and timeouts"""
        connection = None
        try:
            connection = await aiosqlite.connect(
                self.db_path,
                timeout=self._timeout,
                isolation_level=None  # Enable autocommit mode
            )
            
            # Configure connection for better concurrency
            await connection.execute("PRAGMA journal_mode=WAL")
            await connection.execute("PRAGMA synchronous=NORMAL")
            await connection.execute("PRAGMA cache_size=10000")
            await connection.execute("PRAGMA temp_store=memory")
            await connection.execute("PRAGMA busy_timeout=30000")  # 30 seconds
            
            yield connection
            
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if connection:
                await connection.close()
            raise
        finally:
            if connection:
                try:
                    await connection.close()
                except Exception as e:
                    logger.warning(f"Error closing database connection: {e}")
    
    async def _create_tables(self, db):
        """Create all required database tables"""
        tables = [
            """
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
            """,
            """
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
            """,
            """
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
            """,
            """
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                config_type TEXT DEFAULT 'string',
                description TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
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
            """
        ]
        
        for table_sql in tables:
            await db.execute(table_sql)
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_activity ON user_sessions(last_activity)",
            "CREATE INDEX IF NOT EXISTS idx_conversations_mode ON conversations(representation_mode)",
            "CREATE INDEX IF NOT EXISTS idx_llm_usage_session ON llm_usage_logs(session_id)"
        ]
        
        for index_sql in indexes:
            await db.execute(index_sql)
    
    async def _execute_with_retry(self, operation, *args, **kwargs):
        """Execute database operation with retry logic"""
        retries = 0
        while retries < self._retry_attempts:
            try:
                return await operation(*args, **kwargs)
            except (aiosqlite.OperationalError, aiosqlite.DatabaseError) as e:
                retries += 1
                error_message = str(e).lower()
                
                if "database is locked" in error_message or "busy" in error_message:
                    logger.warning(f"Database busy, retry {retries}/{self._retry_attempts}: {e}")
                    if retries < self._retry_attempts:
                        wait_time = self._retry_delay * (2 ** retries)  # Exponential backoff
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error("❌ Database operation failed after all retries")
                        raise
                else:
                    logger.error(f"Database error (non-retryable): {e}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected database error: {e}")
                raise
    
    async def save_conversation(self, conversation_log):
        """Save conversation log to database with improved error handling"""
        async def _save_operation():
            async with self._get_connection() as db:
                # Start transaction
                await db.execute("BEGIN IMMEDIATE")
                try:
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
                        json.dumps(conversation_log.representation_output.dict() if hasattr(conversation_log.representation_output, 'dict') else conversation_log.representation_output),
                        json.dumps(conversation_log.user_preferences) if conversation_log.user_preferences else None,
                        json.dumps(conversation_log.token_usage) if conversation_log.token_usage else None,
                        round(conversation_log.processing_time, 3) if conversation_log.processing_time else None,
                        json.dumps(conversation_log.llm_config) if conversation_log.llm_config else None,
                        conversation_log.timestamp
                    ))
                    
                    conversation_id = cursor.lastrowid
                    
                    # Update session statistics
                    await self._update_session_stats(db, conversation_log)
                    
                    # Log LLM usage
                    await self._log_llm_usage(db, conversation_log)
                    
                    await db.commit()
                    logger.info(f"💾 Conversation saved successfully (ID: {conversation_id})")
                    return conversation_id
                    
                except Exception as e:
                    await db.rollback()
                    logger.error(f"💾 Failed to save conversation: {e}")
                    raise
        
        return await self._execute_with_retry(_save_operation)
    
    async def _update_session_stats(self, db, conversation_log):
        """Update session statistics within existing transaction"""
        total_tokens = conversation_log.token_usage.get('total_tokens', 0) if conversation_log.token_usage else 0
        processing_time = round(conversation_log.processing_time, 3) if conversation_log.processing_time else 0
        
        # Check if session exists
        cursor = await db.execute("SELECT id FROM user_sessions WHERE session_id = ?", (conversation_log.session_id,))
        session_exists = await cursor.fetchone()
        
        if session_exists:
            await db.execute("""
                UPDATE user_sessions 
                SET conversation_count = conversation_count + 1,
                    total_tokens = total_tokens + ?,
                    total_processing_time = total_processing_time + ?,
                    last_activity = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (total_tokens, processing_time, conversation_log.session_id))
        else:
            await db.execute("""
                INSERT INTO user_sessions (
                    session_id, conversation_count, total_tokens, total_processing_time
                ) VALUES (?, 1, ?, ?)
            """, (conversation_log.session_id, total_tokens, processing_time))
    
    async def _log_llm_usage(self, db, conversation_log):
        """Log LLM usage within existing transaction"""
        if not conversation_log.token_usage or not conversation_log.llm_config:
            return
            
        model_name = conversation_log.llm_config.get('model', 'unknown')
        tokens = conversation_log.token_usage
        
        # Cost estimation (would need actual pricing)
        cost_estimate = round(
            (tokens.get('prompt_tokens', 0) * 0.00001) + 
            (tokens.get('completion_tokens', 0) * 0.00002), 
            4
        )
        
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
            cost_estimate,
            round(conversation_log.processing_time, 3) if conversation_log.processing_time else 0
        ))
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve session data with improved error handling"""
        async def _get_operation():
            async with self._get_connection() as db:
                db.row_factory = aiosqlite.Row
                
                # Get session info
                cursor = await db.execute("SELECT * FROM user_sessions WHERE session_id = ?", (session_id,))
                session = await cursor.fetchone()
                
                if not session:
                    return None
                
                # Get recent conversations
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
        
        return await self._execute_with_retry(_get_operation)
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics with improved error handling"""
        async def _stats_operation():
            async with self._get_connection() as db:
                db.row_factory = aiosqlite.Row
                stats = {}
                
                # Total conversations
                cursor = await db.execute("SELECT COUNT(*) as count FROM conversations")
                result = await cursor.fetchone()
                stats['total_conversations'] = result['count'] if result else 0
                
                # Total sessions
                cursor = await db.execute("SELECT COUNT(*) as count FROM user_sessions")
                result = await cursor.fetchone()
                stats['total_sessions'] = result['count'] if result else 0
                
                # Today's conversations
                cursor = await db.execute("""
                    SELECT COUNT(*) as count FROM conversations 
                    WHERE date(timestamp) = date('now')
                """)
                result = await cursor.fetchone()
                stats['todays_conversations'] = result['count'] if result else 0
                
                # Token usage summary
                cursor = await db.execute("""
                    SELECT 
                        SUM(total_tokens) as total_tokens,
                        AVG(total_tokens) as avg_tokens,
                        SUM(cost_estimate) as total_cost
                    FROM llm_usage_logs
                """)
                usage = await cursor.fetchone()
                if usage and usage['total_tokens']:
                    stats['token_usage'] = {
                        'total_tokens': int(usage['total_tokens']),
                        'avg_tokens': round(usage['avg_tokens'], 1),
                        'total_cost': round(usage['total_cost'], 4)
                    }
                else:
                    stats['token_usage'] = {'total_tokens': 0, 'avg_tokens': 0, 'total_cost': 0}
                
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
        
        return await self._execute_with_retry(_stats_operation)
    
    async def get_table_list(self) -> List[str]:
        """Get list of all tables with improved error handling"""
        async def _tables_operation():
            async with self._get_connection() as db:
                cursor = await db.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """)
                tables = await cursor.fetchall()
                return [table[0] for table in tables]
        
        return await self._execute_with_retry(_tables_operation)
    
    async def get_table_data(self, table_name: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Get paginated table data with improved error handling"""
        async def _table_data_operation():
            async with self._get_connection() as db:
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
        
        return await self._execute_with_retry(_table_data_operation)
    
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute raw SQL query with improved error handling"""
        async def _query_operation():
            async with self._get_connection() as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        
        return await self._execute_with_retry(_query_operation)
    
    async def get_conversations(self, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Get conversation logs with pagination and improved error handling"""
        async def _conversations_operation():
            async with self._get_connection() as db:
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
        
        return await self._execute_with_retry(_conversations_operation)
    
    async def health_check(self) -> bool:
        """Check database health with improved error handling"""
        try:
            async with self._get_connection() as db:
                await db.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def close(self):
        """Cleanup database connections"""
        # Clean up any remaining connections
        logger.info("Database manager closed")

# Dependency to get database instance
async def get_db():
    db_manager = DatabaseManager()
    try:
        yield db_manager
    finally:
        await db_manager.close()
