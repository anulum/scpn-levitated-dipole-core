# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — B-rep model tests

"""The exact solids, and the three comparisons each one has to survive.

The measurement this module records is that **the mesh-difference check
is tight in this family**. Every body is bounded by two circles of the
same segment count, so the tier-G1 deficit equals the inscribed-polygon
bound rather than sitting under it, and the whole margin of the check is
the B-rep faceting being finer than tier G1. That is stated as an
assertion rather than left as a coincidence.

Skipped hermetically when the optional back-end is absent.
"""

from __future__ import annotations

import json
import math

import pytest

from geometry_fixtures import anchor_coil_set, anchor_device_configuration

pytest.importorskip("cadquery")

from scpn_levitated_dipole_core.errors import DeviceGeometryError
from scpn_levitated_dipole_core.geometry import (
    BODY_NAMES_BY_STATE,
    STATE_CHARGING,
    STATE_LEVITATED,
    STATES,
)
from scpn_levitated_dipole_core.geometry.cad import (
    CAD_MODEL_NON_CLAIMS,
    CAD_MODEL_SCHEMA,
    DEFAULT_ANGULAR_DEFLECTION_RAD,
    DEFAULT_EVIDENCE_SEGMENTS,
    DEFAULT_LINEAR_DEFLECTION_M,
    DeviceCadModel,
    build_assembly,
    build_cad_model,
    smallest_radii_m,
)

#: Measured: the B-rep kernel reproduces every analytic measure of this
#: body set to within this relative error, which is four orders of
#: magnitude inside the library's own declared measure tolerance.
MEASURED_ANALYTIC_AGREEMENT = 1.0e-14

#: Measured over all ten body placements of the two states: the faceting
#: deficit sits between 4.7239 and 11.9450 per cent of the library's own
#: ``2 d / r`` bound. The spread is not noise. The bound falls as the
#: body's inner radius grows, while what the mesher actually deviates by
#: does not fall with it, so the widest-bore body — the charging coil at
#: 0.65 m inner radius — sits at more than twice the fraction of the
#: narrowest. A single fraction quoted for the family would have hidden
#: that.
MEASURED_FACET_FRACTION_LOW = 0.045
MEASURED_FACET_FRACTION_HIGH = 0.125


@pytest.fixture(scope="module")
def levitated() -> DeviceCadModel:
    """Return the levitated-state B-rep model built once for the module."""
    return build_cad_model(
        anchor_device_configuration(), anchor_coil_set(), STATE_LEVITATED
    )


@pytest.fixture(scope="module")
def charging() -> DeviceCadModel:
    """Return the charging-state B-rep model built once for the module."""
    return build_cad_model(
        anchor_device_configuration(), anchor_coil_set(), STATE_CHARGING
    )


def test_each_state_builds_its_own_five_solids(
    levitated: DeviceCadModel, charging: DeviceCadModel
) -> None:
    """Named and ordered exactly as the tier-G1 model names them."""
    for model, state in ((charging, STATE_CHARGING), (levitated, STATE_LEVITATED)):
        assert (
            tuple(body.name for body in model.assembly.bodies)
            == (BODY_NAMES_BY_STATE[state])
        )
        assert len(model.evidence) == 5


def test_the_kernel_reproduces_every_analytic_measure(
    levitated: DeviceCadModel,
) -> None:
    """Volume and area, both directions, on all five bodies."""
    for item in levitated.evidence:
        assert item.volume_relative_error <= MEASURED_ANALYTIC_AGREEMENT
        assert item.surface_area_relative_error <= MEASURED_ANALYTIC_AGREEMENT


def test_the_faceting_stays_inside_its_declared_bound_by_a_measured_margin(
    levitated: DeviceCadModel, charging: DeviceCadModel
) -> None:
    """And by how much, per body, because the fraction is not one number.

    A check reported as a pass with unknown margin is not evidence. Both
    states are scanned, because the charging coil appears only in one of
    them and it is the body with the widest spread from its bound.
    """
    fractions = [
        item.faceted_volume_relative_deficit / item.faceted_volume_deficit_bound
        for model in (charging, levitated)
        for item in model.evidence
    ]
    assert len(fractions) == 10
    for fraction in fractions:
        assert MEASURED_FACET_FRACTION_LOW < fraction < MEASURED_FACET_FRACTION_HIGH
    assert max(fractions) / min(fractions) > 2.0


