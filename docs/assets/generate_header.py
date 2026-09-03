# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — repository header artwork generator

"""Generate the three README header images (1280x640) for this repository.

Every image is original generated artwork derived from this repository's
own domain surface — the floating superconducting ring in its closed
dipole field, the levitation force balance the configuration model
checks, and the closed-field map. The ring field is computed from a
two-dimensional coil-section current pair, not hand-drawn. The
right-hand text panel states only facts backed by the repository
itself.

Outputs (written next to this script):

- ``repo_header.png`` — the floating ring in its computed dipole field
  with the levitation coil above (used by ``README.md``).
- ``repo_header_force_balance.png`` — the levitation force versus coil
  weight gate.
- ``repo_header_closed_field.png`` — the dense closed-field map.

Generation-time tooling only: requires ``numpy`` and ``matplotlib``,
which are deliberately not part of the pinned development lock. Run as
``python3 docs/assets/generate_header.py`` from the repository root.
The output is deterministic (fixed geometry, no random input).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

OUT_DIR = Path(__file__).resolve().parent

BG = "#00050a"
CYAN = "#00ccff"
MAGENTA = "#ff00ff"
STEEL = "#334466"
PROBE = "#66aaff"
RED = "#ff3366"
GREEN = "#3ddc84"

WIDTH_IN, HEIGHT_IN, DPI = 12.8, 6.4, 100

TITLE_METRICS: list[tuple[str, str]] = [
    ("Device Configuration", "levitated_dipole · closed dipole field"),
    ("Hard Invariant", "superconducting floating coil (LDX-class)"),
    ("Levitation Gate", "force below coil weight flagged"),
    ("Diagnostics & Clocks", "fail-closed vs pinned SPO catalogue"),
    ("Plan Envelope", "v1.1.0 · synthetic · review-only"),
    ("Quality Gates", "100% branch cov · mypy --strict"),
]


def _pyplot() -> Any:
    """Return pyplot configured for headless Agg rendering."""
    import matplotlib as mpl

    mpl.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _glow_cmap() -> Any:
    """Build the family glow colormap (deep navy to cyan)."""
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(
        "scpn_glow",
        ["#00050a", "#001428", "#002d55", "#005588", "#0088bb", "#00ccff"],
    )


def ring_dipole_field(
    nx: int,
    nz: int,
    span_x: float,
    span_z: float,
    ring_radius: float = 0.85,
    z_centre: float = 0.0,
) -> tuple[Any, Any, Any, Any]:
    """Return the poloidal-section field of a coil ring.

    Two opposite line currents at the ring's section positions give the
    closed dipole topology of the poloidal plane.
    """
    x = np.linspace(-span_x, span_x, nx)
    z = np.linspace(-span_z, span_z, nz)
    mesh_x, mesh_z = np.meshgrid(x, z)
    b_x = np.zeros_like(mesh_x)
    b_z = np.zeros_like(mesh_z)
    for x_centre, sign in ((-ring_radius, +1.0), (+ring_radius, -1.0)):
        dx, dz = mesh_x - x_centre, mesh_z - z_centre
        r2 = dx**2 + dz**2 + 0.015
        b_x += -sign * dz / r2
        b_z += +sign * dx / r2
    return mesh_x, mesh_z, b_x, b_z


def _text_panel(fig: Any, subtitle: str) -> None:
    """Draw the family right-hand text panel onto ``fig``."""
    ax = fig.add_axes([0.62, 0.0, 0.38, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(
        0.08,
        0.84,
        "SCPN",
        color="white",
        fontsize=36,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.745,
        "LEVITATED",
        color="white",
        fontsize=26,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.695,
        "DIPOLE CORE",
        color="white",
        fontsize=26,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.635,
        subtitle,
        color=CYAN,
        fontsize=11,
        fontfamily="monospace",
        alpha=0.85,
    )
    ax.plot([0.08, 0.85], [0.595, 0.595], color=STEEL, lw=0.8, alpha=0.5)
    y = 0.535
    for label, value in TITLE_METRICS:
        ax.text(
            0.08,
            y,
            f"▸ {label}",
            color="#6688aa",
            fontsize=9,
            fontfamily="monospace",
            alpha=0.9,
        )
        ax.text(
            0.10,
            y - 0.030,
            value,
            color="#99bbdd",
            fontsize=8,
            fontfamily="monospace",
            alpha=0.7,
        )
        y -= 0.072
    ax.text(
        0.08,
        0.06,
        "© 1996–2026 Miroslav Šotek",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.6,
    )
    ax.text(
        0.08,
        0.03,
        "anulum.li | AGPL-3.0",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.5,
    )


def _art_axes(fig: Any) -> Any:
    """Return the borderless left-hand art axes of ``fig``."""
    ax = fig.add_axes([0.0, 0.0, 0.68, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def _save(fig: Any, plt: Any, name: str) -> None:
    """Save ``fig`` to ``name`` inside the assets directory and close it."""
    target = OUT_DIR / name
    fig.savefig(target, dpi=DPI, facecolor=BG, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    print(f"generated {target}")


def generate_floating_ring() -> None:
    """Generate ``repo_header.png``: the floating ring in its field."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(-2.9, 2.9)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal")

    mesh_x, mesh_z, b_x, b_z = ring_dipole_field(
        320, 200, 2.9, 1.45, ring_radius=0.85, z_centre=-0.15
    )
    magnitude = np.sqrt(b_x**2 + b_z**2)
    ax.contourf(
        mesh_x,
        mesh_z,
        np.log10(magnitude + 2e-2),
        levels=30,
        cmap=_glow_cmap(),
        alpha=0.8,
    )
    ax.streamplot(
        mesh_x,
        mesh_z,
        b_x,
        b_z,
        color=CYAN,
        linewidth=0.6,
        density=1.2,
        arrowsize=0.0,
    )

    theta = np.linspace(0.0, 2.0 * np.pi, 60)
    for coil_x, mark in ((-0.85, "x"), (0.85, "o")):
        ax.plot(
            coil_x,
            -0.15,
            mark,
            color=MAGENTA,
            ms=11,
            mew=2.4,
            alpha=0.95,
        )
        ax.plot(
            coil_x + 0.16 * np.cos(theta),
            -0.15 + 0.16 * np.sin(theta),
            color=MAGENTA,
            lw=1.4,
            alpha=0.85,
        )
    ax.text(
        0,
        -0.5,
        "floating SC coil",
        color=MAGENTA,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    ax.add_patch(
        plt.Rectangle(
            (-0.42, 1.18),
            0.84,
            0.16,
            fill=False,
            ec=GREEN,
            lw=1.6,
            alpha=0.9,
        )
    )
    ax.annotate(
        "",
        xy=(0, 0.35),
        xytext=(0, 1.14),
        arrowprops={
            "arrowstyle": "-",
            "color": GREEN,
            "lw": 0.8,
            "alpha": 0.4,
            "linestyle": ":",
        },
    )
    ax.text(
        0.52,
        1.22,
        "levitation coil",
        color=GREEN,
        fontsize=7.5,
        fontfamily="monospace",
        alpha=0.9,
    )

    ax.text(
        0,
        -1.36,
        "closed dipole field · no ends, no interlinked coil (LDX-class)",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "A Ring Afloat In Its Own Field")
    _save(fig, plt, "repo_header.png")


def generate_force_balance() -> None:
    """Generate ``repo_header_force_balance.png``: the levitation gate."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-3.2, 3.2)

    ax.add_patch(
        plt.Rectangle(
            (3.4, 2.35),
            3.2,
            0.35,
            fill=False,
            ec=GREEN,
            lw=1.8,
            alpha=0.9,
        )
    )
    ax.text(
        5.0,
        2.95,
        "levitation coil",
        color=GREEN,
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    theta = np.linspace(0.0, 2.0 * np.pi, 60)
    for coil_x, mark in ((3.9, "x"), (6.1, "o")):
        ax.plot(coil_x, 0.0, mark, color=MAGENTA, ms=11, mew=2.4, alpha=0.95)
        ax.plot(
            coil_x + 0.24 * np.cos(theta),
            0.24 * np.sin(theta),
            color=MAGENTA,
            lw=1.5,
            alpha=0.9,
        )
    ax.plot([3.9, 6.1], [0, 0], color=MAGENTA, lw=0.6, alpha=0.35)
    ax.text(
        5.0,
        0.5,
        "floating SC coil · persistent current",
        color=MAGENTA,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    ax.annotate(
        "",
        xy=(5.0, 1.9),
        xytext=(5.0, 0.75),
        arrowprops={"arrowstyle": "->", "color": GREEN, "lw": 2.2, "alpha": 0.95},
    )
    ax.text(
        5.18,
        1.35,
        "F_levitation",
        color=GREEN,
        fontsize=9,
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.annotate(
        "",
        xy=(5.0, -1.9),
        xytext=(5.0, -0.75),
        arrowprops={"arrowstyle": "->", "color": RED, "lw": 2.2, "alpha": 0.95},
    )
    ax.text(
        5.18,
        -1.45,
        "m · g",
        color=RED,
        fontsize=9,
        fontfamily="monospace",
        alpha=0.95,
    )

    ax.text(
        5.0,
        -2.55,
        "levitation force below the coil weight is FLAGGED",
        color="#ff8899",
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        5.0,
        -2.95,
        "superconducting requirement is HARD · Garnier et al., FED 81 (2006) 2371",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Levitation As A Checked Balance")
    _save(fig, plt, "repo_header_force_balance.png")


def generate_closed_field() -> None:
    """Generate ``repo_header_closed_field.png``: the closed-field map."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(-2.9, 2.9)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal")

    mesh_x, mesh_z, b_x, b_z = ring_dipole_field(
        360, 220, 2.9, 1.45, ring_radius=0.55, z_centre=0.0
    )
    magnitude = np.sqrt(b_x**2 + b_z**2)
    ax.contourf(
        mesh_x,
        mesh_z,
        np.log10(magnitude + 1e-2),
        levels=40,
        cmap=_glow_cmap(),
        alpha=0.9,
    )
    ax.streamplot(
        mesh_x,
        mesh_z,
        b_x,
        b_z,
        color=CYAN,
        linewidth=0.55,
        density=1.6,
        arrowsize=0.0,
    )
    for coil_x, mark in ((-0.55, "x"), (0.55, "o")):
        ax.plot(coil_x, 0, mark, color=MAGENTA, ms=9, mew=2.0, alpha=0.95)

    ax.text(
        -2.75,
        1.22,
        "every field line closes on itself",
        color=PROBE,
        fontsize=8.5,
        fontfamily="monospace",
        alpha=0.9,
    )
    ax.text(
        0,
        -1.36,
        "planetary-magnetosphere confinement geometry · declared, "
        "validated, never claimed real",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Closed Field, Nothing To Interlink")
    _save(fig, plt, "repo_header_closed_field.png")


if __name__ == "__main__":
    generate_floating_ring()
    generate_force_balance()
    generate_closed_field()
