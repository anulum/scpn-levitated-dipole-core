# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — level-0 physics package

"""Level-0 physics of the levitated-dipole family.

Four modules, one subsystem each, and a fifth that composes them:
:mod:`coil` for the magnet the ring is, :mod:`levitation` for what holds
it up, :mod:`charging` for how current reaches a coil with no leads, and
:mod:`plasma` for what the field confines. :mod:`level0` declares what
the configuration does not carry and evaluates the four on it.

Every relation here is closed form and taken from the filed source.
Design record: ADR 0005.
"""

from __future__ import annotations

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
from scpn_levitated_dipole_core.physics.constants import (
    AMPERES_PER_KILOAMPERE,
    ELECTRON_MASS_KG,
    ELEMENTARY_CHARGE_C,
    MU0,
    PI,
)
from scpn_levitated_dipole_core.physics.level0 import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    ChargingDeclaration,
    HeatingDeclaration,
    Level0Physics,
    OperatingPoint,
    PlasmaDeclaration,
    WindingDeclaration,
    declared_conductor_current_a,
    level0_physics,
)
from scpn_levitated_dipole_core.physics.levitation import (
    levitation_margin,
    required_field_gradient_t_per_m,
    required_radial_field_as_printed_t,
    required_radial_field_from_loop_force_t,
)
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

__all__ = [
    "AMPERES_PER_KILOAMPERE",
    "ELECTRON_MASS_KG",
    "ELEMENTARY_CHARGE_C",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "MU0",
    "PI",
    "ChargingDeclaration",
    "HeatingDeclaration",
    "Level0Physics",
    "OperatingPoint",
    "PlasmaDeclaration",
    "WindingDeclaration",
    "amp_turns_a",
    "anisotropic_beta",
    "charge_transfer_ratio",
    "current_agreement_ratio",
    "current_centroid_diameter_m",
    "declared_conductor_current_a",
    "dipole_moment_a_m2",
    "field_from_perpendicular_beta_t",
    "induced_current_a",
    "level0_physics",
    "levitation_margin",
    "marginal_pressure_ratio",
    "perpendicular_beta",
    "perpendicular_beta_from_anisotropic",
    "require_above",
    "require_turns",
    "required_field_gradient_t_per_m",
    "required_radial_field_as_printed_t",
    "required_radial_field_from_loop_force_t",
    "required_volume_expansion",
    "resonant_field_t",
]
