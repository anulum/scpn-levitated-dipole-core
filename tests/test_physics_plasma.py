# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — plasma relation tests

"""The three plasma relations, and which of them anchors anything.

Exactly one does: the cyclotron resonance, where the source prints a
frequency and the field it resonates at. The beta relations reproduce
the source's own definition and the interchange criterion is a
consistency instrument, and the tests say which is which.
"""

from __future__ import annotations

import math

import pytest

from physics_fixtures import (
    PRINTED_ACHIEVABLE_PRESSURE_RATIO,
    PRINTED_ADIABATIC_INDEX,
    PRINTED_COMBINED_BETA,
    PRINTED_DISPLACED_BETAS,
    PRINTED_HEATING_FREQUENCIES_HZ,
    PRINTED_PEAK_PERPENDICULAR_PRESSURE_PA,
    PRINTED_PRESSURE_ANISOTROPY,
    PRINTED_RESONANT_FIELD_T,
    two_significant_figure_round,
)
from scpn_levitated_dipole_core.errors import DeviceConfigurationError
from scpn_levitated_dipole_core.physics.plasma import (
    anisotropic_beta,
    field_from_perpendicular_beta_t,
    marginal_pressure_ratio,
    perpendicular_beta,
    perpendicular_beta_from_anisotropic,
    require_above,
    required_volume_expansion,
    resonant_field_t,
)

#: Decimal exponent of the printed 0.23 T resonant field's leading digit.
RESONANT_FIELD_EXPONENT = -1


def test_the_printed_resonance_comes_back_out_of_the_relation() -> None:
    """6.4 GHz gives the printed 0.23 T.

    The relation returns 0.228633 T and the source prints 0.23 T, which
    is that value rounded to the two significant figures it carries.
    """
    field = resonant_field_t(PRINTED_HEATING_FREQUENCIES_HZ[1])
    assert field == pytest.approx(0.228633, rel=1.0e-5)
    assert two_significant_figure_round(
        field, RESONANT_FIELD_EXPONENT
    ) == pytest.approx(PRINTED_RESONANT_FIELD_T, rel=1.0e-12)


def test_this_source_rounds_where_a_sibling_family_floors() -> None:
    """A printing convention is a property of a source, not of numbers.

    A sibling family in this group anchors on a volume measured to floor
    on two independent values. Carrying that convention here would have
    produced 0.22 and disagreed with what this source prints.
    """
    field = resonant_field_t(PRINTED_HEATING_FREQUENCIES_HZ[1])
    floored = math.floor(field * 100.0) / 100.0
    assert floored == pytest.approx(0.22, rel=1.0e-12)
    assert floored != PRINTED_RESONANT_FIELD_T


def test_the_lower_frequency_resonates_lower_and_the_source_prints_no_value() -> None:
    """Both frequencies are printed; only one field is.

    The lower resonance is computed and reported and anchors nothing,
    which is the difference this test exists to record.
    """
    low, high = (resonant_field_t(f) for f in PRINTED_HEATING_FREQUENCIES_HZ)
    assert low < high
    assert low == pytest.approx(0.0875235, rel=1.0e-6)


def test_the_resonance_is_linear_in_the_frequency() -> None:
    """The non-relativistic condition is a proportionality."""
    assert resonant_field_t(2.0e9) == pytest.approx(
        2.0 * resonant_field_t(1.0e9), rel=1.0e-12
    )


def test_the_beta_combination_and_its_inverse_round_trip() -> None:
    """The source's own definition, both ways."""
    perpendicular = perpendicular_beta_from_anisotropic(
        PRINTED_COMBINED_BETA, PRINTED_PRESSURE_ANISOTROPY
    )
    assert anisotropic_beta(
        perpendicular, PRINTED_PRESSURE_ANISOTROPY
    ) == pytest.approx(PRINTED_COMBINED_BETA, rel=1.0e-12)
    assert perpendicular == pytest.approx(0.2863636, rel=1.0e-6)
    assert perpendicular > PRINTED_COMBINED_BETA


def test_an_isotropic_plasma_makes_the_combination_the_identity() -> None:
    """At an anisotropy of one the weighting collapses, as it must."""
    assert anisotropic_beta(0.4, 1.0) == pytest.approx(0.4, rel=1.0e-12)


def test_the_field_at_the_pressure_peak_is_derived_and_round_trips() -> None:
    """The source prints no field there; this is what its numbers imply."""
    perpendicular = perpendicular_beta_from_anisotropic(
        PRINTED_COMBINED_BETA, PRINTED_PRESSURE_ANISOTROPY
    )
    field = field_from_perpendicular_beta_t(
        PRINTED_PEAK_PERPENDICULAR_PRESSURE_PA, perpendicular
    )
    assert field == pytest.approx(0.0811319, rel=1.0e-6)
    assert perpendicular_beta(
        PRINTED_PEAK_PERPENDICULAR_PRESSURE_PA, field
    ) == pytest.approx(perpendicular, rel=1.0e-12)


