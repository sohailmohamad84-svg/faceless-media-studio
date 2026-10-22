"""Topic opportunity scoring engine based on transparent 100-point framework."""
from typing import Dict, Any


DEFAULT_WEIGHTS = {
    "demand": 0.20,         # Audience demand & search interest
    "originality": 0.20,    # Originality & differentiation
    "evergreen": 0.15,      # Evergreen longevity vs timely relevance
    "commercial": 0.15,     # Commercial & advertiser relevance (RPM)
    "competition": 0.10,    # Competitive opportunity / gap in existing coverage
    "source_quality": 0.10, # Availability of verified primary sources (SEC, filings)
    "feasibility": 0.10,    # Feasibility with free-first local toolchain
}


def calculate_topic_score(
    demand: float,
    originality: float,
    evergreen: float,
    commercial: float,
    competition: float,
    source_quality: float,
    feasibility: float,
    weights: Dict[str, float] = None,
) -> Dict[str, Any]:
    """Calculate normalized score out of 100 with documented weights.
    Each input parameter is expected on a scale of 0 to 100 (or 0 to 20/15/10).
    Missing values default safely to neutral baselines (50.0).
    """
    w = weights or DEFAULT_WEIGHTS

    # Normalize inputs to 0-100 scale if given on raw dimension scale
    def norm(val, max_val=100.0):
        if val is None:
            return 50.0
        return max(0.0, min(100.0, (val / max_val) * 100.0 if max_val != 100.0 else val))

    d = norm(demand)
    orig = norm(originality)
    eg = norm(evergreen)
    comm = norm(commercial)
    comp = norm(competition)
    sq = norm(source_quality)
    feas = norm(feasibility)

    weighted_total = (
        d * w["demand"]
        + orig * w["originality"]
        + eg * w["evergreen"]
        + comm * w["commercial"]
        + comp * w["competition"]
        + sq * w["source_quality"]
        + feas * w["feasibility"]
    )

    grade = "A+" if weighted_total >= 90 else "A" if weighted_total >= 80 else "B" if weighted_total >= 70 else "C"

    return {
        "total_score": round(weighted_total, 1),
        "grade": grade,
        "metrics": {
            "demand": round(d, 1),
            "originality": round(orig, 1),
            "evergreen": round(eg, 1),
            "commercial": round(comm, 1),
            "competition": round(comp, 1),
            "source_quality": round(sq, 1),
            "feasibility": round(feas, 1),
        },
        "weights": w,
    }
