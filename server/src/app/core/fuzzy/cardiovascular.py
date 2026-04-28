"""
Fuzzy Logic Module 1: Cardiovascular Health Analysis

Inputs:
  bp   (systolic_bp) : Blood pressure in mmHg   [80 – 200]
  hr   (heart_rate)  : Heart rate in bpm         [40 – 150]
  spo2 (spo2_level)  : Oxygen saturation in %    [70 – 100]

Output:
  cardio score       : 0 – 100
  status             : Normal | Warning | Critical

The fuzzy ControlSystem is built once and cached at module level
to avoid the expensive membership-function setup on every request.
"""

import functools
from dataclasses import dataclass

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


# ── Result dataclass ───────────────────────────────────────────────────────────

@dataclass
class CardioResult:
    score: float         # fuzzy output 0–100
    status: str          # Normal | Warning | Critical
    bp_status: str       # Normal | Warning | Critical
    hr_status: str       # Normal | Warning | Critical
    spo2_status: str     # Normal | Warning | Critical


# ── Cached system builder ──────────────────────────────────────────────────────

@functools.lru_cache(maxsize=1)
def _build_cardio_system() -> ctrl.ControlSystem:
    """Build and cache the cardiovascular fuzzy control system.

    This is called once; subsequent calls return the cached object.
    Uses trimf (triangular) membership functions, identical to the
    original notebook implementation.
    """
    # Antecedents
    bp = ctrl.Antecedent(np.arange(80, 201, 1), "bp")
    hr = ctrl.Antecedent(np.arange(40, 151, 1), "hr")
    spo2 = ctrl.Antecedent(np.arange(70, 101, 1), "spo2")

    # Consequent
    cardio = ctrl.Consequent(np.arange(0, 101, 1), "cardio")

    # ── Membership functions ───────────────────────────────────────────────────
    bp["normal"]   = fuzz.trimf(bp.universe, [80,  100, 120])
    bp["warning"]  = fuzz.trimf(bp.universe, [110, 130, 150])
    bp["critical"] = fuzz.trimf(bp.universe, [140, 170, 200])

    hr["normal"]   = fuzz.trimf(hr.universe, [60,  80,  100])
    hr["warning"]  = fuzz.trimf(hr.universe, [90,  105, 120])
    hr["critical"] = fuzz.trimf(hr.universe, [110, 130, 150])

    spo2["normal"]   = fuzz.trimf(spo2.universe, [95, 98, 100])
    spo2["warning"]  = fuzz.trimf(spo2.universe, [90, 93,  96])
    spo2["critical"] = fuzz.trimf(spo2.universe, [70, 85,  92])

    cardio["normal"]   = fuzz.trimf(cardio.universe, [0,  20, 40])
    cardio["warning"]  = fuzz.trimf(cardio.universe, [30, 50, 70])
    cardio["critical"] = fuzz.trimf(cardio.universe, [60, 80, 100])

    # ── Rules ─────────────────────────────────────────────────────────────────
    rule1 = ctrl.Rule(bp["normal"]   & hr["normal"]   & spo2["normal"],   cardio["normal"])
    rule2 = ctrl.Rule(bp["warning"]  | hr["warning"]  | spo2["warning"],  cardio["warning"])
    rule3 = ctrl.Rule(bp["critical"] | hr["critical"] | spo2["critical"], cardio["critical"])

    return ctrl.ControlSystem([rule1, rule2, rule3])


# ── Helper status functions ────────────────────────────────────────────────────

def _score_to_status(score: float) -> str:
    if score <= 40:
        return "Normal"
    if score <= 70:
        return "Warning"
    return "Critical"


def _bp_status(value: float) -> str:
    """Systolic BP thresholds (mmHg)."""
    if value <= 120:
        return "Normal"
    if value <= 140:
        return "Warning"
    return "Critical"


def _hr_status(value: float) -> str:
    """Heart rate thresholds (bpm)."""
    if value <= 100:
        return "Normal"
    if value <= 120:
        return "Warning"
    return "Critical"


def _spo2_status(value: float) -> str:
    """SpO₂ is inverse — lower values are more dangerous."""
    if value >= 95:
        return "Normal"
    if value >= 90:
        return "Warning"
    return "Critical"


# ── Public API ─────────────────────────────────────────────────────────────────

def analyze_cardiovascular(
    systolic_bp: float,
    heart_rate: float,
    spo2_level: float,
) -> CardioResult:
    """Run cardiovascular fuzzy analysis.

    Values outside the universe range are clipped (not rejected) so the
    system always produces a meaningful output even for extreme readings.

    Args:
        systolic_bp: Systolic blood pressure in mmHg.
        heart_rate:  Heart rate in bpm.
        spo2_level:  Oxygen saturation percentage.

    Returns:
        CardioResult with overall score, overall status, and
        per-parameter status labels.
    """
    bp_val   = float(np.clip(systolic_bp, 80,  200))
    hr_val   = float(np.clip(heart_rate,  40,  150))
    spo2_val = float(np.clip(spo2_level,  70,  100))

    system = _build_cardio_system()
    sim = ctrl.ControlSystemSimulation(system)
    sim.input["bp"]   = bp_val
    sim.input["hr"]   = hr_val
    sim.input["spo2"] = spo2_val
    sim.compute()

    score = float(sim.output["cardio"])
    return CardioResult(
        score=round(score, 2),
        status=_score_to_status(score),
        bp_status=_bp_status(systolic_bp),
        hr_status=_hr_status(heart_rate),
        spo2_status=_spo2_status(spo2_level),
    )
