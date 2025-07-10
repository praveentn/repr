# scripts/migrate_database.py
"""
Database migration script for Knowledge Representation Engine
Handles schema updates and data migrations
"""

import asyncio
import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Handles database schema migrations"""
    
    def __init__(self, db_path: str = "data/knowledge_repr.db"):
        self.db_path = Path(db_path)
        self.migrations_dir = Path("migrations")
        self.migrations_dir.mkdir(exist_ok=True)
        
    def get_current_version(self) -> int:
        """Get current database schema version"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version INTEGER PRIMARY KEY,
                        applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        description TEXT
                    )
                """)
                
                cursor.execute("SELECT MAX(version) FROM schema_migrations")
                result = cursor.fetchone()
                return result[0] if result[0] is not None else 0
        except Exception as e:
            logger.error(f"Error getting schema version: {e}")
            return 0
    
    def apply_migration(self, version: int, description: str, sql_commands: List[str]):
        """Apply a single migration"""
        logger.info(f"Applying migration {version}: {description}")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Execute migration commands
                for command in sql_commands:
                    cursor.execute(command)
                
                # Record migration
                cursor.execute("""
                    INSERT INTO schema_migrations (version, description)
                    VALUES (?, ?)
                """, (version, description))
                
                conn.commit()
                logger.info(f"Migration {version} applied successfully")
                
        except Exception as e:
            logger.error(f"Error applying migration {version}: {e}")
            raise
    
    def run_migrations(self):
        """Run all pending migrations"""
        current_version = self.get_current_version()
        logger.info(f"Current database version: {current_version}")
        
        migrations = self.get_migrations()
        
        for migration in migrations:
            if migration['version'] > current_version:
                self.apply_migration(
                    migration['version'],
                    migration['description'],
                    migration['commands']
                )
        
        logger.info("All migrations completed")
    
    def get_migrations(self) -> List[Dict[str, Any]]:
        """Get list of available migrations"""
        return [
            {
                'version': 1,
                'description': 'Add user preferences table',
                'commands': [
                    """
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        preference_key TEXT NOT NULL,
                        preference_value TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, preference_key)
                    )
                    """,
                    "CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id)"
                ]
            },
            {
                'version': 2,
                'description': 'Add representation feedback ratings',
                'commands': [
                    """
                    ALTER TABLE representation_feedback 
                    ADD COLUMN usefulness_rating INTEGER DEFAULT NULL
                    """,
                    """
                    ALTER TABLE representation_feedback 
                    ADD COLUMN clarity_rating INTEGER DEFAULT NULL
                    """
                ]
            },
            {
                'version': 3,
                'description': 'Add performance metrics table',
                'commands': [
                    """
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        endpoint TEXT NOT NULL,
                        method TEXT NOT NULL,
                        response_time REAL NOT NULL,
                        status_code INTEGER NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    "CREATE INDEX idx_performance_metrics_timestamp ON performance_metrics(timestamp)",
                    "CREATE INDEX idx_performance_metrics_endpoint ON performance_metrics(endpoint)"
                ]
            },
            {
                'version': 4,
                'description': 'Add cost tracking fields',
                'commands': [
                    """
                    ALTER TABLE llm_usage_logs 
                    ADD COLUMN model_version TEXT DEFAULT NULL
                    """,
                    """
                    ALTER TABLE llm_usage_logs 
                    ADD COLUMN region TEXT DEFAULT NULL
                    """
                ]
            }
        ]


