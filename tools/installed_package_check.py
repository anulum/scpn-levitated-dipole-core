# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — installed-wheel contract check

"""Exercise the installed package from outside the source checkout.

The installed-wheel workflow builds the wheel, installs it into a clean
environment and runs this script with ``python -I`` from a directory
outside the checkout. The script fails closed unless the package was
imported from the environment rather than the checkout, ships its
``py.typed`` marker, reports matching installed metadata with the pinned
kernel dependency, and serves the public path from a canonical
configuration document and the declared coil set through level-0 physics
to the tessellated device model. In ``base`` mode the optional CAD
back-end must be absent and a CAD request must raise the documented
``CadUnavailableError``; in ``cad`` mode one B-rep model must be built and
carry its STEP digest.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import sys
from pathlib import Path
from typing import Final

DISTRIBUTION: Final = "scpn-levitated-dipole-core"
PACKAGE: Final = "scpn_levitated_dipole_core"
KERNEL_REQUIREMENT: Final = "scpn-reactor-kernels"
MODES: Final = ("base", "cad")

CONFIGURATION_DOCUMENT: Final = (
    b'{"coil":{"coil_current_ka":1.82,"coil_mass_kg":560.0,"coil_radius_m":0.34,'
    b'"superconducting":true},"identifier":"levitated_dipole","levitation":'
    b'{"field_gradient_t_per_m":0.011604236878290021},"registry":{"digest_sha256":'
    b'"786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090",'
    b'"version":"1.0.0"}}\n'
)
"""The anchor configuration of the test suite, from a filed design paper.

