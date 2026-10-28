"""Claim Auditor and Fact-Checking Ledger Module for Faceless Media Studio.
Enforces rigorous factual accuracy, primary source verification, and publication blocking
for unverified, disputed, or unsupported numerical and engineering claims.
"""
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Dict, Any, Optional
import json
from pathlib import Path


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    DISPUTED = "DISPUTED"
    OUTDATED = "OUTDATED"
    UNSUPPORTED = "UNSUPPORTED"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"


class ClaimType(str, Enum):
    NUMERICAL_MEASUREMENT = "NUMERICAL_MEASUREMENT" # Dimensions, weights, costs, speeds
    HISTORICAL_EVENT = "HISTORICAL_EVENT"
    ENGINEERING_MECHANISM = "ENGINEERING_MECHANISM"
    CAUSAL_RELATIONSHIP = "CAUSAL_RELATIONSHIP"
    GEOLOGICAL_PHENOMENON = "GEOLOGICAL_PHENOMENON"
    SAFETY_STATISTIC = "SAFETY_STATISTIC"


@dataclass
class ClaimEntry:
    claim_id: str
    claim_text: str
    claim_type: str
    source_title: str
    source_url: str
    publisher: str
    publication_date: str
    access_date: str
    supporting_excerpt_or_notes: str
    confidence: float # 0.0 to 1.0
    verification_status: str # from VerificationStatus
    script_location: str # e.g. "Scene 1 (0:00 - 0:08)"
    is_material_numerical: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ClaimLedger:
    """Manages the structured claim ledger for an individual video topic."""

    def __init__(self, topic_id: str, topic_title: str):
        self.topic_id = topic_id
        self.topic_title = topic_title
        self.claims: List[ClaimEntry] = []

    def add_claim(self, claim: ClaimEntry) -> None:
        self.claims.append(claim)

    def verify_all(self) -> Dict[str, Any]:
        """
        Evaluates the ledger against the strict Gate 05 Factual Accuracy rule:
        Any UNRESOLVED, DISPUTED, or UNSUPPORTED material claim blocks publication.
        """
        total = len(self.claims)
        verified_count = sum(1 for c in self.claims if c.verification_status == VerificationStatus.VERIFIED)
        blocking_issues = []

        for c in self.claims:
            if c.verification_status in [
                VerificationStatus.UNSUPPORTED,
                VerificationStatus.DISPUTED,
                VerificationStatus.OUTDATED,
                VerificationStatus.REQUIRES_HUMAN_REVIEW
            ]:
                blocking_issues.append({
                    "claim_id": c.claim_id,
                    "text": c.claim_text,
                    "status": c.verification_status,
                    "script_location": c.script_location,
                    "reason": f"Claim status '{c.verification_status}' violates Gate 05 factual accuracy rule."
                })

        passed = len(blocking_issues) == 0 and total > 0
        score = (verified_count / max(1, total)) * 100.0

        return {
            "topic_id": self.topic_id,
            "total_claims": total,
            "verified_claims": verified_count,
            "factual_integrity_score": round(score, 1),
            "passed": passed,
            "blocking_failures": blocking_issues,
            "ledger": [c.to_dict() for c in self.claims]
        }

    def save_ledger(self, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(self.verify_all(), f, indent=2)

    @classmethod
    def load_ledger(cls, json_path: Path) -> "ClaimLedger":
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        ledger = cls(data.get("topic_id", ""), "")
        for c in data.get("ledger", []):
            entry = ClaimEntry(
                claim_id=c["claim_id"],
                claim_text=c["claim_text"],
                claim_type=c["claim_type"],
                source_title=c["source_title"],
                source_url=c["source_url"],
                publisher=c["publisher"],
                publication_date=c["publication_date"],
                access_date=c["access_date"],
                supporting_excerpt_or_notes=c["supporting_excerpt_or_notes"],
                confidence=c.get("confidence", 1.0),
                verification_status=c["verification_status"],
                script_location=c["script_location"],
                is_material_numerical=c.get("is_material_numerical", False)
            )
            ledger.add_claim(entry)
        return ledger
