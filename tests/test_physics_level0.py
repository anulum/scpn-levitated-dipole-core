# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — level-0 record tests

"""The four declarations, the composed record, and what it refuses."""

from __future__ import annotations

import json
import math

import pytest

from physics_fixtures import (
    PRINTED_CHARGING_COIL_MAX_CURRENT_A,
    PRINTED_COMBINED_BETA,
    PRINTED_CURRENT_CENTROID_DIAMETER_M,
    PRINTED_FLOATING_COIL_CURRENT_A,
    PRINTED_FLOATING_COIL_MASS_KG,
    PRINTED_FLOATING_COIL_SELF_INDUCTANCE_H,
    PRINTED_FLOATING_COIL_TURNS,
    PRINTED_HEATING_FREQUENCIES_HZ,
    PRINTED_MUTUAL_INDUCTANCE_H,
    PRINTED_OPERATING_CURRENT_FLOOR_A,
    PRINTED_PRESSURE_ANISOTROPY,
    PRINTED_RESONANT_FIELD_T,
    PRINTED_TOTAL_HEATING_POWER_KW,
    anchor_charging,
    anchor_configuration,
    anchor_heating,
    anchor_plasma,
    anchor_winding,
    two_significant_figure_round,
)
from scpn_levitated_dipole_core.errors import DeviceConfigurationError
from scpn_levitated_dipole_core.physics.level0 import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    ChargingDeclaration,
    HeatingDeclaration,
    Level0Physics,
    PlasmaDeclaration,
    WindingDeclaration,
    declared_conductor_current_a,
    level0_physics,
)

#: Decimal exponent of the printed 0.23 T resonant field's leading digit.
RESONANT_FIELD_EXPONENT = -1


def anchor_record() -> Level0Physics:
    """Compose the record every anchor test reads.

    Returns
    -------
    Level0Physics
        The record built from the filed source's printed values.
    """
    return level0_physics(
        anchor_configuration(),
        anchor_winding(),
        anchor_charging(),
        anchor_heating(),
        anchor_plasma(),
    )


# --- What the record recovers from the source ---


def test_the_record_recovers_the_printed_resonant_field() -> None:
    """One of the two frequencies has a printed field, and it comes back."""
    fields = anchor_record().operating_point.resonant_fields_t
    assert len(fields) == len(PRINTED_HEATING_FREQUENCIES_HZ)
    assert two_significant_figure_round(
        fields[1], RESONANT_FIELD_EXPONENT
    ) == pytest.approx(PRINTED_RESONANT_FIELD_T, rel=1.0e-12)


def test_the_record_carries_the_printed_diameter_and_operating_current() -> None:
    """Two printed quantities, one converted and one composed."""
    operating = anchor_record().operating_point
    assert operating.current_centroid_diameter_m == pytest.approx(
        PRINTED_CURRENT_CENTROID_DIAMETER_M, rel=1.0e-15
    )
    assert operating.winding_amp_turns_a > PRINTED_OPERATING_CURRENT_FLOOR_A


def test_the_record_states_the_two_readings_differ_by_exactly_two() -> None:
    """The factor is a field of the record, not a remark in a docstring."""
    assert anchor_record().operating_point.radial_field_form_ratio == 2.0


def test_the_record_sits_at_a_levitation_margin_of_one() -> None:
    """The declared gradient is derived to balance the printed weight."""
    operating = anchor_record().operating_point
    assert operating.levitation_margin == pytest.approx(1.0, rel=1.0e-12)
    assert operating.coil_weight_n == pytest.approx(
        PRINTED_FLOATING_COIL_MASS_KG * 9.80665, rel=1.0e-12
    )


def test_the_two_levitation_forces_differ_by_the_turn_count() -> None:
    """The configuration's estimate is a single turn and the record says so.

    Reported rather than corrected: the configuration cannot do better,
    because it carries no turn count.
    """
    operating = anchor_record().operating_point
    assert (
        operating.winding_levitation_force_n / operating.single_turn_levitation_force_n
    ) == pytest.approx(PRINTED_FLOATING_COIL_TURNS, rel=1.0e-12)
    assert operating.single_turn_levitation_force_n < operating.coil_weight_n


def test_the_record_reports_the_current_disagreement_without_gating_it() -> None:
    """The induced and the declared current are both printed and differ."""
    operating = anchor_record().operating_point
    assert operating.declared_conductor_current_a == pytest.approx(
        PRINTED_FLOATING_COIL_CURRENT_A, rel=1.0e-12
    )
    assert operating.induced_to_declared_current_ratio == pytest.approx(
        1.0145, rel=1.0e-3
    )
    assert operating.induced_conductor_current_a > PRINTED_FLOATING_COIL_CURRENT_A


