# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — tessellated 3D model tests

"""Two states, one frame each, and the diameters that must nest.

The load-bearing test of this module is
:func:`test_the_three_printed_diameters_nest`. Three numbers printed in
three different sections of the source have to be consistent for the
machine to be assemblable at all, and they are. Everything else here
checks that the record repeats what is printed and declares what is not.
"""

from __future__ import annotations

import dataclasses
import json
import math
from typing import Any

import pytest

from geometry_fixtures import (
    DECLARED_CHARGING_OFFSET_M,
    DECLARED_CRYOSTAT_HEIGHT_M,
    DECLARED_INNER_SUBCOIL_OUTER_DIAMETER_M,
    DECLARED_LEVITATION_COIL_HEIGHT_M,
    DECLARED_MIDDLE_SUBCOIL_OUTER_DIAMETER_M,
    FIXTURE_SEGMENTS,
    PRINTED_CHARGING_COIL_HEIGHT_M,
    PRINTED_CHARGING_COIL_INNER_DIAMETER_M,
    PRINTED_CHARGING_COIL_OUTER_DIAMETER_M,
    PRINTED_CHARGING_STATION_DIAMETER_M,
    PRINTED_CRYOSTAT_INNER_DIAMETER_M,
    PRINTED_CRYOSTAT_OUTER_DIAMETER_M,
    PRINTED_INNER_SUBCOIL_HEIGHT_M,
    PRINTED_INNER_SUBCOIL_INNER_DIAMETER_M,
    PRINTED_LEVITATION_COIL_INNER_DIAMETER_M,
    PRINTED_LEVITATION_COIL_OUTER_DIAMETER_M,
    PRINTED_LEVITATION_COIL_TURNS,
    PRINTED_LEVITATION_SEPARATION_M,
    PRINTED_MIDDLE_SUBCOIL_HEIGHT_M,
    PRINTED_OUTER_SUBCOIL_HEIGHT_M,
    PRINTED_SUPPORT_PLATE_COPPER_M,
    PRINTED_SUPPORT_PLATE_STEEL_M,
    PRINTED_TAPE_HEIGHT_M,
    PRINTED_TAPE_WIDTH_M,
    anchor_coil_set,
    anchor_device_configuration,
)
from scpn_levitated_dipole_core.errors import DeviceGeometryError
from scpn_levitated_dipole_core.geometry import (
    BODY_NAMES_BY_STATE,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    STATE_CHARGING,
    STATE_LEVITATED,
    STATES,
    Annulus,
    CoilSet,
    DeviceModel3D,
    build_model,
)


def _analytic_volume_m3(inner_d: float, outer_d: float, height: float) -> float:
    """Return the closed-form volume of an annular tube."""
    return math.pi * ((outer_d / 2.0) ** 2 - (inner_d / 2.0) ** 2) * height


def test_the_three_printed_diameters_nest() -> None:
    """The floating coil fits the charging station, which fits the coil bore.

    These three numbers are printed in three different places: the
    cryostat's outer limiter diameter, the charging station's diameter and
    the charging coil's bore. If they did not nest the machine could not
    be assembled, so their nesting is a real consistency check on the
    reading rather than a restatement of any one of them.
    """
    assert (
        PRINTED_CRYOSTAT_OUTER_DIAMETER_M
        < PRINTED_CHARGING_STATION_DIAMETER_M
        < PRINTED_CHARGING_COIL_INNER_DIAMETER_M
    )
    station_clearance = (
        PRINTED_CHARGING_STATION_DIAMETER_M - PRINTED_CRYOSTAT_OUTER_DIAMETER_M
    )
    assert station_clearance == pytest.approx(0.017, abs=1.0e-12)


def test_the_charging_bore_clearance_is_the_printed_difference() -> None:
    """The clearance is half a difference of two printed diameters."""
    coils = anchor_coil_set()
    assert coils.charging_bore_clearance_m() == pytest.approx(0.080, abs=1.0e-12)
    assert coils.charging_bore_clearance_m() > 0.0


def test_the_declared_sub_coil_diameters_make_the_pack_continuous() -> None:
    """The source calls the pack continuous; the reading makes it so.

    The two outer diameters are declared, not printed, so the gaps they
    produce are reported rather than gated. That they come out at exactly
    zero is the whole reason the declaration was made this way, and it is
    asserted here so a future change to the fixture cannot pass silently.
    """
    coils = anchor_coil_set()
    assert coils.winding_pack_gaps_m() == (0.0, 0.0)
    inner_outer = DECLARED_INNER_SUBCOIL_OUTER_DIAMETER_M
    middle_outer = DECLARED_MIDDLE_SUBCOIL_OUTER_DIAMETER_M
    assert inner_outer == pytest.approx(0.555)
    assert middle_outer == pytest.approx(0.585)


