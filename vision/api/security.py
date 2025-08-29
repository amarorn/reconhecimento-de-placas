"""
Módulo de Segurança - Tokens JWT
===============================

Funções para criação e verificação de tokens JWT.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

try:
    from jose import JWTError, jwt
    from passlib.context import CryptContext
except ImportError as e:
    print(f"⚠️ Dependências de segurança não disponíveis: {e}")
    JWTError = Exception
    jwt = None
    CryptContext = None

# Configurações JWT
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Context para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") if CryptContext else None

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Cria token de acesso JWT"""
    if not jwt:
        raise RuntimeError("JWT não está disponível")
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Cria refresh token JWT"""
    if not jwt:
        raise RuntimeError("JWT não está disponível")
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifica e decodifica token JWT"""
    if not jwt:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica senha contra hash"""
    if not pwd_context:
        # Fallback simples para desenvolvimento
        return plain_password == hashed_password
    
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    if not pwd_context:
        # Fallback simples para desenvolvimento
        return password
    
    return pwd_context.hash(password)