Every declared value below is the same anchor the physics and geometry tests
use. They serve only as a regression anchor for the installed package;
nothing is asserted about the machine the paper describes.
"""

ANNULI: Final[dict[str, dict[str, float]]] = {
    "inner_subcoil": {
        "inner_diameter_m": 0.552,
        "outer_diameter_m": 0.555,
        "height_m": 0.069,
    },
    "middle_subcoil": {
        "inner_diameter_m": 0.555,
        "outer_diameter_m": 0.585,
        "height_m": 0.125,
    },
    "outer_subcoil": {
        "inner_diameter_m": 0.585,
        "outer_diameter_m": 0.764,
        "height_m": 0.162,
    },
    "cryostat": {
        "inner_diameter_m": 0.445,
        "outer_diameter_m": 1.14,
        "height_m": 0.3474999999999999,
    },
    "charging_coil": {
        "inner_diameter_m": 1.3,
        "outer_diameter_m": 1.6,
        "height_m": 0.75,
    },
    "levitation_coil": {
        "inner_diameter_m": 0.41,
        "outer_diameter_m": 1.32,
        "height_m": 0.0177,
    },
}
"""Declared annuli of the anchor coil set, in metres."""

LEVITATION_SEPARATION_M: Final = 1.61
CHARGING_OFFSET_M: Final = 0.0
WINDING_TURNS: Final = 716.0
CHARGING: Final[dict[str, float]] = {
    "charging_coil_current_a": 425.0,
    "floating_coil_self_inductance_h": 0.389,
    "mutual_inductance_h": 1.69,
}
HEATING_FREQUENCIES_HZ: Final = (2.45e9, 6.4e9)
HEATING_TOTAL_POWER_KW: Final = 5.0
PLASMA: Final[dict[str, float]] = {
    "peak_perpendicular_pressure_pa": 750.0,
    "combined_beta": 0.21,
    "pressure_anisotropy": 5.0,
    "adiabatic_index": 5.0 / 3.0,
    "core_to_edge_pressure_ratio": 1000.0,
}
"""Level-0 declarations of the anchor."""

MODEL_SEGMENTS: Final = 32
"""Tessellation segments of the checked tier-G1 model."""


def layout_findings(package_dir: Path, checkout: Path) -> list[str]:
    """Check where the package was imported from and what it ships.

    Parameters
    ----------
    package_dir
        Directory of the imported package.
    checkout
        Source checkout the installed package must not come from.

    Returns
    -------
    list[str]
        Findings; empty when the package lies outside the checkout and
        carries its ``py.typed`` marker.
    """
    return failed(
        [
            (
                not package_dir.resolve().is_relative_to(checkout.resolve()),
                f"{PACKAGE} imported from the checkout: {package_dir}",
            ),
            (
                (package_dir / "py.typed").is_file(),
                f"{PACKAGE} ships no py.typed marker",
            ),
        ]
    )


def failed(checks: list[tuple[bool, str]]) -> list[str]:
    """Return the messages of the checks that did not hold.

    Parameters
    ----------
    checks
        Pairs of an outcome and the finding reported when it is false.

    Returns
    -------
    list[str]
        Findings in check order.
    """
    return [message for holds, message in checks if not holds]


def metadata_findings(
    version: str,
    distribution_name: str = DISTRIBUTION,
    required: str = KERNEL_REQUIREMENT,
) -> list[str]:
    """Check the installed distribution metadata.

    Parameters
    ----------
    version
        ``__version__`` of the imported package.
    distribution_name
        Installed distribution to read.
    required
        Requirement the distribution must declare.

    Returns
    -------
    list[str]
        Findings; empty when the distribution is installed with the same
        version and declares the required dependency.
    """
    try:
        distribution = importlib.metadata.distribution(distribution_name)
    except importlib.metadata.PackageNotFoundError:
        return [f"{distribution_name} is not installed"]
    requirements = distribution.requires or []
    return failed(
        [
            (
                distribution.version == version,
                f"installed version {distribution.version} != package {version}",
            ),
            (
                any(item.startswith(required) for item in requirements),
                f"{distribution_name} does not require {required}",
            ),
        ]
    )


def public_path_findings(mode: str) -> list[str]:
    """Serve the public path through the installed package.

    Parameters
    ----------
    mode
        ``base`` when the CAD back-end must be absent, ``cad`` when it must
        build a model.

    Returns
    -------
    list[str]
        Findings; empty when every promised capability of the mode works
        and the absent one fails as documented.
    """
    from scpn_reactor_kernels.errors import CadUnavailableError

    from scpn_levitated_dipole_core import configuration_from_bytes
    from scpn_levitated_dipole_core.geometry import (
        STATE_LEVITATED,
        Annulus,
        CoilSet,
        build_model,
    )
    from scpn_levitated_dipole_core.geometry.cad import build_cad_model
    from scpn_levitated_dipole_core.physics import (
        ChargingDeclaration,
        HeatingDeclaration,
        PlasmaDeclaration,
        WindingDeclaration,
        level0_physics,
    )

    configuration = configuration_from_bytes(CONFIGURATION_DOCUMENT)
    coils = CoilSet(
        inner_subcoil=Annulus(**ANNULI["inner_subcoil"]),
        middle_subcoil=Annulus(**ANNULI["middle_subcoil"]),
        outer_subcoil=Annulus(**ANNULI["outer_subcoil"]),
        cryostat=Annulus(**ANNULI["cryostat"]),
        charging_coil=Annulus(**ANNULI["charging_coil"]),
        levitation_coil=Annulus(**ANNULI["levitation_coil"]),
        levitation_separation_m=LEVITATION_SEPARATION_M,
        charging_offset_m=CHARGING_OFFSET_M,
    )
    declarations = (
        WindingDeclaration(turns=WINDING_TURNS),
        ChargingDeclaration(**CHARGING),
        HeatingDeclaration(
            frequencies_hz=HEATING_FREQUENCIES_HZ,
            total_power_kw=HEATING_TOTAL_POWER_KW,
        ),
        PlasmaDeclaration(**PLASMA),
    )
    record = level0_physics(configuration, *declarations).canonical_bytes()
    model = build_model(configuration, coils, STATE_LEVITATED, MODEL_SEGMENTS)
    findings = failed(
        [
            (
                configuration.canonical_bytes() == CONFIGURATION_DOCUMENT,
                "configuration did not round-trip byte for byte",
            ),
            (
                record
                == level0_physics(configuration, *declarations).canonical_bytes(),
                "level-0 record is not deterministic",
            ),
            (
                model.canonical_bytes()
                == build_model(
                    configuration, coils, STATE_LEVITATED, MODEL_SEGMENTS
                ).canonical_bytes(),
                "tessellated model is not deterministic",
            ),
        ]
    )
    if mode == "base":
        try:
            build_cad_model(configuration, coils, STATE_LEVITATED)
        except CadUnavailableError:
            return findings
        return [*findings, "CAD back-end present in the base environment"]
    cad = build_cad_model(configuration, coils, STATE_LEVITATED)
    return findings + failed(
        [
            (len(cad.step_bytes_sha256) == 64, "CAD model carries no STEP digest"),
            (
                cad.configuration_digest_sha256 == configuration.digest_sha256(),
                "CAD model is bound to another configuration",
            ),
        ]
    )


def check_installed(mode: str, checkout: Path) -> list[str]:
    """Run every installed-package check for one environment.

    Parameters
    ----------
    mode
        One of :data:`MODES`.
    checkout
        Source checkout the package must not be imported from.

    Returns
    -------
    list[str]
        All findings; empty when the installed package meets its contract.
    """
    package = importlib.import_module(PACKAGE)
    package_dir = Path(package.__file__ or "").parent
    findings = layout_findings(package_dir, checkout)
    findings += metadata_findings(str(package.__version__))
    findings += public_path_findings(mode)
    return findings


def report(mode: str, findings: list[str]) -> int:
    """Print the outcome of one environment and return its exit status.

    Parameters
    ----------
    mode
        Environment mode that was checked.
    findings
        Findings of :func:`check_installed`.

    Returns
    -------
    int
        ``0`` without findings, else ``1``.
    """
    if findings:
        print(f"installed-package: FAIL {mode}", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding}", file=sys.stderr)
        return 1
    print(f"installed-package: PASS {mode}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the installed-package check from the command line.

    Parameters
    ----------
    argv
        Argument vector; ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        ``0`` when the installed package meets its contract, else ``1``.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=MODES, required=True)
    parser.add_argument("--checkout", type=Path, required=True)
    args = parser.parse_args(argv)
    return report(args.mode, check_installed(args.mode, args.checkout))


if __name__ == "__main__":
    sys.exit(main())
