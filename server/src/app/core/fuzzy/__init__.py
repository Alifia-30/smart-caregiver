"""
Fuzzy Logic package for SmartCaregiver health analysis.

Three analysis modules:
  - cardiovascular : Blood Pressure, Heart Rate, SpO₂
  - metabolic      : Blood Sugar, Cholesterol, Uric Acid, Body Weight
  - infection      : Body Temperature, SpO₂

All modules are orchestrated by engine.py → FuzzyAnalysisResult.
"""

from src.app.core.fuzzy.engine import FuzzyAnalysisResult, run_fuzzy_analysis

__all__ = ["FuzzyAnalysisResult", "run_fuzzy_analysis"]
