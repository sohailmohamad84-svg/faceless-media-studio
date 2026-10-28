"""Production Configuration Manager for Faceless Media Studio.
Loads, validates, and provides access to central settings in config/production.yaml.
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

CONFIG_PATH = Path("config/production.yaml")

class ProductionConfig:
    _cached_config: Optional[Dict[str, Any]] = None

    @classmethod
    def load(cls, force_reload: bool = False) -> Dict[str, Any]:
        """Load and validate the central production configuration YAML."""
        if cls._cached_config is not None and not force_reload:
            return cls._cached_config

        if not CONFIG_PATH.exists():
            raise FileNotFoundError(f"Configuration file not found: {CONFIG_PATH.resolve()}")

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
