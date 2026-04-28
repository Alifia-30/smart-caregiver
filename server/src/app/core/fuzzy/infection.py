"""
Fuzzy Logic Module 3: Infection / Respiratory Health Analysis

Inputs:
  temp (body_temperature) : Body temperature in °C  [34 – 42]
  spo2 (spo2_level)       : Oxygen saturation in %  [70 – 100]

Output:
  infection score         : 0 – 100
  status                  : Normal | Warning | Critical

Note: spo2_level is shared with the Cardiovascular module.
Both modules receive the same value from the health record.
"""

import functools
from dataclasses import dataclass

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


# ── Result dataclass ───────────────────────────────────────────────────────────

@dataclass
class InfectionResult:
    score: float          # fuzzy output 0–100
    status: str           # Normal | Warning | Critical
    temp_status: str      # Normal | Warning | Critical
    spo2_status: str      # Normal | Warning | Critical


# ── Cached system builder ──────────────────────────────────────────────────────

@functools.lru_cache(maxsize=1)
def _build_infection_system() -> ctrl.ControlSystem:
    """Build and cache the infection/respiratory fuzzy control system."""
    # Antecedents
    temp = ctrl.Antecedent(np.arange(34, 42.1, 0.1), "temp")   # step 0.1 for decimal precision
    spo2 = ctrl.Antecedent(np.arange(70, 101,  1),   "spo2")

    # Consequent
    infection = ctrl.Consequent(np.arange(0, 101, 1), "infection")

    # ── Membership functions ───────────────────────────────────────────────────
    temp["normal"]   = fuzz.trimf(temp.universe, [34,   36.5, 37.5])
    temp["warning"]  = fuzz.trimf(temp.universe, [37,   38,   39])
    temp["critical"] = fuzz.trimf(temp.universe, [38.5, 40,   42])

    spo2["normal"]   = fuzz.trimf(spo2.universe, [95, 98, 100])
    spo2["warning"]  = fuzz.trimf(spo2.universe, [90, 93,  96])
    spo2["critical"] = fuzz.trimf(spo2.universe, [70, 85,  92])

    infection["normal"]   = fuzz.trimf(infection.universe, [0,  20, 40])
    infection["warning"]  = fuzz.trimf(infection.universe, [30, 50, 70])
    infection["critical"] = fuzz.trimf(infection.universe, [60, 80, 100])

    # ── Rules ─────────────────────────────────────────────────────────────────
    rule1 = ctrl.Rule(temp["normal"]   & spo2["normal"],   infection["normal"])
    rule2 = ctrl.Rule(temp["warning"]  | spo2["warning"],  infection["warning"])
    rule3 = ctrl.Rule(temp["critical"] | spo2["critical"], infection["critical"])

    return ctrl.ControlSystem([rule1, rule2, rule3])


# ── Helper status functions ────────────────────────────────────────────────────

def _score_to_status(score: float) -> str:
    if score <= 40:
        return "Normal"
    if score <= 70:
        return "Warning"
    return "Critical"


def _temp_status(value: float) -> str:
    """Body temperature thresholds (°C)."""
    if value <= 37.5:
        return "Normal"
    if value <= 38.5:
        return "Warning"
    return "Critical"


def _spo2_status(value: float) -> str:
    """SpO₂ is inverse — lower is more dangerous."""
    if value >= 95:
        return "Normal"
    if value >= 90:
        return "Warning"
    return "Critical"


# ── Public API ─────────────────────────────────────────────────────────────────

def analyze_infection(
    body_temperature: float,
    spo2_level: float,
) -> InfectionResult:
    """Run infection/respiratory fuzzy analysis.

    Args:
        body_temperature: Body temperature in °C.
        spo2_level:       Oxygen saturation percentage.

    Returns:
        InfectionResult with overall score and per-parameter labels.
    """
    temp_val = float(np.clip(body_temperature, 34.0, 42.0))
    spo2_val = float(np.clip(spo2_level,       70.0, 100.0))

    system = _build_infection_system()
    sim = ctrl.ControlSystemSimulation(system)
    sim.input["temp"] = temp_val
    sim.input["spo2"] = spo2_val
    sim.compute()

    score = float(sim.output["infection"])
    return InfectionResult(
        score=round(score, 2),
        status=_score_to_status(score),
        temp_status=_temp_status(body_temperature),
        spo2_status=_spo2_status(spo2_level),
    )
