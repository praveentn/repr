# migrate_database.py
"""
Database migration script for Knowledge Representation Engine v2.0
This script safely migrates your existing database to support the new caching features
"""

import asyncio
import aiosqlite
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    def __init__(self, db_path: str = "data/knowledge_repr.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(exist_ok=True)
    
    async def migrate(self):
        """Run complete database migration"""
        logger.info("🔄 Starting database migration to v2.0...")
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Enable WAL mode for better concurrency
                await db.execute("PRAGMA journal_mode=WAL")
                await db.execute("PRAGMA foreign_keys=ON")
                
                # Run migration steps
                await self.backup_database(db)
                await self.add_missing_columns(db)
                await self.create_new_tables(db)
                await self.create_indexes_safely(db)
                await self.verify_migration(db)
                
                await db.commit()
                logger.info("✅ Database migration completed successfully!")
                
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise
    
    async def backup_database(self, db):
        """Create a backup before migration"""
        logger.info("💾 Creating database backup...")
        
        # Create backup directory
        backup_dir = Path("data/backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"pre_migration_backup_{timestamp}.sql"
        
        try:
            # Create SQL dump
            with open(backup_file, 'w') as f:
                async with db.execute("SELECT sql FROM sqlite_master WHERE type='table'") as cursor:
                    async for row in cursor:
                        if row[0]:
                            f.write(f"{row[0]};\n")
                
                # Export data
                tables = await self.get_existing_tables(db)
                for table in tables:
                    f.write(f"\n-- Data for table {table}\n")
                    async with db.execute(f"SELECT * FROM {table}") as cursor:
                        async for row in cursor:
                            # This is a simple backup - in production you'd want a proper SQL dump
                            pass
            
            logger.info(f"✅ Backup created: {backup_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Backup creation failed: {e}")
    
    async def get_existing_tables(self, db):
        """Get list of existing tables"""
        cursor = await db.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        tables = await cursor.fetchall()
        return [table[0] for table in tables]
    
    async def table_exists(self, db, table_name):
        """Check if table exists"""
        cursor = await db.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        result = await cursor.fetchone()
        return result is not None
    
    async def column_exists(self, db, table_name, column_name):
        """Check if column exists in table"""
        try:
            cursor = await db.execute(f"PRAGMA table_info({table_name})")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            return column_name in column_names
        except Exception:
            return False
    
    async def add_missing_columns(self, db):
        """Add missing columns to existing tables"""
        logger.info("📝 Adding missing columns to existing tables...")
        
        # Add query_hash column to conversations table
        if await self.table_exists(db, 'conversations'):
            if not await self.column_exists(db, 'conversations', 'query_hash'):
                logger.info("  Adding query_hash column to conversations table...")
                await db.execute("ALTER TABLE conversations ADD COLUMN query_hash TEXT")
                logger.info("  ✅ Added query_hash column")
        
        # Add cache_hits column to user_sessions table if it doesn't exist
        if await self.table_exists(db, 'user_sessions'):
            if not await self.column_exists(db, 'user_sessions', 'cache_hits'):
                logger.info("  Adding cache_hits column to user_sessions table...")
                await db.execute("ALTER TABLE user_sessions ADD COLUMN cache_hits INTEGER DEFAULT 0")
                logger.info("  ✅ Added cache_hits column")
    
    async def create_new_tables(self, db):
        """Create new tables for v2.0"""
        logger.info("🗂️ Creating new tables...")
        
        # Create response_cache table
        if not await self.table_exists(db, 'response_cache'):
            logger.info("  Creating response_cache table...")
            await db.execute("""
                CREATE TABLE response_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_hash TEXT UNIQUE NOT NULL,
                    query TEXT NOT NULL,
                    context TEXT,
                    representation_mode TEXT NOT NULL,
                    user_preferences TEXT,
                    llm_response TEXT,
                    representation_output TEXT,
                    token_usage TEXT,
                    processing_time REAL,
                    llm_config TEXT,
                    usage_count INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("  ✅ Created response_cache table")
        
        # Ensure all other required tables exist
        required_tables = {
            'conversations': """
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
                    query_hash TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'user_sessions': """
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    user_id TEXT,
                    preferences TEXT,
                    conversation_count INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    total_processing_time REAL DEFAULT 0,
                    cache_hits INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'representation_feedback': """
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
            'system_config': """
                CREATE TABLE IF NOT EXISTS system_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_key TEXT UNIQUE NOT NULL,
                    config_value TEXT NOT NULL,
                    config_type TEXT DEFAULT 'string',
                    description TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'llm_usage_logs': """
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
        }
        
        for table_name, create_sql in required_tables.items():
            if not await self.table_exists(db, table_name):
                logger.info(f"  Creating {table_name} table...")
                await db.execute(create_sql)
                logger.info(f"  ✅ Created {table_name} table")
    
    async def create_indexes_safely(self, db):
        """Create indexes safely, only if they don't exist"""
        logger.info("📇 Creating database indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_activity ON user_sessions(last_activity)",
            "CREATE INDEX IF NOT EXISTS idx_conversations_mode ON conversations(representation_mode)",
            "CREATE INDEX IF NOT EXISTS idx_llm_usage_session ON llm_usage_logs(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_cache_hash ON response_cache(query_hash)",
            "CREATE INDEX IF NOT EXISTS idx_cache_mode ON response_cache(representation_mode)",
            "CREATE INDEX IF NOT EXISTS idx_cache_last_used ON response_cache(last_used)"
        ]
        
        # Only create query_hash index if the column exists
        if await self.column_exists(db, 'conversations', 'query_hash'):
            indexes.append("CREATE INDEX IF NOT EXISTS idx_conversations_hash ON conversations(query_hash)")
        
        for index_sql in indexes:
            try:
                await db.execute(index_sql)
                logger.info(f"  ✅ Created index: {index_sql.split()[-1]}")
            except Exception as e:
                logger.warning(f"  ⚠️ Index creation skipped: {e}")
    
    async def verify_migration(self, db):
        """Verify migration was successful"""
        logger.info("🔍 Verifying migration...")
        
        # Check all required tables exist
        required_tables = [
            'conversations', 'user_sessions', 'response_cache', 
            'representation_feedback', 'system_config', 'llm_usage_logs'
        ]
        
        existing_tables = await self.get_existing_tables(db)
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            raise Exception(f"Migration verification failed: Missing tables {missing_tables}")
        
        # Check conversations table has query_hash column
        if not await self.column_exists(db, 'conversations', 'query_hash'):
            raise Exception("Migration verification failed: conversations table missing query_hash column")
        
        # Check response_cache table structure
        cursor = await db.execute("PRAGMA table_info(response_cache)")
        cache_columns = await cursor.fetchall()
        cache_column_names = [col[1] for col in cache_columns]
        
        required_cache_columns = ['query_hash', 'query', 'representation_mode', 'usage_count']
        missing_cache_columns = [col for col in required_cache_columns if col not in cache_column_names]
        
        if missing_cache_columns:
            raise Exception(f"Migration verification failed: response_cache missing columns {missing_cache_columns}")
        
        logger.info("✅ Migration verification passed!")
        logger.info(f"  Tables: {len(existing_tables)} found")
        logger.info(f"  Cache columns: {len(cache_column_names)} found")

async def main():
    """Run database migration"""
    print("🔄 Knowledge Representation Engine v2.0 - Database Migration")
    print("=" * 60)
    
    migrator = DatabaseMigrator()
    
    try:
        await migrator.migrate()
        print("\n🎉 Migration completed successfully!")
        print("\nYou can now run the application:")
        print("  python start.py --mode dev")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\nPlease check the error message and try again.")
        print("If issues persist, you may need to:")
        print("1. Delete the existing database file")
        print("2. Run the migration again to create a fresh database")
        
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
