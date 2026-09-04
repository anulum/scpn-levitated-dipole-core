# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — floating-coil magnet tests

"""The floating coil as a magnet: ampere-turns, diameter and moment."""

from __future__ import annotations

import math

import pytest

from physics_fixtures import (
    DERIVED_AMPERE_TURNS_A,
    DERIVED_COIL_CURRENT_KA,
    DERIVED_COIL_RADIUS_M,
    NOT_REPRODUCED_AMPERE_TURNS_A,
    PRINTED_CURRENT_CENTROID_DIAMETER_M,
    PRINTED_FLOATING_COIL_TURNS,
    PRINTED_OPERATING_CURRENT_FLOOR_A,
    anchor_configuration,
)
from scpn_levitated_dipole_core.errors import DeviceConfigurationError
from scpn_levitated_dipole_core.physics.coil import (
    amp_turns_a,
    current_centroid_diameter_m,
    dipole_moment_a_m2,
    require_turns,
)


def test_the_printed_turns_and_current_give_the_printed_operating_current() -> None:
    """The source calls the ampere-turns the coil's operating current.

    It prints that figure only as a floor, ``>1.2 MA``, and the printed
    turn count with the printed conductor current clears it.
    """
    ampere_turns = amp_turns_a(PRINTED_FLOATING_COIL_TURNS, DERIVED_COIL_CURRENT_KA)
    assert ampere_turns == pytest.approx(DERIVED_AMPERE_TURNS_A, rel=1.0e-12)
    assert ampere_turns > PRINTED_OPERATING_CURRENT_FLOOR_A


def test_the_printed_one_and_a_half_megaampere_turns_is_not_reproduced() -> None:
    """A second printed figure for the same quantity does not come out.

    The source says the conductor carries "over 1.5 MA turns". Its own
    printed operational current and turn count give 1.303 MA-turns. The
    figure anchors nothing and adjusting an input until it appeared was
    available and is not what happened.
    """
    ampere_turns = amp_turns_a(PRINTED_FLOATING_COIL_TURNS, DERIVED_COIL_CURRENT_KA)
    assert ampere_turns < NOT_REPRODUCED_AMPERE_TURNS_A
    assert ampere_turns == pytest.approx(1.30312e6, rel=1.0e-5)


def test_the_diameter_is_twice_the_radius_and_is_the_printed_one() -> None:
    """The configuration carries a radius; the source prints a diameter."""
    diameter = current_centroid_diameter_m(DERIVED_COIL_RADIUS_M)
    assert diameter == pytest.approx(PRINTED_CURRENT_CENTROID_DIAMETER_M, rel=1.0e-15)
    assert diameter == 2.0 * DERIVED_COIL_RADIUS_M


def test_the_winding_moment_exceeds_the_single_turn_one_by_the_turn_count() -> None:
    """Two moments, one formula, and the turn count between them.

    The configuration's own estimate is a single loop because it has no
    turn count to use. This is the number that difference amounts to.
    """
    configuration = anchor_configuration()
    single = configuration.coil.magnetic_moment_a_m2()
    winding = dipole_moment_a_m2(DERIVED_COIL_RADIUS_M, DERIVED_AMPERE_TURNS_A)
    assert winding / single == pytest.approx(PRINTED_FLOATING_COIL_TURNS, rel=1.0e-12)


def test_the_winding_moment_is_the_standard_loop_result() -> None:
    """``m = pi R^2 (N I)`` and nothing beyond it."""
    assert dipole_moment_a_m2(
        DERIVED_COIL_RADIUS_M, DERIVED_AMPERE_TURNS_A
    ) == pytest.approx(
        math.pi * DERIVED_COIL_RADIUS_M**2 * DERIVED_AMPERE_TURNS_A, rel=0.0
    )


def test_a_fractional_turn_count_is_admitted() -> None:
    """The source prints 8388.5 turns for the charging coil.

    A validator that demanded a whole number would refuse a winding this
    family's own source describes.
    """
    assert require_turns("turns", 8388.5) == 8388.5
    assert amp_turns_a(8388.5, 1.0) == pytest.approx(8388.5e3, rel=1.0e-12)


@pytest.mark.parametrize("bad", [0.0, -1.0, math.nan, math.inf])
def test_a_non_positive_turn_count_is_refused(bad: float) -> None:
    """A winding with no turns is not a winding."""
    with pytest.raises(DeviceConfigurationError, match=r"turns"):
        require_turns("turns", bad)


@pytest.mark.parametrize(
    ("turns", "current"),
    [(0.0, 1.0), (1.0, 0.0), (math.nan, 1.0), (1.0, math.inf)],
)
def test_amp_turns_refuses_either_input(turns: float, current: float) -> None:
    """Both arguments are validated, not only the first."""
    with pytest.raises(DeviceConfigurationError):
        amp_turns_a(turns, current)


@pytest.mark.parametrize("bad", [0.0, -0.5, math.nan])
def test_the_diameter_refuses_a_non_positive_radius(bad: float) -> None:
    """A coil of no radius has no centroid."""
    with pytest.raises(DeviceConfigurationError, match=r"coil_radius_m"):
        current_centroid_diameter_m(bad)


@pytest.mark.parametrize(
    ("radius", "ampere_turns"), [(0.0, 1.0), (1.0, 0.0), (1.0, math.nan)]
)
def test_the_moment_refuses_either_input(radius: float, ampere_turns: float) -> None:
    """Both arguments are validated."""
    with pytest.raises(DeviceConfigurationError):
        dipole_moment_a_m2(radius, ampere_turns)
