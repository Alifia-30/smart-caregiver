import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import AsyncSessionLocal
from src.database.models import (
    User, ElderlyProfile, HealthRecord, HealthThreshold,
    Schedule, AIActivityRecommendation, ViewerInvitation
)
from src.database.enums import (
    MobilityLevel, ElderlyStatus, HealthStatus, HealthParameter,
    ScheduleType, RecurrenceType, ActivityCategory, RecommendationStatus,
    InvitationStatus
)
from src.app.core.security import hash_password

async def clear_db(session: AsyncSession):
    """Clear all data from tables before seeding."""
    await session.execute(delete(ViewerInvitation))
    await session.execute(delete(AIActivityRecommendation))
    await session.execute(delete(Schedule))
    await session.execute(delete(HealthRecord))
    await session.execute(delete(HealthThreshold))
    await session.execute(delete(ElderlyProfile))
    await session.execute(delete(User))
    await session.commit()
    print("Database cleared.")

async def seed_data():
    async with AsyncSessionLocal() as session:
        await clear_db(session)

        # 1. Create Users
        caregiver = User(
            full_name="Andi Caregiver",
            email="caregiver@example.com",
            hashed_password=hash_password("password123"),
            is_email_verified=True,
            is_active=True
        )
        viewer = User(
            full_name="Budi Viewer",
            email="viewer@example.com",
            hashed_password=hash_password("password123"),
            is_email_verified=True,
            is_active=True
        )
        session.add_all([caregiver, viewer])
        await session.flush()

        # 2. Create Elderly Profiles
        budi = ElderlyProfile(
            caregiver_id=caregiver.id,
            full_name="Budi Santoso",
            age=75,
            gender="male",
            medical_history="Hypertension, mild arthritis",
            mobility_level=MobilityLevel.INDEPENDENT,
            status=ElderlyStatus.ACTIVE
        )
        siti = ElderlyProfile(
            caregiver_id=caregiver.id,
            full_name="Siti Aminah",
            age=80,
            gender="female",
            medical_history="Type 2 Diabetes, osteoporosis",
            mobility_level=MobilityLevel.ASSISTED,
            status=ElderlyStatus.ACTIVE
        )
        session.add_all([budi, siti])
        await session.flush()

        # 3. Create Health Thresholds
        thresholds = [
            # Budi's Thresholds
            HealthThreshold(elderly_id=budi.id, parameter=HealthParameter.SYSTOLIC_BP, min_value=90, max_value=140),
            HealthThreshold(elderly_id=budi.id, parameter=HealthParameter.DIASTOLIC_BP, min_value=60, max_value=90),
            HealthThreshold(elderly_id=budi.id, parameter=HealthParameter.HEART_RATE, min_value=60, max_value=100),
            
            # Siti's Thresholds
            HealthThreshold(elderly_id=siti.id, parameter=HealthParameter.BLOOD_SUGAR, min_value=70, max_value=180),
            HealthThreshold(elderly_id=siti.id, parameter=HealthParameter.BODY_TEMPERATURE, min_value=36.0, max_value=37.5),
        ]
        session.add_all(thresholds)

        # 4. Create Health Records (Historical data)
        now = datetime.now(tz=timezone.utc)
        records = []
        for i in range(7):
            recorded_at = now - timedelta(days=i)
            # Budi's records (Stable)
            records.append(HealthRecord(
                elderly_id=budi.id,
                recorded_by=caregiver.id,
                systolic_bp=120 + (i % 5),
                diastolic_bp=80 + (i % 3),
                heart_rate=72 + (i % 4),
                health_status=HealthStatus.NORMAL,
                recorded_at=recorded_at
            ))
            # Siti's records (One alert today)
            status = HealthStatus.NORMAL if i > 0 else HealthStatus.NEEDS_ATTENTION
            sugar = 110 + (i * 5) if i > 0 else 220 # High sugar today
            records.append(HealthRecord(
                elderly_id=siti.id,
                recorded_by=caregiver.id,
                blood_sugar=sugar,
                body_temperature=36.6,
                health_status=status,
                complaints="Feeling a bit dizzy" if i == 0 else None,
                recorded_at=recorded_at
            ))
        session.add_all(records)

        # 5. Create Schedules
        schedules = [
            Schedule(
                elderly_id=budi.id,
                created_by=caregiver.id,
                schedule_type=ScheduleType.MEDICATION,
                title="Obat Darah Tinggi",
                description="Amlodipine 5mg - 1 tablet setelah sarapan",
                scheduled_at=now.replace(hour=8, minute=0),
                recurrence_type=RecurrenceType.DAILY
            ),
            Schedule(
                elderly_id=siti.id,
                created_by=caregiver.id,
                schedule_type=ScheduleType.DAILY_ACTIVITY,
                title="Jalan Santai Sore",
                description="Jalan di taman depan rumah selama 15 menit",
                scheduled_at=now.replace(hour=16, minute=30),
                recurrence_type=RecurrenceType.DAILY
            )
        ]
        session.add_all(schedules)

        # 6. Create AI Recommendations
        rec = AIActivityRecommendation(
            elderly_id=budi.id,
            activity_name="Senam Lansia Ringan",
            category=ActivityCategory.PHYSICAL,
            description="Latihan peregangan sendi untuk mengurangi kaku karena arthritis.",
            duration_minutes=15,
            frequency_suggestion="3x seminggu",
            ai_reasoning="Mengingat riwayat arthritis ringan, aktivitas low-impact sangat disarankan.",
            status=RecommendationStatus.PENDING
        )
        session.add_all([rec])

        # 7. Create Viewer Invitation (Accepted)
        invitation = ViewerInvitation(
            elderly_id=budi.id,
            invited_by=caregiver.id,
            viewer_id=viewer.id,
            email=viewer.email,
            token=str(uuid.uuid4()),
            status=InvitationStatus.ACCEPTED,
            expires_at=now + timedelta(days=7),
            accepted_at=now - timedelta(days=1)
        )
        session.add_all([invitation])

        await session.commit()
        print(f"Successfully seeded data:")
        print(f"- Caregiver: {caregiver.email} (password123)")
        print(f"- Viewer: {viewer.email} (password123)")
        print(f"- Elderly Profiles: Budi Santoso, Siti Aminah")

if __name__ == "__main__":
    asyncio.run(seed_data())
