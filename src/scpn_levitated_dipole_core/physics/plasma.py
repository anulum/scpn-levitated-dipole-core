# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — what the plasma is asked to do

"""The three plasma relations the filed source writes down.

**Where the plasma is heated.** Electron cyclotron resonance puts the
absorbing surface where the electron gyrofrequency matches the injected
microwave frequency, ``B = 2 pi m_e f / e``. The source prints a
frequency and the field it resonates at, so this relation is anchored on
two printed numbers and is not merely implemented.

**How much pressure the field is holding.** A dipole plasma is strongly
anisotropic, and the source defines the figure it quotes as
``beta = (2 beta_perp + beta_par) / 3`` with ``beta_perp = 2 mu0 p / B^2``
and a stated perpendicular-to-parallel pressure ratio. Both the combined
beta and the perpendicular pressure are printed; the field at the
pressure peak is **not**, so this module can invert the definition to
report that field and the record names it derived.

**Why a dipole is stable at all.** MHD interchange stability in a dipole
comes from compressibility rather than from average good curvature: a
flux tube that expands enough as it moves outward can support a pressure
gradient without interchanging. The source writes the criterion as
``p_0 / p_sol < (U_sol / U_0)^gamma``. It prints ``gamma`` and states
that the pressure ratio can be made larger than a thousand, but prints
**no flux-tube volume ratio**, so the useful direction is the inverse:
what expansion a stated pressure ratio demands. That number is a
consistency instrument and nothing anchors it.

Nothing here solves an equilibrium, integrates a transport equation or
evaluates a stability spectrum.
"""

from __future__ import annotations

import math

from scpn_levitated_dipole_core.errors import DeviceConfigurationError
from scpn_levitated_dipole_core.parameters import require_positive
from scpn_levitated_dipole_core.physics.constants import (
    ELECTRON_MASS_KG,
    ELEMENTARY_CHARGE_C,
    MU0,
    PI,
)


def require_above(name: str, value: float, floor: float) -> float:
    """Return a value when it is finite and strictly above a floor.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.
    floor
        Bound the value must exceed.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If the value is non-finite, not strictly positive, or does not
        exceed the floor.

    Notes
    -----
    Every plasma quantity this module's callers declare has a floor
    that is not zero: an anisotropy ratio at one is an isotropic
    plasma, an adiabatic index at one is an isothermal gas, and a
    pressure ratio at one is no gradient at all. Each is a different
    physical situation rather than a degenerate case of this one.
    """
    require_positive(name, value)
    if value <= floor:
        raise DeviceConfigurationError(f"{name}: must exceed {floor!r}, got {value!r}")
    return value


def resonant_field_t(frequency_hz: float) -> float:
    """Return the field at which electrons resonate with a frequency.

    Parameters
    ----------
    frequency_hz
        Injected microwave frequency, in hertz; strictly positive.

    Returns
    -------
    float
        ``B = 2 pi m_e f / e`` in tesla, the non-relativistic electron
        cyclotron resonance condition.

    Raises
    ------
    DeviceConfigurationError
        If the frequency leaves its documented interval.

    Notes
    -----
    Non-relativistic. The source's own hot electrons reach tens of
    kiloelectronvolts, where the relativistic mass increase moves the
    resonance; that correction is not carried and the record's
    non-claims say so.
    """
    require_positive("frequency_hz", frequency_hz)
    return 2.0 * PI * ELECTRON_MASS_KG * frequency_hz / ELEMENTARY_CHARGE_C


def perpendicular_beta(pressure_pa: float, field_t: float) -> float:
    """Return the perpendicular beta of a pressure in a field.

    Parameters
    ----------
    pressure_pa
        Perpendicular plasma pressure, in pascals; strictly positive.
    field_t
        Magnetic field, in tesla; strictly positive.

    Returns
    -------
    float
        ``beta_perp = 2 mu0 p / B^2``, dimensionless.

    Raises
    ------
    DeviceConfigurationError
        If either input leaves its documented interval.
    """
    require_positive("pressure_pa", pressure_pa)
    require_positive("field_t", field_t)
    return 2.0 * MU0 * pressure_pa / (field_t * field_t)


