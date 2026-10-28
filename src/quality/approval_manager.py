"""Creator Approval & Publishing Safety State Machine for Faceless Media Studio.
Implements Part 12: Strict human-in-the-loop authorization, cryptographic file hash binding,
automatic approval invalidation upon bitstream modification, and upload blocking.
"""
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


APPROVAL_STORE_PATH = Path("data/creator_approvals.json")


class CreatorApprovalManager:
    """Enforces absolute publishing safety and cryptographic bitstream binding."""

    @classmethod
    def _load_store(cls) -> Dict[str, Any]:
        if not APPROVAL_STORE_PATH.exists():
            return {}
        try:
            with open(APPROVAL_STORE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @classmethod
    def _save_store(cls, data: Dict[str, Any]) -> None:
        APPROVAL_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(APPROVAL_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def compute_file_hash(cls, file_path: Path) -> str:
        """Computes SHA-256 checksum of an MP4 export."""
        if not file_path.exists():
            return ""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @classmethod
    def grant_approval(
        cls,
        video_id: str,
        video_file_path: Path,
        reviewer_name: str = "Creator",
        notes: str = "Explicit sign-off granted"
    ) -> Dict[str, Any]:
        """
        Explicitly records human approval bound cryptographically to the exact file SHA-256 hash.
        """
        if not video_file_path.exists():
            raise FileNotFoundError(f"Cannot approve missing video file: {video_file_path}")

        file_hash = cls.compute_file_hash(video_file_path)
        record = {
            "video_id": video_id,
            "file_path": str(video_file_path),
            "file_sha256": file_hash,
            "approved_at": datetime.utcnow().isoformat() + "Z",
            "reviewer_name": reviewer_name,
            "notes": notes,
            "status": "CREATOR_APPROVED"
        }

        store = cls._load_store()
        store[video_id] = record
        cls._save_store(store)
        return record

    @classmethod
    def revoke_approval(cls, video_id: str, reason: str = "Creator revoked approval") -> None:
        """Revokes any active approval for a video."""
        store = cls._load_store()
        if video_id in store:
            store[video_id]["status"] = "APPROVAL_REVOKED"
            store[video_id]["revocation_reason"] = reason
            store[video_id]["revoked_at"] = datetime.utcnow().isoformat() + "Z"
            cls._save_store(store)

    @classmethod
    def verify_upload_authorization(cls, video_id: str, video_file_path: Path) -> Dict[str, Any]:
        """
        Mandatory gatekeeper executed before ANY upload or API transmission:
        Returns authorized=True ONLY IF explicit approval exists AND current file hash matches approved hash.
        """
        if not video_file_path.exists():
            return {
                "authorized": False,
                "reason": f"Video file not found at: {video_file_path}"
            }

        store = cls._load_store()
        record = store.get(video_id)

        if not record:
            return {
                "authorized": False,
                "reason": f"UNAPPROVED VIDEO: Topic '{video_id}' has not received explicit creator approval."
            }

        if record.get("status") != "CREATOR_APPROVED":
            return {
                "authorized": False,
                "reason": f"INVALID APPROVAL: Prior approval for '{video_id}' has status '{record.get('status')}'."
            }

        current_hash = cls.compute_file_hash(video_file_path)
        approved_hash = record.get("file_sha256")

        if current_hash != approved_hash:
            # File changed since approval! Automatically invalidate approval
            cls.revoke_approval(video_id, reason="Bitstream modified after approval (hash mismatch)")
            return {
                "authorized": False,
                "reason": f"HASH MISMATCH: Video file was re-rendered or modified after approval. Prior approval invalidated. (Current: {current_hash[:12]} vs Approved: {approved_hash[:12]})"
            }

        return {
            "authorized": True,
            "video_id": video_id,
            "file_sha256": current_hash,
            "approved_at": record.get("approved_at"),
            "reviewer": record.get("reviewer_name")
        }
