import enum


class AuthProvider(str, enum.Enum):
    EMAIL = "email"
    GOOGLE = "google"


class MobilityLevel(str, enum.Enum):
    INDEPENDENT = "independent"
    ASSISTED = "assisted"
    WHEELCHAIR = "wheelchair"
    BEDRIDDEN = "bedridden"


class ElderlyStatus(str, enum.Enum):
    ACTIVE = "active"
    CRITICAL = "critical"
    INACTIVE = "inactive"


class HealthStatus(str, enum.Enum):
    NORMAL = "normal"
    WARNING = "warning"          # set by fuzzy logic analysis
    NEEDS_ATTENTION = "needs_attention"   # set by threshold-based checks
    CRITICAL = "critical"


class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    EXPIRED = "expired"


class ScheduleType(str, enum.Enum):
    MEDICATION = "medication"
    ROUTINE_CHECKUP = "routine_checkup"
    DAILY_ACTIVITY = "daily_activity"


class RecurrenceType(str, enum.Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"           # uses recurrence_rule (iCal RRULE)


class RecommendationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ActivityCategory(str, enum.Enum):
    PHYSICAL = "physical"       # senam kursi, jalan santai
    COGNITIVE = "cognitive"     # teka-teki, membaca
    SOCIAL = "social"           # berkumpul, mengobrol
    CREATIVE = "creative"       # melukis, kerajinan tangan
    RELAXATION = "relaxation"   # meditasi, pernapasan
    NATURE = "nature"           # berkebun, berjemur
    MUSIC = "music"             # terapi musik, menyanyi


class NotificationType(str, enum.Enum):
    HEALTH_RECORDED = "health_recorded"
    CRITICAL_ALERT = "critical_alert"
    WEEKLY_SUMMARY = "weekly_summary"
    ALARM_REMINDER = "alarm_reminder"
    ACTIVITY_RECOMMENDATION = "activity_recommendation"
    INVITATION = "invitation"


class NotificationChannel(str, enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"


class HealthParameter(str, enum.Enum):
    SYSTOLIC_BP = "systolic_bp"
    DIASTOLIC_BP = "diastolic_bp"
    BLOOD_SUGAR = "blood_sugar"
    HEART_RATE = "heart_rate"
    BODY_TEMPERATURE = "body_temperature"
    BODY_WEIGHT = "body_weight"
    CHOLESTEROL = "cholesterol"          # mg/dL — metabolic module
    URIC_ACID = "uric_acid"              # mg/dL — metabolic module
    SPO2_LEVEL = "spo2_level"            # %     — cardio & infection modules