def anisotropic_beta(perpendicular: float, anisotropy: float) -> float:
    """Combine perpendicular and parallel betas the way the source does.

    Parameters
    ----------
    perpendicular
        Perpendicular beta; strictly positive.
    anisotropy
        Ratio of perpendicular to parallel pressure; strictly positive.
        The source quotes a value of five for its high-beta discharge.

    Returns
    -------
    float
        ``(2 beta_perp + beta_par) / 3`` with
        ``beta_par = beta_perp / anisotropy``, which is the quantity the
        source reports as its maximum local beta.

    Raises
    ------
    DeviceConfigurationError
        If either input leaves its documented interval.
    """
    require_positive("perpendicular", perpendicular)
    require_positive("anisotropy", anisotropy)
    return perpendicular * (2.0 + 1.0 / anisotropy) / 3.0


def perpendicular_beta_from_anisotropic(combined: float, anisotropy: float) -> float:
    """Invert :func:`anisotropic_beta` for the perpendicular component.

    Parameters
    ----------
    combined
        The combined beta the source quotes; strictly positive.
    anisotropy
        Ratio of perpendicular to parallel pressure; strictly positive.

    Returns
    -------
    float
        The perpendicular beta that produces ``combined``.

    Raises
    ------
    DeviceConfigurationError
        If either input leaves its documented interval.
    """
    require_positive("combined", combined)
    require_positive("anisotropy", anisotropy)
    return combined * 3.0 / (2.0 + 1.0 / anisotropy)


def field_from_perpendicular_beta_t(pressure_pa: float, perpendicular: float) -> float:
    """Return the field a pressure and a perpendicular beta imply.

    Parameters
    ----------
    pressure_pa
        Perpendicular plasma pressure, in pascals; strictly positive.
    perpendicular
        Perpendicular beta; strictly positive.

    Returns
    -------
    float
        ``B = sqrt(2 mu0 p / beta_perp)`` in tesla.

    Raises
    ------
    DeviceConfigurationError
        If either input leaves its documented interval.

    Notes
    -----
    **Derived, never an anchor.** The source prints the pressure and the
    combined beta but no field at the pressure peak, so this returns a
    number the source does not state and the record names it as such.
    """
    require_positive("pressure_pa", pressure_pa)
    require_positive("perpendicular", perpendicular)
    return math.sqrt(2.0 * MU0 * pressure_pa / perpendicular)


def marginal_pressure_ratio(volume_expansion: float, adiabatic_index: float) -> float:
    """Return the pressure ratio a flux-tube expansion can support.

    Parameters
    ----------
    volume_expansion
        Ratio of the edge flux-tube differential volume to the core's;
        strictly positive.
    adiabatic_index
        Ratio of specific heats; strictly positive. The source uses
        five thirds.

    Returns
    -------
    float
        ``(U_sol / U_0)^gamma``, the largest core-to-edge pressure ratio
        the interchange criterion admits.

    Raises
    ------
    DeviceConfigurationError
        If either input leaves its documented interval.
    """
    require_positive("volume_expansion", volume_expansion)
    require_positive("adiabatic_index", adiabatic_index)
    return float(volume_expansion**adiabatic_index)


def required_volume_expansion(pressure_ratio: float, adiabatic_index: float) -> float:
    """Return the flux-tube expansion a pressure ratio demands.

    Parameters
    ----------
    pressure_ratio
        Core-to-edge pressure ratio; strictly positive.
    adiabatic_index
        Ratio of specific heats; strictly positive.

    Returns
    -------
    float
        ``(p_0 / p_sol)^(1 / gamma)``, the inverse of
        :func:`marginal_pressure_ratio`.

    Raises
    ------
    DeviceConfigurationError
        If either input leaves its documented interval.

    Notes
    -----
    This is the direction the filed source leaves open: it prints the
    adiabatic index and states that the pressure ratio can exceed a
    thousand, and prints no flux-tube volume anywhere. The number this
    returns is a consistency instrument and nothing anchors it.
    """
    require_positive("pressure_ratio", pressure_ratio)
    require_positive("adiabatic_index", adiabatic_index)
    return float(pressure_ratio ** (1.0 / adiabatic_index))
