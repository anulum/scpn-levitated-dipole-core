# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — B-rep model of the coil set

"""The same coil set as exact B-rep solids (tier G2).

Tier G1 inscribes polygons in circles and its volumes are therefore
always short of the analytic ones. Tier G2 builds the same six bodies as
exact solids of revolution through a pinned third-party kernel, exports
normalised STEP, and checks each body three ways: against its own
analytic closed form, against a faceting of itself, and against the
tier-G1 mesh of the same body at a declared resolution.

**The two states of the tier-G1 record are the two states here**, for the
same reason and with the same absence: no transformation between them
exists in this repository, because the source prints no distance between
the floating and charging coils.

The back-end is optional. Importing this module without it raises the
library's own unavailability error rather than a missing-attribute
failure, and every other capability of this repository works without it.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.cad import (
    BodyEvidence,
    BrepAssembly,
    BrepBody,
    annular_tube_brep,
    assembly_evidence,
    facet_assembly,
    step_bytes,
    step_sha256,
)
from scpn_reactor_kernels.geometry import TriangleMesh

from scpn_levitated_dipole_core.configuration import DeviceConfiguration
from scpn_levitated_dipole_core.errors import DeviceGeometryError
from scpn_levitated_dipole_core.geometry.model import (
    BODY_NAMES_BY_STATE,
    STATE_CHARGING,
    STATES,
    CoilSet,
    build_model,
)

#: Schema token of the B-rep model record.
CAD_MODEL_SCHEMA: Final = "scpn.levitated-dipole-cad-model.v1"

#: Faceting deflections the record declares. Measured on this body set
#: rather than reused from a sibling family: at 1e-6 m linear and 0.3 rad
#: angular every body's faceted volume stays inside the library's own
#: deficit bound, and the linear term is the one that binds.
DEFAULT_LINEAR_DEFLECTION_M: Final = 1.0e-6
DEFAULT_ANGULAR_DEFLECTION_RAD: Final = 0.3

#: Segment count of the tier-G1 meshes the evidence compares against.
DEFAULT_EVIDENCE_SEGMENTS: Final = 32

#: What the record does not claim, beyond the tier-G1 non-claims.
CAD_MODEL_NON_CLAIMS: Final = (
    (
        "the B-rep kernel is a pinned third-party dependency and is not the"
        " bit-exact floor of this group"
    ),
    "no STEP entity carries a material, a tolerance or a manufacturing note",
    "the faceted meshes are the kernel's own approximation, not tier G1's",
    "no transformation between the charging and levitated states is defined",
)


def _body(
    name: str,
    inner_diameter_m: float,
    outer_diameter_m: float,
    height_m: float,
    centre_z_m: float,
) -> BrepBody:
    """Build one annular B-rep body about a declared centre height.

    Parameters
    ----------
    name
        Node name of the body.
    inner_diameter_m, outer_diameter_m
        Diameters, in metres.
    height_m
        Height, in metres.
    centre_z_m
        Height of the body's mid-plane, in metres.

    Returns
    -------
    BrepBody
        The solid with its analytic volume and surface area.

    Raises
    ------
    CadError
        If the library refuses a dimension;
        :class:`~scpn_reactor_kernels.errors.CadUnavailableError` if the
        back-end is absent.
    """
    half = height_m / 2.0
    return annular_tube_brep(
        inner_diameter_m / 2.0,
        outer_diameter_m / 2.0,
        centre_z_m - half,
        centre_z_m + half,
        name,
        "conductor",
        "declared",
    )


def build_assembly(coils: CoilSet, state: str) -> BrepAssembly:
    """Build the B-rep assembly of one coil set in one state.

    Parameters
    ----------
    coils
        The declared coil set.
    state
        One of the two states of the tier-G1 model.

    Returns
    -------
    BrepAssembly
        The five solids, in the order of the state's body names.

    Raises
    ------
    DeviceGeometryError
        If the state is not one of the two.
    CadError
        If the library refuses a dimension.
    """
    if state not in STATES:
        raise DeviceGeometryError(f"state: must be one of {STATES!r}, got {state!r}")
    names = BODY_NAMES_BY_STATE[state]
    bodies = [
        _body(name, coil.inner_diameter_m, coil.outer_diameter_m, coil.height_m, 0.0)
        for name, coil in zip(names[:3], coils.subcoils, strict=True)
    ]
    bodies.append(
        _body(
            names[3],
            coils.cryostat.inner_diameter_m,
            coils.cryostat.outer_diameter_m,
            coils.cryostat.height_m,
            0.0,
        )
    )
    if state == STATE_CHARGING:
        bodies.append(
            _body(
                names[4],
                coils.charging_coil.inner_diameter_m,
                coils.charging_coil.outer_diameter_m,
                coils.charging_coil.height_m,
                coils.charging_offset_m,
            )
        )
    else:
        bodies.append(
            _body(
                names[4],
                coils.levitation_coil.inner_diameter_m,
                coils.levitation_coil.outer_diameter_m,
                coils.levitation_coil.height_m,
                coils.levitation_separation_m,
            )
        )
    return BrepAssembly(tuple(bodies))


def smallest_radii_m(coils: CoilSet, state: str) -> tuple[float | None, ...]:
    """Return the smallest curvature radius of each body of a state.

    Parameters
    ----------
    coils
        The declared coil set.
    state
        One of the two states.

    Returns
    -------
    tuple of (float or None)
        The inner radius of every body, which is its smallest radius of
        curvature. **No entry is None**: every body of this device is a
        surface of revolution and none is a prism, so the deficit bound
        the library computes is a real bound for all five rather than a
        number that happens to pass.

    Raises
    ------
    DeviceGeometryError
        If the state is not one of the two.
    """
    if state not in STATES:
        raise DeviceGeometryError(f"state: must be one of {STATES!r}, got {state!r}")
    radii = [coil.inner_diameter_m / 2.0 for coil in coils.subcoils]
    radii.append(coils.cryostat.inner_diameter_m / 2.0)
    if state == STATE_CHARGING:
        radii.append(coils.charging_coil.inner_diameter_m / 2.0)
    else:
        radii.append(coils.levitation_coil.inner_diameter_m / 2.0)
    return tuple(radii)


def _step_extras(
    configuration: DeviceConfiguration, state: str, coils: CoilSet
) -> dict[str, Any]:
    """Return the provenance extras embedded in the STEP header."""
    return {
        "schema": CAD_MODEL_SCHEMA,
        "identifier": configuration.identifier,
        "state": state,
        "configuration_digest_sha256": configuration.digest_sha256(),
        "winding_pack_gaps_m": list(coils.winding_pack_gaps_m()),
        "charging_bore_clearance_m": coils.charging_bore_clearance_m(),
    }


@dataclass(frozen=True, slots=True)
class DeviceCadModel:
    """A B-rep model of one coil set in one state, with its evidence.

    Parameters
    ----------
    identifier
        Registry identifier of the configuration.
    state
        Which of the two arrangements this model places.
    configuration_digest_sha256
        Digest of the configuration the model was built for.
    linear_deflection_m, angular_deflection_rad
        Faceting deflections the evidence was taken at.
    evidence_segments
        Segment count of the tier-G1 meshes the evidence compares against.
    assembly
        The B-rep assembly.
    faceted
        The kernel's own faceting of every body.
    evidence
        One evidence record per body, in body order.
    step_bytes_sha256
        Digest of the normalised STEP export.
    """

    identifier: str
    state: str
    configuration_digest_sha256: str
    linear_deflection_m: float
    angular_deflection_rad: float
    evidence_segments: int
    assembly: BrepAssembly
    faceted: tuple[TriangleMesh, ...]
    evidence: tuple[BodyEvidence, ...]
    step_bytes_sha256: str

    def record(self) -> dict[str, Any]:
        """Return the model as a plain record.

        Returns
        -------
        dict
            Schema token, identity, state, the deflections, every body's
            three comparisons with their bounds, the STEP digest and the
            non-claims.
        """
        return {
            "schema": CAD_MODEL_SCHEMA,
            "identifier": self.identifier,
            "state": self.state,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "linear_deflection_m": self.linear_deflection_m,
            "angular_deflection_rad": self.angular_deflection_rad,
            "evidence_segments": self.evidence_segments,
            "step_bytes_sha256": self.step_bytes_sha256,
            "bodies": [
                {
                    "name": item.name,
                    "analytic_volume_m3": item.analytic_volume_m3,
                    "brep_volume_m3": item.brep_volume_m3,
                    "volume_relative_error": item.volume_relative_error,
                    "analytic_surface_area_m2": item.analytic_surface_area_m2,
                    "brep_surface_area_m2": item.brep_surface_area_m2,
                    "surface_area_relative_error": item.surface_area_relative_error,
                    "faceted_volume_m3": item.faceted_volume_m3,
                    "faceted_volume_relative_deficit": (
                        item.faceted_volume_relative_deficit
                    ),
                    "faceted_volume_deficit_bound": item.faceted_volume_deficit_bound,
                    "reference_mesh_volume_m3": item.reference_mesh_volume_m3,
                    "mesh_volume_relative_difference": (
                        item.mesh_volume_relative_difference
                    ),
                    "mesh_volume_difference_bound": item.mesh_volume_difference_bound,
                }
                for item in self.evidence
            ],
            "non_claims": list(CAD_MODEL_NON_CLAIMS),
        }

    def canonical_bytes(self) -> bytes:
        """Return the record as canonical UTF-8 JSON bytes."""
        return json.dumps(
            self.record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")

    def digest_sha256(self) -> str:
        """Return the SHA-256 digest of :meth:`canonical_bytes` as lowercase hex."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def build_cad_model(
    configuration: DeviceConfiguration,
    coils: CoilSet,
    state: str,
    linear_deflection_m: float = DEFAULT_LINEAR_DEFLECTION_M,
    angular_deflection_rad: float = DEFAULT_ANGULAR_DEFLECTION_RAD,
    evidence_segments: int = DEFAULT_EVIDENCE_SEGMENTS,
) -> DeviceCadModel:
    """Build the B-rep model of one coil set in one state, with its evidence.

    Parameters
    ----------
    configuration
        The configuration the model is built for.
    coils
        The declared coil set.
    state
        One of the two states.
    linear_deflection_m, angular_deflection_rad
        Faceting deflections; the library validates them.
    evidence_segments
        Segment count of the tier-G1 meshes compared against.

    Returns
    -------
    DeviceCadModel
        The assembly, its faceting, one evidence record per body and the
        digest of the normalised STEP export.

    Raises
    ------
    DeviceGeometryError
        If the state is not one of the two.
    CadError
        If the library refuses a dimension or a deflection.
    """
    assembly = build_assembly(coils, state)
    faceted = facet_assembly(assembly, linear_deflection_m, angular_deflection_rad)
    reference = build_model(configuration, coils, state, evidence_segments).meshes
    evidence = assembly_evidence(
        assembly.bodies,
        smallest_radii_m(coils, state),
        faceted,
        reference,
        linear_deflection_m,
        evidence_segments,
    )
    extras = _step_extras(configuration, state, coils)
    return DeviceCadModel(
        identifier=configuration.identifier,
        state=state,
        configuration_digest_sha256=configuration.digest_sha256(),
        linear_deflection_m=linear_deflection_m,
        angular_deflection_rad=angular_deflection_rad,
        evidence_segments=evidence_segments,
        assembly=assembly,
        faceted=faceted,
        evidence=evidence,
        step_bytes_sha256=step_sha256(step_bytes(assembly, extras)),
    )
