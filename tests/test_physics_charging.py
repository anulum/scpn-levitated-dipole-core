# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — inductive charging tests

"""The one place a printed number comes back out of a relation.

The source prints two inductances, a charging current and the
ampere-turns that combination produces. Nothing about that is a
restatement: three printed inputs go into a flux-conservation relation
and the fourth printed number comes out.
"""

from __future__ import annotations

import math

import pytest

from physics_fixtures import (
    NOT_REPRODUCED_AMPERE_TURNS_A,
    PRINTED_CHARGING_COIL_MAX_CURRENT_A,
    PRINTED_FLOATING_COIL_CURRENT_A,
    PRINTED_FLOATING_COIL_SELF_INDUCTANCE_H,
    PRINTED_FLOATING_COIL_TURNS,
    PRINTED_MUTUAL_INDUCTANCE_H,
    PRINTED_WORKED_CASE_CHARGING_CURRENT_A,
    PRINTED_WORKED_CASE_FLOATING_COIL_CHARGE_KA_TURNS,
    two_significant_figure_round,
)
from scpn_levitated_dipole_core.errors import DeviceConfigurationError
from scpn_levitated_dipole_core.physics.charging import (
    charge_transfer_ratio,
    current_agreement_ratio,
    induced_current_a,
)

#: Amperes in a kiloampere, for comparing against a printed kA-turn figure.
AMPERES_PER_KILOAMPERE = 1.0e3
#: Decimal exponent of the printed 930 kA-turn figure's leading digit.
CHARGE_EXPONENT = 2


def test_the_worked_case_reproduces_the_printed_ampere_turns() -> None:
    """300 A into the charging coil gives the printed 930 kA-turns.

    This is the family's strongest anchor: two printed inductances and a
    printed charging current, through flux conservation and the printed
    turn count, return a printed result the relation was not fitted to.
    """
    induced = induced_current_a(
        PRINTED_WORKED_CASE_CHARGING_CURRENT_A,
        PRINTED_MUTUAL_INDUCTANCE_H,
        PRINTED_FLOATING_COIL_SELF_INDUCTANCE_H,
    )
    charge_ka_turns = induced * PRINTED_FLOATING_COIL_TURNS / AMPERES_PER_KILOAMPERE
    assert charge_ka_turns == pytest.approx(933.19, rel=1.0e-4)
    assert two_significant_figure_round(
        charge_ka_turns, CHARGE_EXPONENT
    ) == pytest.approx(PRINTED_WORKED_CASE_FLOATING_COIL_CHARGE_KA_TURNS, rel=1.0e-12)


def test_the_transfer_ratio_exceeds_one_because_the_source_says_so() -> None:
    """The mutual inductance is larger than the floating coil's own.

    A validator that had insisted on a coupling coefficient below one
    would have refused the source's own printed pair.
    """
    ratio = charge_transfer_ratio(
        PRINTED_MUTUAL_INDUCTANCE_H, PRINTED_FLOATING_COIL_SELF_INDUCTANCE_H
    )
    assert ratio > 1.0
    assert ratio == pytest.approx(4.344473, rel=1.0e-6)


def test_the_maximum_charge_does_not_return_the_printed_operational_current() -> None:
    """Two printed statements about one current disagree by 1.4 %.

    The printed inductances at the printed maximum charging current give
    1846 A; the source prints the operational current as 1820 A. The
    ratio is reported by the record and gated nowhere, because the
    source does not reconcile them.
    """
    induced = induced_current_a(
        PRINTED_CHARGING_COIL_MAX_CURRENT_A,
        PRINTED_MUTUAL_INDUCTANCE_H,
        PRINTED_FLOATING_COIL_SELF_INDUCTANCE_H,
    )
    assert induced == pytest.approx(1846.4, rel=1.0e-4)
    ratio = current_agreement_ratio(induced, PRINTED_FLOATING_COIL_CURRENT_A)
    assert ratio == pytest.approx(1.0145, rel=1.0e-3)
    assert ratio != 1.0


def test_even_the_maximum_charge_falls_short_of_the_unreproduced_figure() -> None:
    """The most favourable printed combination still misses 1.5 MA-turns.

    Checked at the maximum rather than only at the operational current,
    because a claim that a figure is unreachable has to be tested where
    the numbers are largest.
    """
    induced = induced_current_a(
        PRINTED_CHARGING_COIL_MAX_CURRENT_A,
        PRINTED_MUTUAL_INDUCTANCE_H,
        PRINTED_FLOATING_COIL_SELF_INDUCTANCE_H,
    )
    assert induced * PRINTED_FLOATING_COIL_TURNS < NOT_REPRODUCED_AMPERE_TURNS_A


def test_the_induced_current_is_linear_in_the_charging_current() -> None:
    """Flux conservation is a ratio, not a curve."""
    first = induced_current_a(
        100.0, PRINTED_MUTUAL_INDUCTANCE_H, PRINTED_FLOATING_COIL_SELF_INDUCTANCE_H
    )
    second = induced_current_a(
        200.0, PRINTED_MUTUAL_INDUCTANCE_H, PRINTED_FLOATING_COIL_SELF_INDUCTANCE_H
    )
    assert second == pytest.approx(2.0 * first, rel=1.0e-12)


@pytest.mark.parametrize(
    ("mutual", "own"), [(0.0, 1.0), (1.0, 0.0), (math.nan, 1.0), (1.0, math.inf)]
)
def test_the_transfer_ratio_refuses_either_inductance(
    mutual: float, own: float
) -> None:
    """Both inductances are validated."""
    with pytest.raises(DeviceConfigurationError):
        charge_transfer_ratio(mutual, own)


@pytest.mark.parametrize("bad", [0.0, -1.0, math.nan])
def test_the_induced_current_refuses_a_bad_charging_current(bad: float) -> None:
    """The charging current is validated before the inductances."""
    with pytest.raises(DeviceConfigurationError, match=r"charging_coil_current_a"):
        induced_current_a(
            bad,
            PRINTED_MUTUAL_INDUCTANCE_H,
            PRINTED_FLOATING_COIL_SELF_INDUCTANCE_H,
        )


@pytest.mark.parametrize(
    ("induced", "declared"), [(0.0, 1.0), (1.0, 0.0), (1.0, math.nan)]
)
def test_the_agreement_ratio_refuses_either_input(
    induced: float, declared: float
) -> None:
    """Both currents are validated."""
    with pytest.raises(DeviceConfigurationError):
        current_agreement_ratio(induced, declared)
