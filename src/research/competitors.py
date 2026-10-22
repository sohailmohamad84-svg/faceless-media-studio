"""Competitor intelligence and gap analysis tracker for Faceless Media Studio."""
from typing import List, Dict, Any


BENCHMARK_COMPETITORS = [
    {
        "channel_name": "Company Man",
        "subscribers": "1.82M",
        "total_views": "322M+",
        "video_count": 510,
        "avg_views_per_video": "630K",
        "upload_frequency": "1 video every 2 weeks",
        "content_style": "Nostalgic retail and corporate rise/fall overviews",
        "strengths": "Consistent voice, clean timeline graphics, accessible storytelling",
        "weaknesses": "Lighter on deep balance sheet/unit economics analysis, older visual aesthetic",
        "our_differentiation": "Deeper forensic unit economics breakdowns and modern kinetic infographic styling",
    },
    {
        "channel_name": "ModernMBA",
        "subscribers": "830K",
        "total_views": "63M+",
        "video_count": 62,
        "avg_views_per_video": "600K+",
        "upload_frequency": "1 video per month",
        "content_style": "High-level strategic analysis of modern corporate business models",
        "strengths": "Deep financial literacy, executive-level insights, high retention",
        "weaknesses": "Infrequent uploads (months apart), dense academic tone can deter general viewers",
        "our_differentiation": "More accessible narrative hooks paired with predictable bi-weekly cadence",
    },
    {
        "channel_name": "MagnatesMedia",
        "subscribers": "1.92M",
        "total_views": "194M+",
        "video_count": 140,
        "avg_views_per_video": "850K+",
        "upload_frequency": "1 video every 3 weeks",
        "content_style": "Cinematic 3D animation, dramatic corporate true-crime framing",
        "strengths": "Ultra-high production value, sensational storytelling hooks",
        "weaknesses": "Exorbitant 3D production budgets, occasionally borders on sensationalism over data",
        "our_differentiation": "Data-backed, verified SEC filing clarity with zero sensationalized fluff",
    },
    {
        "channel_name": "Slidebean",
        "subscribers": "460K",
        "total_views": "48M+",
        "video_count": 320,
        "avg_views_per_video": "150K",
        "upload_frequency": "Weekly",
        "content_style": "Startup pitch decks, founder failure autopsies",
        "strengths": "Founder perspective, real pitch deck breakdowns",
        "weaknesses": "Often focused narrowly on venture startups rather than global consumer icons",
        "our_differentiation": "Broader consumer brand appeal with universal household names",
    },
]


def get_competitor_insights() -> List[Dict[str, Any]]:
    """Return benchmark competitor analysis."""
    return BENCHMARK_COMPETITORS