def test_the_mesh_difference_check_is_tight_and_not_generous(
    levitated: DeviceCadModel,
) -> None:
    """The margin of this check is the faceting, and nothing else.

    Every body here is bounded by two circles of the same segment count,
    so the tier-G1 deficit **equals** the inscribed-polygon bound. The
    difference the library measures is therefore the bound minus the
    faceting deficit, which is why the two numbers agree to four decimal
    places and why the check would trip on any real error in either tier.
    """
    exact_bound = 1.0 - (DEFAULT_EVIDENCE_SEGMENTS / (2.0 * math.pi)) * math.sin(
        2.0 * math.pi / DEFAULT_EVIDENCE_SEGMENTS
    )
    for item in levitated.evidence:
        assert item.mesh_volume_difference_bound == pytest.approx(
            exact_bound, rel=1.0e-12
        )
        margin = item.mesh_volume_difference_bound - (
            item.mesh_volume_relative_difference
        )
        assert margin > 0.0
        assert margin == pytest.approx(item.faceted_volume_relative_deficit, rel=5.0e-2)


def test_every_body_declares_a_real_curvature_radius() -> None:
    """No body of this device is a prism, so no radius is None.

    A sibling family had to pass ``None`` for its prisms, because a
    curvature bound computed from a number that is not a curvature would
    pass whatever the mesher did. Here every body is a surface of
    revolution and the bound is a real bound for all five.
    """
    for radius in smallest_radii_m(anchor_coil_set(), STATE_LEVITATED):
        assert radius is not None
        assert radius > 0.0


def test_the_two_states_share_four_solids_and_differ_in_the_fifth(
    levitated: DeviceCadModel, charging: DeviceCadModel
) -> None:
    """One machine in two arrangements, in tier G2 as in tier G1."""
    for first, second in zip(
        charging.evidence[:4], levitated.evidence[:4], strict=True
    ):
        assert first.name == second.name
        assert first.analytic_volume_m3 == second.analytic_volume_m3
    assert charging.evidence[4].name != levitated.evidence[4].name
    assert charging.step_bytes_sha256 != levitated.step_bytes_sha256
    assert charging.digest_sha256() != levitated.digest_sha256()


def test_the_step_export_is_deterministic(levitated: DeviceCadModel) -> None:
    """The same model exports the same bytes, so the digest is a digest."""
    again = build_cad_model(
        anchor_device_configuration(), anchor_coil_set(), STATE_LEVITATED
    )
    assert again.step_bytes_sha256 == levitated.step_bytes_sha256


def test_the_record_is_canonical_and_names_its_deflections(
    levitated: DeviceCadModel,
) -> None:
    """Everything the evidence rests on is in the record."""
    record = json.loads(levitated.canonical_bytes())
    assert record["schema"] == CAD_MODEL_SCHEMA
    assert record["state"] == STATE_LEVITATED
    assert record["linear_deflection_m"] == DEFAULT_LINEAR_DEFLECTION_M
    assert record["angular_deflection_rad"] == DEFAULT_ANGULAR_DEFLECTION_RAD
    assert record["evidence_segments"] == DEFAULT_EVIDENCE_SEGMENTS
    assert record["non_claims"] == list(CAD_MODEL_NON_CLAIMS)
    assert len(record["bodies"]) == 5
    assert levitated.digest_sha256() == levitated.digest_sha256()


def test_the_non_claims_name_the_back_end_as_third_party() -> None:
    """The B-rep kernel is pinned, not ours, and the record says so."""
    joined = " ".join(CAD_MODEL_NON_CLAIMS)
    assert "third-party" in joined
    assert "no transformation" in joined


@pytest.mark.parametrize("state", STATES)
def test_the_assembly_manifest_digests(state: str) -> None:
    """Every state produces a manifest digest of the expected shape."""
    assembly = build_assembly(anchor_coil_set(), state)
    digest = assembly.manifest_sha256()
    assert len(digest) == 64
    assert digest == digest.lower()


def test_an_unknown_state_is_refused_by_both_entry_points() -> None:
    """The assembly builder and the radius helper both validate it."""
    coils = anchor_coil_set()
    with pytest.raises(DeviceGeometryError):
        build_assembly(coils, "hovering")
    with pytest.raises(DeviceGeometryError):
        smallest_radii_m(coils, "hovering")
    with pytest.raises(DeviceGeometryError):
        build_cad_model(anchor_device_configuration(), coils, "hovering")
