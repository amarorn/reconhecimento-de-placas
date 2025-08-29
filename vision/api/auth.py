"""
Sistema de Autenticação - Arquitetura de Visão Computacional
===========================================================

Sistema de autenticação JWT com gerenciamento de usuários e permissões.
"""

import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from functools import wraps

# Dependências de autenticação
try:
    from jose import JWTError, jwt
    from passlib.context import CryptContext
    from fastapi import HTTPException, Depends, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
except ImportError as e:
    print(f"⚠️ Dependências de autenticação não disponíveis: {e}")
    print("Instale com: pip install python-jose[cryptography] passlib[bcrypt]")
    JWTError = Exception
    CryptContext = None
    HTTPException = Exception
    Depends = lambda x: x
    status = None
    HTTPBearer = None
    HTTPAuthorizationCredentials = None

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# =============================================================================

# Configurações padrão (devem ser sobrescritas em produção)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Contexto de criptografia
if CryptContext:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
else:
    pwd_context = None

# Esquema de autenticação
if HTTPBearer:
    security = HTTPBearer()
else:
    security = None

# =============================================================================
# MODELOS DE USUÁRIO
# =============================================================================

class User:
    """Modelo de usuário do sistema"""
    
    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        hashed_password: str,
        is_active: bool = True,
        permissions: List[str] = None,
        created_at: datetime = None
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.permissions = permissions or []
        self.created_at = created_at or datetime.utcnow()
    
    def has_permission(self, permission: str) -> bool:
        """Verifica se o usuário tem uma permissão específica"""
        return permission in self.permissions
    
    def has_any_permission(self, permissions: List[str]) -> bool:
        """Verifica se o usuário tem pelo menos uma das permissões"""
        return any(self.has_permission(p) for p in permissions)
    
    def has_all_permissions(self, permissions: List[str]) -> bool:
        """Verifica se o usuário tem todas as permissões"""
        return all(self.has_permission(p) for p in permissions)

class UserInDB(User):
    """Usuário armazenado no banco de dados"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_login = None
        self.login_attempts = 0
        self.locked_until = None

# =============================================================================
# FUNÇÕES DE CRIPTOGRAFIA
# =============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    if not pwd_context:
        return False
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    if not pwd_context:
        return password  # Fallback inseguro
    return pwd_context.hash(password)

# =============================================================================
# FUNÇÕES DE TOKEN JWT
# =============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria token de acesso JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Cria token de refresh JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifica e decodifica um token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodifica um token JWT (sem verificação de assinatura)"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# =============================================================================
# GESTOR DE AUTENTICAÇÃO
# =============================================================================

class AuthManager:
    """Gerenciador principal de autenticação"""
    
    def __init__(self):
        self.users: Dict[str, UserInDB] = {}
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self._initialize_default_users()
    
    def _initialize_default_users(self):
        """Inicializa usuários padrão do sistema"""
        # Usuário admin padrão
        admin_user = UserInDB(
            user_id="admin-001",
            username="admin",
            email="admin@vision.com",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            permissions=["admin", "read", "write", "delete", "monitor"]
        )
        
        # Usuário de teste
        test_user = UserInDB(
            user_id="test-001",
            username="test",
            email="test@vision.com",
            hashed_password=get_password_hash("test123"),
            is_active=True,
            permissions=["read", "write"]
        )
        
        # Usuário de monitoramento
        monitor_user = UserInDB(
            user_id="monitor-001",
            username="monitor",
            email="monitor@vision.com",
            hashed_password=get_password_hash("monitor123"),
            is_active=True,
            permissions=["read", "monitor"]
        )
        
        self.users[admin_user.user_id] = admin_user
        self.users[test_user.user_id] = test_user
        self.users[monitor_user.user_id] = monitor_user
    
    def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """Autentica um usuário com username e senha"""
        for user in self.users.values():
            if user.username == username and verify_password(password, user.hashed_password):
                if not user.is_active:
                    return None
                
                # Atualizar último login
                user.last_login = datetime.utcnow()
                user.login_attempts = 0
                
                return user
        return None
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        permissions: List[str] = None
    ) -> UserInDB:
        """Cria um novo usuário"""
        # Verificar se username já existe
        for user in self.users.values():
            if user.username == username:
                raise ValueError(f"Username '{username}' já existe")
        
        # Criar novo usuário
        user_id = f"user-{int(time.time())}"
        user = UserInDB(
            user_id=user_id,
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            permissions=permissions or ["read"],
            is_active=True
        )
        
        self.users[user_id] = user
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Obtém usuário por ID"""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """Obtém usuário por username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def update_user_permissions(self, user_id: str, permissions: List[str]) -> bool:
        """Atualiza permissões de um usuário"""
        user = self.get_user_by_id(user_id)
        if user:
            user.permissions = permissions
            return True
        return False
    
    def deactivate_user(self, user_id: str) -> bool:
        """Desativa um usuário"""
        user = self.get_user_by_id(user_id)
        if user:
            user.is_active = False
            return True
        return False
    
    def activate_user(self, user_id: str) -> bool:
        """Ativa um usuário"""
        user = self.get_user_by_id(user_id)
        if user:
            user.is_active = True
            return True
        return False
    
    def list_users(self) -> List[UserInDB]:
        """Lista todos os usuários"""
        return list(self.users.values())
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas dos usuários"""
        total_users = len(self.users)
        active_users = sum(1 for u in self.users.values() if u.is_active)
        inactive_users = total_users - active_users
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "last_updated": datetime.utcnow().isoformat()
        }

