# ======================================================
# IMPORTS
# ======================================================
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ======================================================
# DATABASE CONFIG (MYSQL)
# ======================================================
DATABASE_URL = "mysql+pymysql://root:root123@localhost/retinex_ai"

# ======================================================
# ENGINE
# ======================================================
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# ======================================================
# SESSION
# ======================================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ======================================================
# BASE
# ======================================================
Base = declarative_base()

# ======================================================
# DEPENDENCY
# ======================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()