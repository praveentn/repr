CREATE TABLE conversations (
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
                );
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    user_id TEXT,
                    preferences TEXT,
                    conversation_count INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    total_processing_time REAL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
                );
CREATE TABLE representation_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    session_id TEXT,
                    rating INTEGER,
                    feedback_text TEXT,
                    representation_mode TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                );
CREATE TABLE system_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_key TEXT UNIQUE NOT NULL,
                    config_value TEXT NOT NULL,
                    config_type TEXT DEFAULT 'string',
                    description TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
CREATE TABLE llm_usage_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    total_tokens INTEGER,
                    cost_estimate REAL,
                    response_time REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
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
            );

-- Data for table conversations

-- Data for table user_sessions

-- Data for table representation_feedback

-- Data for table system_config

-- Data for table llm_usage_logs

-- Data for table response_cache