def test_the_record_reports_a_derived_field_at_the_pressure_peak() -> None:
    """The source prints no field there and the non-claims say so."""
    operating = anchor_record().operating_point
    assert operating.field_at_pressure_peak_t == pytest.approx(0.0811319, rel=1.0e-6)
    assert operating.perpendicular_beta > PRINTED_COMBINED_BETA


def test_the_record_reports_the_flux_tube_expansion_the_source_omits() -> None:
    """A consistency instrument, named one in the non-claims."""
    assert anchor_record().operating_point.required_volume_expansion == (
        pytest.approx(63.0957, rel=1.0e-5)
    )


def test_the_declared_current_conversion_happens_once() -> None:
    """Kiloamperes to amperes, in the one place that owns it."""
    assert declared_conductor_current_a(anchor_configuration()) == pytest.approx(
        PRINTED_FLOATING_COIL_CURRENT_A, rel=1.0e-12
    )


# --- The record itself ---


def test_the_record_is_schema_tagged_and_carries_its_non_claims() -> None:
    """Every record states what it is and what it is not."""
    record = anchor_record().to_record()
    assert record["schema"] == LEVEL0_SCHEMA
    assert record["schema_version"] == LEVEL0_SCHEMA_VERSION
    assert record["non_claims"] == list(LEVEL0_NON_CLAIMS)
    assert set(record) == {
        "schema",
        "schema_version",
        "configuration_digest_sha256",
        "winding",
        "charging",
        "heating",
        "plasma",
        "operating_point",
        "non_claims",
    }


@pytest.mark.parametrize(
    "phrase",
    [
        "average diameter of the coil",
        "is not the operational current the source prints",
        "the source prints no field there",
        "consistency instrument",
        "non-relativistic",
        "single-turn estimate",
    ],
)
def test_the_non_claims_name_every_tension_the_record_carries(phrase: str) -> None:
    """Each disagreement in the source is written down, not just handled."""
    assert any(phrase in claim for claim in LEVEL0_NON_CLAIMS)


def test_the_canonical_bytes_are_sorted_and_newline_terminated() -> None:
    """The record serialises the way every record here serialises."""
    data = anchor_record().canonical_bytes()
    assert data.endswith(b"\n")
    text = data.decode("utf-8")
    assert text.rstrip("\n") == json.dumps(
        json.loads(text), sort_keys=True, separators=(",", ":")
    )


def test_the_digest_identifies_the_record_and_moves_with_it() -> None:
    """The same inputs give the same digest; a changed one does not."""
    first = anchor_record()
    assert first.digest_sha256() == anchor_record().digest_sha256()
    other = level0_physics(
        anchor_configuration(),
        WindingDeclaration(turns=PRINTED_FLOATING_COIL_TURNS + 1.0),
        anchor_charging(),
        anchor_heating(),
        anchor_plasma(),
    )
    assert other.digest_sha256() != first.digest_sha256()


def test_the_record_binds_the_configuration_it_was_built_from() -> None:
    """Provenance is a digest, not a name."""
    configuration = anchor_configuration()
    record = level0_physics(
        configuration,
        anchor_winding(),
        anchor_charging(),
        anchor_heating(),
        anchor_plasma(),
    )
    assert record.configuration_digest_sha256 == configuration.digest_sha256()


def test_every_declaration_projects_exactly_its_own_fields() -> None:
    """A declaration's record is its declared values and nothing else."""
    record = anchor_record()
    assert set(record.winding.to_record()) == {"turns"}
    assert set(record.charging.to_record()) == {
        "charging_coil_current_a",
        "floating_coil_self_inductance_h",
        "mutual_inductance_h",
    }
    assert set(record.heating.to_record()) == {
        "frequencies_hz",
        "total_power_kw",
    }
    assert set(record.plasma.to_record()) == {
        "peak_perpendicular_pressure_pa",
        "combined_beta",
        "pressure_anisotropy",
        "adiabatic_index",
        "core_to_edge_pressure_ratio",
    }


def test_the_heating_record_carries_both_printed_frequencies() -> None:
    """A tuple, because the source drives two sources at once."""
    heating = anchor_heating().to_record()
    assert heating["frequencies_hz"] == list(PRINTED_HEATING_FREQUENCIES_HZ)
    assert heating["total_power_kw"] == PRINTED_TOTAL_HEATING_POWER_KW


# --- Refusals ---


