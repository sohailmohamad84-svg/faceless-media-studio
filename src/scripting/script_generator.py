"""Documentary Script Generator & Narrative Planner for Faceless Media Studio.
Implements flexible, non-rigid scene architecture (5-10 scenes), natural spoken cadence,
word-count-based timing estimation, and radiant-gold subtitle phrase structuring.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import math
import re


@dataclass
class ScenePlan:
    scene_num: int
    title: str
    narrative_function: str # e.g. "HOOK", "STAKES", "CHALLENGE", "MECHANISM", "ESCALATION", "BREAKTHROUGH", "CONSEQUENCE", "PAYOFF_CTA"
    narration_text: str
    subtitle_phrases: List[str]
    estimated_duration_sec: float
    visual_type: str # "AUTHENTIC_FOOTAGE", "SCHEMATIC_CUTAWAY", "AI_RECONSTRUCTION", "SATELLITE_DEM"
    visual_description: str
    foley: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def word_count(self) -> int:
        return len(self.narration_text.split())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DocumentaryScript:
    topic_id: str
    title: str
    hook: str
    scenes: List[ScenePlan]
    estimated_total_duration: float
    total_word_count: int
    voice_id: str = "en-US-ChristopherNeural"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ScriptGenerator:
    """Generates natural, highly engaging documentary scripts with timing estimates."""

    # Words per minute for en-US-ChristopherNeural at natural pacing (+10-14% boost)
    WORDS_PER_MINUTE = 160.0

    @classmethod
    def estimate_speech_duration(cls, text: str, speaking_rate: float = 1.0) -> float:
        """Calculates expected vocal duration in seconds."""
        clean_text = re.sub(r"[^\w\s]", "", text)
        words = len(clean_text.split())
        base_sec = (words / cls.WORDS_PER_MINUTE) * 60.0
        # Add slight pause buffer for commas, periods, and technical terms
        punctuation_pause = text.count(".") * 0.35 + text.count(",") * 0.18 + text.count(":") * 0.25
        return round((base_sec / speaking_rate) + punctuation_pause, 2)

    @classmethod
    def build_script(
        cls,
        topic_id: str,
        title: str,
        hook: str,
        scenes_data: List[Dict[str, Any]],
        voice_id: str = "en-US-ChristopherNeural",
        speaking_rate: float = 1.12
    ) -> DocumentaryScript:
        """Compiles validated scenes into a DocumentaryScript object with timing estimates."""
        scene_plans = []
        total_words = 0
        total_duration = 0.0

        for sc in scenes_data:
            num = sc.get("scene_num", len(scene_plans) + 1)
            text = sc.get("narration_text", "").strip()
            phrases = sc.get("subtitle_phrases", [])
            if not phrases and text:
                # Default phrase split by punctuation
                phrases = [p.strip() for p in re.split(r"(?<=[.,:])\s+", text) if p.strip()]

            dur = cls.estimate_speech_duration(text, speaking_rate=speaking_rate)
            plan = ScenePlan(
                scene_num=num,
                title=sc.get("title", f"Scene {num}"),
                narrative_function=sc.get("narrative_function", "NARRATIVE_STEP"),
                narration_text=text,
                subtitle_phrases=phrases,
                estimated_duration_sec=dur,
                visual_type=sc.get("visual_type", "AI_RECONSTRUCTION"),
                visual_description=sc.get("prompt", sc.get("visual_description", "")),
                foley=sc.get("foley", [])
            )
            scene_plans.append(plan)
            total_words += plan.word_count
            total_duration += dur

        return DocumentaryScript(
            topic_id=topic_id,
            title=title,
            hook=hook,
            scenes=scene_plans,
            estimated_total_duration=round(total_duration, 1),
            total_word_count=total_words,
            voice_id=voice_id
        )