def test_the_cryostat_height_is_the_toroidal_reading_of_two_printed_diameters() -> None:
    """The source's word "toroidal" supplies the height it does not print.

    A body of circular cross-section with an inner diameter of 0.445 m
    and an outer of 1.140 m is 0.3475 m tall. The model still builds an
    annular tube, because the printed data is annular; the toroidal
    wording contributes the missing height and nothing else.
    """
    height = DECLARED_CRYOSTAT_HEIGHT_M
    assert height == pytest.approx(0.3475, abs=1.0e-12)
    assert (
        DECLARED_CRYOSTAT_HEIGHT_M
        == (PRINTED_CRYOSTAT_OUTER_DIAMETER_M - PRINTED_CRYOSTAT_INNER_DIAMETER_M) / 2.0
    )
    assert DECLARED_CRYOSTAT_HEIGHT_M > PRINTED_OUTER_SUBCOIL_HEIGHT_M


def test_the_levitation_coil_height_comes_from_printed_thicknesses() -> None:
    """Three printed thicknesses and a tape width, and nothing else."""
    height = DECLARED_LEVITATION_COIL_HEIGHT_M
    assert height == pytest.approx(0.0177, abs=1.0e-12)
    assert DECLARED_LEVITATION_COIL_HEIGHT_M == (
        PRINTED_SUPPORT_PLATE_STEEL_M
        + 2.0 * PRINTED_SUPPORT_PLATE_COPPER_M
        + 2.0 * PRINTED_TAPE_WIDTH_M
    )


def test_the_levitation_coil_turn_stack_nearly_fills_its_printed_span() -> None:
    """Four printed numbers that nearly close, reported and never gated.

    Table 2 prints 2800 turns, a tape 0.168 mm high, and inner and outer
    diameters of 410 and 1320 mm. The turns laid side by side span
    470.4 mm against a printed radial span of 455.0 mm, a ratio of
    1.0338. The source calls the winding a double pancake, which would
    predict two radial stacks rather than one, so this is a disagreement
    the record carries as a number and does not resolve.
    """
    radial_span = (
        PRINTED_LEVITATION_COIL_OUTER_DIAMETER_M
        - PRINTED_LEVITATION_COIL_INNER_DIAMETER_M
    ) / 2.0
    stack = PRINTED_LEVITATION_COIL_TURNS * PRINTED_TAPE_HEIGHT_M
    assert radial_span == pytest.approx(0.4550, abs=1.0e-12)
    assert stack == pytest.approx(0.4704, abs=1.0e-12)
    assert stack / radial_span == pytest.approx(1.0338, rel=1.0e-4)


@pytest.mark.parametrize("state", STATES)
def test_each_state_places_exactly_its_own_body_set(state: str) -> None:
    """Five bodies, named and ordered by the state."""
    model = build_model(
        anchor_device_configuration(), anchor_coil_set(), state, FIXTURE_SEGMENTS
    )
    assert tuple(mesh.name for mesh in model.meshes) == BODY_NAMES_BY_STATE[state]
    assert len(model.meshes) == 5


def test_the_two_states_share_the_floating_coil_and_differ_in_the_fifth_body() -> None:
    """One machine in two arrangements, not two machines."""
    coils, configuration = anchor_coil_set(), anchor_device_configuration()
    charging = build_model(configuration, coils, STATE_CHARGING, FIXTURE_SEGMENTS)
    levitated = build_model(configuration, coils, STATE_LEVITATED, FIXTURE_SEGMENTS)
    for first, second in zip(charging.meshes[:4], levitated.meshes[:4], strict=True):
        assert first.name == second.name
        assert first.vertices == second.vertices
    assert charging.meshes[4].name != levitated.meshes[4].name
    assert charging.digest_sha256() != levitated.digest_sha256()


def test_the_three_sub_coils_share_one_vertical_centre() -> None:
    """The source prints "aligned vertical centers"; the model obeys it."""
    model = build_model(
        anchor_device_configuration(),
        anchor_coil_set(),
        STATE_LEVITATED,
        FIXTURE_SEGMENTS,
    )
    for mesh, height in zip(
        model.meshes[:3],
        (
            PRINTED_INNER_SUBCOIL_HEIGHT_M,
            PRINTED_MIDDLE_SUBCOIL_HEIGHT_M,
            PRINTED_OUTER_SUBCOIL_HEIGHT_M,
        ),
        strict=True,
    ):
        lows = {vertex[2] for vertex in mesh.vertices}
        assert min(lows) == pytest.approx(0.0 - height / 2.0, abs=1.0e-15)
        assert max(lows) == pytest.approx(height / 2.0, abs=1.0e-15)


