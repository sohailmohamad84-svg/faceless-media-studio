"""Automated Repair and Learning Loop Module for Faceless Media Studio.
Implements Part 16: Automated diagnosis, bounded remediation (up to max_render_retries),
and historical ledger of quality repairs and learning rules.
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

REPAIR_LOG_PATH = Path("data/quality_repairs_log.json")


class QualityRepairEngine:
    """Diagnoses failure modes and applies calibrated parameter adjustments."""

    @classmethod
    def diagnose_and_suggest_repair(cls, blocking_failures: List[str], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyzes failure list and generates actionable repair prescriptions."""
        repairs = []

        for fail in blocking_failures:
            f_lower = fail.lower()
            if "true peak" in f_lower or "gate-06" in f_lower:
                measured_tp = metrics.get("true_peak_dbtp", -1.0)
                repairs.append({
                    "gate": "GATE-06_AUDIO_COMPLIANCE",
                    "root_cause": f"Lossy AAC compression bounce (+0.35 dB) pushed true peak to {measured_tp} dBTP.",
                    "action": "ADJUST_TRUE_PEAK_TARGET",
                    "prescription": "Reduce TARGET_TRUE_PEAK in FlowMasterEngine from -1.5 to -2.0 dBTP."
                })
            elif "bitrate" in f_lower or "gate-02" in f_lower:
                repairs.append({
                    "gate": "GATE-02_TECHNICAL_COMPLIANCE",
                    "root_cause": "Video bitrate below 9,000 kbps broadcast threshold.",
                    "action": "INCREASE_ENCODING_BITRATE",
                    "prescription": "Lower libx264 CRF from 18 to 16 or enforce -b:v 10M."
                })
            elif "subtitle" in f_lower or "safe zone" in f_lower:
                repairs.append({
                    "gate": "GATE-07_SUBTITLE_READABILITY",
                    "root_cause": "Subtitle vertical position encroaches on YouTube Shorts UI safe zone.",
                    "action": "RECENTER_SUBTITLES",
                    "prescription": "Set MarginV=820 with Arial Black 54pt and radiant gold tags."
                })
            elif "claim" in f_lower or "gate-05" in f_lower:
                repairs.append({
                    "gate": "GATE-05_FACTUAL_ACCURACY",
                    "root_cause": "Unresolved material claim in script.",
                    "action": "SOURCE_OR_REWRITE_CLAIM",
                    "prescription": "Qualify numerical statement with institutional authority source (e.g. NASA, USGS, CTBUH)."
                })
            elif "asset" in f_lower or "gate-08" in f_lower:
                repairs.append({
                    "gate": "GATE-08_COPYRIGHT_AND_ASSET_RIGHTS",
                    "root_cause": "External asset lacks clear commercial reuse license.",
                    "action": "SUBSTITUTE_ASSET",
                    "prescription": "Replace asset with verified Public Domain or CC-BY media from Wikimedia Commons/Pexels."
                })
            elif "watermark" in f_lower or "delogo" in f_lower:
                repairs.append({
                    "gate": "GATE-09_SYNTHETIC_MEDIA_PROVENANCE",
                    "root_cause": "Destructive provenance erasure attempted.",
                    "action": "PRESERVE_PROVENANCE",
                    "prescription": "Halt delogo filters; preserve DeepMind SynthID corner marks."
                })

        return repairs

    @classmethod
    def record_repair_event(
        cls,
        topic_id: str,
        attempt_number: int,
        failure_reasons: List[str],
        repairs_applied: List[Dict[str, Any]],
        previous_score: int,
        new_score: int
    ) -> None:
        """Appends repair diagnosis and learning record to quality log."""
        REPAIR_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        history = []
        if REPAIR_LOG_PATH.exists():
            try:
                with open(REPAIR_LOG_PATH, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []

        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "topic_id": topic_id,
            "attempt_number": attempt_number,
            "failure_reasons": failure_reasons,
            "repairs_applied": repairs_applied,
            "previous_score": previous_score,
            "new_score": new_score,
            "resolved": new_score >= 95
        }
        history.append(event)

        with open(REPAIR_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
