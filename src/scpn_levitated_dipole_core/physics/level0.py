# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — level-0 physics record

"""Level-0 physics record of the owned levitated-dipole configuration.

The configuration carries a floating coil's radius, conductor current
and mass, and one levitation field gradient. Four things it does not
carry are declared here in four objects, each about one subsystem the
filed source describes: the **winding** that turns a conductor current
into ampere-turns, the **charging circuit** that puts current into a
coil with no leads, the **heating** that decides where the plasma
absorbs power, and the **plasma** whose pressure the field is holding.

The record then evaluates
:mod:`~scpn_levitated_dipole_core.physics.coil` on the magnet,
:mod:`~scpn_levitated_dipole_core.physics.levitation` on what holds it
up, :mod:`~scpn_levitated_dipole_core.physics.charging` on how it was
charged and :mod:`~scpn_levitated_dipole_core.physics.plasma` on what it
confines.

**Two printed statements of the source do not agree with each other, and
the record reports both rather than choosing.** Its levitation relation
names a symbol that makes it differ from the standard loop force balance
by exactly a factor of two, and the current its printed inductances and
maximum charging current induce is not quite the operational current it
prints elsewhere. Neither is adjusted, neither is gated, and the
non-claims name both.

**The configuration's own levitation force is superseded here, not
repeated.** It evaluates ``F = m dB/dz`` on a single turn, because the
configuration carries no turn count; the source's coil has 716 of them.
The record reports both forces and takes its margin from the winding,
which is the one the design has to supply.

**Nothing here is integrated in time and nothing runs backwards.** No
filed source in this family prints a confinement time, a fusion power or
a gain, so none is implied from the others.

Design record: ADR 0005.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_levitated_dipole_core.configuration import DeviceConfiguration
from scpn_levitated_dipole_core.errors import DeviceConfigurationError
from scpn_levitated_dipole_core.parameters import require_positive
from scpn_levitated_dipole_core.physics.charging import (
    charge_transfer_ratio,
    current_agreement_ratio,
    induced_current_a,
)
from scpn_levitated_dipole_core.physics.coil import (
    amp_turns_a,
    current_centroid_diameter_m,
    dipole_moment_a_m2,
    require_turns,
)
from scpn_levitated_dipole_core.physics.constants import AMPERES_PER_KILOAMPERE
from scpn_levitated_dipole_core.physics.levitation import (
    levitation_margin,
    required_field_gradient_t_per_m,
    required_radial_field_as_printed_t,
    required_radial_field_from_loop_force_t,
)
from scpn_levitated_dipole_core.physics.plasma import (
    field_from_perpendicular_beta_t,
    perpendicular_beta_from_anisotropic,
    require_above,
    required_volume_expansion,
    resonant_field_t,
)

LEVEL0_SCHEMA: Final = "scpn.levitated-dipole-level0-physics.v1"
LEVEL0_SCHEMA_VERSION: Final = "1.0.0"

LEVEL0_NON_CLAIMS: Final = (
    (
        "closed-form evaluation of published levitated-dipole relations on a "
        "declared winding, charging circuit, heating system and plasma; "
        "nothing here is integrated in time"
    ),
    (
        "no equilibrium is solved, no transport equation is evaluated and no "
        "stability spectrum is computed anywhere here"
    ),
    (
        "the source's levitation relation names its length symbol the "
        "average diameter of the coil, which makes it differ from the "
        "standard loop force balance by exactly a factor of two; both forms "
        "are reported, the source prints no value of that field, and no "
        "reading of the authors' intent is asserted"
    ),
    (
        "the conductor current the printed inductances and maximum charging "
        "current induce is not the operational current the source prints "
        "elsewhere; the ratio is reported and nothing is gated on it, "
        "because the source does not reconcile the two"
    ),
    (
        "the field at the pressure peak is derived by inverting the source's "
        "own beta definition on its own printed numbers; the source prints "
        "no field there and this is not an anchor"
    ),
    (
        "the flux-tube volume expansion is a consistency instrument: the "
        "source prints the adiabatic index and a pressure ratio it says can "
        "be reached, and prints no flux-tube volume anywhere"
    ),
    (
        "the cyclotron resonance is non-relativistic, while the source's own "
        "hot electrons reach tens of kiloelectronvolts, where the "
        "relativistic mass shift moves the resonance"
    ),
    (
        "the plasma quantities describe one published discharge of one "
        "experiment and are not a design point, an average or a projection"
    ),
    (
        "the configuration's own levitation force is a single-turn estimate "
        "and is reported as one; the margin here is taken from the winding's "
        "moment, and the two differ by the declared turn count"
    ),
    (
        "no value describes or validates any real machine or shot; an anchor "
        "reproduces a number a filed source prints and nothing further"
    ),
)


@dataclass(frozen=True, slots=True)
class WindingDeclaration:
    """Declared winding of the floating coil.

    Parameters
    ----------
    turns
        Turn count of the winding; strictly positive and not required
        to be a whole number, because the filed source prints a
        fractional count for the charging coil.

    Raises
    ------
    DeviceConfigurationError
        If the count is non-finite or not strictly positive.

    Notes
    -----
    The radius and the conductor current are not here. They belong to
    the configuration's own floating coil, which owns them.
    """

    turns: float

    def __post_init__(self) -> None:
        """Validate the declared winding.

        Raises
        ------
        DeviceConfigurationError
            If the count is non-finite or not strictly positive.
        """
        require_turns("turns", self.turns)

    def to_record(self) -> dict[str, Any]:
        """Project the declaration to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per declared field.
        """
        return {"turns": self.turns}


@dataclass(frozen=True, slots=True)
class ChargingDeclaration:
    """Declared inductive charging circuit of the floating coil.

    Parameters
    ----------
    charging_coil_current_a
        Charging-coil current before its discharge, in amperes;
        strictly positive.
    floating_coil_self_inductance_h
        Self-inductance of the floating coil, in henries; strictly
        positive.
    mutual_inductance_h
        Mutual inductance between the two coils, in henries; strictly
        positive and **below the floating coil's self-inductance is not
        required** — the filed source prints a mutual inductance several
        times the floating coil's own, which is what makes the transfer
        ratio exceed one.

    Raises
    ------
    DeviceConfigurationError
        If any value is non-finite or not strictly positive.
    """

    charging_coil_current_a: float
    floating_coil_self_inductance_h: float
    mutual_inductance_h: float

    def __post_init__(self) -> None:
        """Validate the declared charging circuit.

        Raises
        ------
        DeviceConfigurationError
            If any value is non-finite or not strictly positive.
        """
        require_positive("charging_coil_current_a", self.charging_coil_current_a)
        require_positive(
            "floating_coil_self_inductance_h",
            self.floating_coil_self_inductance_h,
        )
        require_positive("mutual_inductance_h", self.mutual_inductance_h)

    def to_record(self) -> dict[str, Any]:
        """Project the declaration to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per declared field.
        """
        return {
            "charging_coil_current_a": self.charging_coil_current_a,
            "floating_coil_self_inductance_h": (self.floating_coil_self_inductance_h),
            "mutual_inductance_h": self.mutual_inductance_h,
        }


@dataclass(frozen=True, slots=True)
class HeatingDeclaration:
    """Declared electron cyclotron heating system.

    Parameters
    ----------
    frequencies_hz
        Injected microwave frequencies, in hertz; non-empty and every
        entry strictly positive. The filed source drives two sources at
        once, so this is a tuple rather than a single value.
    total_power_kw
        Total injected microwave power, in kilowatts; strictly
        positive.

    Raises
    ------
    DeviceConfigurationError
        If the tuple is empty, or any value is non-finite or not
        strictly positive.
    """

    frequencies_hz: tuple[float, ...]
    total_power_kw: float

    def __post_init__(self) -> None:
        """Validate the declared heating system.

        Raises
        ------
        DeviceConfigurationError
            If the tuple is empty, or any value is non-finite or not
            strictly positive.
        """
        if not self.frequencies_hz:
            raise DeviceConfigurationError(
                "frequencies_hz: must declare at least one frequency, got ()"
            )
        for index, frequency in enumerate(self.frequencies_hz):
            require_positive(f"frequencies_hz[{index}]", frequency)
        require_positive("total_power_kw", self.total_power_kw)

    def to_record(self) -> dict[str, Any]:
        """Project the declaration to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per declared field.
        """
        return {
            "frequencies_hz": list(self.frequencies_hz),
            "total_power_kw": self.total_power_kw,
        }


@dataclass(frozen=True, slots=True)
class PlasmaDeclaration:
    """Declared plasma state of one published discharge.

    Parameters
    ----------
    peak_perpendicular_pressure_pa
        Perpendicular plasma pressure at the pressure peak, in pascals;
        strictly positive.
    combined_beta
        The anisotropy-weighted beta the source quotes for the
        discharge; strictly positive. **No upper bound is imposed**: a
        dipole is stable above unity by design and the source says so
        explicitly, so a beta over one is the regime rather than an
        error.
    pressure_anisotropy
        Ratio of perpendicular to parallel pressure; strictly above
        one, because the state this describes is an anisotropic one and
        a ratio at or below one is a different plasma.
    adiabatic_index
        Ratio of specific heats used in the interchange criterion;
        strictly above one.
    core_to_edge_pressure_ratio
        Core-to-edge pressure ratio the source states is reachable;
        strictly above one.

    Raises
    ------
    DeviceConfigurationError
        If any value is non-finite, not strictly positive, or fails to
        exceed the bound its field documents.
    """

    peak_perpendicular_pressure_pa: float
    combined_beta: float
    pressure_anisotropy: float
    adiabatic_index: float
    core_to_edge_pressure_ratio: float

    def __post_init__(self) -> None:
        """Validate the declared plasma state.

        Raises
        ------
        DeviceConfigurationError
            If any value is non-finite, not strictly positive, or fails
            to exceed the bound its field documents.
        """
        require_positive(
            "peak_perpendicular_pressure_pa", self.peak_perpendicular_pressure_pa
        )
        require_positive("combined_beta", self.combined_beta)
        require_above("pressure_anisotropy", self.pressure_anisotropy, 1.0)
        require_above("adiabatic_index", self.adiabatic_index, 1.0)
        require_above(
            "core_to_edge_pressure_ratio", self.core_to_edge_pressure_ratio, 1.0
        )

    def to_record(self) -> dict[str, Any]:
        """Project the declaration to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per declared field.
        """
        return {
            "peak_perpendicular_pressure_pa": (self.peak_perpendicular_pressure_pa),
            "combined_beta": self.combined_beta,
            "pressure_anisotropy": self.pressure_anisotropy,
            "adiabatic_index": self.adiabatic_index,
            "core_to_edge_pressure_ratio": self.core_to_edge_pressure_ratio,
        }


@dataclass(frozen=True, slots=True)
class OperatingPoint:
    """Composed level-0 operating point of one configuration.

    Parameters
    ----------
    winding_amp_turns_a
        Ampere-turns of the floating coil at its declared conductor
        current.
    current_centroid_diameter_m
        Diameter of the current centroid, the symbol the source's
        levitation relation names.
    dipole_moment_a_m2
        Magnetic moment of the winding.
    coil_weight_n
        Weight of the floating coil.
    required_radial_field_as_printed_t
        Radial field the source's relation gives read literally.
    required_radial_field_from_loop_force_t
        Radial field the standard loop force balance gives.
    radial_field_form_ratio
        The second over the first. It is exactly two, and the record
        carries it so the discrepancy is a number rather than a remark.
    required_field_gradient_t_per_m
        Axial gradient that would just support the coil.
    declared_field_gradient_t_per_m
        Axial gradient the configuration declares.
    single_turn_levitation_force_n
        Axial force the configuration's own estimate reports. It uses
        the **single-turn** magnetic moment, because the configuration
        carries no turn count, so it is smaller than the winding's by
        exactly that count and cannot balance the weight at any
        plausible gradient.
    winding_levitation_force_n
        Axial force the declared gradient produces on the **winding**,
        which is the force the source's own design has to supply.
    levitation_margin
        The winding force as a multiple of the weight.
    charge_transfer_ratio
        Floating-coil current per unit of charging-coil current.
    induced_conductor_current_a
        Conductor current the declared charging circuit induces.
    induced_amp_turns_a
        Ampere-turns that current carries through the declared winding.
    declared_conductor_current_a
        Conductor current the configuration declares.
    induced_to_declared_current_ratio
        The induced current over the declared one; reported, not gated.
    resonant_fields_t
        Field at which each declared frequency resonates, in the
        declared order.
    perpendicular_beta
        Perpendicular beta implied by the declared combined beta and
        the declared anisotropy.
    field_at_pressure_peak_t
        Field the perpendicular beta and pressure imply; derived.
    required_volume_expansion
        Flux-tube expansion the declared pressure ratio demands.
    """

    winding_amp_turns_a: float
    current_centroid_diameter_m: float
    dipole_moment_a_m2: float
    coil_weight_n: float
    required_radial_field_as_printed_t: float
    required_radial_field_from_loop_force_t: float
    radial_field_form_ratio: float
    required_field_gradient_t_per_m: float
    declared_field_gradient_t_per_m: float
    single_turn_levitation_force_n: float
    winding_levitation_force_n: float
    levitation_margin: float
    charge_transfer_ratio: float
    induced_conductor_current_a: float
    induced_amp_turns_a: float
    declared_conductor_current_a: float
    induced_to_declared_current_ratio: float
    resonant_fields_t: tuple[float, ...]
    perpendicular_beta: float
    field_at_pressure_peak_t: float
    required_volume_expansion: float

    def to_record(self) -> dict[str, Any]:
        """Project the operating point to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per field, in the declaration order of the class.
        """
        return {
            "winding_amp_turns_a": self.winding_amp_turns_a,
            "current_centroid_diameter_m": self.current_centroid_diameter_m,
            "dipole_moment_a_m2": self.dipole_moment_a_m2,
            "coil_weight_n": self.coil_weight_n,
            "required_radial_field_as_printed_t": (
                self.required_radial_field_as_printed_t
            ),
            "required_radial_field_from_loop_force_t": (
                self.required_radial_field_from_loop_force_t
            ),
            "radial_field_form_ratio": self.radial_field_form_ratio,
            "required_field_gradient_t_per_m": (self.required_field_gradient_t_per_m),
            "declared_field_gradient_t_per_m": (self.declared_field_gradient_t_per_m),
            "single_turn_levitation_force_n": (self.single_turn_levitation_force_n),
            "winding_levitation_force_n": self.winding_levitation_force_n,
            "levitation_margin": self.levitation_margin,
            "charge_transfer_ratio": self.charge_transfer_ratio,
            "induced_conductor_current_a": self.induced_conductor_current_a,
            "induced_amp_turns_a": self.induced_amp_turns_a,
            "declared_conductor_current_a": self.declared_conductor_current_a,
            "induced_to_declared_current_ratio": (
                self.induced_to_declared_current_ratio
            ),
            "resonant_fields_t": list(self.resonant_fields_t),
            "perpendicular_beta": self.perpendicular_beta,
            "field_at_pressure_peak_t": self.field_at_pressure_peak_t,
            "required_volume_expansion": self.required_volume_expansion,
        }


@dataclass(frozen=True, slots=True)
class Level0Physics:
    """Composed level-0 record of one configuration.

    Parameters
    ----------
    configuration_digest_sha256
        Digest of the configuration the record was built from.
    winding
        The declared winding.
    charging
        The declared inductive charging circuit.
    heating
        The declared electron cyclotron heating system.
    plasma
        The declared plasma state.
    operating_point
        The composed operating point.
    """

    configuration_digest_sha256: str
    winding: WindingDeclaration
    charging: ChargingDeclaration
    heating: HeatingDeclaration
    plasma: PlasmaDeclaration
    operating_point: OperatingPoint

    def to_record(self) -> dict[str, Any]:
        """Project the record to a JSON-serialisable object.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with its non-claims.
        """
        return {
            "schema": LEVEL0_SCHEMA,
            "schema_version": LEVEL0_SCHEMA_VERSION,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "winding": self.winding.to_record(),
            "charging": self.charging.to_record(),
            "heating": self.heating.to_record(),
            "plasma": self.plasma.to_record(),
            "operating_point": self.operating_point.to_record(),
            "non_claims": list(LEVEL0_NON_CLAIMS),
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the record canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact record.

        Returns
        -------
        str
            SHA-256 of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def declared_conductor_current_a(configuration: DeviceConfiguration) -> float:
    """Return the configuration's conductor current in amperes.

    Parameters
    ----------
    configuration
        Validated levitated-dipole configuration.

    Returns
    -------
    float
        The coil current the configuration declares, converted from
        kiloamperes once.
    """
    return configuration.coil.coil_current_ka * AMPERES_PER_KILOAMPERE


def level0_physics(
    configuration: DeviceConfiguration,
    winding: WindingDeclaration,
    charging: ChargingDeclaration,
    heating: HeatingDeclaration,
    plasma: PlasmaDeclaration,
) -> Level0Physics:
    """Compose the level-0 physics record of one validated configuration.

    Parameters
    ----------
    configuration
        Validated levitated-dipole configuration supplying the coil's
        radius, conductor current and mass and the levitation gradient.
    winding
        Declared winding.
    charging
        Declared inductive charging circuit.
    heating
        Declared electron cyclotron heating system.
    plasma
        Declared plasma state.

    Returns
    -------
    Level0Physics
        The composed record.

    Raises
    ------
    DeviceConfigurationError
        If a declared value leaves its documented interval; the
        refusals name the field.
    """
    radius = configuration.coil.coil_radius_m
    diameter = current_centroid_diameter_m(radius)
    ampere_turns = amp_turns_a(winding.turns, configuration.coil.coil_current_ka)
    moment = dipole_moment_a_m2(radius, ampere_turns)
    weight = configuration.coil.weight_n()
    printed_field = required_radial_field_as_printed_t(weight, diameter, ampere_turns)
    loop_field = required_radial_field_from_loop_force_t(weight, radius, ampere_turns)
    induced = induced_current_a(
        charging.charging_coil_current_a,
        charging.mutual_inductance_h,
        charging.floating_coil_self_inductance_h,
    )
    declared_current = declared_conductor_current_a(configuration)
    winding_force = moment * configuration.levitation.field_gradient_t_per_m
    perpendicular = perpendicular_beta_from_anisotropic(
        plasma.combined_beta, plasma.pressure_anisotropy
    )
    return Level0Physics(
        configuration_digest_sha256=configuration.digest_sha256(),
        winding=winding,
        charging=charging,
        heating=heating,
        plasma=plasma,
        operating_point=OperatingPoint(
            winding_amp_turns_a=ampere_turns,
            current_centroid_diameter_m=diameter,
            dipole_moment_a_m2=moment,
            coil_weight_n=weight,
            required_radial_field_as_printed_t=printed_field,
            required_radial_field_from_loop_force_t=loop_field,
            radial_field_form_ratio=loop_field / printed_field,
            required_field_gradient_t_per_m=required_field_gradient_t_per_m(
                weight, moment
            ),
            declared_field_gradient_t_per_m=(
                configuration.levitation.field_gradient_t_per_m
            ),
            single_turn_levitation_force_n=configuration.levitation_force_n(),
            winding_levitation_force_n=winding_force,
            levitation_margin=levitation_margin(winding_force, weight),
            charge_transfer_ratio=charge_transfer_ratio(
                charging.mutual_inductance_h,
                charging.floating_coil_self_inductance_h,
            ),
            induced_conductor_current_a=induced,
            induced_amp_turns_a=induced * winding.turns,
            declared_conductor_current_a=declared_current,
            induced_to_declared_current_ratio=current_agreement_ratio(
                induced, declared_current
            ),
            resonant_fields_t=tuple(
                resonant_field_t(frequency) for frequency in heating.frequencies_hz
            ),
            perpendicular_beta=perpendicular,
            field_at_pressure_peak_t=field_from_perpendicular_beta_t(
                plasma.peak_perpendicular_pressure_pa, perpendicular
            ),
            required_volume_expansion=required_volume_expansion(
                plasma.core_to_edge_pressure_ratio, plasma.adiabatic_index
            ),
        ),
    )
