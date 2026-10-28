"""Production Configuration Manager for Faceless Media Studio.
Loads, validates, and provides access to central settings in config/production.yaml.
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

CONFIG_PATH = Path("config/production.yaml")

class ProductionConfig:
    _cached_config: Optional[Dict[str, Any]] = None

    @classmethod
    def _fallback_default_config(cls) -> Dict[str, Any]:
        """Provides default valid production configuration if PyYAML is not yet loaded."""
        return {
            "channel": {
                "name": "Apex op legend",
                "brand_title": "Faceless Media Studio",
                "niche_categories": ["Extreme Engineering", "Megastructures & Megaprojects"],
                "preferred_language": "en-US",
                "target_audience": "United States & Global English-Speaking Documentary Audience",
                "narration_voice": "en-US-ChristopherNeural",
                "brand_colors": {"primary_gold": "#FFE020", "background_dark": "#0B0F19"},
                "subtitle_style": {"font_name": "Arial Black", "font_size": 54, "margin_v": 820},
                "standard_cta": "Subscribe to Faceless Media Studio for daily forensic documentaries.",
                "default_duration_seconds": 65,
                "daily_production_target": 1,
            },
            "video": {
                "output_resolution": {"width": 1080, "height": 1920},
                "aspect_ratio": "9:16",
                "frame_rate": 60.0,
                "video_codec": "libx264",
                "pixel_format": "yuv420p",
                "crf": 17,
                "preset": "medium",
                "video_bitrate_target_kbps": 10000,
                "video_bitrate_min_kbps": 8500,
                "audio_codec": "aac",
                "audio_bitrate_kbps": 192,
                "audio_sample_rate_hz": 48000,
                "audio_channels": 2,
                "audio_loudness_target_lufs": -14.0,
                "audio_true_peak_ceiling_dbtp": -1.20,
                "audio_loudness_range_min_lufs": -17.0,
                "audio_loudness_range_max_lufs": -13.0,
            },
            "workflow": {
                "default_upload_permission": "DENIED",
                "creator_approval_required": True,
                "enforce_file_hash_binding": True,
                "auto_invalidate_on_edit": True,
            },
            "integrations": {
                "google_flow": {"browser_mode": "persistent_profile"},
                "youtube": {"channel_name": "Apex op legend"},
            }
        }

    @classmethod
    def load(cls, force_reload: bool = False) -> Dict[str, Any]:
        """Load and validate the central production configuration YAML."""
        if cls._cached_config is not None and not force_reload:
            return cls._cached_config

        if not CONFIG_PATH.exists() or yaml is None:
            cfg = cls._fallback_default_config()
            cls._cached_config = cfg
            return cfg

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

        cls.validate(cfg)
        cls._cached_config = cfg
        return cfg

    @classmethod
    def save(cls, cfg: Dict[str, Any]) -> None:
        """Save updated configuration to config/production.yaml."""
        cls.validate(cfg)
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        if yaml is not None:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                yaml.dump(cfg, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        cls._cached_config = cfg

    @classmethod
    def validate(cls, cfg: Dict[str, Any]) -> bool:
        """Validate critical production constraints."""
        required_sections = ["channel", "video", "workflow", "integrations"]
        for sec in required_sections:
            if sec not in cfg:
                raise ValueError(f"Missing required configuration section: '{sec}'")

        # Validate video targets
        vid = cfg.get("video", {})
        if vid.get("output_resolution", {}).get("width") != 1080 or vid.get("output_resolution", {}).get("height") != 1920:
            raise ValueError("Output resolution must be 1080x1920 for YouTube Shorts.")

        tp_ceiling = vid.get("audio_true_peak_ceiling_dbtp", -1.0)
        if tp_ceiling > -1.0:
            raise ValueError(f"True peak ceiling ({tp_ceiling} dBTP) cannot exceed YouTube -1.0 dBTP limit.")

        min_bitrate = vid.get("video_bitrate_min_kbps", 0)
        if min_bitrate < 8000:
            raise ValueError(f"Video bitrate minimum ({min_bitrate} kbps) must be at least 8000 kbps for broadcast quality.")

        # Validate workflow safeguards
        wf = cfg.get("workflow", {})
        if wf.get("default_upload_permission") != "DENIED":
            raise ValueError("Security violation: default_upload_permission must be DENIED.")
        if not wf.get("creator_approval_required"):
            raise ValueError("Security violation: creator_approval_required must be True.")

        return True

    @classmethod
    def get(cls, section: str, default: Any = None) -> Any:
        cfg = cls.load()
        return cfg.get(section, default)

    @classmethod
    def get_channel(cls) -> Dict[str, Any]:
        return cls.get("channel", {})

    @classmethod
    def get_video(cls) -> Dict[str, Any]:
        return cls.get("video", {})

    @classmethod
    def get_workflow(cls) -> Dict[str, Any]:
        return cls.get("workflow", {})

    @classmethod
    def get_integrations(cls) -> Dict[str, Any]:
        return cls.get("integrations", {})
