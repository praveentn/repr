# core/auth.py
import hashlib
import secrets
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

@dataclass
class User:
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

@dataclass
class SessionInfo:
    session_id: str
    user_id: Optional[int]
    created_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str

class AuthManager:
    """Authentication and authorization manager"""
    
    def __init__(self, secret_key: str = "your-secret-key-here"):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.token_expire_hours = 24
        self.sessions = {}  # In-memory session storage (would use Redis in production)
        
    def hash_password(self, password: str, salt: Optional[str] = None) -> str:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_hex = hashed_password.split(':')
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return password_hash.hex() == hash_hex
        except ValueError:
            return False
    
    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        return secrets.token_urlsafe(32)
    
    def create_session(self, user_id: Optional[int], request: Request) -> str:
        """Create new session"""
        session_id = self.generate_session_id()
        
        session_info = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        self.sessions[session_id] = session_info
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information"""
        session = self.sessions.get(session_id)
        if session:
            # Update last activity
            session.last_activity = datetime.now()
        return session
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session.last_activity > timedelta(hours=self.token_expire_hours):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.invalidate_session(session_id)
    
    def create_jwt_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT token"""
        payload = {
            "user_id": user_data.get("id"),
            "username": user_data.get("username"),
            "role": user_data.get("role", "user"),
            "exp": datetime.utcnow() + timedelta(hours=self.token_expire_hours),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def require_auth(self, required_role: Optional[str] = None):
        """Decorator for requiring authentication"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # This would be implemented based on your authentication needs
                return func(*args, **kwargs)
            return wrapper
        return decorator

class RateLimiter:
    """Simple rate limiting implementation"""
    
    def __init__(self, max_requests: int = 60, window_minutes: int = 1):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.requests = {}  # IP -> list of timestamps
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed"""
        current_time = time.time()
        window_start = current_time - (self.window_minutes * 60)
        
        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
        else:
            self.requests[identifier] = []
        
        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(current_time)
            return True
        
        return False
    
    def get_remaining_requests(self, identifier: str) -> int:
        """Get remaining requests for identifier"""
        current_time = time.time()
        window_start = current_time - (self.window_minutes * 60)
        
        if identifier in self.requests:
            recent_requests = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
            return max(0, self.max_requests - len(recent_requests))
        
        return self.max_requests

class SecurityUtils:
    """Security utility functions"""
    
    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_password(length: int = 16, include_symbols: bool = True) -> str:
        """Generate secure password"""
        import string
        
        chars = string.ascii_letters + string.digits
        if include_symbols:
            chars += "!@#$%^&*"
        
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 10000) -> str:
        """Sanitize user input"""
        import html
        
        # Remove potential XSS
        sanitized = html.escape(text)
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """Check if filename is safe"""
        import re
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'\.\.',  # Directory traversal
            r'[<>:"|?*]',  # Invalid filename characters
            r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$',  # Windows reserved names
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return False
        
        return True
    
    @staticmethod
    def validate_file_type(filename: str, allowed_types: list) -> bool:
        """Validate file type"""
        file_extension = filename.split('.')[-1].lower()
        return file_extension in [ext.lower() for ext in allowed_types]

# Security middleware
security = HTTPBearer(auto_error=False)

async def get_current_session(request: Request) -> Optional[SessionInfo]:
    """Get current session from request"""
    # Try to get session ID from cookie or header
    session_id = request.cookies.get("session_id") or request.headers.get("X-Session-ID")
    
    if not session_id:
        return None
    
    auth_manager = AuthManager()
    return auth_manager.get_session(session_id)

async def get_current_user(request: Request) -> Optional[User]:
    """Get current user from session"""
    session = await get_current_session(request)
    if not session or not session.user_id:
        return None
    
    # In a real implementation, you would fetch user from database
    # For now, return a mock user
    return User(
        id=session.user_id,
        username="user",
        email="user@example.com",
        role="user",
        is_active=True,
        created_at=datetime.now()
    )

async def require_auth(request: Request) -> User:
    """Require authentication for endpoint"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

async def require_admin(request: Request) -> User:
    """Require admin role for endpoint"""
    user = await require_auth(request)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

async def check_rate_limit(request: Request, rate_limiter: RateLimiter = None) -> bool:
    """Check rate limiting"""
    if not rate_limiter:
        rate_limiter = RateLimiter()
    
    client_ip = request.client.host if request.client else "unknown"
    
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    return True

# Utility functions for session management

def create_anonymous_session(request: Request) -> str:
    """Create anonymous session for unauthenticated users"""
    auth_manager = AuthManager()
    return auth_manager.create_session(user_id=None, request=request)

def validate_session_token(token: str) -> Optional[Dict[str, Any]]:
    """Validate session token"""
    auth_manager = AuthManager()
    return auth_manager.verify_jwt_token(token)

def get_session_info(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session information as dictionary"""
    auth_manager = AuthManager()
    session = auth_manager.get_session(session_id)
    
    if not session:
        return None
    
    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "created_at": session.created_at.isoformat(),
        "last_activity": session.last_activity.isoformat(),
        "ip_address": session.ip_address,
        "user_agent": session.user_agent
    }

# Authentication decorators and dependencies

def create_auth_dependency(required_role: Optional[str] = None):
    """Create FastAPI dependency for authentication"""
    async def auth_dependency(request: Request):
        user = await get_current_user(request)
        
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if required_role and user.role != required_role:
            raise HTTPException(status_code=403, detail=f"Role '{required_role}' required")
        
        return user
    
    return auth_dependency

# Initialize global instances
auth_manager = AuthManager()
rate_limiter = RateLimiter()
security_utils = SecurityUtils()

# Export commonly used functions
__all__ = [
    'AuthManager',
    'RateLimiter',
    'SecurityUtils',
    'User',
    'SessionInfo',
    'get_current_session',
    'get_current_user',
    'require_auth',
    'require_admin',
    'check_rate_limit',
    'create_anonymous_session',
    'validate_session_token',
    'get_session_info',
    'create_auth_dependency',
    'auth_manager',
    'rate_limiter',
    'security_utils'
]
