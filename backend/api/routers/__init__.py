from .auth import router as auth
from .predictions import router as predictions
from .admin import router as admin
from .reports import router as reports
from .users import router as users

__all__ = ["auth", "predictions", "admin", "reports", "users"]
