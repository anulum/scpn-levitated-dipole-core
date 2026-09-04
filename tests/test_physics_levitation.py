# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — levitation force-balance tests

"""Holding the ring up, in the two forms the source leaves open.

The factor-of-two test is the point of this module. It is not asserting
that the source is wrong; it is asserting that the two readings of one
printed sentence differ by exactly two, so that a reader of the record
sees a number instead of a doubt.
"""

from __future__ import annotations

import math

import pytest

from physics_fixtures import (
    DECLARED_FIELD_GRADIENT_T_PER_M,
    DERIVED_AMPERE_TURNS_A,
    DERIVED_COIL_RADIUS_M,
    PRINTED_CURRENT_CENTROID_DIAMETER_M,
    PRINTED_FLOATING_COIL_MASS_KG,
    anchor_configuration,
)
from scpn_levitated_dipole_core.errors import DeviceConfigurationError
from scpn_levitated_dipole_core.parameters import STANDARD_GRAVITY_M_S2
from scpn_levitated_dipole_core.physics.coil import dipole_moment_a_m2
from scpn_levitated_dipole_core.physics.levitation import (
    levitation_margin,
    required_field_gradient_t_per_m,
    required_radial_field_as_printed_t,
    required_radial_field_from_loop_force_t,
)

WEIGHT_N = PRINTED_FLOATING_COIL_MASS_KG * STANDARD_GRAVITY_M_S2


def test_the_two_readings_of_the_printed_relation_differ_by_exactly_two() -> None:
    """The source's symbol is the diameter; the loop balance uses radius.

    Exactly two, in floating point and not approximately, because the
    diameter is exactly twice the radius and everything else in the two
    expressions is identical.
    """
    printed = required_radial_field_as_printed_t(
        WEIGHT_N, PRINTED_CURRENT_CENTROID_DIAMETER_M, DERIVED_AMPERE_TURNS_A
    )
    loop = required_radial_field_from_loop_force_t(
        WEIGHT_N, DERIVED_COIL_RADIUS_M, DERIVED_AMPERE_TURNS_A
    )
    assert loop / printed == 2.0


def test_both_readings_land_in_the_millitesla_range() -> None:
    """Neither reading is absurd, which is why neither can be dismissed.

    If one of the two had come out at a field no levitation coil could
    produce, the ambiguity would have resolved itself. Both are ordinary
    millitesla-scale numbers, so it does not.
    """
    printed = required_radial_field_as_printed_t(
        WEIGHT_N, PRINTED_CURRENT_CENTROID_DIAMETER_M, DERIVED_AMPERE_TURNS_A
    )
    loop = required_radial_field_from_loop_force_t(
        WEIGHT_N, DERIVED_COIL_RADIUS_M, DERIVED_AMPERE_TURNS_A
    )
    assert printed == pytest.approx(9.8636e-4, rel=1.0e-4)
    assert loop == pytest.approx(1.9727e-3, rel=1.0e-4)


def test_the_loop_reading_is_the_textbook_force_balance() -> None:
    """``F = I L B`` with ``L`` the circumference, and nothing else."""
    loop = required_radial_field_from_loop_force_t(
        WEIGHT_N, DERIVED_COIL_RADIUS_M, DERIVED_AMPERE_TURNS_A
    )
    circumference = 2.0 * math.pi * DERIVED_COIL_RADIUS_M
    assert DERIVED_AMPERE_TURNS_A * circumference * loop == pytest.approx(
        WEIGHT_N, rel=1.0e-12
    )


def test_the_required_gradient_balances_the_weight_exactly() -> None:
    """``F = m dB/dz`` inverted, on the winding's moment."""
    moment = dipole_moment_a_m2(DERIVED_COIL_RADIUS_M, DERIVED_AMPERE_TURNS_A)
    gradient = required_field_gradient_t_per_m(WEIGHT_N, moment)
    assert moment * gradient == pytest.approx(WEIGHT_N, rel=1.0e-12)
    assert gradient == pytest.approx(DECLARED_FIELD_GRADIENT_T_PER_M, rel=1.0e-12)


def test_the_anchor_configuration_sits_at_a_margin_of_one() -> None:
    """The declared gradient is derived to balance, not chosen to pass.

    A fixture that declared a comfortable gradient would make the margin
    test pass forever while measuring the choice rather than the
    relation.
    """
    configuration = anchor_configuration()
    moment = dipole_moment_a_m2(DERIVED_COIL_RADIUS_M, DERIVED_AMPERE_TURNS_A)
    force = moment * configuration.levitation.field_gradient_t_per_m
    assert levitation_margin(force, WEIGHT_N) == pytest.approx(1.0, rel=1.0e-12)


def test_the_margin_falls_below_one_when_the_gradient_does() -> None:
    """The margin is a gate that a wrong answer trips."""
    assert levitation_margin(WEIGHT_N / 2.0, WEIGHT_N) == pytest.approx(0.5)
    assert levitation_margin(2.0 * WEIGHT_N, WEIGHT_N) == pytest.approx(2.0)


@pytest.mark.parametrize(
    ("weight", "length", "ampere_turns"),
    [
        (0.0, 1.0, 1.0),
        (1.0, 0.0, 1.0),
        (1.0, 1.0, 0.0),
        (math.nan, 1.0, 1.0),
        (1.0, math.inf, 1.0),
    ],
)
def test_the_printed_form_refuses_every_bad_input(
    weight: float, length: float, ampere_turns: float
) -> None:
    """All three arguments are validated, not only the first."""
    with pytest.raises(DeviceConfigurationError):
        required_radial_field_as_printed_t(weight, length, ampere_turns)


@pytest.mark.parametrize(
    ("weight", "length", "ampere_turns"),
    [(0.0, 1.0, 1.0), (1.0, 0.0, 1.0), (1.0, 1.0, math.nan)],
)
def test_the_loop_form_refuses_every_bad_input(
    weight: float, length: float, ampere_turns: float
) -> None:
    """All three arguments are validated here too."""
    with pytest.raises(DeviceConfigurationError):
        required_radial_field_from_loop_force_t(weight, length, ampere_turns)


@pytest.mark.parametrize(("weight", "moment"), [(0.0, 1.0), (1.0, 0.0)])
def test_the_gradient_refuses_either_input(weight: float, moment: float) -> None:
    """Both arguments are validated."""
    with pytest.raises(DeviceConfigurationError):
        required_field_gradient_t_per_m(weight, moment)


@pytest.mark.parametrize(("force", "weight"), [(0.0, 1.0), (1.0, 0.0)])
def test_the_margin_refuses_either_input(force: float, weight: float) -> None:
    """Both arguments are validated."""
    with pytest.raises(DeviceConfigurationError):
        levitation_margin(force, weight)
