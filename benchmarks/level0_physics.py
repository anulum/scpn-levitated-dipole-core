# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — level-0 physics benchmark

"""Benchmark the level-0 physics of this package on the Python floor.

Follows the ecosystem benchmark standard: warm-up, repeated samples,
percentiles, one row per (operation, backend), unavailable backends marked
explicitly, full provenance in the artefact. Two operations are timed:

- ``closed_forms``: the resonant field, the perpendicular beta, the
  marginal pressure ratio and the induced charging current over a
  deterministic grid of synthetic inputs; each sample times one full grid
  pass;
- ``level0_record``: the composed level-0 record with its canonical bytes
  for the anchor configuration and declarations the test suite uses (from a
  filed design paper; nothing is asserted about the machine), with the
  perpendicular pressure varied over the grid.

This package has no native crate. The ``rust_native`` row records that
explicitly instead of omitting it. Nothing measured here is a physics
claim, and a run on a loaded host is a smoke timing, not a performance
measurement.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import platform
import shutil
import statistics
import subprocess
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

ROOT: Final = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scpn_levitated_dipole_core.configuration import (  # noqa: E402
    DeviceConfiguration,
    configuration_from_bytes,
)
from scpn_levitated_dipole_core.physics import (  # noqa: E402
    ChargingDeclaration,
    HeatingDeclaration,
    PlasmaDeclaration,
    WindingDeclaration,
    level0_physics,
    resonant_field_t,
)
from scpn_levitated_dipole_core.physics.charging import (  # noqa: E402
    induced_current_a,
)
from scpn_levitated_dipole_core.physics.plasma import (  # noqa: E402
    marginal_pressure_ratio,
    perpendicular_beta,
)

SCHEMA: Final = "scpn-levitated-dipole-core.level0-physics-benchmark.v1"
NATIVE_STATUS: Final = (
    "unavailable: this package has no native crate; the level-0 kernels are "
    "closed forms using + - * /, sqrt and one real power, and the native "
    "decision of audit plan Q01 awaits the owner"
)
ANCHOR_CONFIGURATION: Final = (
    b'{"coil":{"coil_current_ka":1.82,"coil_mass_kg":560.0,"coil_radius_m":0.34,'
    b'"superconducting":true},"identifier":"levitated_dipole","levitation":'
    b'{"field_gradient_t_per_m":0.011604236878290021},"registry":{"digest_sha256":'
    b'"786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090",'
    b'"version":"1.0.0"}}\n'
)


def grid(points: int) -> list[tuple[float, float, float]]:
    """Build a deterministic synthetic grid.

    Parameters
    ----------
    points
        Number of grid points.

    Returns
    -------
    list of (float, float, float)
        ``(frequency_hz, pressure_pa, field_t)`` triples.
    """
    return [
        (
            1.0e9 + 9.0e9 * (index % 97) / 96.0,
            100.0 + 1900.0 * (index % 89) / 88.0,
            0.05 + 0.95 * (index % 83) / 82.0,
        )
        for index in range(points)
    ]


def closed_forms_pass(sample_grid: list[tuple[float, float, float]]) -> float:
    """Evaluate the closed forms once over the grid.

    Parameters
    ----------
    sample_grid
        Grid of synthetic inputs.

    Returns
    -------
    float
        Checksum of the results, so the work cannot be optimised away.
    """
    total = 0.0
    for frequency, pressure, field in sample_grid:
        total += resonant_field_t(frequency)
        total += perpendicular_beta(pressure, field)
        total += marginal_pressure_ratio(1.0 + field, 5.0 / 3.0)
        total += induced_current_a(425.0, 1.69, 0.389)
    return total


def record_pass_factory(
    configuration: DeviceConfiguration,
) -> Callable[[list[tuple[float, float, float]]], float]:
    """Return a grid pass that composes and serialises level-0 records.

    Parameters
    ----------
    configuration
        Validated configuration every record is built from.

    Returns
    -------
    callable
        The pass; the pressure of each grid point is the declared
        perpendicular pressure, everything else is the anchor.
    """
    winding = WindingDeclaration(turns=716.0)
    charging = ChargingDeclaration(
        charging_coil_current_a=425.0,
        floating_coil_self_inductance_h=0.389,
        mutual_inductance_h=1.69,
    )
    heating = HeatingDeclaration(frequencies_hz=(2.45e9, 6.4e9), total_power_kw=5.0)

    def record_pass(sample_grid: list[tuple[float, float, float]]) -> float:
        total = 0
        for _frequency, pressure, _field in sample_grid:
            plasma = PlasmaDeclaration(
                peak_perpendicular_pressure_pa=pressure,
                combined_beta=0.21,
                pressure_anisotropy=5.0,
                adiabatic_index=5.0 / 3.0,
                core_to_edge_pressure_ratio=1000.0,
            )
            record = level0_physics(configuration, winding, charging, heating, plasma)
            total += len(record.canonical_bytes())
        return float(total)

    return record_pass


def measure(
    run: Callable[[list[tuple[float, float, float]]], float],
    sample_grid: list[tuple[float, float, float]],
    warmup: int,
    repeats: int,
) -> dict[str, float]:
    """Time repeated grid passes and summarise them.

    Parameters
    ----------
    run
        Grid pass to time.
    sample_grid
        Parameter grid.
    warmup
        Discarded leading passes.
    repeats
        Timed passes.

    Returns
    -------
    dict[str, float]
        Percentiles, mean, min, max in microseconds per grid point and the
        throughput in points per second (P50-based).
    """
    for _ in range(warmup):
        run(sample_grid)
    samples: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter_ns()
        run(sample_grid)
        samples.append((time.perf_counter_ns() - start) / 1e3 / len(sample_grid))
    ordered = sorted(samples)

    def percentile(fraction: float) -> float:
        return ordered[min(len(ordered) - 1, round(fraction * (len(ordered) - 1)))]

    p50 = percentile(0.5)
    return {
        "p50_us_per_point": p50,
        "p95_us_per_point": percentile(0.95),
        "p99_us_per_point": percentile(0.99),
        "mean_us_per_point": statistics.fmean(samples),
        "min_us_per_point": ordered[0],
        "max_us_per_point": ordered[-1],
        "throughput_points_per_s": 1e6 / p50,
    }


def provenance() -> dict[str, Any]:
    """Collect the environment provenance of a run.

    Returns
    -------
    dict[str, Any]
        Interpreter, platform, CPU model, commit and host-load context.
    """
    cpu_model = "unknown"
    with contextlib.suppress(OSError):
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                cpu_model = line.split(":", 1)[1].strip()
                break
    load = "unavailable"
    with contextlib.suppress(OSError):
        load = Path("/proc/loadavg").read_text(encoding="utf-8").split()[0]
    commit = "unknown"
    git = shutil.which("git")
    if git is not None:
        with contextlib.suppress(OSError):
            # A fixed argument vector with the resolved executable; no shell.
            commit = subprocess.run(  # noqa: S603
                [git, "rev-parse", "HEAD"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            ).stdout.strip()
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_model": cpu_model,
        "load_average_1min_at_start": load,
        "commit": commit,
        "isolated_cores": False,
    }


def main(argv: list[str] | None = None) -> int:
    """Run the benchmark command-line interface.

    Parameters
    ----------
    argv
        Argument vector; None reads sys.argv.

    Returns
    -------
    int
        0 on completion.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--points", type=int, default=20_000)
    parser.add_argument("--record-points", type=int, default=2_000)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--label", default="local")
    parser.add_argument("--output", type=Path, default=ROOT / "benchmarks" / "results")
    args = parser.parse_args(argv)
    sample_grid = grid(args.points)
    record_grid = grid(args.record_points)
    record_pass = record_pass_factory(configuration_from_bytes(ANCHOR_CONFIGURATION))
    results: list[dict[str, Any]] = [
        {
            "name": "closed_forms",
            "backend": "python_floor",
            "stats": measure(closed_forms_pass, sample_grid, args.warmup, args.repeats),
            "status": "measured",
        },
        {
            "name": "closed_forms",
            "backend": "rust_native",
            "stats": None,
            "status": NATIVE_STATUS,
        },
        {
            "name": "level0_record",
            "backend": "python_floor",
            "stats": measure(record_pass, record_grid, args.warmup, args.repeats),
            "status": "measured",
        },
        {
            "name": "level0_record",
            "backend": "rust_native",
            "stats": None,
            "status": NATIVE_STATUS,
        },
    ]
    artefact = {
        "schema": SCHEMA,
        "generated_at": datetime.now(UTC).isoformat(),
        "label": args.label,
        "platform": provenance(),
        "parameters": {
            "points": args.points,
            "record_points": args.record_points,
            "warmup": args.warmup,
            "repeats": args.repeats,
        },
        "results": results,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output / f"level0_physics.{args.label}.json"
    target.write_text(
        json.dumps(artefact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"benchmark: wrote {target}")
    for row in results:
        print(f"  {row['name']} {row['backend']}: {row['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
