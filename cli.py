"""
AWS Post-Quantum Cryptography (PQC) Audit & Quantum-Safe Migration Sentinel - Interactive CLI
"""

import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from core.pqc_standards import PqcStandardsEngine, PQC_ALGORITHM_REGISTRY
from core.qvi_calculator import QviCalculator, CloudCryptoAsset
from core.migration_engine import MigrationBlueprintEngine

console = Console()


def get_mock_enterprise_cloud_inventory():
    return [
        CloudCryptoAsset(
            asset_id="cf-dist-01",
            asset_type="CLOUDFRONT_DISTRIBUTION",
            name="customer-portal-api.corporate.com",
            arn="arn:aws:cloudfront::000000000000:distribution/EDIST01",
            active_algorithm_or_policy="TLSv1.2_2021 (Classical ECDHE-RSA)",
            data_classification="RESTRICTED_PII",
            secret_lifespan_years=7
        ),
        CloudCryptoAsset(
            asset_id="s3-vault-02",
            asset_type="S3_BUCKET",
            name="financial-transaction-archives-prod",
            arn="arn:aws:s3:::financial-transaction-archives-prod",
            active_algorithm_or_policy="SSE-KMS (RSA-2048 Envelope)",
            data_classification="FINANCIAL",
            secret_lifespan_years=10
        ),
        CloudCryptoAsset(
            asset_id="alb-ext-03",
            asset_type="ALB_LISTENER",
            name="payment-gateway-alb-listener",
            arn="arn:aws:elasticloadbalancing:us-east-1:000000000000:listener/app/alb/123",
            active_algorithm_or_policy="ELBSecurityPolicy-TLS13-1-2-2021-06",
            data_classification="FINANCIAL",
            secret_lifespan_years=5
        ),
        CloudCryptoAsset(
            asset_id="kms-key-04",
            asset_type="KMS_KEY",
            name="core-database-storage-key",
            arn="arn:aws:kms:us-east-1:000000000000:key/k-aes256",
            active_algorithm_or_policy="SYMMETRIC_DEFAULT (AES-256-GCM)",
            data_classification="INTERNAL",
            secret_lifespan_years=3
        ),
        CloudCryptoAsset(
            asset_id="cf-edge-05",
            asset_type="CLOUDFRONT_DISTRIBUTION",
            name="public-marketing-cdn.corporate.com",
            arn="arn:aws:cloudfront::000000000000:distribution/EDIST05",
            active_algorithm_or_policy="TLSv1.3-PQ-X25519MLKEM768",
            data_classification="PUBLIC",
            secret_lifespan_years=1
        )
    ]


