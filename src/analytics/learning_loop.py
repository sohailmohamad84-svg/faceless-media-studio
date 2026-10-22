"""Performance learning loop and topic feedback optimization engine."""
from typing import Dict, Any, List
from src.database.repository import AnalyticsRepository, TopicRepository


class LearningLoop:
    @staticmethod
    def generate_recommendations() -> Dict[str, Any]:
        """Analyze recent retention and CTR metrics to generate actionable content insights."""
        snapshots = AnalyticsRepository.list_snapshots()
        if not snapshots:
            return {
                "has_data": False,
                "message": "Publish your first batch of videos to begin accumulating learning loop insights.",
                "actionable_tips": [
                    "Ensure your first 30 seconds feature a specific dollar or metric hook.",
                    "Use high-contrast thumbnails with ≤ 4 words.",
                    "Maintain audio pacing between 130 and 145 words per minute.",
                ],
            }

        latest = snapshots[-1]
        prior = snapshots[-2] if len(snapshots) > 1 else snapshots[0]

        ctr_trend = "improving" if latest.ctr_pct >= prior.ctr_pct else "declining"
        retention_trend = "improving" if latest.avg_pct_viewed >= prior.avg_pct_viewed else "declining"

        tips = []
        if latest.ctr_pct < 6.0:
            tips.append("CTR is below 6.0%: Test higher contrast background badges on thumbnails and reframe titles with curiosity gaps.")
        else:
            tips.append(f"CTR is strong at {latest.ctr_pct}%: Continue using the current thumbnail title formula.")

        if latest.avg_pct_viewed < 45.0:
            tips.append(f"Retention is {latest.avg_pct_viewed}%: Cut preamble sentences in the first 2 minutes; bring the first chart forward.")
        else:
            tips.append(f"Excellent retention ({latest.avg_pct_viewed}%): Viewers are staying for the second half case study evidence.")

        return {
            "has_data": True,
            "latest_ctr_pct": latest.ctr_pct,
            "latest_retention_pct": latest.avg_pct_viewed,
            "ctr_trend": ctr_trend,
            "retention_trend": retention_trend,
            "actionable_tips": tips,
        }
