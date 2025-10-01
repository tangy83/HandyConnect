#!/usr/bin/env python3
"""
Security Hardening Module for HandyConnect Phase 12
Comprehensive security measures and hardening
"""

import os
import hashlib
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import jwt
from functools import wraps
import re
import html

logger = logging.getLogger(__name__)

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    # Authentication settings
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    password_min_length: int = 12
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True
    
    # Session settings
    session_timeout_minutes: int = 30
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    # Rate limiting
    rate_limit_requests_per_minute: int = 60
    rate_limit_requests_per_hour: int = 1000
    
    # Input validation
    max_input_length: int = 10000
    allowed_file_types: List[str] = None
    max_file_size_mb: int = 10
    
    # CORS settings
    allowed_origins: List[str] = None
    allowed_methods: List[str] = None
    allowed_headers: List[str] = None
    
    # Security headers
    enable_security_headers: bool = True
    enable_csp: bool = True
    enable_hsts: bool = True
    
    def __post_init__(self):
        if self.allowed_file_types is None:
            self.allowed_file_types = ['.txt', '.pdf', '.doc', '.docx', '.jpg', '.png', '.gif']
        
        if self.allowed_origins is None:
            self.allowed_origins = ['http://localhost:5001', 'https://localhost:5001']
        
        if self.allowed_methods is None:
            self.allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        
        if self.allowed_headers is None:
            self.allowed_headers = ['Content-Type', 'Authorization', 'X-Requested-With']

@dataclass
class SecurityEvent:
    """Security event log entry"""
    id: str
    event_type: str  # login_attempt, rate_limit, suspicious_activity, etc.
    severity: str  # low, medium, high, critical
    description: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    user_id: Optional[str] = None
    details: Dict[str, Any] = None

@dataclass
class UserSession:
    """User session information"""
    session_id: str
    user_id: str
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    is_active: bool = True
    login_attempts: int = 0
    locked_until: Optional[datetime] = None

