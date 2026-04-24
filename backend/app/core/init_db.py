from app.core.database import Base, engine

# ✅ IMPORT ALL MODELS (THIS IS THE FIX)
from app.models.user import User
from app.models.history import History
from app.models.screening import Screening


def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()