def test_the_levitation_coil_sits_at_the_printed_separation() -> None:
    """1.610 m above the floating coil, from Table 2 and nowhere else."""
    model = build_model(
        anchor_device_configuration(),
        anchor_coil_set(),
        STATE_LEVITATED,
        FIXTURE_SEGMENTS,
    )
    heights = [vertex[2] for vertex in model.meshes[4].vertices]
    centre = (min(heights) + max(heights)) / 2.0
    assert centre == pytest.approx(PRINTED_LEVITATION_SEPARATION_M, abs=1.0e-12)


def test_the_charging_coil_sits_at_the_declared_offset() -> None:
    """Zero, because the source prints no offset at all."""
    model = build_model(
        anchor_device_configuration(),
        anchor_coil_set(),
        STATE_CHARGING,
        FIXTURE_SEGMENTS,
    )
    heights = [vertex[2] for vertex in model.meshes[4].vertices]
    centre = (min(heights) + max(heights)) / 2.0
    assert centre == pytest.approx(DECLARED_CHARGING_OFFSET_M, abs=1.0e-12)


@pytest.mark.parametrize("state", STATES)
def test_every_mesh_volume_is_short_of_its_closed_form(state: str) -> None:
    """An inscribed polygon can only under-fill the circle it sits in."""
    coils = anchor_coil_set()
    model = build_model(anchor_device_configuration(), coils, state, FIXTURE_SEGMENTS)
    bodies: list[Annulus] = [*coils.subcoils, coils.cryostat]
    bodies.append(
        coils.charging_coil if state == STATE_CHARGING else coils.levitation_coil
    )
    for mesh, body in zip(model.meshes, bodies, strict=True):
        analytic = _analytic_volume_m3(
            body.inner_diameter_m, body.outer_diameter_m, body.height_m
        )
        measured = mesh.signed_volume_m3()
        assert 0.0 < measured < analytic
        assert (analytic - measured) / analytic == pytest.approx(6.4131e-3, rel=1.0e-3)


def _inscribed_polygon_deficit(segments: int) -> float:
    """Return the exact area deficit of a regular inscribed polygon."""
    return 1.0 - (segments / (2.0 * math.pi)) * math.sin(2.0 * math.pi / segments)


@pytest.mark.parametrize("segments", [8, 16, 32, 64, 128, 256])
def test_the_mesh_deficit_is_the_inscribed_polygon_deficit_exactly(
    segments: int,
) -> None:
    """Not merely bounded by it: equal to it, to twelve significant figures.

    An annular tube is bounded by two circles of the same segment count,
    so both its radii shrink by the same polygon ratio and its volume
    scales by exactly that ratio. The polygon bound is therefore
    **attained** for this body rather than approached, which is what makes
    the tier-G2 evidence check in this family a tight gate rather than a
    generous one.
    """
    coils, configuration = anchor_coil_set(), anchor_device_configuration()
    analytic = _analytic_volume_m3(
        coils.cryostat.inner_diameter_m,
        coils.cryostat.outer_diameter_m,
        coils.cryostat.height_m,
    )
    model = build_model(configuration, coils, STATE_LEVITATED, segments)
    measured = model.meshes[3].signed_volume_m3()
    deficit = (analytic - measured) / analytic
    assert deficit == pytest.approx(_inscribed_polygon_deficit(segments), rel=1.0e-11)


def test_the_record_is_canonical_and_digests_stably() -> None:
    """Same inputs, same bytes, same digest."""
    coils, configuration = anchor_coil_set(), anchor_device_configuration()
    first = build_model(configuration, coils, STATE_LEVITATED, FIXTURE_SEGMENTS)
    second = build_model(configuration, coils, STATE_LEVITATED, FIXTURE_SEGMENTS)
    assert first.canonical_bytes() == second.canonical_bytes()
    assert first.digest_sha256() == second.digest_sha256()
    record = json.loads(first.canonical_bytes())
    assert record["schema"] == MODEL_SCHEMA
    assert record["state"] == STATE_LEVITATED
    assert record["configuration_digest_sha256"] == configuration.digest_sha256()
    assert record["non_claims"] == list(MODEL_NON_CLAIMS)
    assert len(record["body_volumes_m3"]) == 5


def test_the_record_names_the_units_of_every_numeric_field() -> None:
    """A number without a unit is not a record."""
    model = build_model(
        anchor_device_configuration(),
        anchor_coil_set(),
        STATE_CHARGING,
        FIXTURE_SEGMENTS,
    )
    record = model.record()
    for field in ("body_volumes_m3", "body_surface_areas_m2"):
        assert field in record["units"]


def test_the_non_claims_name_the_torus_and_the_vessel() -> None:
    """Two things this record deliberately does not build."""
    joined = " ".join(MODEL_NON_CLAIMS)
    assert "torus" in joined
    assert "vacuum vessel is not modelled" in joined
    assert "no transformation" in joined


