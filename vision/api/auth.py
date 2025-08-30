#!/usr/bin/env python3
"""
Sistema de Autenticação - API de Visão Computacional
====================================================

Este módulo implementa o sistema de autenticação JWT para a API.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum

try:
    from fastapi import Depends, HTTPException, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from passlib.context import CryptContext
    from jose import JWTError, jwt
except ImportError:
    HTTPBearer = None
    CryptContext = None
    JWTError = None
    jwt = None

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if CryptContext:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
else:
    pwd_context = None

if HTTPBearer:
    security = HTTPBearer()
else:
    security = None


class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    TRAIN = "train"
    DEPLOY = "deploy"


class User:
    def __init__(self, user_id: str, username: str, email: str, 
                 permissions: List[str] = None, is_active: bool = True):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.permissions = permissions or [Permission.READ]
        self.is_active = is_active
        self.created_at = datetime.utcnow()
        self.last_login = None
        self.login_attempts = 0
    
    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions
    
    def has_any_permission(self, permissions: List[str]) -> bool:
        return any(self.has_permission(p) for p in permissions)
    
    def has_all_permissions(self, permissions: List[str]) -> bool:
        return all(self.has_permission(p) for p in permissions)


class UserInDB(User):
    def __init__(self, user_id: str, username: str, email: str, 
                 hashed_password: str, permissions: List[str] = None, is_active: bool = True):
        super().__init__(user_id, username, email, permissions, is_active)
        self.hashed_password = hashed_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not pwd_context:
        return False
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    if not pwd_context:
        return password
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    if not jwt:
        return "dummy-token"
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    if not jwt:
        return "dummy-refresh-token"
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    if not jwt:
        return {"sub": "dummy-user", "username": "dummy"}
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


class AuthManager:
    def __init__(self):
        self.users: Dict[str, UserInDB] = {}
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self._initialize_default_users()
    
    def _initialize_default_users(self):
        default_admin = UserInDB(
            user_id="admin-001",
            username="admin",
            email="admin@vision.com",
            hashed_password=get_password_hash("admin123"),
            permissions=[Permission.ADMIN, Permission.READ, Permission.WRITE, Permission.TRAIN, Permission.DEPLOY],
            is_active=True
        )
        
        default_user = UserInDB(
            user_id="user-001",
            username="user",
            email="user@vision.com",
            hashed_password=get_password_hash("user123"),
            permissions=[Permission.READ, Permission.WRITE],
            is_active=True
        )
        
        self.users[default_admin.user_id] = default_admin
        self.users[default_user.user_id] = default_user
        
        logger.info("Usuários padrão inicializados")
    
    def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        for user in self.users.values():
            if user.username == username and verify_password(password, user.hashed_password):
                if not user.is_active:
                    return None
                
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
        user_id = f"user-{len(self.users) + 1:03d}"
        hashed_password = get_password_hash(password)
        
        user = UserInDB(
            user_id=user_id,
            username=username,
            email=email,
            hashed_password=hashed_password,
            permissions=permissions or [Permission.READ],
            is_active=True
        )
        
        self.users[user_id] = user
        logger.info(f"Usuário criado: {username}")
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def update_user_permissions(self, user_id: str, permissions: List[str]) -> bool:
        user = self.get_user_by_id(user_id)
        if user:
            user.permissions = permissions
            return True
        return False
    
    def deactivate_user(self, user_id: str) -> bool:
        user = self.get_user_by_id(user_id)
        if user:
            user.is_active = False
            return True
        return False
    
    def activate_user(self, user_id: str) -> bool:
        user = self.get_user_by_id(user_id)
        if user:
            user.is_active = True
            return True
        return False
    
    def list_users(self) -> List[UserInDB]:
        return list(self.users.values())
    
    def get_user_stats(self) -> Dict[str, Any]:
        total_users = len(self.users)
        active_users = sum(1 for u in self.users.values() if u.is_active)
        inactive_users = total_users - active_users
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "last_updated": datetime.utcnow().isoformat()
        }


auth_manager = AuthManager()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInDB:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais não fornecidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("username")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    current_user = auth_manager.get_user_by_username(username)
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    
    return current_user


def require_permission(permission: str):
    def permission_dependency(current_user: UserInDB = Depends(get_current_user)):
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão necessária: {permission}"
            )
        return current_user
    return permission_dependency


def require_any_permission(permissions: List[str]):
    def permission_dependency(current_user: UserInDB = Depends(get_current_user)):
        if not current_user.has_any_permission(permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão necessária: uma de {permissions}"
            )
        return current_user
    return permission_dependency
