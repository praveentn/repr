# core/utils.py
import json
import csv
import os
import zipfile
import tempfile
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import logging
import hashlib
import time
from functools import wraps
import pandas as pd
from io import StringIO, BytesIO

class FileUtils:
    """File handling utilities"""
    
    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> bool:
        """Ensure directory exists"""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logging.error(f"Error creating directory {path}: {e}")
            return False
    
    @staticmethod
    def safe_write_file(filepath: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
        """Safely write file with error handling"""
        try:
            # Ensure parent directory exists
            FileUtils.ensure_directory(Path(filepath).parent)
            
            # Write to temporary file first, then rename
            temp_file = f"{filepath}.tmp"
            with open(temp_file, 'w', encoding=encoding) as f:
                f.write(content)
            
            # Atomic rename
            os.rename(temp_file, filepath)
            return True
        except Exception as e:
            logging.error(f"Error writing file {filepath}: {e}")
            return False
    
    @staticmethod
    def safe_read_file(filepath: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
        """Safely read file with error handling"""
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            logging.error(f"Error reading file {filepath}: {e}")
            return None
    
    @staticmethod
    def get_file_size(filepath: Union[str, Path]) -> int:
        """Get file size in bytes"""
        try:
            return Path(filepath).stat().st_size
        except Exception:
            return 0
    
    @staticmethod
    def is_file_recent(filepath: Union[str, Path], max_age_hours: int = 24) -> bool:
        """Check if file was modified recently"""
        try:
            file_time = datetime.fromtimestamp(Path(filepath).stat().st_mtime)
            return datetime.now() - file_time < timedelta(hours=max_age_hours)
        except Exception:
            return False
    
    @staticmethod
    def clean_old_files(directory: Union[str, Path], max_age_days: int = 30, pattern: str = "*") -> int:
        """Clean old files from directory"""
        try:
            directory = Path(directory)
            if not directory.exists():
                return 0
            
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            deleted_count = 0
            
            for file_path in directory.glob(pattern):
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
            
            return deleted_count
        except Exception as e:
            logging.error(f"Error cleaning old files: {e}")
            return 0

class DataExportUtils:
    """Data export utilities"""
    
    @staticmethod
    def export_to_json(data: Any, filepath: Union[str, Path]) -> bool:
        """Export data to JSON file"""
        try:
            json_content = json.dumps(data, indent=2, default=str, ensure_ascii=False)
            return FileUtils.safe_write_file(filepath, json_content)
        except Exception as e:
            logging.error(f"Error exporting to JSON: {e}")
            return False
    
    @staticmethod
    def export_to_csv(data: List[Dict], filepath: Union[str, Path]) -> bool:
        """Export data to CSV file"""
        try:
            if not data:
                return False
            
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8')
            return True
        except Exception as e:
            logging.error(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def export_to_excel(data: Dict[str, List[Dict]], filepath: Union[str, Path]) -> bool:
        """Export data to Excel file with multiple sheets"""
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for sheet_name, sheet_data in data.items():
                    if sheet_data:
                        df = pd.DataFrame(sheet_data)
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            return True
        except Exception as e:
            logging.error(f"Error exporting to Excel: {e}")
            return False
    
    @staticmethod
    def create_zip_export(files: Dict[str, Any], zip_filepath: Union[str, Path]) -> bool:
        """Create ZIP file with multiple exported files"""
        try:
            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for filename, content in files.items():
                    if isinstance(content, (dict, list)):
                        # JSON content
                        json_content = json.dumps(content, indent=2, default=str)
                        zipf.writestr(filename, json_content)
                    elif isinstance(content, str):
                        # Text content
                        zipf.writestr(filename, content)
                    elif isinstance(content, bytes):
                        # Binary content
                        zipf.writestr(filename, content)
            return True
        except Exception as e:
            logging.error(f"Error creating ZIP export: {e}")
            return False

class CacheUtils:
    """Simple in-memory caching utilities"""
    
    def __init__(self, default_ttl: int = 3600):
        self.cache = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if key in self.cache:
            value, expiry = self.cache[key]
            if time.time() < expiry:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cached value"""
        if ttl is None:
            ttl = self.default_ttl
        expiry = time.time() + ttl
        self.cache[key] = (value, expiry)
    
    def delete(self, key: str) -> bool:
        """Delete cached value"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cached values"""
        self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry) in self.cache.items()
            if current_time >= expiry
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)

class PerformanceUtils:
    """Performance monitoring utilities"""
    
    @staticmethod
    def measure_execution_time(func):
        """Decorator to measure function execution time"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logging.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logging.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
                "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                "percent": process.memory_percent()
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_system_stats() -> Dict[str, Any]:
        """Get system performance statistics"""
        try:
            import psutil
            
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "process_count": len(psutil.pids())
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}

class ValidationUtils:
    """Input validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        import re
        pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        import re
        # Remove dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:251-len(ext)] + ext
        return sanitized
    
    @staticmethod
    def validate_json(json_string: str) -> bool:
        """Validate JSON string"""
        try:
            json.loads(json_string)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
    
    @staticmethod
    def limit_string_length(text: str, max_length: int, suffix: str = "...") -> str:
        """Limit string length with suffix"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

class HashUtils:
    """Hashing and checksum utilities"""
    
    @staticmethod
    def generate_file_hash(filepath: Union[str, Path], algorithm: str = 'sha256') -> Optional[str]:
        """Generate hash for file"""
        try:
            hash_func = getattr(hashlib, algorithm)()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            logging.error(f"Error generating file hash: {e}")
            return None
    
    @staticmethod
    def generate_content_hash(content: str, algorithm: str = 'sha256') -> str:
        """Generate hash for content"""
        hash_func = getattr(hashlib, algorithm)()
        hash_func.update(content.encode('utf-8'))
        return hash_func.hexdigest()
    
    @staticmethod
    def verify_file_integrity(filepath: Union[str, Path], expected_hash: str, algorithm: str = 'sha256') -> bool:
        """Verify file integrity using hash"""
        actual_hash = HashUtils.generate_file_hash(filepath, algorithm)
        return actual_hash == expected_hash if actual_hash else False

class LoggingUtils:
    """Logging utilities"""
    
    @staticmethod
    def setup_logging(
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        log_format: str = "json"
    ) -> None:
        """Setup application logging"""
        
        level = getattr(logging, log_level.upper(), logging.INFO)
        
        if log_format == "json":
            formatter = logging.Formatter(
                '{"timestamp":"%(asctime)s","level":"%(levelname)s","module":"%(name)s","message":"%(message)s"}'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        handlers = [console_handler]
        
        # File handler
        if log_file:
            FileUtils.ensure_directory(Path(log_file).parent)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        
        logging.basicConfig(
            level=level,
            handlers=handlers,
            force=True
        )
    
    @staticmethod
    def log_api_request(request_id: str, method: str, path: str, processing_time: float) -> None:
        """Log API request"""
        logging.info(f"API Request - ID: {request_id}, Method: {method}, Path: {path}, Time: {processing_time:.3f}s")
    
    @staticmethod
    def log_llm_usage(model: str, tokens: int, cost: float, processing_time: float) -> None:
        """Log LLM usage"""
        logging.info(f"LLM Usage - Model: {model}, Tokens: {tokens}, Cost: ${cost:.4f}, Time: {processing_time:.3f}s")

class AsyncUtils:
    """Async utilities"""
    
    @staticmethod
    async def run_with_timeout(coro, timeout_seconds: float):
        """Run coroutine with timeout"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout_seconds)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
    
    @staticmethod
    async def gather_with_concurrency(tasks: List, max_concurrency: int = 10):
        """Run tasks with limited concurrency"""
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def bounded_task(task):
            async with semaphore:
                return await task
        
        return await asyncio.gather(*[bounded_task(task) for task in tasks])

# Global utility instances
cache = CacheUtils()
performance = PerformanceUtils()
validation = ValidationUtils()
file_utils = FileUtils()
export_utils = DataExportUtils()
hash_utils = HashUtils()
logging_utils = LoggingUtils()
async_utils = AsyncUtils()

# Commonly used functions
def get_timestamp() -> str:
    """Get current timestamp as string"""
    return datetime.now().isoformat()

def format_bytes(bytes_value: int) -> str:
    """Format bytes as human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def format_duration(seconds: float) -> str:
    """Format duration in seconds as human readable string"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"

def generate_unique_id() -> str:
    """Generate unique ID"""
    import uuid
    return str(uuid.uuid4())

def is_production() -> bool:
    """Check if running in production environment"""
    return os.getenv("ENVIRONMENT", "development").lower() == "production"

# Export all utilities
__all__ = [
    'FileUtils', 'DataExportUtils', 'CacheUtils', 'PerformanceUtils',
    'ValidationUtils', 'HashUtils', 'LoggingUtils', 'AsyncUtils',
    'cache', 'performance', 'validation', 'file_utils', 'export_utils',
    'hash_utils', 'logging_utils', 'async_utils',
    'get_timestamp', 'format_bytes', 'format_duration', 'generate_unique_id', 'is_production'
]
