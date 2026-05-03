"""
Recommendation Service — business logic for AI activity recommendations.
REQ-016: AI reads onboarding profile → generates activity recommendations
REQ-017: Caregiver views recommendations per elderly
REQ-018: Approve → auto-create schedule entry
"""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from openai import AsyncOpenAI
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.enums import (
    ActivityCategory,
    RecommendationStatus,
    ScheduleType,
)
from src.database.models.elderly import ElderlyProfile
from src.database.models.recommendation import AIActivityRecommendation

from src.app.services import schedule_service


GROQ_MODEL = "qwen/qwen3-32b"
PROMPT_VERSION = "v1"


def _parse_llm_response(text: str) -> dict:
    """Parse LLM response into structured recommendation data."""
    activity_name = ""
    category = ActivityCategory.PHYSICAL
    description = ""
    duration_minutes = 30
    frequency_suggestion = "3x per minggu"
    ai_reasoning = text

    lines = text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.lower().startswith("activity:") or line.lower().startswith("activity name:"):
            activity_name = line.split(":", 1)[1].strip()
        elif line.lower().startswith("category:"):
            cat_str = line.split(":", 1)[1].strip().lower()
            for cat in ActivityCategory:
                if cat.value == cat_str:
                    category = cat
                    break
        elif line.lower().startswith("description:"):
            description = line.split(":", 1)[1].strip()
        elif line.lower().startswith("duration:"):
            dur_str = line.split(":", 1)[1].strip().lower().replace("menit", "").replace("minutes", "").strip()
            try:
                duration_minutes = int(dur_str)
            except ValueError:
                pass
        elif line.lower().startswith("frequency:"):
            frequency_suggestion = line.split(":", 1)[1].strip()
        elif line.lower().startswith("reasoning:"):
            ai_reasoning = line.split(":", 1)[1].strip()

    if not activity_name and text.strip():
        activity_name = text.strip().split("\n")[0][:255]

    return {
        "activity_name": activity_name[:255] if activity_name else "Aktivitas Baru",
        "category": category.value,
        "description": description[:1000] if description else None,
        "duration_minutes": duration_minutes if 1 <= duration_minutes <= 1440 else 30,
        "frequency_suggestion": frequency_suggestion[:100] if frequency_suggestion else "3x per minggu",
        "ai_reasoning": ai_reasoning[:2000] if ai_reasoning else None,
    }


async def generate_recommendation(
    db: AsyncSession,
    elderly_id: uuid.UUID,
    additional_context: Optional[str] = None,
) -> AIActivityRecommendation:
    """Generate AI activity recommendation using GROQ."""
    stmt = select(ElderlyProfile).where(ElderlyProfile.id == elderly_id)
    result = await db.execute(stmt)
    elderly = result.scalar_one_or_none()

    if not elderly:
        raise ValueError(f"Elderly profile {elderly_id} not found")

    prompt = _build_prompt(elderly, additional_context)
    parsed = await _call_groq(prompt)

    recommendation = AIActivityRecommendation(
        elderly_id=elderly_id,
        activity_name=parsed["activity_name"],
        category=parsed["category"],
        description=parsed["description"],
        duration_minutes=parsed["duration_minutes"],
        frequency_suggestion=parsed["frequency_suggestion"],
        ai_reasoning=parsed["ai_reasoning"],
        ai_model_version=GROQ_MODEL,
        ai_prompt_version=PROMPT_VERSION,
        status=RecommendationStatus.PENDING,
    )

    db.add(recommendation)
    await db.flush()
    await db.refresh(recommendation)
    return recommendation


def _build_prompt(
    elderly: ElderlyProfile,
    additional_context: Optional[str] = None,
) -> str:
    """Build prompt for Groq LLM."""
    mobility_val = elderly.mobility_level.value if hasattr(elderly.mobility_level, 'value') else elderly.mobility_level
    mobility_display = {
        "independent": "mandiri - dapat bergerak tanpa bantuan",
        "assisted": "membutuhkan bantuan terbatas",
        "wheelchair": "menggunakan kursi roda",
        "bedridden": "terbatas di tempat tidur",
    }.get(mobility_val, mobility_val)

    hobbies = elderly.hobbies_interests or "tidak ada"
    medical = elderly.medical_history or "tidak ada"
    physical = elderly.physical_condition or "tidak ada"

    prompt = f"""Anda adalah asisten perawatan lansia yang menyarankan aktivitas yang aman dan sesuai.

Profil lansia:
- Nama: {elderly.full_name}
- Usia: {elderly.age} tahun
- Mobilitas: {mobility_display}
- Hoby/Minat: {hobbies}
- Riwayat medis: {medical}
- Kondisi fisik: {physical}
"""
    if additional_context:
        prompt += f"\nKonteks tambahan: {additional_context}"

    prompt += f"""

Berdasarkan profil di atas, berikan 1 rekomendasi aktivitas yang sesuai_FORMAT JSON:
{{
  "activity": "nama aktivitas",
  "category": "physical/cognitive/social/creative/relaxation/nature/music",
  "description": "deskripsi singkat aktivitas",
  "duration_minutes": 30,
  "frequency": "contoh: 3x per minggu",
  "reasoning": "alasan mengapa aktivitas ini tepat untuk lansia ini"
}}

PENTING:
1. Aktivitas harus aman sesuai tingkat mobilitas
2. Perhatikan kontraindikasi dari riwayat medis
3. Pertimbangkan hoby/minat yang sudah ada
4. Gunakan format JSON saja, tanpa teks lain
"""

    return prompt


