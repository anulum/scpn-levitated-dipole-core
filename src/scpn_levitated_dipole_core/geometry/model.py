# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — tessellated 3D model of the coil set

"""The coil set of a levitated dipole, as tessellated bodies (tier G1).

**Every body of this device is an annular tube**, and that is a reading of
the source rather than a convenience. The filed source describes the
floating coil's winding pack as "three rectangular sub-coils with aligned
vertical centers" and prints an inner diameter and a height for each; it
prints an inner diameter, an outer diameter and a height for the charging
coil, and an inner and outer diameter for the levitation coil. Nothing in
the printed geometry is a torus of circular cross-section, and nothing
here builds one.

**The device is modelled in two states, and no transformation between
them exists in this repository.** A levitated dipole is one machine that
stands in two arrangements: charging, with the floating coil lowered into
the charging station inside the charging coil, and levitated, with the
floating coil at the centre of the vacuum vessel and the levitation coil
above it. The source prints the levitation coil's vertical separation from
the floating coil and prints nothing about the charging coil's. Placing
all three coils in one frame would therefore assert a distance the source
does not give, so the two states are two models in two frames and the
absence of a transformation between them is structural rather than
documentary.

**The vacuum vessel is not modelled.** The source prints exactly one
number for it, its 5 m diameter, and its own schematic draws a faceted
body of revolution whose profile is given nowhere. A sphere or a cylinder
of that diameter would be a substitute for a shape that is not stated, so
this record carries no vessel at all and says so in its non-claims.

Nothing here is an engineering model. No body carries a material property,
no clearance is a design margin, and the meshes are inscribed
approximations of the analytic surfaces at a declared resolution.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.geometry import (
    TriangleMesh,
    annular_tube,
)

from scpn_levitated_dipole_core.configuration import DeviceConfiguration
from scpn_levitated_dipole_core.errors import DeviceGeometryError

#: Schema token of the tessellated model record.
MODEL_SCHEMA: Final = "scpn.levitated-dipole-3d-model.v1"

#: Metres per millimetre; the source prints the charging and levitation
#: coils in millimetres and the floating coil in metres.
MILLIMETRE_M: Final = 1.0e-3

#: The two states the source describes.
STATE_CHARGING: Final = "charging"
STATE_LEVITATED: Final = "levitated"
STATES: Final = (STATE_CHARGING, STATE_LEVITATED)

#: Bodies placed in each state, in build order.
CHARGING_BODY_NAMES: Final = (
    "floating_coil_inner_subcoil",
    "floating_coil_middle_subcoil",
    "floating_coil_outer_subcoil",
    "floating_coil_cryostat",
    "charging_coil_winding_pack",
)
LEVITATED_BODY_NAMES: Final = (
    "floating_coil_inner_subcoil",
    "floating_coil_middle_subcoil",
    "floating_coil_outer_subcoil",
    "floating_coil_cryostat",
    "levitation_coil_winding_pack",
)
BODY_NAMES_BY_STATE: Final = {
    STATE_CHARGING: CHARGING_BODY_NAMES,
    STATE_LEVITATED: LEVITATED_BODY_NAMES,
}

#: Units of every numeric field of the record.
MODEL_UNITS: Final = {
    "body_volumes_m3": "m^3",
    "body_surface_areas_m2": "m^2",
    "winding_pack_gaps_m": "m",
    "cryostat_radial_clearance_m": "m",
    "charging_bore_clearance_m": "m",
}

#: What the record does not claim.
MODEL_NON_CLAIMS: Final = (
    (
        "no body is a torus of circular cross-section; the source's printed"
        " geometry is annular and this record builds nothing else"
    ),
    "the vacuum vessel is not modelled, because one diameter does not fix a shape",
    "no transformation between the charging and levitated states is defined",
    "no body carries a material, a temperature or a structural property",
    "no clearance reported here is a design margin or an assembly tolerance",
    "the meshes are inscribed approximations, so every volume is an underestimate",
    "no field of this record is a measurement of a built machine",
    "the source prints no vertical offset between the floating and charging coils",
    "the winding-pack sub-coil outer diameters are declared, not printed",
    "the cryostat and levitation-coil heights are declared, not printed",
)


def _require_positive(name: str, value: float) -> float:
    """Return a strictly positive declared length.

    Parameters
    ----------
    name
        Field name reported in the rejection.
    value
        Value under validation, in metres.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceGeometryError
        If the value is not finite and strictly positive.
    """
    if not math.isfinite(value) or value <= 0.0:
        raise DeviceGeometryError(
            f"{name}: must be finite and strictly positive, got {value!r}"
        )
    return value


def _require_ordered(
    inner_name: str, inner: float, outer_name: str, outer: float
) -> None:
    """Refuse an annulus whose outer radius does not exceed its inner one.

    Parameters
    ----------
    inner_name, outer_name
        Field names reported in the rejection.
    inner, outer
        Diameters or radii, in the same unit.

    Raises
    ------
    DeviceGeometryError
        If ``outer`` does not strictly exceed ``inner``.
    """
    if not (outer > inner):
        raise DeviceGeometryError(
            f"{outer_name}: must exceed {inner_name}, got "
            f"{inner_name}={inner!r} {outer_name}={outer!r}"
        )


@dataclass(frozen=True, slots=True)
class Annulus:
    """A body given by two diameters and a height.

    Every body of this device is one of these, so there is one type
    rather than one per role: a sub-coil, a cryostat shell and a
    charging coil differ in what they are for, not in what they are.

    Parameters
    ----------
    inner_diameter_m, outer_diameter_m
        Diameters, in metres. The source prints both for the outer
        sub-coil, the charging coil and the levitation coil, and prints
        only the inner one for the two inner sub-coils; which is which is
        recorded where the values are declared, not here.
    height_m
        Height, in metres. Printed for the three sub-coils and the
        charging coil, declared for the cryostat and the levitation
        coil.

    Raises
    ------
    DeviceGeometryError
        If any dimension leaves its documented interval or the outer
        diameter does not exceed the inner one.
    """

    inner_diameter_m: float
    outer_diameter_m: float
    height_m: float

    def __post_init__(self) -> None:
        """Validate one annular body.

        Raises
        ------
        DeviceGeometryError
            If any dimension is inadmissible.
        """
        _require_positive("inner_diameter_m", self.inner_diameter_m)
        _require_positive("outer_diameter_m", self.outer_diameter_m)
        _require_positive("height_m", self.height_m)
        _require_ordered(
            "inner_diameter_m",
            self.inner_diameter_m,
            "outer_diameter_m",
            self.outer_diameter_m,
        )


@dataclass(frozen=True, slots=True)
class CoilSet:
    """The declared coil set of one levitated dipole.

    Parameters
    ----------
    inner_subcoil, middle_subcoil, outer_subcoil
        The three rectangular sub-coils of the floating coil's winding
        pack, innermost first. The source prints that their vertical
        centres are aligned, so this record places all three about one
        height and a test asserts it.
    cryostat
        The floating coil's cryostat shell.
    charging_coil
        The charging coil's winding pack.
    levitation_coil
        The levitation coil's winding pack.
    levitation_separation_m
        Vertical separation of the levitation coil from the floating
        coil, in metres; printed by the source.
    charging_offset_m
        Vertical offset of the charging coil's centre from the floating
        coil's, in metres, in the charging state. **The source prints no
        such offset**; it says the charging coil surrounds the charging
        station the floating coil is lowered into. Zero is the coaxial,
        co-centred reading and is what the anchor declares.

    Raises
    ------
    DeviceGeometryError
        If any dimension is inadmissible, if the sub-coils are not
        radially ordered, or if the floating coil's cryostat does not fit
        inside the charging coil's bore.
    """

    inner_subcoil: Annulus
    middle_subcoil: Annulus
    outer_subcoil: Annulus
    cryostat: Annulus
    charging_coil: Annulus
    levitation_coil: Annulus
    levitation_separation_m: float
    charging_offset_m: float

    def __post_init__(self) -> None:
        """Validate the set and the two printed nesting relations.

        Raises
        ------
        DeviceGeometryError
            If the sub-coils are not radially ordered or the cryostat
            does not fit the charging bore.
        """
        _require_positive("levitation_separation_m", self.levitation_separation_m)
        if not math.isfinite(self.charging_offset_m):
            raise DeviceGeometryError(
                f"charging_offset_m: must be finite, got {self.charging_offset_m!r}"
            )
        ordered = (self.inner_subcoil, self.middle_subcoil, self.outer_subcoil)
        for index in range(len(ordered) - 1):
            _require_ordered(
                f"subcoil[{index}].outer_diameter_m",
                ordered[index].inner_diameter_m,
                f"subcoil[{index + 1}].inner_diameter_m",
                ordered[index + 1].inner_diameter_m,
            )
        # The source prints three diameters that nest: the cryostat's outer
        # limiter diameter is smaller than the charging station's, which is
        # smaller than the charging coil's bore. Only the outermost of the
        # three is checkable here, and it is checked rather than assumed.
        _require_ordered(
            "cryostat.outer_diameter_m",
            self.cryostat.outer_diameter_m,
            "charging_coil.inner_diameter_m",
            self.charging_coil.inner_diameter_m,
        )

    @property
    def subcoils(self) -> tuple[Annulus, Annulus, Annulus]:
        """The three sub-coils, innermost first."""
        return (self.inner_subcoil, self.middle_subcoil, self.outer_subcoil)

    def winding_pack_gaps_m(self) -> tuple[float, float]:
        """Return the radial gaps between neighbouring sub-coils.

        Returns
        -------
        tuple of (float, float)
            ``(inner-to-middle, middle-to-outer)`` gaps in metres, each
            as a radius rather than a diameter. The source calls the pack
            "continuous", so a set whose gaps are zero is the reading that
            makes the word true; the gaps are **reported, never gated**,
            because the two outer diameters that fix them are declared
            rather than printed.
        """
        return (
            (self.middle_subcoil.inner_diameter_m - self.inner_subcoil.outer_diameter_m)
            / 2.0,
            (self.outer_subcoil.inner_diameter_m - self.middle_subcoil.outer_diameter_m)
            / 2.0,
        )

    def cryostat_radial_clearance_m(self) -> float:
        """Return the radial clearance between the winding pack and the cryostat.

        Returns
        -------
        float
            Half the difference between the cryostat's outer diameter and
            the outer sub-coil's, in metres. Reported, never gated.
        """
        return (
            self.cryostat.outer_diameter_m - self.outer_subcoil.outer_diameter_m
        ) / 2.0

    def charging_bore_clearance_m(self) -> float:
        """Return the radial clearance of the cryostat inside the charging bore.

        Returns
        -------
        float
            Half the difference between the charging coil's inner
            diameter and the cryostat's outer diameter, in metres. It is
            strictly positive by construction, because the constructor
            refuses a set in which the floating coil could not enter the
            charging coil at all.
        """
        return (
            self.charging_coil.inner_diameter_m - self.cryostat.outer_diameter_m
        ) / 2.0


def _tube(
    body_name: str,
    inner_diameter_m: float,
    outer_diameter_m: float,
    height_m: float,
    centre_z_m: float,
    segments: int,
) -> TriangleMesh:
    """Tessellate one annular body about a declared centre height.

    Parameters
    ----------
    body_name
        Node name of the body.
    inner_diameter_m, outer_diameter_m
        Diameters, in metres.
    height_m
        Height, in metres.
    centre_z_m
        Height of the body's mid-plane, in metres.
    segments
        Circumferential segments; the library validates the count.

    Returns
    -------
    TriangleMesh
        The validated closed mesh.

    Raises
    ------
    GeometryError
        If the library refuses the dimensions or the segment count.
    """
    half = height_m / 2.0
    vertices, faces = annular_tube(
        inner_diameter_m / 2.0,
        outer_diameter_m / 2.0,
        centre_z_m - half,
        centre_z_m + half,
        segments,
    )
    return TriangleMesh(
        name=body_name,
        role="conductor",
        material_identifier="declared",
        vertices=vertices,
        faces=faces,
    )


@dataclass(frozen=True, slots=True)
class DeviceModel3D:
    """A tessellated model of one coil set in one state.

    Parameters
    ----------
    identifier
        Registry identifier of the configuration the model was built for.
    state
        Which of the two arrangements this model places.
    configuration_digest_sha256
        Digest of the configuration the model was built for.
    segments
        Circumferential segment count every body was built at.
    meshes
        The validated closed meshes, in the order of the state's body
        names.

    Raises
    ------
    DeviceGeometryError
        If the state is not one of the two, or the mesh names do not
        match the state's body set in order.
    """

    identifier: str
    state: str
    configuration_digest_sha256: str
    segments: int
    meshes: tuple[TriangleMesh, ...]

    def __post_init__(self) -> None:
        """Validate the state and its body set.

        Raises
        ------
        DeviceGeometryError
            If the state is unknown or the body set does not match it.
        """
        if self.state not in STATES:
            raise DeviceGeometryError(
                f"state: must be one of {STATES!r}, got {self.state!r}"
            )
        expected = BODY_NAMES_BY_STATE[self.state]
        got = tuple(mesh.name for mesh in self.meshes)
        if got != expected:
            raise DeviceGeometryError(
                f"meshes: state {self.state!r} places {expected!r}, got {got!r}"
            )

    def body_volumes_m3(self) -> tuple[float, ...]:
        """Signed volume of every body, in the order of the body names."""
        return tuple(mesh.signed_volume_m3() for mesh in self.meshes)

    def body_surface_areas_m2(self) -> tuple[float, ...]:
        """Surface area of every body, in the order of the body names."""
        return tuple(mesh.surface_area_m2() for mesh in self.meshes)

    def record(self) -> dict[str, Any]:
        """Return the model as a plain record.

        Returns
        -------
        dict
            Schema token, identity, state, resolution, body names and
            their measures, the units of every numeric field and the
            non-claims. Nothing derived is omitted and nothing is
            rounded.
        """
        return {
            "schema": MODEL_SCHEMA,
            "identifier": self.identifier,
            "state": self.state,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "segments": self.segments,
            "body_names": list(BODY_NAMES_BY_STATE[self.state]),
            "body_volumes_m3": list(self.body_volumes_m3()),
            "body_surface_areas_m2": list(self.body_surface_areas_m2()),
            "units": dict(MODEL_UNITS),
            "non_claims": list(MODEL_NON_CLAIMS),
        }

    def canonical_bytes(self) -> bytes:
        """Return the record as canonical UTF-8 JSON bytes."""
        return json.dumps(
            self.record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")

    def digest_sha256(self) -> str:
        """Return the SHA-256 digest of :meth:`canonical_bytes` as lowercase hex."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def build_model(
    configuration: DeviceConfiguration,
    coils: CoilSet,
    state: str,
    segments: int,
) -> DeviceModel3D:
    """Build the tessellated model of one coil set in one state.

    Parameters
    ----------
    configuration
        The configuration the model is built for; only its identifier and
        digest enter the record.
    coils
        The declared coil set.
    state
        One of :data:`STATE_CHARGING` or :data:`STATE_LEVITATED`.
    segments
        Circumferential segments per body; the library enforces at least
        eight and a multiple of eight.

    Returns
    -------
    DeviceModel3D
        The model, with the floating coil's mid-plane at ``z = 0`` in
        both states.

    Raises
    ------
    DeviceGeometryError
        If the state is not one of the two.
    GeometryError
        If the library refuses a dimension or the segment count.

    Notes
    -----
    The frame origin is the floating coil's mid-plane in **both** states,
    which is the one placement the source supports in each: the three
    sub-coils have aligned vertical centres, printed, and the cryostat
    encloses them. What differs is the fifth body. In the levitated state
    it is the levitation coil at the **printed** separation above; in the
    charging state it is the charging coil at a **declared** offset,
    because the source prints none.
    """
    if state not in STATES:
        raise DeviceGeometryError(f"state: must be one of {STATES!r}, got {state!r}")
    meshes = [
        _tube(
            name,
            coil.inner_diameter_m,
            coil.outer_diameter_m,
            coil.height_m,
            0.0,
            segments,
        )
        for name, coil in zip(CHARGING_BODY_NAMES[:3], coils.subcoils, strict=True)
    ]
    meshes.append(
        _tube(
            "floating_coil_cryostat",
            coils.cryostat.inner_diameter_m,
            coils.cryostat.outer_diameter_m,
            coils.cryostat.height_m,
            0.0,
            segments,
        )
    )
    if state == STATE_CHARGING:
        meshes.append(
            _tube(
                "charging_coil_winding_pack",
                coils.charging_coil.inner_diameter_m,
                coils.charging_coil.outer_diameter_m,
                coils.charging_coil.height_m,
                coils.charging_offset_m,
                segments,
            )
        )
    else:
        meshes.append(
            _tube(
                "levitation_coil_winding_pack",
                coils.levitation_coil.inner_diameter_m,
                coils.levitation_coil.outer_diameter_m,
                coils.levitation_coil.height_m,
                coils.levitation_separation_m,
                segments,
            )
        )
    return DeviceModel3D(
        identifier=configuration.identifier,
        state=state,
        configuration_digest_sha256=configuration.digest_sha256(),
        segments=segments,
        meshes=tuple(meshes),
    )
