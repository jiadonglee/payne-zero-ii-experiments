"""Canonical M-giant dual-path validation ledger.

The ledger is compiled from closeout records through 2026-09-13.  It is the
machine-readable source for unique-target counts.  Full atmosphere products
are not required to regenerate the tally; they are required to re-solve.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .experiment_identity import config_fingerprint


REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = (
    REPO_ROOT / "notes" / "ledgers" / "m_star_dual_path_validation_v1.json"
)
SUMMARY_PATH = LEDGER_PATH.with_name("m_star_dual_path_validation_v1_summary.md")
PLOT_PATH = LEDGER_PATH.with_name("m_star_dual_path_validation_v1.png")
REPRO_ROOT = LEDGER_PATH.with_name("m_star_evidence_repro_v1")

LABEL_FIELDS = (
    "teff_K",
    "logg",
    "metallicity",
    "alpha_enhancement",
    "carbon_enhancement",
    "microturbulence_km_s",
)
DEFAULT_FIXED_LABELS = {
    "alpha_enhancement": 0.0,
    "carbon_enhancement": 0.0,
    "microturbulence_km_s": 2.0,
}


def stellar_label_key(
    teff_k: float,
    logg: float,
    metallicity: float,
    *,
    alpha_enhancement: float = 0.0,
    carbon_enhancement: float = 0.0,
    microturbulence_km_s: float = 2.0,
) -> tuple[float, float, float, float, float, float]:
    return (
        round(float(teff_k), 3),
        round(float(logg), 4),
        round(float(metallicity), 4),
        round(float(alpha_enhancement), 4),
        round(float(carbon_enhancement), 4),
        round(float(microturbulence_km_s), 4),
    )


def _fixed_label_defaults(
    defaults: Mapping[str, Any] | None = None,
) -> dict[str, float]:
    values = dict(DEFAULT_FIXED_LABELS)
    if defaults:
        for field in DEFAULT_FIXED_LABELS:
            if field in defaults and defaults[field] is not None:
                values[field] = float(defaults[field])
    return values


def stellar_label_key_from_row(
    row: Mapping[str, Any],
    *,
    defaults: Mapping[str, Any] | None = None,
) -> tuple[float, float, float, float, float, float]:
    """Return the complete six-dimensional stellar-label identity.

    Historical ledger rows omitted the three fixed labels because they were
    constant for that campaign.  Missing values therefore inherit the
    campaign defaults, while explicit values remain part of the identity.
    """

    fixed = _fixed_label_defaults(defaults)
    return stellar_label_key(
        row["teff_K"],
        row["logg"],
        row["metallicity"],
        alpha_enhancement=row.get("alpha_enhancement", fixed["alpha_enhancement"]),
        carbon_enhancement=row.get("carbon_enhancement", fixed["carbon_enhancement"]),
        microturbulence_km_s=row.get(
            "microturbulence_km_s", fixed["microturbulence_km_s"]
        ),
    )


def materialize_stellar_labels(
    row: Mapping[str, Any],
    *,
    defaults: Mapping[str, Any] | None = None,
) -> dict[str, float]:
    """Return a row copy with every identity field explicit."""

    key = stellar_label_key_from_row(row, defaults=defaults)
    return dict(zip(LABEL_FIELDS, key))


def load_ledger(path: Path | None = None) -> dict[str, Any]:
    ledger_path = LEDGER_PATH if path is None else Path(path)
    payload = json.loads(ledger_path.read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"ledger is not an object: {ledger_path}")
    return payload


def unique_giant_rows(ledger: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    payload = load_ledger() if ledger is None else ledger
    defaults = payload.get("fixed_labels", DEFAULT_FIXED_LABELS)
    rows = [
        {
            **dict(row),
            **materialize_stellar_labels(row, defaults=defaults),
        }
        for row in payload["m_giant_dual_path"]
    ]
    seen: dict[tuple[float, float, float, float, float, float], int] = {}
    duplicates = []
    for row in rows:
        key = stellar_label_key_from_row(row, defaults=defaults)
        if key in seen:
            duplicates.append(key)
        seen[key] = seen.get(key, 0) + 1
    if duplicates:
        raise ValueError(f"duplicate stellar labels in ledger: {duplicates}")
    return rows


def summarize_giant_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    defaults: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    unique_keys = {
        stellar_label_key_from_row(row, defaults=defaults) for row in rows
    }
    spectrum = [row for row in rows if row.get("spectrum_consistent")]
    within_60 = [row for row in rows if row.get("within_budget_60")]
    over_60 = [
        row
        for row in rows
        if row.get("spectrum_consistent") and row.get("within_budget_60") is False
    ]
    over_budget_labels = [
        {
            **{
                field: materialize_stellar_labels(row, defaults=defaults)[field]
                for field in LABEL_FIELDS
            },
            "emulator_frozen_iteration": row.get("emulator_frozen_iteration"),
        }
        for row in over_60
    ]
    observed_ranges = {}
    for field in LABEL_FIELDS:
        values = sorted(
            {
                float(materialize_stellar_labels(row, defaults=defaults)[field])
                for row in rows
            }
        )
        observed_ranges[field] = {
            "min": values[0] if values else None,
            "max": values[-1] if values else None,
            "n_unique": len(values),
            "values": values,
        }
    return {
        "n_unique": len(unique_keys),
        "n_rows": len(rows),
        "n_spectrum_consistent": len(spectrum),
        "n_within_budget_60": len(within_60),
        "n_over_budget_60": len(over_60),
        "over_budget_points": over_budget_labels,
        "observed_label_ranges": observed_ranges,
        "t3250_resolved": any(
            abs(float(row["teff_K"]) - 3250.0) < 1e-6
            and abs(float(row["logg"]) - 2.0) < 1e-6
            and abs(float(row["metallicity"]) - 0.0) < 1e-6
            and row.get("spectrum_consistent")
            for row in rows
        ),
    }


def assert_unique_stellar_labels(
    rows: Iterable[Mapping[str, Any]],
    *,
    defaults: Mapping[str, Any] | None = None,
) -> None:
    seen: set[tuple[float, float, float, float, float, float]] = set()
    duplicates = []
    for row in rows:
        key = stellar_label_key_from_row(row, defaults=defaults)
        if key in seen:
            duplicates.append(key)
        seen.add(key)
    if duplicates:
        raise ValueError(f"duplicate stellar labels: {duplicates}")


def canonical_tally(path: Path | None = None) -> dict[str, Any]:
    ledger = load_ledger(path)
    rows = unique_giant_rows(ledger)
    tally = summarize_giant_rows(rows, defaults=ledger.get("fixed_labels"))
    dwarf = ledger["m_dwarf_safezone_v2"]
    recorded_counting = dict(ledger.get("counting", {}))
    # Preserve the historical 21/21 string for auditability, but make every
    # numerical field in the public tally a value recomputed from the rows.
    recorded_counting.update(
        {
            "unique_targets": tally["n_unique"],
            "spectrum_consistent": tally["n_spectrum_consistent"],
            "emulator_within_60": tally["n_within_budget_60"],
            "emulator_over_60": tally["n_over_budget_60"],
            "over_budget_point": tally["over_budget_points"][0]
            if tally["over_budget_points"]
            else None,
            "derived_from_full_label_rows": True,
        }
    )
    tally.update(
        {
            "ledger_id": ledger["ledger_id"],
            "counting": recorded_counting,
            "fixed_labels": _fixed_label_defaults(ledger.get("fixed_labels")),
            "dwarf_n_validation": dwarf["n_validation"],
            "dwarf_n_formal_converge_within_30": dwarf["n_formal_converge_within_30"],
            "dwarf_n_tio_pass_among_converged": dwarf["n_tio_pass_among_converged"],
            "fit_smoke_continuous_inversion": ledger["fit_smoke_v1"][
                "continuous_offgrid_inversion"
            ],
        }
    )
    return tally


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "teff_K",
        "logg",
        "metallicity",
        "alpha_enhancement",
        "carbon_enhancement",
        "microturbulence_km_s",
        "cohort",
        "closing_campaign",
        "numerically_stable",
        "spectrum_consistent",
        "within_budget_60",
        "emulator_frozen_iteration",
        "reference_frozen_iteration",
        "tio_max",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def format_tally_markdown(tally: Mapping[str, Any]) -> str:
    over = tally["over_budget_points"]
    over_text = ", ".join(
        f"{item['teff_K']:.0f} K, log g={item['logg']}, [M/H]={item['metallicity']:+.1f}"
        for item in over
    ) or "none"
    ranges = tally["observed_label_ranges"]
    observed = "; ".join(
        f"{field}={ranges[field]['min']:g}..{ranges[field]['max']:g}"
        for field in LABEL_FIELDS
    )
    return (
        f"- unique M-giant dual-path targets: **{tally['n_unique']}**\n"
        f"- spectrally consistent endpoints: **{tally['n_spectrum_consistent']}/{tally['n_unique']}**\n"
        f"- emulator within 60 iterations: **{tally['n_within_budget_60']}/{tally['n_unique']}**\n"
        f"- emulator over 60 iterations: **{tally['n_over_budget_60']}** ({over_text})\n"
        f"- t3250 reference constructable: **{tally['t3250_resolved']}**\n"
        f"- observed six-label ranges (discrete rows only): {observed}\n"
        f"- M-dwarf opened validation: {tally['dwarf_n_formal_converge_within_30']}/"
        f"{tally['dwarf_n_validation']} formal converge in 30 iterations; "
        f"{tally['dwarf_n_tio_pass_among_converged']} TiO pass among those\n"
    )


def write_summary(path: Path, tally: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "# M-star dual-path validation summary\n\n"
    text += "Generated from `m_star_dual_path_validation_v1.json`; the JSON ledger is the source table.\n\n"
    text += format_tally_markdown(tally)
    text += "\nThe observed ranges list the values present in the 18 rows. They are not a claim that the intervening parameter box was validated.\n"
    path.write_text(text)


def write_validation_plot(
    path: Path,
    rows: Sequence[Mapping[str, Any]],
    tally: Mapping[str, Any],
) -> None:
    """Write a compact count plus label-space plot from the same rows."""

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.8), constrained_layout=True)
    counts = [
        tally["n_unique"],
        tally["n_spectrum_consistent"],
        tally["n_within_budget_60"],
        tally["n_over_budget_60"],
    ]
    labels = ["unique", "spectral", "within 60", "over 60"]
    bars = axes[0].bar(labels, counts, color=["#6c757d", "#2a9d8f", "#457b9d", "#e76f51"])
    axes[0].set_ylabel("targets")
    axes[0].set_ylim(0, max(counts) + 2)
    axes[0].set_title("Canonical counts")
    axes[0].tick_params(axis="x", rotation=25)
    for bar, count in zip(bars, counts):
        axes[0].text(bar.get_x() + bar.get_width() / 2, count + 0.15, str(count), ha="center")

    metallicity = [float(row["metallicity"]) for row in rows]
    within = [bool(row.get("within_budget_60")) for row in rows]
    scatter = axes[1].scatter(
        [row["teff_K"] for row in rows],
        [row["logg"] for row in rows],
        c=metallicity,
        cmap="viridis",
        marker="o",
        s=42,
        edgecolors=["#264653" if value else "#e76f51" for value in within],
        linewidths=1.2,
    )
    axes[1].set_xlabel(r"$T_{\rm eff}$ (K)")
    axes[1].set_ylabel(r"$\log g$")
    axes[1].set_title("Observed label rows")
    axes[1].grid(alpha=0.25)
    colorbar = fig.colorbar(scatter, ax=axes[1], pad=0.02)
    colorbar.set_label("[M/H]")
    axes[1].legend(
        handles=[
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#777", markeredgecolor="#264653", label="within 60", markersize=7),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#777", markeredgecolor="#e76f51", label="over 60", markersize=7),
        ],
        loc="best",
        frameon=False,
    )
    fig.suptitle("M-giant dual-path ledger (18 unique targets)")
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _node_id_from_row(row: Mapping[str, Any]) -> str:
    return (
        f"g{float(row['logg']):+05.2f}_m{float(row['metallicity']):+05.2f}"
        f"_a{float(row['alpha_enhancement']):+05.2f}"
        f"_c{float(row['carbon_enhancement']):+05.2f}"
        f"_x{float(row['microturbulence_km_s']):.2f}_t{int(row['teff_K']):04d}"
    )


def _scalar_diagnostic_sources(
    node_ids: set[str] | None = None,
) -> list[tuple[str, Path]]:
    roots = [
        ("m_star_stop_rule_v1", REPO_ROOT / "results" / "m_star_stop_rule_v1"),
        ("m_star_sixty_budget_v1", REPO_ROOT / "results" / "m_star_sixty_budget_v1"),
        ("m_star_gravity_walk_v1", REPO_ROOT / "results" / "m_star_gravity_walk_v1"),
    ]
    found: list[tuple[str, Path]] = []
    for campaign, root in roots:
        if not root.is_dir():
            continue
        for source in sorted(root.rglob("iterations.jsonl")):
            relative = source.relative_to(root)
            parts = relative.parts
            node = next((part for part in parts if part.startswith("g")), "unknown")
            if node_ids is not None and node not in node_ids:
                continue
            arm = next(
                (part for part in parts if part in {"emulator", "reference", "reference_walk", "candidate", "truth"}),
                "unknown",
            )
            found.append((f"{campaign}/{node}/{arm}", source))
    return found


def write_repro_package(
    root: Path,
    *,
    ledger: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    tally: Mapping[str, Any],
) -> None:
    """Export compact identities and scalar traces without copying NPZ files."""

    root.mkdir(parents=True, exist_ok=True)
    identity = {
        "ledger_id": ledger["ledger_id"],
        "source_snapshot": ledger.get("source_snapshot"),
        "git_commit_at_export": _git_commit_for_repro(),
        "labels": [
            {
                "node_id": _node_id_from_row(row),
                **{field: row[field] for field in LABEL_FIELDS},
                "cohort": row.get("cohort"),
                "sources": row.get("sources", []),
            }
            for row in rows
        ],
    }
    identity["input_identity_hash"] = config_fingerprint(
        {"ledger_id": identity["ledger_id"], "labels": identity["labels"]}
    )
    (root / "input_identity.json").write_text(json.dumps(identity, indent=2, sort_keys=True) + "\n")
    config = {
        "emulator_budget": 60,
        "emulator_campaign_cap": 90,
        "reference_budget": 240,
        "reference_relax_cap": 120,
        "spectral_gate_max": 5.0e-3,
        "fixed_labels": tally["fixed_labels"],
        "stop_rule": {
            "tio_max_change": 5.0e-4,
            "temperature_p95": 1.0e-4,
            "mass_dex_p95": 1.0e-3,
            "consecutive_segments": 2,
            "segment_length": 5,
        },
        "protocol_sources": [
            "notes/m_star_stop_rule_v1_closeout_20260909.md",
            "notes/m_star_sixty_budget_v1_closeout_20260913.md",
            "notes/m_star_gravity_walk_v1_closeout_20260913.md",
        ],
    }
    config["config_hash"] = config_fingerprint(config)
    (root / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    diagnostics_path = root / "scalar_diagnostics.jsonl"
    diagnostic_count = 0
    node_ids = {_node_id_from_row(row) for row in rows}
    with diagnostics_path.open("w") as output:
        for source_id, source in _scalar_diagnostic_sources(node_ids):
            try:
                lines = source.read_text().splitlines()
            except OSError:
                continue
            for line in lines:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(record, dict):
                    continue
                output.write(json.dumps({"source": source_id, **record}, sort_keys=True) + "\n")
                diagnostic_count += 1
    final_metrics = {
        "canonical_tally": tally,
        "diagnostic_record_count": diagnostic_count,
        "config_hash": config["config_hash"],
        "input_identity_hash": identity["input_identity_hash"],
        "ledger_path": str(LEDGER_PATH),
    }
    (root / "final_metrics.json").write_text(json.dumps(final_metrics, indent=2, sort_keys=True) + "\n")
    products = []
    for row in rows:
        node = _node_id_from_row(row)
        candidates = [
            REPO_ROOT / "results" / "m_star_stop_rule_v1" / "validate" / node,
            REPO_ROOT / "results" / "m_star_sixty_budget_v1" / "points" / node,
            REPO_ROOT / "results" / "m_star_gravity_walk_v1" / "points" / node,
        ]
        products.append(
            {
                "node_id": node,
                "available_local_paths": [str(path) for path in candidates if path.exists()],
                "expected_paths": [str(path) for path in candidates],
                "sources": row.get("sources", []),
            }
        )
    manifest = {
        "large_products_included": False,
        "products": products,
        "retrieval": (
            "Use the available_local_paths when present. For absent products, use the "
            "absolute result/product paths recorded in the cited closeout JSON or run "
            "the corresponding campaign driver on a synchronized Garching checkout; "
            "this package does not claim absent NPZ products are present."
        ),
    }
    (root / "product_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    readme = (
        "# M-star evidence reproduction package\n\n"
        "The canonical input is `../m_star_dual_path_validation_v1.json`. This package "
        "contains the six-label identities and their input hash, fixed configuration "
        "and config hash, scalar iteration diagnostics extracted from available result directories, final metrics, and "
        "a product manifest. Large NPZ/checkpoint products are intentionally not copied.\n\n"
        "Regenerate the ledger CSV, summary, figure, and this package with:\n\n"
        "```sh\nPYTHONPATH=. python -m experiments.reduced_state_emulator.m_star_validation_ledger\n```\n\n"
        "`product_manifest.json` records which products are present locally and how to "
        "retrieve missing products from the paths in the closeouts.\n"
    )
    (root / "README.md").write_text(readme)


def _git_commit_for_repro() -> str | None:
    try:
        import subprocess

        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=LEDGER_PATH)
    parser.add_argument(
        "--csv",
        type=Path,
        default=LEDGER_PATH.with_suffix(".csv"),
    )
    parser.add_argument("--summary", type=Path, default=SUMMARY_PATH)
    parser.add_argument("--plot", type=Path, default=PLOT_PATH)
    parser.add_argument("--repro-root", type=Path, default=REPRO_ROOT)
    parser.add_argument("--no-repro-package", action="store_true")
    args = parser.parse_args(argv)
    ledger = load_ledger(args.ledger)
    rows = unique_giant_rows(ledger)
    tally = canonical_tally(args.ledger)
    write_csv(args.csv, rows)
    write_summary(args.summary, tally)
    write_validation_plot(args.plot, rows, tally)
    if not args.no_repro_package:
        write_repro_package(args.repro_root, ledger=ledger, rows=rows, tally=tally)
    print(json.dumps(tally, indent=2, sort_keys=True))
    print(format_tally_markdown(tally), end="")
    print(f"wrote {args.csv}")
    print(f"wrote {args.summary}")
    print(f"wrote {args.plot}")
    if not args.no_repro_package:
        print(f"wrote {args.repro_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
