"""Budget protection circuit and cost control manager for Faceless Media Studio."""
from config.settings import DEFAULT_BUDGET_INR, MONTHLY_BUDGET_CEILING_INR
from src.database.repository import ChannelRepository, CostRepository


class BudgetExceededError(Exception):
    """Raised when an operation would exceed the monthly spending ceiling."""
    pass


class CostManager:
    @staticmethod
    def get_spending_status() -> dict:
        channel = ChannelRepository.get_channel()
        ceiling = channel.monthly_budget_ceiling or MONTHLY_BUDGET_CEILING_INR
        current_spend = CostRepository.get_monthly_spend()
        remaining = max(0.0, ceiling - current_spend)
        return {
            "current_spend_inr": current_spend,
            "ceiling_inr": ceiling,
            "remaining_budget_inr": remaining,
            "is_spend_allowed": current_spend < ceiling,
        }

    @staticmethod
    def check_and_record_cost(service_name: str, operation: str, estimated_cost_inr: float, notes: str = "") -> bool:
        """Check if an estimated cost fits within the monthly budget ceiling.
        If cost is 0.0, it is recorded and approved immediately.
        If cost > 0.0, verifies against ceiling and records entry.
        """
        status = CostManager.get_spending_status()
        if estimated_cost_inr > 0.0:
            if status["current_spend_inr"] + estimated_cost_inr > status["ceiling_inr"]:
                raise BudgetExceededError(
                    f"Cost {estimated_cost_inr} INR would exceed monthly ceiling of {status['ceiling_inr']} INR. "
                    f"Current spend: {status['current_spend_inr']} INR."
                )

        CostRepository.record_cost(
            service_name=service_name,
            operation=operation,
            cost_inr=estimated_cost_inr,
            notes=notes,
        )
        return True