@pytest.mark.parametrize("bad", [0.0, -1.0, math.nan])
def test_the_winding_refuses_a_bad_turn_count(bad: float) -> None:
    """A declaration is validated at construction, never at use."""
    with pytest.raises(DeviceConfigurationError, match=r"turns"):
        WindingDeclaration(turns=bad)


@pytest.mark.parametrize(
    ("current", "own", "mutual"),
    [(0.0, 1.0, 1.0), (1.0, 0.0, 1.0), (1.0, 1.0, 0.0), (1.0, math.nan, 1.0)],
)
def test_the_charging_declaration_refuses_every_bad_field(
    current: float, own: float, mutual: float
) -> None:
    """All three fields are validated."""
    with pytest.raises(DeviceConfigurationError):
        ChargingDeclaration(
            charging_coil_current_a=current,
            floating_coil_self_inductance_h=own,
            mutual_inductance_h=mutual,
        )


def test_the_heating_declaration_refuses_an_empty_frequency_tuple() -> None:
    """A heating system with no frequency heats nothing."""
    with pytest.raises(DeviceConfigurationError, match=r"at least one frequency"):
        HeatingDeclaration(frequencies_hz=(), total_power_kw=1.0)


def test_the_heating_declaration_names_the_offending_frequency_by_index() -> None:
    """A refusal that says which entry is wrong, not merely that one is."""
    with pytest.raises(DeviceConfigurationError, match=r"frequencies_hz\[1\]"):
        HeatingDeclaration(frequencies_hz=(1.0e9, -1.0), total_power_kw=1.0)


def test_the_heating_declaration_refuses_a_bad_power() -> None:
    """The power is validated after the frequencies."""
    with pytest.raises(DeviceConfigurationError, match=r"total_power_kw"):
        HeatingDeclaration(frequencies_hz=(1.0e9,), total_power_kw=0.0)


@pytest.mark.parametrize(
    ("pressure", "beta", "anisotropy", "index", "ratio"),
    [
        (0.0, 0.2, 5.0, 1.6, 10.0),
        (1.0, 0.0, 5.0, 1.6, 10.0),
        (1.0, 0.2, 1.0, 1.6, 10.0),
        (1.0, 0.2, 5.0, 1.0, 10.0),
        (1.0, 0.2, 5.0, 1.6, 1.0),
        (1.0, 0.2, 5.0, 1.6, math.nan),
    ],
)
def test_the_plasma_declaration_refuses_every_bad_field(
    pressure: float, beta: float, anisotropy: float, index: float, ratio: float
) -> None:
    """Every field is validated, and three of them against a floor of one."""
    with pytest.raises(DeviceConfigurationError):
        PlasmaDeclaration(
            peak_perpendicular_pressure_pa=pressure,
            combined_beta=beta,
            pressure_anisotropy=anisotropy,
            adiabatic_index=index,
            core_to_edge_pressure_ratio=ratio,
        )


def test_the_plasma_declaration_admits_a_beta_above_one() -> None:
    """The regime this family models is exactly that one."""
    declaration = PlasmaDeclaration(
        peak_perpendicular_pressure_pa=750.0,
        combined_beta=1.5,
        pressure_anisotropy=PRINTED_PRESSURE_ANISOTROPY,
        adiabatic_index=5.0 / 3.0,
        core_to_edge_pressure_ratio=1.0e3,
    )
    assert declaration.combined_beta == 1.5


@pytest.mark.parametrize(
    "field",
    ["turns", "charging_coil_current_a", "total_power_kw", "combined_beta"],
)
def test_every_declaration_is_frozen(field: str) -> None:
    """A declaration a caller can edit is not a declaration."""
    declarations = {
        "turns": anchor_winding(),
        "charging_coil_current_a": anchor_charging(),
        "total_power_kw": anchor_heating(),
        "combined_beta": anchor_plasma(),
    }
    with pytest.raises((AttributeError, TypeError)):
        setattr(declarations[field], field, 1.0)


def test_the_composition_refuses_a_configuration_the_relations_reject() -> None:
    """A refusal from a relation reaches the caller, never a default."""
    with pytest.raises(DeviceConfigurationError):
        level0_physics(
            anchor_configuration(),
            anchor_winding(),
            ChargingDeclaration(
                charging_coil_current_a=PRINTED_CHARGING_COIL_MAX_CURRENT_A,
                floating_coil_self_inductance_h=(
                    PRINTED_FLOATING_COIL_SELF_INDUCTANCE_H
                ),
                mutual_inductance_h=PRINTED_MUTUAL_INDUCTANCE_H,
            ),
            HeatingDeclaration(frequencies_hz=(), total_power_kw=1.0),
            anchor_plasma(),
        )
