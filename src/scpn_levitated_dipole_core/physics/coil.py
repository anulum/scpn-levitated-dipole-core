# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — the floating coil as a magnet

"""What the floating coil is, as a magnet rather than as an object.

The configuration carries one conductor current and one mean radius. A
multi-turn winding is a magnet of ``N I`` ampere-turns, and every
relation the filed source prints about the levitated ring is written in
those, never in the conductor current alone. **The turn count is the one
thing the configuration does not carry**, so it is declared, and this
module is where the two meet.

**A turn count is not necessarily an integer.** The filed source prints
``8388.5`` turns for the charging coil, so a fractional count is a real
quantity in this family and the validator admits one rather than
demanding a whole number it would then have to explain.

The dipole moment is ``m = pi R^2 (N I)``, the same standard result the
configuration's own single-turn estimate uses, evaluated on the winding
the source describes instead of on one loop.
"""

from __future__ import annotations

from scpn_levitated_dipole_core.parameters import require_positive
from scpn_levitated_dipole_core.physics.constants import (
    AMPERES_PER_KILOAMPERE,
    PI,
)


def require_turns(name: str, value: float) -> float:
    """Return a turn count when finite and strictly positive.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Turn count under validation.

    Returns
    -------
    float
        The validated turn count.

    Raises
    ------
    DeviceConfigurationError
        If the count is non-finite or not strictly positive.

    Notes
    -----
    Deliberately not an integer check. The filed source prints a
    charging-coil turn count of ``8388.5``, so a winding with a half
    turn is something this family's sources actually describe.
    """
    return require_positive(name, value)


def amp_turns_a(turns: float, coil_current_ka: float) -> float:
    """Return the winding's ampere-turns.

    Parameters
    ----------
    turns
        Turn count of the winding; strictly positive.
    coil_current_ka
        Conductor current in kiloamperes; strictly positive.

    Returns
    -------
    float
        ``N I`` in amperes, the quantity the source calls the coil's
        operating current and states in megaampere-turns.

    Raises
    ------
    DeviceConfigurationError
        If either input leaves its documented interval.
    """
    require_turns("turns", turns)
    require_positive("coil_current_ka", coil_current_ka)
    return turns * coil_current_ka * AMPERES_PER_KILOAMPERE


def current_centroid_diameter_m(coil_radius_m: float) -> float:
    """Return the diameter of the current centroid.

    Parameters
    ----------
    coil_radius_m
        Mean radius of the winding's current centroid, in metres;
        strictly positive.

    Returns
    -------
    float
        Twice the radius.

    Notes
    -----
    This exists because the filed source's levitation relation is
    written in the coil's **diameter** and the configuration carries a
    radius. Converting at one named place keeps the factor of two from
    being introduced silently at a call site, which matters here more
    than usual: see :mod:`~scpn_levitated_dipole_core.physics.levitation`
    for a printed relation whose stated symbol makes it differ from the
    standard force balance by exactly that factor.
    """
    require_positive("coil_radius_m", coil_radius_m)
    return 2.0 * coil_radius_m


def dipole_moment_a_m2(coil_radius_m: float, winding_amp_turns_a: float) -> float:
    """Return the magnetic moment of the winding.

    Parameters
    ----------
    coil_radius_m
        Mean radius of the current centroid, in metres; strictly
        positive.
    winding_amp_turns_a
        Ampere-turns of the winding; strictly positive.

    Returns
    -------
    float
        ``m = pi R^2 (N I)`` in ampere-square-metres.

    Raises
    ------
    DeviceConfigurationError
        If either input leaves its documented interval.

    Notes
    -----
    The configuration's own ``magnetic_moment_a_m2`` evaluates the same
    formula on the conductor current, so it is the moment of a **single
    turn**. This one is the moment of the coil. They differ by the turn
    count and neither is wrong; the record reports this one because
    every printed relation about the levitated ring uses ampere-turns.
    """
    require_positive("coil_radius_m", coil_radius_m)
    require_positive("winding_amp_turns_a", winding_amp_turns_a)
    return PI * coil_radius_m**2 * winding_amp_turns_a
