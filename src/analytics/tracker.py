"""Analytics snapshot tracking and performance benchmarking."""
from typing import List, Dict, Any
from src.database.models import AnalyticsSnapshot
from src.database.repository import AnalyticsRepository


class AnalyticsTracker:
    @staticmethod
    def seed_sample_growth_data() -> None:
        """Seed realistic initial milestone growth data if database has no records."""
        existing = AnalyticsRepository.list_snapshots()
        if existing:
            return

        snapshots = [
            AnalyticsSnapshot(date="2026-08-01", channel_views=4200, watch_time_hours=310.0, impressions=58000, ctr_pct=5.8, avg_view_duration_sec=265.0, avg_pct_viewed=42.0, subscribers_gained=85, estimated_revenue_usd=0.0, estimated_revenue_inr=0.0),
            AnalyticsSnapshot(date="2026-08-15", channel_views=11800, watch_time_hours=890.0, impressions=142000, ctr_pct=6.2, avg_view_duration_sec=280.0, avg_pct_viewed=44.5, subscribers_gained=240, estimated_revenue_usd=0.0, estimated_revenue_inr=0.0),
            AnalyticsSnapshot(date="2026-09-01", channel_views=28500, watch_time_hours=2150.0, impressions=340000, ctr_pct=6.6, avg_view_duration_sec=300.0, avg_pct_viewed=46.0, subscribers_gained=590, estimated_revenue_usd=0.0, estimated_revenue_inr=0.0),
            AnalyticsSnapshot(date="2026-09-15", channel_views=54000, watch_time_hours=4200.0, impressions=620000, ctr_pct=6.9, avg_view_duration_sec=310.0, avg_pct_viewed=47.2, subscribers_gained=1150, estimated_revenue_usd=0.0, estimated_revenue_inr=0.0),
            AnalyticsSnapshot(date="2026-10-01", channel_views=96000, watch_time_hours=7500.0, impressions=1100000, ctr_pct=7.1, avg_view_duration_sec=315.0, avg_pct_viewed=48.0, subscribers_gained=2200, estimated_revenue_usd=1344.0, estimated_revenue_inr=112224.0),
        ]
        for s in snapshots:
            AnalyticsRepository.add_snapshot(s)
