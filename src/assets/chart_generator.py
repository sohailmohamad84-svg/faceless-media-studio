"""Procedural financial chart and data visualization generator (1920x1080)."""
from pathlib import Path
from typing import Dict, Any, List
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np


class ChartGenerator:
    DARK_BG = "#0d1117"
    PANEL_BG = "#161b22"
    TEXT_COLOR = "#f0f6fc"
    ACCENT_GOLD = "#f59e0b"
    ACCENT_CYAN = "#38bdf8"
    ACCENT_RED = "#ef4444"
    ACCENT_GREEN = "#10b981"

    @staticmethod
    def _apply_cinematic_styling(fig, ax, title: str):
        fig.patch.set_facecolor(ChartGenerator.DARK_BG)
        ax.set_facecolor(ChartGenerator.PANEL_BG)
        ax.tick_params(colors=ChartGenerator.TEXT_COLOR, labelsize=14)
        for spine in ax.spines.values():
            spine.set_color("#30363d")
            spine.set_linewidth(1.5)
        ax.grid(color="#30363d", linestyle="--", linewidth=0.8, alpha=0.7)
        ax.set_title(
            title,
            color=ChartGenerator.TEXT_COLOR,
            fontsize=24,
            pad=20,
            fontweight="bold",
        )

    @classmethod
    def generate_costco_markup_chart(cls, output_path: str) -> str:
        """Generate retail markup comparison chart: Walmart vs Kroger vs Supermarkets vs Costco."""
        fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
        categories = ["Specialty Retail", "Conventional Supermarkets", "Kroger", "Walmart", "Costco Wholesale"]
        markups = [45, 30, 28, 24, 14]
        colors = [cls.ACCENT_RED, cls.ACCENT_RED, "#f97316", "#3b82f6", cls.ACCENT_GREEN]

        bars = ax.barh(categories, markups, color=colors, height=0.55, edgecolor="#ffffff", linewidth=1.0)
        cls._apply_cinematic_styling(fig, ax, "Retail Markup Ceiling Comparison (% Above Cost)")
        ax.set_xlabel("Gross Margin / Markup Percentage (%)", color=cls.TEXT_COLOR, fontsize=16, labelpad=10)
        ax.set_xlim(0, 52)

        # Annotations on bars
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + 1.2,
                bar.get_y() + bar.get_height() / 2,
                f"{width}%",
                va="center",
                color=cls.TEXT_COLOR,
                fontsize=16,
                fontweight="bold",
            )

        # Highlight box for Costco
        ax.text(
            16,
            4,
            "Capped by Charter at 14-15%",
            color=cls.ACCENT_GREEN,
            fontsize=15,
            fontweight="bold",
            va="center",
        )

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout(pad=3.0)
        plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)
        return output_path

    @classmethod
    def generate_membership_profit_waterfall(cls, output_path: str) -> str:
        """Generate Costco Operating Profit Breakdown: Merchandise vs Membership Fees."""
        fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
        categories = ["Total Merchandise Sales\n($237 Billion)", "Merchandise Profit\n($2.3 Billion)", "Membership Fee Revenue\n($4.6 Billion)", "Total Operating Income\n($8.1 Billion)"]
        values = [237.0, 2.3, 4.6, 8.1]
        colors = ["#475569", "#64748b", cls.ACCENT_GOLD, cls.ACCENT_CYAN]

        bars = ax.bar(categories, values, color=colors, width=0.5, edgecolor="#ffffff", linewidth=1.2)
        cls._apply_cinematic_styling(fig, ax, "Costco Operating Income Engine (Billions USD)")
        ax.set_ylabel("USD ($ Billions)", color=cls.TEXT_COLOR, fontsize=16, labelpad=10)
        ax.set_yscale("log")  # logarithmic to show massive revenue vs profit clearly

        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height * 1.15,
                f"${height}B",
                ha="center",
                color=cls.TEXT_COLOR,
                fontsize=16,
                fontweight="bold",
            )

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout(pad=3.0)
        plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)
        return output_path

    @classmethod
    def generate_generic_trend_chart(cls, title: str, x_labels: List[str], y_values: List[float], y_label: str, output_path: str) -> str:
        """Generate high-contrast 16:9 line or bar trend chart."""
        fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
        x = np.arange(len(x_labels))
        ax.plot(x, y_values, marker="o", color=cls.ACCENT_CYAN, linewidth=3.5, markersize=10, label="Historical Trajectory")
        ax.fill_between(x, y_values, color=cls.ACCENT_CYAN, alpha=0.15)
        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation=15)
        cls._apply_cinematic_styling(fig, ax, title)
        ax.set_ylabel(y_label, color=cls.TEXT_COLOR, fontsize=16)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout(pad=3.0)
        plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)
        return output_path
