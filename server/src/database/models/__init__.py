"""
Import all models here so SQLAlchemy's mapper registry is populated
before Alembic or create_all() is called.
"""

from src.database.models.user import OAuthAccount, User
from src.database.models.elderly import ElderlyProfile, ViewerInvitation
from src.database.models.health import HealthRecord, HealthThreshold
from src.database.models.schedule import Schedule, ScheduleAlarm
from src.database.models.recommendation import AIActivityRecommendation
from src.database.models.notification import Notification, NotificationPreference

__all__ = [
    "User",
    "OAuthAccount",
    "ElderlyProfile",
    "ViewerInvitation",
    "HealthRecord",
    "HealthThreshold",
    "Schedule",
    "ScheduleAlarm",
    "AIActivityRecommendation",
    "Notification",
    "NotificationPreference",
]
