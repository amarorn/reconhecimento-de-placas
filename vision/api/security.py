
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

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") if CryptContext else None

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
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
    if not pwd_context:
        return plain_password == hashed_password
    
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
