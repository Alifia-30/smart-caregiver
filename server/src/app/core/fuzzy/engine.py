"""
Fuzzy Engine: Orchestrator for all three health analysis modules.

Usage (sync):
    result = run_fuzzy_analysis(
        systolic_bp=145, heart_rate=105, spo2_level=94,
        blood_sugar=180, cholesterol=220, uric_acid=8, body_weight=75,
        body_temperature=38.5,
    )

Usage (async FastAPI context):
    import asyncio
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: run_fuzzy_analysis(...))

Module activation rules:
  - Cardiovascular : runs when ALL of (systolic_bp, heart_rate, spo2_level) are provided
  - Metabolic      : runs when ANY of (blood_sugar, cholesterol, uric_acid, body_weight) is provided
  - Infection      : runs when ALL of (body_temperature, spo2_level) are provided

final_score is the unweighted average of active module scores.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from src.app.core.fuzzy.cardiovascular import CardioResult, analyze_cardiovascular
from src.app.core.fuzzy.infection import InfectionResult, analyze_infection
from src.app.core.fuzzy.metabolic import MetabolicResult, analyze_metabolic


# ── Result dataclass ───────────────────────────────────────────────────────────

@dataclass
class FuzzyAnalysisResult:
    """Aggregated result from all active fuzzy health modules."""

    cardio: Optional[CardioResult] = None
    metabolic: Optional[MetabolicResult] = None
    infection: Optional[InfectionResult] = None
    final_score: float = 0.0
    final_status: str = "Normal"     # Normal | Warning | Critical

    def to_detail_dict(self) -> dict[str, Any]:
        """Flatten all per-parameter status labels into a single dict."""
        detail: dict[str, Any] = {
            "final_score": self.final_score,
            "final_status": self.final_status,
        }

        if self.cardio:
            detail["cardiovascular"] = {
                "score": self.cardio.score,
                "status": self.cardio.status,
                "parameters": {
                    "blood_pressure": self.cardio.bp_status,
                    "heart_rate": self.cardio.hr_status,
                    "spo2": self.cardio.spo2_status,
                },
            }

        if self.metabolic:
            detail["metabolic"] = {
                "score": self.metabolic.score,
                "status": self.metabolic.status,
                "parameters": {
                    "blood_sugar": self.metabolic.sugar_status,
                    "cholesterol": self.metabolic.chol_status,
                    "uric_acid": self.metabolic.uric_status,
                    "body_weight": self.metabolic.weight_status,
                },
            }

        if self.infection:
            detail["infection"] = {
                "score": self.infection.score,
                "status": self.infection.status,
                "parameters": {
                    "body_temperature": self.infection.temp_status,
                    "spo2": self.infection.spo2_status,
                },
            }

        return detail


def _status_from_score(score: float) -> str:
    if score <= 40:
        return "Normal"
    if score <= 70:
        return "Warning"
    return "Critical"


# ── Public API ─────────────────────────────────────────────────────────────────

def run_fuzzy_analysis(
    *,
    systolic_bp: Optional[float] = None,
    heart_rate: Optional[float] = None,
    spo2_level: Optional[float] = None,
    blood_sugar: Optional[float] = None,
    cholesterol: Optional[float] = None,
    uric_acid: Optional[float] = None,
    body_weight: Optional[float] = None,
    body_temperature: Optional[float] = None,
) -> FuzzyAnalysisResult:
    """Orchestrate fuzzy health analysis across all available modules.

    Parameters are keyword-only so callers cannot accidentally pass them
    in the wrong order.

    Args:
        systolic_bp:      Systolic blood pressure (mmHg)  — Cardiovascular
        heart_rate:       Heart rate (bpm)                — Cardiovascular
        spo2_level:       SpO₂ saturation (%)             — Cardiovascular & Infection
        blood_sugar:      Blood glucose (mg/dL)           — Metabolic
        cholesterol:      Total cholesterol (mg/dL)       — Metabolic
        uric_acid:        Uric acid (mg/dL)               — Metabolic
        body_weight:      Body weight (kg)                — Metabolic
        body_temperature: Body temperature (°C)           — Infection

    Returns:
        FuzzyAnalysisResult with per-module results and a final
        aggregated score/status.
    """
    result = FuzzyAnalysisResult()
    scores: list[float] = []

    # ── Module 1: Cardiovascular ───────────────────────────────────────────────
    if all(v is not None for v in [systolic_bp, heart_rate, spo2_level]):
        result.cardio = analyze_cardiovascular(
            systolic_bp=systolic_bp,   # type: ignore[arg-type]
            heart_rate=heart_rate,     # type: ignore[arg-type]
            spo2_level=spo2_level,     # type: ignore[arg-type]
        )
        scores.append(result.cardio.score)

    # ── Module 2: Metabolic ────────────────────────────────────────────────────
    # Runs if at least one metabolic parameter is provided
    if any(v is not None for v in [blood_sugar, cholesterol, uric_acid, body_weight]):
        result.metabolic = analyze_metabolic(
            blood_sugar=blood_sugar,
            cholesterol=cholesterol,
            uric_acid=uric_acid,
            body_weight=body_weight,
        )
        scores.append(result.metabolic.score)

    # ── Module 3: Infection ────────────────────────────────────────────────────
    if all(v is not None for v in [body_temperature, spo2_level]):
        result.infection = analyze_infection(
            body_temperature=body_temperature,  # type: ignore[arg-type]
            spo2_level=spo2_level,              # type: ignore[arg-type]
        )
        scores.append(result.infection.score)

    # ── Aggregate ──────────────────────────────────────────────────────────────
    if scores:
        result.final_score = round(sum(scores) / len(scores), 2)
        result.final_status = _status_from_score(result.final_score)

    return result
