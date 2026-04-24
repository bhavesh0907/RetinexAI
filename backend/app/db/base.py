# app/db/base.py

from app.db.database import Base

from app.models.screening import Screening

# 🔥 Import ALL models here (ONLY for registration)
from app.models import user