def run_cli():
    console.print(Panel.fit(
        "[bold magenta]POST-QUANTUM CLOUD CRYPTOGRAPHY SENTINEL (PQC)[/bold magenta]\n"
        "[cyan]NIST FIPS 203 (ML-KEM) Audit · Quantum Vulnerability Index (QVI) · Hybrid Migration Mesh[/cyan]",
        border_style="magenta"
    ))

    with console.status("[bold yellow]Scanning AWS KMS, CloudFront, ALB, and S3 cryptographic posture..."):
        assets = get_mock_enterprise_cloud_inventory()
        qvi_result = QviCalculator.calculate_qvi(assets)

    # 1. NIST Threat Registry Table
    console.print("\n[bold cyan]=== NIST POST-QUANTUM ALGORITHM STATUS (FIPS 203 / 204) ===[/bold cyan]")
    nist_table = Table(show_header=True, header_style="bold green")
    nist_table.add_column("Algorithm", width=20)
    nist_table.add_column("Classical Bits", width=16)
    nist_table.add_column("Shor Impact", width=18)
    nist_table.add_column("Post-Quantum Bits", width=18)
    nist_table.add_column("NIST Status", width=22)

    for name, p in list(PQC_ALGORITHM_REGISTRY.items())[:6]:
        nist_table.add_row(
            name,
            f"{p.classical_security_bits} bits",
            "[bold red]COMPLETELY BROKEN[/bold red]" if p.broken_by_shor else "[green]UNAFFECTED[/green]",
            f"{p.estimated_post_quantum_security_bits} bits",
            f"[bold cyan]{p.nist_status}[/bold cyan]" if "FIPS" in p.nist_status or "QUANTUM" in p.nist_status else f"[red]{p.nist_status}[/red]"
        )
    console.print(nist_table)

    # 2. Audited Cloud Assets
    console.print("\n[bold yellow]=== ENTERPRISE CLOUD INVENTORY CRYPTOGRAPHIC AUDIT ===[/bold yellow]")
    asset_table = Table(show_header=True, header_style="bold blue")
    asset_table.add_column("Resource Name", width=34)
    asset_table.add_column("Type", width=22)
    asset_table.add_column("Active Crypto Spec", width=30)
    asset_table.add_column("Data Class", width=16)
    asset_table.add_column("HNDL Risk", width=14)

    for a in assets:
        is_pqc = "MLKEM" in a.active_algorithm_or_policy or "AES-256" in a.active_algorithm_or_policy
        hndl_risk = "[green]LOW[/green]" if is_pqc else "[bold red]CRITICAL[/bold red]"
        asset_table.add_row(
            a.name,
            a.asset_type,
            f"[green]{a.active_algorithm_or_policy}[/green]" if is_pqc else f"[red]{a.active_algorithm_or_policy}[/red]",
            a.data_classification,
            hndl_risk
        )
    console.print(asset_table)

    # 3. QVI Scorecard
    console.print("\n[bold red]=== QUANTUM VULNERABILITY INDEX (QVI) SCORECARD ===[/bold red]")
    qvi_table = Table(show_header=True, header_style="bold magenta")
    qvi_table.add_column("Metric", width=38)
    qvi_table.add_column("Score / Status", width=26)

    qvi_table.add_row("Total Cloud Assets Audited", str(qvi_result["total_audited"]))
    qvi_table.add_row("Quantum-Safe / Hybrid Assets", f"[green]{qvi_result['quantum_safe_assets_count']}[/green]")
    qvi_table.add_row("Immediate HNDL High-Risk Assets", f"[bold red]{qvi_result['hndl_high_risk_assets_count']}[/bold red]")
    qvi_table.add_row("Quantum Vulnerability Rating", f"[bold red]{qvi_result['rating']}[/bold red]")
    qvi_table.add_row("Composite QVI Score (0 - 100)", f"[bold red]{qvi_result['qvi_score']} / 100[/bold red]")
    console.print(qvi_table)

    # 4. Remediation Blueprint
    console.print("\n[bold green]=== SYNTHESIZED HYBRID PQC TERRAFORM MIGRATIONS ===[/bold green]")
    cf_patch = MigrationBlueprintEngine.generate_cloudfront_pqc_patch("EDIST01", "TLSv1.2_2021")
    s3_patch = MigrationBlueprintEngine.generate_s3_dsse_pqc_patch("financial-transaction-archives-prod", "arn:aws:kms:us-east-1:000000000000:key/k-dsse")

    console.print(f"\n[bold cyan]> {cf_patch['title']}[/bold cyan] - [dim]{cf_patch['rationale']}[/dim]")
    syntax_cf = Syntax(cf_patch["terraform"], "terraform", theme="monokai", line_numbers=True)
    console.print(syntax_cf)

    console.print(f"\n[bold cyan]> {s3_patch['title']}[/bold cyan] - [dim]{s3_patch['rationale']}[/dim]")
    syntax_s3 = Syntax(s3_patch["terraform"], "terraform", theme="monokai", line_numbers=True)
    console.print(syntax_s3)

    console.print("\n[bold green][SUCCESS] Post-Quantum Audit & Migration Blueprints Generated Successfully.[/bold green]\n")


if __name__ == "__main__":
    run_cli()
