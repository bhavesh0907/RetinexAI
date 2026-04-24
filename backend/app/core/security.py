from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

SECRET_KEY = "supersecretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_BCRYPT_BYTES = 72

def _password_too_long(password: str) -> bool:
    return len(password.encode("utf-8")) > MAX_BCRYPT_BYTES

def hash_password(password: str) -> str:
    if _password_too_long(password):
        raise ValueError("Password cannot be longer than 72 bytes for bcrypt.")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if _password_too_long(plain_password):
        return False
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=8)
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_token(token: str):
    try:
        print("🔍 RAW TOKEN RECEIVED:", token)

        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        print("🧼 CLEAN TOKEN:", token)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        print("✅ DECODED PAYLOAD:", payload)

        return payload

    except JWTError as e:
        print("❌ JWT Decode Error:", str(e))
        return None