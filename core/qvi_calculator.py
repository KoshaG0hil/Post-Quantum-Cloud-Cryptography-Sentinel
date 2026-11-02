"""
Quantum Vulnerability Index (QVI) Calculator
Computes aggregate cloud exposure score (0 - 100) based on Harvest Now, Decrypt Later (HNDL) risk,
cryptographic agility, and algorithm obsolescence.
"""

from typing import List, Dict, Any
from pydantic import BaseModel


class CloudCryptoAsset(BaseModel):
    asset_id: str
    asset_type: str  # CLOUDFRONT_DISTRIBUTION, ALB_LISTENER, KMS_KEY, S3_BUCKET
    name: str
    arn: str
    active_algorithm_or_policy: str
    data_classification: str  # RESTRICTED_PII, FINANCIAL, INTERNAL, PUBLIC
    secret_lifespan_years: int  # HNDL risk multiplier (data valuable for 5+ years)


class QviCalculator:
    """Calculates objective Quantum Vulnerability Index (QVI) score."""

    @staticmethod
    def calculate_qvi(assets: List[CloudCryptoAsset]) -> Dict[str, Any]:
        if not assets:
            return {
                "qvi_score": 0.0,
                "rating": "ZERO_EXPOSURE",
                "hndl_high_risk_assets_count": 0,
                "quantum_safe_assets_count": 0,
                "total_audited": 0
            }

        total_weight = 0.0
        vulnerability_points = 0.0
        hndl_high_risk_count = 0
        quantum_safe_count = 0

        classification_multipliers = {
            "RESTRICTED_PII": 2.0,
            "FINANCIAL": 2.0,
            "INTERNAL": 1.2,
            "PUBLIC": 0.3
        }

        for asset in assets:
            multiplier = classification_multipliers.get(asset.data_classification, 1.0)
            lifespan_factor = 1.0 + (min(asset.secret_lifespan_years, 10) * 0.1)  # HNDL multiplier
            weight = multiplier * lifespan_factor
            total_weight += weight

            policy = asset.active_algorithm_or_policy.upper()

            # Check if asset uses post-quantum hybrid or AES-256
            if "MLKEM" in policy or "KYBER" in policy or "FIPS_203" in policy:
                quantum_safe_count += 1
                asset_risk = 0.0
            elif "AES-256" in policy or "SYMMETRIC_DEFAULT" in policy:
                # AES-256 retains 128-bit quantum security under Grover's algorithm
                quantum_safe_count += 1
                asset_risk = 5.0  # minimal residual risk
            elif "RSA-2048" in policy or "ECDHE" in policy or "TLSV1.2" in policy:
                # Completely broken by Shor's algorithm!
                asset_risk = 100.0
                if asset.secret_lifespan_years >= 3 and asset.data_classification in ["RESTRICTED_PII", "FINANCIAL"]:
                    hndl_high_risk_count += 1
            else:
                asset_risk = 70.0

            vulnerability_points += (asset_risk * weight)

        raw_qvi = vulnerability_points / max(total_weight, 1.0)
        qvi_score = round(min(100.0, max(0.0, raw_qvi)), 1)

        if qvi_score >= 75.0:
            rating = "CRITICAL_QUANTUM_RISK"
        elif qvi_score >= 50.0:
            rating = "ELEVATED_HNDL_EXPOSURE"
        elif qvi_score >= 25.0:
            rating = "TRANSITIONAL_RISK"
        else:
            rating = "QUANTUM_RESISTANT"

        return {
            "qvi_score": qvi_score,
            "rating": rating,
            "hndl_high_risk_assets_count": hndl_high_risk_count,
            "quantum_safe_assets_count": quantum_safe_count,
            "total_audited": len(assets)
        }
