"""
NIST Post-Quantum Cryptography (PQC) Standards & Quantum Threat Matrix
Encapsulates FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA),
and Grover/Shor algorithm vulnerabilities for cloud assets.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel


class QuantumThreatProfile(BaseModel):
    algorithm: str
    key_size: int
    classical_security_bits: int
    quantum_vulnerability_type: str  # SHOR_BREAKS, GROVER_HALVES, QUANTUM_SAFE, HYBRID_PQC
    broken_by_shor: bool
    estimated_post_quantum_security_bits: int
    nist_status: str  # DEPRECATED, TRANSITIONAL, FIPS_203_COMPLIANT, QUANTUM_RESISTANT


PQC_ALGORITHM_REGISTRY: Dict[str, QuantumThreatProfile] = {
    # Classical Asymmetric (Completely broken by Shor's Algorithm)
    "RSA-2048": QuantumThreatProfile(
        algorithm="RSA",
        key_size=2048,
        classical_security_bits=112,
        quantum_vulnerability_type="SHOR_BREAKS",
        broken_by_shor=True,
        estimated_post_quantum_security_bits=0,
        nist_status="DEPRECATED"
    ),
    "RSA-4096": QuantumThreatProfile(
        algorithm="RSA",
        key_size=4096,
        classical_security_bits=128,
        quantum_vulnerability_type="SHOR_BREAKS",
        broken_by_shor=True,
        estimated_post_quantum_security_bits=0,
        nist_status="DEPRECATED"
    ),
    "ECDSA-P256": QuantumThreatProfile(
        algorithm="ECDSA",
        key_size=256,
        classical_security_bits=128,
        quantum_vulnerability_type="SHOR_BREAKS",
        broken_by_shor=True,
        estimated_post_quantum_security_bits=0,
        nist_status="DEPRECATED"
    ),
    "ECDHE-X25519": QuantumThreatProfile(
        algorithm="ECDHE",
        key_size=256,
        classical_security_bits=128,
        quantum_vulnerability_type="SHOR_BREAKS",
        broken_by_shor=True,
        estimated_post_quantum_security_bits=0,
        nist_status="DEPRECATED"
    ),

    # Symmetric Encryption (Grover's Algorithm halves security level: 256 -> 128 bits)
    "AES-128": QuantumThreatProfile(
        algorithm="AES",
        key_size=128,
        classical_security_bits=128,
        quantum_vulnerability_type="GROVER_HALVES",
        broken_by_shor=False,
        estimated_post_quantum_security_bits=64,
        nist_status="TRANSITIONAL"
    ),
    "AES-256-GCM": QuantumThreatProfile(
        algorithm="AES-GCM",
        key_size=256,
        classical_security_bits=256,
        quantum_vulnerability_type="QUANTUM_RESISTANT",
        broken_by_shor=False,
        estimated_post_quantum_security_bits=128,
        nist_status="QUANTUM_RESISTANT"
    ),

    # NIST Standardized Post-Quantum Cryptography (FIPS 203 / Hybrid KEMs)
    "X25519_MLKEM768": QuantumThreatProfile(
        algorithm="X25519+ML-KEM-768",
        key_size=768,
        classical_security_bits=192,
        quantum_vulnerability_type="HYBRID_PQC",
        broken_by_shor=False,
        estimated_post_quantum_security_bits=192,
        nist_status="FIPS_203_COMPLIANT"
    ),
    "SecP256r1_MLKEM768": QuantumThreatProfile(
        algorithm="SecP256r1+ML-KEM-768",
        key_size=768,
        classical_security_bits=192,
        quantum_vulnerability_type="HYBRID_PQC",
        broken_by_shor=False,
        estimated_post_quantum_security_bits=192,
        nist_status="FIPS_203_COMPLIANT"
    )
}


class PqcStandardsEngine:
    """Evaluates algorithms and policies against NIST Post-Quantum standards."""

    @staticmethod
    def evaluate_algorithm(algo_name: str) -> QuantumThreatProfile:
        return PQC_ALGORITHM_REGISTRY.get(
            algo_name,
            QuantumThreatProfile(
                algorithm=algo_name,
                key_size=0,
                classical_security_bits=0,
                quantum_vulnerability_type="SHOR_BREAKS",
                broken_by_shor=True,
                estimated_post_quantum_security_bits=0,
                nist_status="DEPRECATED"
            )
        )

    @staticmethod
    def is_tls_policy_quantum_safe(policy_name: str) -> bool:
        """
        Evaluates whether an AWS CloudFront or ALB security policy supports
        Hybrid Post-Quantum Key Exchange (e.g. TLSv1.3-PQ or X25519MLKEM768).
        """
        pq_keywords = ["MLKEM", "KYBER", "PQ-", "POST-QUANTUM", "HYBRID-PQC"]
        return any(k in policy_name.upper() for k in pq_keywords)
