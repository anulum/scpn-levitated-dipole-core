# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — levitated-dipole parameter model

"""Validated parameter objects of a levitated-dipole configuration.

The derived quantities implement two standard magnetostatics results and
nothing more: the magnetic moment of a circular coil ``m = pi R^2 I``
and the axial force on a dipole in a field gradient ``F = m dB/dz``.
Both are rough consistency instruments with documented applicability
bounds (LDX-class layout; D. T. Garnier et al., Fusion Eng. Des. 81
(2006) 2371); no claim about any real machine follows from them.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

from scpn_levitated_dipole_core.errors import DeviceConfigurationError

STANDARD_GRAVITY_M_S2: Final = 9.80665


def require_finite(name: str, value: float) -> float:
    """Return ``value`` when finite, otherwise fail closed.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is NaN or infinite; non-finite input is rejected,
        never clamped.
    """
    if not math.isfinite(value):
        raise DeviceConfigurationError(f"{name}: must be finite, got {value!r}")
    return value


def require_positive(name: str, value: float) -> float:
    """Return ``value`` when finite and strictly positive.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is non-finite or not strictly positive.
    """
    require_finite(name, value)
    if value <= 0.0:
        raise DeviceConfigurationError(
            f"{name}: must be strictly positive, got {value!r}"
        )
    return value


@dataclass(frozen=True, slots=True)
class FloatingCoil:
    """Floating-coil parameters of a levitated dipole.

    Parameters
    ----------
    coil_radius_m
        Mean coil radius ``R`` in metres; strictly positive.
    coil_current_ka
        Persistent coil current ``I`` in kiloamperes; strictly
        positive.
    coil_mass_kg
        Coil mass ``M`` in kilograms; strictly positive.
    superconducting
        Must be true — a persistent, lead-free current is what makes
        levitated-dipole confinement possible.

    Raises
    ------
    DeviceConfigurationError
        If any parameter violates its bound or the coil is not
        superconducting.
    """

    coil_radius_m: float
    coil_current_ka: float
    coil_mass_kg: float
    superconducting: bool

    def __post_init__(self) -> None:
        """Validate the floating-coil invariants.

        Raises
        ------
        DeviceConfigurationError
            If any parameter violates its bound or the coil is not
            superconducting.
        """
        require_positive("coil_radius_m", self.coil_radius_m)
        require_positive("coil_current_ka", self.coil_current_ka)
        require_positive("coil_mass_kg", self.coil_mass_kg)
        if not self.superconducting:
            raise DeviceConfigurationError(
                "superconducting: must be true — levitation requires a "
                "persistent, lead-free coil current"
            )

    def magnetic_moment_a_m2(self) -> float:
        """Magnetic moment of the validated coil.

        Returns
        -------
        float
            ``m = pi R^2 I`` in ampere-square-metres, with the current
            in amperes.
        """
        return math.pi * self.coil_radius_m**2 * (self.coil_current_ka * 1.0e3)

    def weight_n(self) -> float:
        """Weight of the validated coil.

        Returns
        -------
        float
            ``W = M g`` in newtons with standard gravity.
        """
        return self.coil_mass_kg * STANDARD_GRAVITY_M_S2


@dataclass(frozen=True, slots=True)
class LevitationEnvironment:
    """Levitation-field environment at the floating-coil position.

    Parameters
    ----------
    field_gradient_t_per_m
        Axial gradient ``dB/dz`` of the levitation field at the
        floating-coil position, in tesla per metre; strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If the gradient is non-finite or not strictly positive.
    """

    field_gradient_t_per_m: float

    def __post_init__(self) -> None:
        """Validate the levitation-environment invariants.

        Raises
        ------
        DeviceConfigurationError
            If the gradient is non-finite or not strictly positive.
        """
        require_positive("field_gradient_t_per_m", self.field_gradient_t_per_m)
