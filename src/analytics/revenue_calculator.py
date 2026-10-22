"""Revenue and financial forecasting calculator with editable assumptions."""
from typing import Dict, Any


USD_TO_INR_RATE = 83.50  # Baseline exchange rate


def calculate_revenue_projections(
    monthly_views: int,
    assumed_rpm_usd: float,
    affiliate_conversion_rate: float = 0.0005,
    avg_affiliate_payout_usd: float = 40.0,
    monthly_sponsorship_usd: float = 0.0,
    monthly_software_costs_inr: float = 0.0,
) -> Dict[str, Any]:
    """Calculate monthly gross revenue, expenses, and net profit across scenarios.
    All calculations are transparent modeling scenarios, not speculative promises.
    """
    adsense_usd = (monthly_views / 1000.0) * assumed_rpm_usd
    affiliate_conversions = monthly_views * affiliate_conversion_rate
    affiliate_usd = affiliate_conversions * avg_affiliate_payout_usd
    gross_usd = adsense_usd + affiliate_usd + monthly_sponsorship_usd

    gross_inr = gross_usd * USD_TO_INR_RATE
    net_inr = max(0.0, gross_inr - monthly_software_costs_inr)

    # Calculate views needed to reach milestones (assuming same proportions)
    # Target 1: ₹1,00,000 INR
    target_1_usd = 100000.0 / USD_TO_INR_RATE
    # Target 2: ₹5,00,000 INR
    target_2_usd = 500000.0 / USD_TO_INR_RATE

    effective_rpm_usd = (gross_usd / monthly_views) * 1000.0 if monthly_views > 0 else assumed_rpm_usd
    views_for_1_lakh = int((target_1_usd / effective_rpm_usd) * 1000.0) if effective_rpm_usd > 0 else 0
    views_for_5_lakh = int((target_2_usd / effective_rpm_usd) * 1000.0) if effective_rpm_usd > 0 else 0

    return {
        "monthly_views": monthly_views,
        "assumed_rpm_usd": assumed_rpm_usd,
        "adsense_usd": round(adsense_usd, 2),
        "affiliate_usd": round(affiliate_usd, 2),
        "sponsorship_usd": round(monthly_sponsorship_usd, 2),
        "gross_usd": round(gross_usd, 2),
        "gross_inr": round(gross_inr, 2),
        "costs_inr": round(monthly_software_costs_inr, 2),
        "net_profit_inr": round(net_inr, 2),
        "milestones": {
            "views_needed_for_1_lakh_inr": views_for_1_lakh,
            "views_needed_for_5_lakh_inr": views_for_5_lakh,
        },
    }