async def _call_groq(prompt: str) -> dict:
    """Call Groq LLM API and return parsed recommendation dict."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY environment variable not set")

    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    try:
        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Anda adalah asisten perawatan lansia. Selalu respuesta dalam format JSON yang diminta.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )

        content = response.choices[0].message.content

        # Clean content: remove "<think>" and "</think>" tokens
        cleaned = re.sub(r"<think>[\s\S]*?</think>", "", content).strip()

        # Extract JSON from content
        json_match = re.search(r"\{[\s\S]*\}", cleaned)
        if json_match:
            parsed = json.loads(json_match.group())

            # Check if ai_reasoning contains nested JSON (LLM put JSON inside a string field)
            raw_reasoning = parsed.get("reasoning", "")
            if raw_reasoning and isinstance(raw_reasoning, str):
                try:
                    inner = json.loads(raw_reasoning)
                    parsed.update(inner)
                except (json.JSONDecodeError, TypeError):
                    pass

            activity = parsed.get("activity") or parsed.get("activity_name") or "Aktivitas Baru"
            category = parsed.get("category", "physical")
            description = parsed.get("description")
            duration = parsed.get("duration_minutes", 30)
            frequency = parsed.get("frequency") or parsed.get("frequency_suggestion", "3x per minggu")
            reasoning = parsed.get("reasoning", "") or ""

            return {
                "activity_name": activity,
                "category": category,
                "description": description,
                "duration_minutes": duration,
                "frequency_suggestion": frequency,
                "ai_reasoning": reasoning,
            }

        # Fallback: return cleaned content as reasoning
        return {
            "activity_name": "Aktivitas Baru",
            "category": "physical",
            "description": None,
            "duration_minutes": 30,
            "frequency_suggestion": "3x per minggu",
            "ai_reasoning": cleaned[:2000],
        }

    except Exception as e:
        raise RuntimeError(f"Groq API call failed: {str(e)}")


async def get_recommendation(
    db: AsyncSession,
    recommendation_id: uuid.UUID,
) -> Optional[AIActivityRecommendation]:
    """Get a recommendation by ID."""
    stmt = select(AIActivityRecommendation).where(
        AIActivityRecommendation.id == recommendation_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_recommendations(
    db: AsyncSession,
    elderly_id: uuid.UUID,
    status: Optional[RecommendationStatus] = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[int, List[AIActivityRecommendation]]:
    """List recommendations for an elderly profile."""
    conditions = [AIActivityRecommendation.elderly_id == elderly_id]

    if status:
        conditions.append(AIActivityRecommendation.status == status)

    stmt = (
        select(AIActivityRecommendation)
        .where(and_(*conditions))
        .order_by(AIActivityRecommendation.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    count_stmt = (
        select(func.count())
        .select_from(AIActivityRecommendation)
        .where(and_(*conditions))
    )

    result = await db.execute(stmt)
    count_result = await db.execute(count_stmt)

    recommendations = result.scalars().all()
    total = count_result.scalar() or 0

    return total, list(recommendations)


async def approve_recommendation(
    db: AsyncSession,
    recommendation_id: uuid.UUID,
    approver_id: uuid.UUID,
    scheduled_at: Optional[datetime] = None,
    duration_minutes: Optional[int] = None,
    reminder_minutes: Optional[List[int]] = None,
) -> tuple[AIActivityRecommendation, Optional[uuid.UUID]]:
    """
    Approve a recommendation and optionally create a schedule.
    REQ-018: Approve → auto-create schedule entry
    Returns (recommendation, schedule_id)
    """
    recommendation = await get_recommendation(db, recommendation_id)

    if not recommendation:
        raise ValueError(f"Recommendation {recommendation_id} not found")

    if recommendation.status != RecommendationStatus.PENDING:
        raise ValueError(f"Cannot approve recommendation with status {recommendation.status}")

    recommendation.status = RecommendationStatus.APPROVED
    recommendation.approved_by = approver_id
    recommendation.approved_at = datetime.now(timezone.utc)

    schedule_id = None
    if scheduled_at:
        schedule = await schedule_service.create_schedule(
            db=db,
            elderly_id=recommendation.elderly_id,
            creator_id=approver_id,
            schedule_type=ScheduleType.DAILY_ACTIVITY.value,
            title=recommendation.activity_name,
            description=recommendation.description,
            scheduled_at=scheduled_at,
            duration_minutes=duration_minutes or recommendation.duration_minutes,
            source="ai_approved",
            ai_recommendation_id=recommendation_id,
            reminder_minutes=reminder_minutes,
        )
        schedule_id = schedule.id

    await db.flush()
    await db.refresh(recommendation)
    return recommendation, schedule_id


async def reject_recommendation(
    db: AsyncSession,
    recommendation_id: uuid.UUID,
    approver_id: uuid.UUID,
    reason: Optional[str] = None,
) -> AIActivityRecommendation:
    """Reject a recommendation."""
    recommendation = await get_recommendation(db, recommendation_id)

    if not recommendation:
        raise ValueError(f"Recommendation {recommendation_id} not found")

    if recommendation.status != RecommendationStatus.PENDING:
        raise ValueError(f"Cannot reject recommendation with status {recommendation.status}")

    recommendation.status = RecommendationStatus.REJECTED
    recommendation.approved_by = approver_id
    recommendation.approved_at = datetime.now(timezone.utc)
    recommendation.rejection_reason = reason[:500] if reason else None

    await db.flush()
    await db.refresh(recommendation)
    return recommendation