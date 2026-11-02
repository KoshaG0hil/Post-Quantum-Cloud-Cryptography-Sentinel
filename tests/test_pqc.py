"""
Unit Tests for Post-Quantum Cloud Cryptography Sentinel
"""

import pytest
from core.pqc_standards import PqcStandardsEngine, PQC_ALGORITHM_REGISTRY
from core.qvi_calculator import QviCalculator, CloudCryptoAsset
from core.migration_engine import MigrationBlueprintEngine


def test_pqc_standards_evaluation():
    rsa_profile = PqcStandardsEngine.evaluate_algorithm("RSA-2048")
    assert rsa_profile.broken_by_shor is True
    assert rsa_profile.estimated_post_quantum_security_bits == 0
    assert rsa_profile.nist_status == "DEPRECATED"

    kyber_profile = PqcStandardsEngine.evaluate_algorithm("X25519_MLKEM768")
    assert kyber_profile.broken_by_shor is False
    assert kyber_profile.quantum_vulnerability_type == "HYBRID_PQC"
    assert kyber_profile.nist_status == "FIPS_203_COMPLIANT"


def test_tls_policy_checker():
    assert PqcStandardsEngine.is_tls_policy_quantum_safe("TLSv1.3-PQ-X25519MLKEM768") is True
    assert PqcStandardsEngine.is_tls_policy_quantum_safe("TLSv1.2_2021") is False


def test_qvi_calculator_high_risk():
    vulnerable_assets = [
        CloudCryptoAsset(
            asset_id="test-1",
            asset_type="CLOUDFRONT_DISTRIBUTION",
            name="prod-api",
            arn="arn:aws:cloudfront::1",
            active_algorithm_or_policy="TLSv1.2_2021",
            data_classification="RESTRICTED_PII",
            secret_lifespan_years=8
        ),
        CloudCryptoAsset(
            asset_id="test-2",
            asset_type="S3_BUCKET",
            name="prod-data",
            arn="arn:aws:s3:::prod-data",
            active_algorithm_or_policy="RSA-2048",
            data_classification="FINANCIAL",
            secret_lifespan_years=10
        )
    ]

    result = QviCalculator.calculate_qvi(vulnerable_assets)
    assert result["qvi_score"] >= 80.0
    assert result["rating"] == "CRITICAL_QUANTUM_RISK"
    assert result["hndl_high_risk_assets_count"] == 2


def test_qvi_calculator_quantum_safe():
    safe_assets = [
        CloudCryptoAsset(
            asset_id="test-safe-1",
            asset_type="CLOUDFRONT_DISTRIBUTION",
            name="pqc-api",
            arn="arn:aws:cloudfront::1",
            active_algorithm_or_policy="TLSv1.3-PQ-MLKEM",
            data_classification="RESTRICTED_PII",
            secret_lifespan_years=5
        ),
        CloudCryptoAsset(
            asset_id="test-safe-2",
            asset_type="KMS_KEY",
            name="pqc-key",
            arn="arn:aws:kms:::1",
            active_algorithm_or_policy="AES-256-GCM",
            data_classification="INTERNAL",
            secret_lifespan_years=2
        )
    ]

    result = QviCalculator.calculate_qvi(safe_assets)
    assert result["qvi_score"] <= 10.0
    assert result["quantum_safe_assets_count"] == 2


def test_migration_blueprint_engine():
    patch_cf = MigrationBlueprintEngine.generate_cloudfront_pqc_patch("EDIST99", "TLSv1.2")
    assert "minimum_protocol_version = \"TLSv1.3\"" in patch_cf["terraform"]

    patch_s3 = MigrationBlueprintEngine.generate_s3_dsse_pqc_patch("my-archive", "arn:aws:kms:test")
    assert "sse_algorithm     = \"aws:kms:dsse\"" in patch_s3["terraform"]
