# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — parameter model tests

"""Every validation branch of the levitated-dipole parameter model.

All parameter sets in this module are synthetic fixtures; none describes
any real machine.
"""

from __future__ import annotations

import math
from typing import Any

import pytest

from scpn_levitated_dipole_core.errors import DeviceConfigurationError
from scpn_levitated_dipole_core.parameters import (
    STANDARD_GRAVITY_M_S2,
    FloatingCoil,
    LevitationEnvironment,
    require_finite,
    require_positive,
)


def synthetic_coil(**overrides: Any) -> FloatingCoil:
    """Build a valid synthetic floating coil with optional overrides."""
    values: dict[str, Any] = {
        "coil_radius_m": 1.0,
        "coil_current_ka": 1000.0,
        "coil_mass_kg": 500.0,
        "superconducting": True,
    }
    values.update(overrides)
    return FloatingCoil(**values)


def test_require_finite_accepts_and_rejects() -> None:
    """The finite guard returns the value and rejects NaN and infinity."""
    assert require_finite("x", 1.5) == 1.5
    for bad in (math.nan, math.inf, -math.inf):
        with pytest.raises(DeviceConfigurationError, match="x: must be finite"):
            require_finite("x", bad)


def test_require_positive_accepts_and_rejects() -> None:
    """The positive guard returns the value and rejects zero and below."""
    assert require_positive("x", 0.1) == 0.1
    for bad in (0.0, -2.0):
        with pytest.raises(DeviceConfigurationError, match="strictly positive"):
            require_positive("x", bad)
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        require_positive("x", math.nan)


def test_magnetic_moment_and_weight_formulas() -> None:
    """The coil derives its moment and weight from the standard formulas."""
    coil = synthetic_coil()
    assert coil.magnetic_moment_a_m2() == pytest.approx(math.pi * 1.0 * 1.0e6)
    assert coil.weight_n() == pytest.approx(500.0 * STANDARD_GRAVITY_M_S2)


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"coil_radius_m": 0.0}, "coil_radius_m"),
        ({"coil_current_ka": -1.0}, "coil_current_ka"),
        ({"coil_mass_kg": 0.0}, "coil_mass_kg"),
        ({"coil_radius_m": math.nan}, "coil_radius_m"),
        ({"superconducting": False}, "superconducting"),
    ],
)
def test_invalid_coil_is_rejected(overrides: dict[str, Any], fragment: str) -> None:
    """Each floating-coil violation is rejected with its field name."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        synthetic_coil(**overrides)


def test_valid_environment_constructs() -> None:
    """A valid levitation environment constructs unchanged."""
    environment = LevitationEnvironment(field_gradient_t_per_m=0.005)
    assert environment.field_gradient_t_per_m == 0.005


def test_invalid_environment_is_rejected() -> None:
    """Non-positive gradients are rejected."""
    with pytest.raises(DeviceConfigurationError, match="field_gradient_t_per_m"):
        LevitationEnvironment(field_gradient_t_per_m=0.0)
    with pytest.raises(DeviceConfigurationError, match="field_gradient_t_per_m"):
        LevitationEnvironment(field_gradient_t_per_m=math.inf)