def test_an_unknown_state_is_refused_by_the_builder_and_the_record() -> None:
    """Both entry points validate the state, not only the first."""
    coils, configuration = anchor_coil_set(), anchor_device_configuration()
    with pytest.raises(DeviceGeometryError):
        build_model(configuration, coils, "hovering", FIXTURE_SEGMENTS)
    model = build_model(configuration, coils, STATE_LEVITATED, FIXTURE_SEGMENTS)
    with pytest.raises(DeviceGeometryError):
        DeviceModel3D(
            identifier=model.identifier,
            state="hovering",
            configuration_digest_sha256=model.configuration_digest_sha256,
            segments=model.segments,
            meshes=model.meshes,
        )


def test_a_body_set_that_does_not_match_the_state_is_refused() -> None:
    """A record cannot carry the charging bodies and claim to be levitated."""
    coils, configuration = anchor_coil_set(), anchor_device_configuration()
    charging = build_model(configuration, coils, STATE_CHARGING, FIXTURE_SEGMENTS)
    with pytest.raises(DeviceGeometryError):
        DeviceModel3D(
            identifier=charging.identifier,
            state=STATE_LEVITATED,
            configuration_digest_sha256=charging.configuration_digest_sha256,
            segments=charging.segments,
            meshes=charging.meshes,
        )


@pytest.mark.parametrize(
    ("inner", "outer", "height"),
    [
        (0.0, 1.0, 1.0),
        (1.0, 0.0, 1.0),
        (1.0, 2.0, 0.0),
        (math.nan, 1.0, 1.0),
        (1.0, math.inf, 1.0),
        (1.0, 1.0, 1.0),
        (2.0, 1.0, 1.0),
    ],
)
def test_an_inadmissible_body_is_refused(
    inner: float, outer: float, height: float
) -> None:
    """All three dimensions and their order are validated."""
    with pytest.raises(DeviceGeometryError):
        Annulus(inner_diameter_m=inner, outer_diameter_m=outer, height_m=height)


def _replaced(coils: CoilSet, **changes: Any) -> CoilSet:
    """Return the anchor coil set with named fields replaced.

    ``dataclasses.replace`` re-runs ``__post_init__``, which is the point:
    a refusal test must reach the validation rather than sidestep it.
    """
    return dataclasses.replace(coils, **changes)


def test_sub_coils_out_of_radial_order_are_refused() -> None:
    """A pack whose sub-coils overlap is not a pack."""
    coils = anchor_coil_set()
    swapped = Annulus(
        inner_diameter_m=PRINTED_INNER_SUBCOIL_INNER_DIAMETER_M,
        outer_diameter_m=DECLARED_INNER_SUBCOIL_OUTER_DIAMETER_M,
        height_m=PRINTED_INNER_SUBCOIL_HEIGHT_M,
    )
    with pytest.raises(DeviceGeometryError):
        _replaced(coils, middle_subcoil=swapped)


def test_a_floating_coil_too_large_for_the_charging_bore_is_refused() -> None:
    """The printed nesting is a gate, and a wrong answer trips it."""
    coils = anchor_coil_set()
    narrow = Annulus(
        inner_diameter_m=PRINTED_CRYOSTAT_OUTER_DIAMETER_M - 0.01,
        outer_diameter_m=PRINTED_CHARGING_COIL_OUTER_DIAMETER_M,
        height_m=PRINTED_CHARGING_COIL_HEIGHT_M,
    )
    with pytest.raises(DeviceGeometryError):
        _replaced(coils, charging_coil=narrow)


@pytest.mark.parametrize("separation", [0.0, -1.0, math.nan, math.inf])
def test_an_inadmissible_levitation_separation_is_refused(separation: float) -> None:
    """The one printed placement is validated like any other length."""
    coils = anchor_coil_set()
    with pytest.raises(DeviceGeometryError):
        _replaced(coils, levitation_separation_m=separation)


def test_a_non_finite_charging_offset_is_refused() -> None:
    """The declared offset may be any finite number, including zero."""
    coils = anchor_coil_set()
    with pytest.raises(DeviceGeometryError):
        _replaced(coils, charging_offset_m=math.nan)
    assert _replaced(coils, charging_offset_m=-0.4).charging_offset_m == -0.4


def test_the_clearances_are_reported_and_not_gated() -> None:
    """Both are differences of declared or printed diameters, nothing more."""
    coils = anchor_coil_set()
    assert coils.cryostat_radial_clearance_m() == pytest.approx(0.188, abs=1.0e-12)
    assert coils.charging_bore_clearance_m() == pytest.approx(0.080, abs=1.0e-12)