class SecurityHardener:
    """Comprehensive security hardening system"""
    
    def __init__(self):
        self.config = self._load_security_config()
        self.active_sessions = {}
        self.security_events = []
        self.blocked_ips = set()
        self.rate_limit_tracker = {}
        
        logger.info("Security Hardener initialized")
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration"""
        # Generate JWT secret if not provided
        jwt_secret = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
        
        return SecurityConfig(
            jwt_secret=jwt_secret,
            jwt_algorithm="HS256",
            jwt_expiration_hours=int(os.getenv('JWT_EXPIRATION_HOURS', 24)),
            password_min_length=int(os.getenv('PASSWORD_MIN_LENGTH', 12)),
            rate_limit_requests_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', 60)),
            rate_limit_requests_per_hour=int(os.getenv('RATE_LIMIT_PER_HOUR', 1000))
        )
    
    def hash_password(self, password: str) -> str:
        """Hash password using secure method"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_hex = password_hash.split(':')
            password_hash_bytes = bytes.fromhex(hash_hex)
            
            computed_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            
            return secrets.compare_digest(password_hash_bytes, computed_hash)
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        result = {
            'is_valid': True,
            'errors': [],
            'strength_score': 0,
            'requirements_met': {}
        }
        
        # Length requirement
        if len(password) < self.config.password_min_length:
            result['errors'].append(f"Password must be at least {self.config.password_min_length} characters long")
            result['is_valid'] = False
        else:
            result['requirements_met']['length'] = True
            result['strength_score'] += 20
        
        # Uppercase requirement
        if self.config.password_require_uppercase and not re.search(r'[A-Z]', password):
            result['errors'].append("Password must contain at least one uppercase letter")
            result['is_valid'] = False
        else:
            result['requirements_met']['uppercase'] = True
            result['strength_score'] += 20
        
        # Lowercase requirement
        if self.config.password_require_lowercase and not re.search(r'[a-z]', password):
            result['errors'].append("Password must contain at least one lowercase letter")
            result['is_valid'] = False
        else:
            result['requirements_met']['lowercase'] = True
            result['strength_score'] += 20
        
        # Number requirement
        if self.config.password_require_numbers and not re.search(r'\d', password):
            result['errors'].append("Password must contain at least one number")
            result['is_valid'] = False
        else:
            result['requirements_met']['numbers'] = True
            result['strength_score'] += 20
        
        # Special character requirement
        if self.config.password_require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result['errors'].append("Password must contain at least one special character")
            result['is_valid'] = False
        else:
            result['requirements_met']['special'] = True
            result['strength_score'] += 20
        
        # Common password check
        common_passwords = ['password', '123456', 'admin', 'qwerty', 'letmein']
        if password.lower() in common_passwords:
            result['errors'].append("Password is too common")
            result['is_valid'] = False
            result['strength_score'] -= 50
        
        return result
    
    def generate_jwt_token(self, user_id: str, additional_claims: Dict[str, Any] = None) -> str:
        """Generate JWT token"""
        try:
            now = datetime.now(timezone.utc)
            payload = {
                'user_id': user_id,
                'iat': now,
                'exp': now + timedelta(hours=self.config.jwt_expiration_hours),
                'jti': secrets.token_urlsafe(16)  # JWT ID for uniqueness
            }
            
            if additional_claims:
                payload.update(additional_claims)
            
            token = jwt.encode(payload, self.config.jwt_secret, algorithm=self.config.jwt_algorithm)
            return token
            
        except Exception as e:
            logger.error(f"Error generating JWT token: {e}")
            raise
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token, 
                self.config.jwt_secret, 
                algorithms=[self.config.jwt_algorithm]
            )
            return {'valid': True, 'payload': payload}
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError as e:
            return {'valid': False, 'error': f'Invalid token: {str(e)}'}
    
    def sanitize_input(self, input_data: Any) -> Any:
        """Sanitize user input to prevent XSS and injection attacks"""
        if isinstance(input_data, str):
            # HTML escape
            sanitized = html.escape(input_data)
            
            # Remove potentially dangerous characters
            sanitized = re.sub(r'[<>"\']', '', sanitized)
            
            # Limit length
            if len(sanitized) > self.config.max_input_length:
                sanitized = sanitized[:self.config.max_input_length]
            
            return sanitized
        
        elif isinstance(input_data, dict):
            return {key: self.sanitize_input(value) for key, value in input_data.items()}
        
        elif isinstance(input_data, list):
            return [self.sanitize_input(item) for item in input_data]
        
        else:
            return input_data
    
    def validate_file_upload(self, filename: str, file_size: int) -> Dict[str, Any]:
        """Validate file upload"""
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check file extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in self.config.allowed_file_types:
            result['errors'].append(f"File type {file_ext} is not allowed")
            result['is_valid'] = False
        
        # Check file size
        max_size_bytes = self.config.max_file_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            result['errors'].append(f"File size exceeds maximum allowed size of {self.config.max_file_size_mb}MB")
            result['is_valid'] = False
        
        # Check filename for suspicious patterns
        suspicious_patterns = ['..', '/', '\\', '<', '>', '|', '?', '*']
        for pattern in suspicious_patterns:
            if pattern in filename:
                result['errors'].append("Filename contains suspicious characters")
                result['is_valid'] = False
                break
        
        return result
    
    def check_rate_limit(self, ip_address: str, endpoint: str = None) -> Dict[str, Any]:
        """Check rate limiting for IP address"""
        now = datetime.now(timezone.utc)
        key = f"{ip_address}:{endpoint}" if endpoint else ip_address
        
        if key not in self.rate_limit_tracker:
            self.rate_limit_tracker[key] = {
                'requests': [],
                'blocked_until': None
            }
        
        tracker = self.rate_limit_tracker[key]
        
        # Check if currently blocked
        if tracker['blocked_until'] and now < tracker['blocked_until']:
            return {
                'allowed': False,
                'reason': 'Rate limit exceeded',
                'retry_after': int((tracker['blocked_until'] - now).total_seconds())
            }
        
        # Clean old requests
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        tracker['requests'] = [req_time for req_time in tracker['requests'] if req_time > hour_ago]
        
        # Count requests in last minute and hour
        requests_last_minute = len([req for req in tracker['requests'] if req > minute_ago])
        requests_last_hour = len(tracker['requests'])
        
        # Check limits
        if requests_last_minute >= self.config.rate_limit_requests_per_minute:
            tracker['blocked_until'] = now + timedelta(minutes=1)
            self.log_security_event('rate_limit', 'medium', 
                                  f"Rate limit exceeded for {ip_address}", 
                                  ip_address, 'Rate Limiter')
            return {
                'allowed': False,
                'reason': 'Too many requests per minute',
                'retry_after': 60
            }
        
        if requests_last_hour >= self.config.rate_limit_requests_per_hour:
            tracker['blocked_until'] = now + timedelta(hours=1)
            self.log_security_event('rate_limit', 'high', 
                                  f"Hourly rate limit exceeded for {ip_address}", 
                                  ip_address, 'Rate Limiter')
            return {
                'allowed': False,
                'reason': 'Too many requests per hour',
                'retry_after': 3600
            }
        
        # Add current request
        tracker['requests'].append(now)
        
        return {'allowed': True}
    
    def create_user_session(self, user_id: str, ip_address: str, user_agent: str) -> str:
        """Create new user session"""
        session_id = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=now,
            last_activity=now
        )
        
        self.active_sessions[session_id] = session
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id
    
    def validate_session(self, session_id: str, ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Validate user session"""
        if session_id not in self.active_sessions:
            return {'valid': False, 'reason': 'Session not found'}
        
        session = self.active_sessions[session_id]
        now = datetime.now(timezone.utc)
        
        # Check if session is active
        if not session.is_active:
            return {'valid': False, 'reason': 'Session inactive'}
        
        # Check if session is locked
        if session.locked_until and now < session.locked_until:
            return {'valid': False, 'reason': 'Session locked'}
        
        # Check session timeout
        timeout_threshold = now - timedelta(minutes=self.config.session_timeout_minutes)
        if session.last_activity < timeout_threshold:
            session.is_active = False
            return {'valid': False, 'reason': 'Session expired'}
        
        # Check IP address consistency
        if session.ip_address != ip_address:
            self.log_security_event('suspicious_activity', 'medium',
                                  f"IP address changed for session {session_id}",
                                  ip_address, 'Session Manager',
                                  {'old_ip': session.ip_address, 'new_ip': ip_address})
            # Don't invalidate session, but log the event
        
        # Update last activity
        session.last_activity = now
        
        return {'valid': True, 'session': session}
    
    def handle_login_attempt(self, user_id: str, ip_address: str, user_agent: str, success: bool) -> Dict[str, Any]:
        """Handle login attempt and apply security measures"""
        # Find existing session or create tracking
        session_key = f"{user_id}:{ip_address}"
        
        if session_key not in self.active_sessions:
            # Create tracking session for failed attempts
            session_id = secrets.token_urlsafe(16)
            session = UserSession(
                session_id=session_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                created_at=datetime.now(timezone.utc),
                last_activity=datetime.now(timezone.utc)
            )
            self.active_sessions[session_key] = session
        
        session = self.active_sessions[session_key]
        
        if success:
            # Reset login attempts on successful login
            session.login_attempts = 0
            session.locked_until = None
            session.is_active = True
            
            self.log_security_event('login_success', 'low', 
                                  f"Successful login for user {user_id}", 
                                  ip_address, 'Authentication')
            
            return {'success': True, 'session_id': session.session_id}
        
        else:
            # Increment failed attempts
            session.login_attempts += 1
            
            self.log_security_event('login_failed', 'medium', 
                                  f"Failed login attempt for user {user_id} (attempt {session.login_attempts})", 
                                  ip_address, 'Authentication')
            
            # Lock account if max attempts reached
            if session.login_attempts >= self.config.max_login_attempts:
                session.locked_until = datetime.now(timezone.utc) + timedelta(minutes=self.config.lockout_duration_minutes)
                
                self.log_security_event('account_locked', 'high', 
                                      f"Account locked for user {user_id} due to excessive failed attempts", 
                                      ip_address, 'Authentication')
                
                return {
                    'success': False, 
                    'locked': True, 
                    'lockout_duration': self.config.lockout_duration_minutes
                }
            
            return {'success': False, 'attempts_remaining': self.config.max_login_attempts - session.login_attempts}
    
    def log_security_event(self, event_type: str, severity: str, description: str, 
                          ip_address: str, user_agent: str = 'Unknown', 
                          user_id: str = None, details: Dict[str, Any] = None):
        """Log security event"""
        event = SecurityEvent(
            id=secrets.token_urlsafe(16),
            event_type=event_type,
            severity=severity,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            details=details or {}
        )
        
        self.security_events.append(event)
        
        # Log to file as well
        logger.warning(f"Security Event: {event_type} - {description} (IP: {ip_address})")
        
        # Clean old events (keep last 1000)
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
    
    def get_security_events(self, event_type: str = None, severity: str = None, 
                           hours: int = 24) -> List[SecurityEvent]:
        """Get security events with optional filtering"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        filtered_events = [
            event for event in self.security_events
            if event.timestamp > cutoff_time
        ]
        
        if event_type:
            filtered_events = [event for event in filtered_events if event.event_type == event_type]
        
        if severity:
            filtered_events = [event for event in filtered_events if event.severity == severity]
        
        return sorted(filtered_events, key=lambda x: x.timestamp, reverse=True)
    
    def block_ip(self, ip_address: str, reason: str = "Suspicious activity"):
        """Block IP address"""
        self.blocked_ips.add(ip_address)
        self.log_security_event('ip_blocked', 'high', 
                              f"IP {ip_address} blocked: {reason}", 
                              ip_address, 'IP Blocker')
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        return ip_address in self.blocked_ips
    
    def generate_security_headers(self) -> Dict[str, str]:
        """Generate security headers for HTTP responses"""
        headers = {}
        
        if self.config.enable_security_headers:
            headers.update({
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Referrer-Policy': 'strict-origin-when-cross-origin',
                'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
            })
        
        if self.config.enable_hsts:
            headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        if self.config.enable_csp:
            csp_policy = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://cdn.jsdelivr.net; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
            headers['Content-Security-Policy'] = csp_policy
        
        return headers
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)
        
        recent_events = [event for event in self.security_events if event.timestamp > last_24h]
        
        return {
            'generated_at': now.isoformat(),
            'summary': {
                'total_events_24h': len(recent_events),
                'events_by_type': {
                    event_type: len([e for e in recent_events if e.event_type == event_type])
                    for event_type in set(e.event_type for e in recent_events)
                },
                'events_by_severity': {
                    severity: len([e for e in recent_events if e.severity == severity])
                    for severity in set(e.severity for e in recent_events)
                },
                'active_sessions': len([s for s in self.active_sessions.values() if s.is_active]),
                'blocked_ips': len(self.blocked_ips),
                'rate_limited_ips': len(self.rate_limit_tracker)
            },
            'recent_events': [asdict(event) for event in recent_events[-50:]],  # Last 50 events
            'configuration': asdict(self.config)
        }

# Security decorators for Flask routes
def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # This would be implemented with actual Flask request handling
        # For now, return the function as-is
        return f(*args, **kwargs)
    return decorated_function

def require_permissions(permissions: List[str]):
    """Decorator to require specific permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This would check user permissions
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit(requests_per_minute: int = 60):
    """Decorator to apply rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This would apply rate limiting
            return f(*args, **kwargs)
        return decorated_function
    return decorator
