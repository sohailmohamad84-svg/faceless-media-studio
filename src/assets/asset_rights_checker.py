"""Asset Rights Checker & Licensing Verification Module for Faceless Media Studio.
Enforces Part 7: Real footage first, authentic provenance, Creative Commons compliance,
and strict copyright gate blocking for unverified or restricted assets.
"""
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Dict, Any, Optional
import json
from pathlib import Path


class RightsStatus(str, Enum):
    RIGHTS_VERIFIED = "RIGHTS_VERIFIED"
    ATTRIBUTION_REQUIRED = "ATTRIBUTION_REQUIRED"
    RESTRICTED = "RESTRICTED"
    UNKNOWN = "UNKNOWN"
    REJECTED = "REJECTED"


@dataclass
class AssetManifestEntry:
    asset_id: str
    original_title: str
    original_url: str
    creator_or_rights_holder: str
    source_platform: str
    download_url: str
    license_name: str
    license_url: str
    commercial_use_permitted: bool
    attribution_required: bool
    modification_permitted: bool
    restrictions_or_exclusions: str
    download_date: str
    local_file_path: str
    intended_scene: str
    verification_status: str # from RightsStatus
    attribution_credit_text: str = ""
    is_ai_reconstruction: bool = False
    ai_provenance_signals_intact: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AssetRightsChecker:
    """Evaluates the legal reusability of every video, photo, audio, and font asset."""

    @classmethod
    def evaluate_asset(cls, asset: AssetManifestEntry) -> RightsStatus:
        """Determines legal status based on licence and platform permissions."""
        lic = asset.license_name.upper()

        # Public Domain / CC0 / US Government work
        if any(term in lic for term in ["CC0", "PUBLIC DOMAIN", "US GOVERNMENT", "NASA", "NOAA", "PDM"]):
            if asset.commercial_use_permitted:
                return RightsStatus.RIGHTS_VERIFIED

        # Permissive commercial with attribution (CC-BY, Pixabay, Pexels)
        if any(term in lic for term in ["CC BY", "CC-BY", "CREATIVE COMMONS ATTRIBUTION"]):
            if "NC" not in lic and "NONCOMMERCIAL" not in lic:
                return RightsStatus.ATTRIBUTION_REQUIRED
            else:
                return RightsStatus.RESTRICTED

        # Pexels / Pixabay License
        if "PEXELS" in lic or "PIXABAY" in lic:
            return RightsStatus.RIGHTS_VERIFIED

        # Non-commercial or No-derivatives restrictions block commercial YouTube Shorts
        if any(term in lic for term in ["NC", "NON-COMMERCIAL", "NONCOMMERCIAL", "ND", "NO DERIVATIVES"]):
            return RightsStatus.RESTRICTED

        # AI-generated content (Google Veo 2 / Google Flow / SynthID)
        if asset.is_ai_reconstruction:
            if asset.ai_provenance_signals_intact:
                return RightsStatus.RIGHTS_VERIFIED
            else:
                return RightsStatus.REJECTED # Tampering with provenance violates YouTube ToS

        return RightsStatus.UNKNOWN

    @classmethod
    def verify_manifest(cls, manifest_entries: List[AssetManifestEntry]) -> Dict[str, Any]:
        """
        Validates the entire asset manifest for an episode against Gate 08:
        Blocks publication if any asset has UNKNOWN, RESTRICTED, or REJECTED status.
        """
        blocking_failures = []
        attributions = []

        for a in manifest_entries:
            st = cls.evaluate_asset(a)
            a.verification_status = st.value

            if st in [RightsStatus.UNKNOWN, RightsStatus.RESTRICTED, RightsStatus.REJECTED]:
                blocking_failures.append({
                    "asset_id": a.asset_id,
                    "title": a.original_title,
                    "scene": a.intended_scene,
                    "status": st.value,
                    "reason": f"Asset {a.asset_id} has invalid rights status '{st.value}'. Cannot enter final render."
                })
            elif st == RightsStatus.ATTRIBUTION_REQUIRED:
                credit = a.attribution_credit_text or f"Footage: '{a.original_title}' by {a.creator_or_rights_holder} ({a.license_name})"
                attributions.append(credit)

        passed = len(blocking_failures) == 0 and len(manifest_entries) > 0

        return {
            "total_assets": len(manifest_entries),
            "passed": passed,
            "blocking_failures": blocking_failures,
            "required_attributions": attributions,
            "manifest": [a.to_dict() for a in manifest_entries]
        }