# =============================================================================
# INSTÂNCIA GLOBAL
# =============================================================================

auth_manager = AuthManager()

# =============================================================================
# FUNÇÕES DE DEPENDÊNCIA
# =============================================================================

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInDB:
    """Obtém o usuário atual baseado no token JWT"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth_manager.get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
    
    return user

def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Obtém o usuário ativo atual"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user

# =============================================================================
# DECORATORS DE PERMISSÃO
# =============================================================================

def require_permission(permission: str):
    """Decorator para requerer uma permissão específica"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Implementar verificação de permissão
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_any_permission(permissions: List[str]):
    """Decorator para requerer pelo menos uma das permissões"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Implementar verificação de permissão
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_all_permissions(permissions: List[str]):
    """Decorator para requerer todas as permissões"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Implementar verificação de permissão
            return func(*args, **kwargs)
        return wrapper
    return decorator

# =============================================================================
# FUNÇÕES DE UTILIDADE
# =============================================================================

def generate_password_reset_token(email: str) -> str:
    """Gera token para reset de senha"""
    delta = timedelta(hours=1)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "email": email, "type": "password_reset"},
        SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt

def verify_password_reset_token(token: str) -> Optional[str]:
    """Verifica token de reset de senha"""
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded_token["type"] != "password_reset":
            return None
        return decoded_token["email"]
    except JWTError:
        return None

def is_token_expired(token: str) -> bool:
    """Verifica se um token está expirado"""
    payload = decode_token(token)
    if not payload:
        return True
    
    exp = payload.get("exp")
    if not exp:
        return True
    
    return datetime.utcnow().timestamp() > exp

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# =============================================================================

def update_security_config(
    secret_key: str = None,
    access_token_expire_minutes: int = None,
    refresh_token_expire_days: int = None
):
    """Atualiza configurações de segurança"""
    global SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
    
    if secret_key:
        SECRET_KEY = secret_key
    
    if access_token_expire_minutes:
        ACCESS_TOKEN_EXPIRE_MINUTES = access_token_expire_minutes
    
    if refresh_token_expire_days:
        REFRESH_TOKEN_EXPIRE_DAYS = refresh_token_expire_days

def get_security_config() -> Dict[str, Any]:
    """Obtém configurações de segurança atuais"""
    return {
        "algorithm": ALGORITHM,
        "access_token_expire_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
        "refresh_token_expire_days": REFRESH_TOKEN_EXPIRE_DAYS,
        "secret_key_length": len(SECRET_KEY) if SECRET_KEY else 0
    }