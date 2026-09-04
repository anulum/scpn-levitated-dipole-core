# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — holding the ring up

"""What it takes to hold the floating ring against its own weight.

**Two forms of one relation are carried here, and the reason is a
discrepancy in the source rather than a choice of ours.**

The filed source prints the required radial field as

    B_r = M_d g / (2 pi a I_d)

and states in the same sentence that ``a`` is the **average diameter of
the coil**. The standard force balance on a current loop in a radial
field is ``F = I L B_r`` with ``L`` the loop's circumference, giving
``B_r = M g / (2 pi R I)`` with ``R`` the **radius**. Since the diameter
is twice the radius, the printed relation read literally returns exactly
**half** what the loop balance requires.

Both are computed and reported, the ratio between them is reported, and
**neither is adjusted**. The source prints no value of ``B_r`` anywhere,
so nothing in this family anchors either form; what can be said is what
each gives and that they differ by a factor of two. Deciding which the
authors meant would be reading intent into a printed sentence, and the
record's non-claims say so.

The axial relation is separate and has no such ambiguity: a magnetic
moment in a field gradient feels ``F = m dB/dz``, which is what the
configuration already uses to report a levitation force. This module
inverts it to say what gradient the weight actually requires.
"""

from __future__ import annotations

from scpn_levitated_dipole_core.parameters import require_positive
from scpn_levitated_dipole_core.physics.constants import PI


def required_radial_field_as_printed_t(
    weight_n: float, centroid_diameter_m: float, winding_amp_turns_a: float
) -> float:
    """Return the radial field the source's relation gives, as printed.

    Parameters
    ----------
    weight_n
        Weight of the floating coil, in newtons; strictly positive.
    centroid_diameter_m
        Diameter of the current centroid, in metres; strictly positive.
        This is the symbol the source names, and naming it here is what
        keeps the discrepancy visible.
    winding_amp_turns_a
        Ampere-turns of the winding; strictly positive.

    Returns
    -------
    float
        ``M g / (2 pi a I)`` in tesla, with ``a`` the diameter exactly
        as the source's sentence defines it.

    Raises
    ------
    DeviceConfigurationError
        If any input leaves its documented interval.
    """
    require_positive("weight_n", weight_n)
    require_positive("centroid_diameter_m", centroid_diameter_m)
    require_positive("winding_amp_turns_a", winding_amp_turns_a)
    return weight_n / (2.0 * PI * centroid_diameter_m * winding_amp_turns_a)


def required_radial_field_from_loop_force_t(
    weight_n: float, coil_radius_m: float, winding_amp_turns_a: float
) -> float:
    """Return the radial field the loop force balance gives.

    Parameters
    ----------
    weight_n
        Weight of the floating coil, in newtons; strictly positive.
    coil_radius_m
        Mean radius of the current centroid, in metres; strictly
        positive.
    winding_amp_turns_a
        Ampere-turns of the winding; strictly positive.

    Returns
    -------
    float
        ``M g / (2 pi R I)`` in tesla, from ``F = I L B_r`` with ``L``
        the loop circumference.

    Raises
    ------
    DeviceConfigurationError
        If any input leaves its documented interval.

    Notes
    -----
    This is not a correction of the printed relation. It is the standard
    result stated alongside it so that a reader can see both, and the
    record reports the ratio rather than a verdict.
    """
    require_positive("weight_n", weight_n)
    require_positive("coil_radius_m", coil_radius_m)
    require_positive("winding_amp_turns_a", winding_amp_turns_a)
    return weight_n / (2.0 * PI * coil_radius_m * winding_amp_turns_a)


def required_field_gradient_t_per_m(
    weight_n: float, dipole_moment_a_m2: float
) -> float:
    """Return the axial gradient that would just support the coil.

    Parameters
    ----------
    weight_n
        Weight of the floating coil, in newtons; strictly positive.
    dipole_moment_a_m2
        Magnetic moment of the winding; strictly positive.

    Returns
    -------
    float
        ``dB/dz = M g / m`` in tesla per metre, from ``F = m dB/dz``.

    Raises
    ------
    DeviceConfigurationError
        If either input leaves its documented interval.
    """
    require_positive("weight_n", weight_n)
    require_positive("dipole_moment_a_m2", dipole_moment_a_m2)
    return weight_n / dipole_moment_a_m2


def levitation_margin(levitation_force_n: float, weight_n: float) -> float:
    """Return the levitation force as a multiple of the weight.

    Parameters
    ----------
    levitation_force_n
        Axial force available on the floating coil, in newtons;
        strictly positive.
    weight_n
        Weight of the floating coil, in newtons; strictly positive.

    Returns
    -------
    float
        ``F / W``. Values below one mean the declared environment does
        not hold the coil up; the configuration already reports that as
        an advisory finding and this is the number behind it.

    Raises
    ------
    DeviceConfigurationError
        If either input leaves its documented interval.
    """
    require_positive("levitation_force_n", levitation_force_n)
    require_positive("weight_n", weight_n)
    return levitation_force_n / weight_n