def test_the_printed_displaced_betas_bracket_the_quoted_one() -> None:
    """21 % is one of three the source prints, and the middle one.

    Recording the other two keeps the quoted figure from being read as a
    single determined value when the source presents it as sensitive to
    where the pressure peak is assumed to sit.
    """
    outward, inward = PRINTED_DISPLACED_BETAS
    assert inward < PRINTED_COMBINED_BETA < outward


def test_a_beta_above_one_is_admitted_because_a_dipole_reaches_it() -> None:
    """The source defines its regime as beta above unity.

    A validator with an upper bound of one would have refused the
    condition this family exists to model.
    """
    assert anisotropic_beta(2.0, PRINTED_PRESSURE_ANISOTROPY) > 1.0
    assert perpendicular_beta(1.0e5, 0.1) > 1.0


def test_the_interchange_criterion_and_its_inverse_round_trip() -> None:
    """What expansion a pressure ratio needs, and back again."""
    expansion = required_volume_expansion(
        PRINTED_ACHIEVABLE_PRESSURE_RATIO, PRINTED_ADIABATIC_INDEX
    )
    assert expansion == pytest.approx(63.0957, rel=1.0e-5)
    assert marginal_pressure_ratio(expansion, PRINTED_ADIABATIC_INDEX) == pytest.approx(
        PRINTED_ACHIEVABLE_PRESSURE_RATIO, rel=1.0e-12
    )


def test_a_larger_expansion_supports_a_larger_pressure_ratio() -> None:
    """The criterion is monotone, which is the whole of its content."""
    small = marginal_pressure_ratio(10.0, PRINTED_ADIABATIC_INDEX)
    large = marginal_pressure_ratio(20.0, PRINTED_ADIABATIC_INDEX)
    assert large > small


@pytest.mark.parametrize("bad", [0.0, -1.0, math.nan, math.inf])
def test_the_resonance_refuses_a_bad_frequency(bad: float) -> None:
    """A frequency that is not a frequency."""
    with pytest.raises(DeviceConfigurationError, match=r"frequency_hz"):
        resonant_field_t(bad)


@pytest.mark.parametrize(
    ("pressure", "field"), [(0.0, 1.0), (1.0, 0.0), (math.nan, 1.0)]
)
def test_the_perpendicular_beta_refuses_either_input(
    pressure: float, field: float
) -> None:
    """Both arguments are validated."""
    with pytest.raises(DeviceConfigurationError):
        perpendicular_beta(pressure, field)


@pytest.mark.parametrize(
    ("beta", "anisotropy"), [(0.0, 1.0), (1.0, 0.0), (1.0, math.nan)]
)
def test_the_combination_refuses_either_input(beta: float, anisotropy: float) -> None:
    """Both arguments are validated."""
    with pytest.raises(DeviceConfigurationError):
        anisotropic_beta(beta, anisotropy)


@pytest.mark.parametrize(
    ("beta", "anisotropy"), [(0.0, 1.0), (1.0, 0.0), (math.inf, 1.0)]
)
def test_the_inverse_combination_refuses_either_input(
    beta: float, anisotropy: float
) -> None:
    """Both arguments are validated."""
    with pytest.raises(DeviceConfigurationError):
        perpendicular_beta_from_anisotropic(beta, anisotropy)


@pytest.mark.parametrize(
    ("pressure", "beta"), [(0.0, 1.0), (1.0, 0.0), (1.0, math.nan)]
)
def test_the_field_inversion_refuses_either_input(pressure: float, beta: float) -> None:
    """Both arguments are validated."""
    with pytest.raises(DeviceConfigurationError):
        field_from_perpendicular_beta_t(pressure, beta)


@pytest.mark.parametrize(
    ("expansion", "index"), [(0.0, 1.5), (1.5, 0.0), (math.nan, 1.5)]
)
def test_the_marginal_ratio_refuses_either_input(
    expansion: float, index: float
) -> None:
    """Both arguments are validated."""
    with pytest.raises(DeviceConfigurationError):
        marginal_pressure_ratio(expansion, index)


@pytest.mark.parametrize(("ratio", "index"), [(0.0, 1.5), (1.5, 0.0), (1.5, math.inf)])
def test_the_required_expansion_refuses_either_input(
    ratio: float, index: float
) -> None:
    """Both arguments are validated."""
    with pytest.raises(DeviceConfigurationError):
        required_volume_expansion(ratio, index)


def test_the_floor_validator_admits_above_and_refuses_at_or_below() -> None:
    """A quantity at its floor is a different situation, not a limit."""
    assert require_above("value", 1.5, 1.0) == 1.5
    with pytest.raises(DeviceConfigurationError, match=r"must exceed 1.0"):
        require_above("value", 1.0, 1.0)
    with pytest.raises(DeviceConfigurationError, match=r"must exceed 1.0"):
        require_above("value", 0.5, 1.0)
    with pytest.raises(DeviceConfigurationError, match=r"strictly positive"):
        require_above("value", -1.0, 1.0)
