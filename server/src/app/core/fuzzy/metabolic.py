"""
Fuzzy Logic Module 2: Metabolic Health Analysis

Inputs:
  sugar (blood_sugar) : Blood glucose in mg/dL  [70  – 400]
  chol  (cholesterol) : Cholesterol in mg/dL    [100 – 400]
  uric  (uric_acid)   : Uric acid in mg/dL      [1   – 15]
  w     (body_weight) : Body weight in kg        [30  – 150]

Output:
  metabolic score     : 0 – 100
  status              : Normal | Warning | Critical
"""

from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import Optional

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


# ── Result dataclass ───────────────────────────────────────────────────────────

@dataclass
class MetabolicResult:
    score: float          # fuzzy output 0–100
    status: str           # Normal | Warning | Critical
    sugar_status: str     # Normal | Warning | Critical
    chol_status: str      # Normal | Warning | Critical
    uric_status: str      # Normal | Warning | Critical
    weight_status: str    # Normal | Warning | Critical


# ── Cached system builder ──────────────────────────────────────────────────────

@functools.lru_cache(maxsize=1)
def _build_metabolic_system() -> ctrl.ControlSystem:
    """Build and cache the metabolic fuzzy control system."""
    # Antecedents
    sugar = ctrl.Antecedent(np.arange(70,  401, 1), "sugar")
    chol  = ctrl.Antecedent(np.arange(100, 401, 1), "chol")
    uric  = ctrl.Antecedent(np.arange(1,   16,  1), "uric")
    w     = ctrl.Antecedent(np.arange(30,  151, 1), "w")

    # Consequent
    metabolic = ctrl.Consequent(np.arange(0, 101, 1), "metabolic")

    # ── Membership functions ───────────────────────────────────────────────────
    sugar["normal"]   = fuzz.trimf(sugar.universe, [70,  100, 140])
    sugar["warning"]  = fuzz.trimf(sugar.universe, [130, 170, 220])
    sugar["critical"] = fuzz.trimf(sugar.universe, [200, 300, 400])

    chol["normal"]   = fuzz.trimf(chol.universe, [100, 150, 200])
    chol["warning"]  = fuzz.trimf(chol.universe, [180, 220, 260])
    chol["critical"] = fuzz.trimf(chol.universe, [240, 300, 400])

    uric["normal"]   = fuzz.trimf(uric.universe, [1, 4,  7])
    uric["warning"]  = fuzz.trimf(uric.universe, [6, 8,  10])
    uric["critical"] = fuzz.trimf(uric.universe, [9, 12, 15])

    w["normal"]   = fuzz.trimf(w.universe, [40,  60,  75])
    w["warning"]  = fuzz.trimf(w.universe, [70,  85,  100])
    w["critical"] = fuzz.trimf(w.universe, [95,  120, 150])

    metabolic["normal"]   = fuzz.trimf(metabolic.universe, [0,  20, 40])
    metabolic["warning"]  = fuzz.trimf(metabolic.universe, [30, 50, 70])
    metabolic["critical"] = fuzz.trimf(metabolic.universe, [60, 80, 100])

    # ── Rules ─────────────────────────────────────────────────────────────────
    rule1 = ctrl.Rule(
        sugar["normal"] & chol["normal"] & uric["normal"],
        metabolic["normal"],
    )
    rule2 = ctrl.Rule(
        sugar["warning"] | chol["warning"] | uric["warning"] | w["warning"],
        metabolic["warning"],
    )
    rule3 = ctrl.Rule(
        sugar["critical"] | chol["critical"] | uric["critical"] | w["critical"],
        metabolic["critical"],
    )

    return ctrl.ControlSystem([rule1, rule2, rule3])


# ── Helper status functions ────────────────────────────────────────────────────

def _score_to_status(score: float) -> str:
    if score <= 40:
        return "Normal"
    if score <= 70:
        return "Warning"
    return "Critical"


def _sugar_status(value: float) -> str:
    """Blood sugar thresholds (mg/dL)."""
    if value <= 140:
        return "Normal"
    if value <= 200:
        return "Warning"
    return "Critical"


def _chol_status(value: float) -> str:
    """Cholesterol thresholds (mg/dL)."""
    if value <= 200:
        return "Normal"
    if value <= 240:
        return "Warning"
    return "Critical"


def _uric_status(value: float) -> str:
    """Uric acid thresholds (mg/dL)."""
    if value <= 7:
        return "Normal"
    if value <= 9:
        return "Warning"
    return "Critical"


def _weight_status(value: float) -> str:
    """Body weight thresholds (kg)."""
    if value <= 75:
        return "Normal"
    if value <= 95:
        return "Warning"
    return "Critical"


# ── Public API ─────────────────────────────────────────────────────────────────

# Sensible "normal" defaults used when a parameter is missing so the
# absent parameter does not unfairly push the score toward Warning/Critical.
_DEFAULT_SUGAR  = 100.0   # mg/dL  — mid-normal
_DEFAULT_CHOL   = 150.0   # mg/dL  — mid-normal
_DEFAULT_URIC   = 4.0     # mg/dL  — mid-normal
_DEFAULT_WEIGHT = 60.0    # kg     — mid-normal


def analyze_metabolic(
    blood_sugar: Optional[float] = None,
    cholesterol: Optional[float] = None,
    uric_acid: Optional[float] = None,
    body_weight: Optional[float] = None,
) -> MetabolicResult:
    """Run metabolic fuzzy analysis.

    Any parameter that is None is substituted with a neutral "normal"
    default so it does not influence the output.  The per-parameter
    status fields are set to "N/A" for missing values.

    Args:
        blood_sugar: Blood glucose in mg/dL.
        cholesterol: Total cholesterol in mg/dL.
        uric_acid:   Uric acid in mg/dL.
        body_weight: Body weight in kg.

    Returns:
        MetabolicResult with overall score and per-parameter labels.
    """
    has_sugar  = blood_sugar  is not None
    has_chol   = cholesterol  is not None
    has_uric   = uric_acid    is not None
    has_weight = body_weight  is not None

    sugar_val  = float(np.clip(blood_sugar  if has_sugar  else _DEFAULT_SUGAR,  70,  400))
    chol_val   = float(np.clip(cholesterol  if has_chol   else _DEFAULT_CHOL,   100, 400))
    uric_val   = float(np.clip(uric_acid    if has_uric   else _DEFAULT_URIC,   1,   15))
    weight_val = float(np.clip(body_weight  if has_weight else _DEFAULT_WEIGHT, 30,  150))

    system = _build_metabolic_system()
    sim = ctrl.ControlSystemSimulation(system)
    sim.input["sugar"] = sugar_val
    sim.input["chol"]  = chol_val
    sim.input["uric"]  = uric_val
    sim.input["w"]     = weight_val
    sim.compute()

    score = float(sim.output["metabolic"])
    return MetabolicResult(
        score=round(score, 2),
        status=_score_to_status(score),
        sugar_status=_sugar_status(blood_sugar)  if has_sugar  else "N/A",
        chol_status=_chol_status(cholesterol)    if has_chol   else "N/A",
        uric_status=_uric_status(uric_acid)      if has_uric   else "N/A",
        weight_status=_weight_status(body_weight) if has_weight else "N/A",
    )
