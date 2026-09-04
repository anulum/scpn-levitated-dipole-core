# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — device capability package

"""Device capability models of the SCPN levitated-dipole device family.

Public surface of the ``device_configuration_model``,
``diagnostic_clock_semantics`` and ``level0_device_physics``
capabilities at ``computational_prototype`` maturity: validated
parameter objects, synthetic diagnostic and clock declarations aligned
with the pinned SPO observability catalogue, what the levitated ring is
as a magnet and what it takes to hold it up, how current reaches a coil
with no electrical leads and what the field confines, documented
consistency estimates, canonical serialisation with SHA-256 digests,
and data-only pins to the SPO registries. No claim about any real
machine or diagnostic is made anywhere in this package.
"""

from __future__ import annotations

from typing import Final

from scpn_levitated_dipole_core.configuration import (
    OWNED_CONFIGURATIONS,
    ConsistencyFinding,
    DeviceConfiguration,
    RegistryBinding,
    configuration_from_bytes,
    configuration_from_record,
)
from scpn_levitated_dipole_core.errors import (
    DeviceConfigurationError,
    DiagnosticPlanError,
)
from scpn_levitated_dipole_core.observability import (
    APPLICABLE_CANDIDATES,
    CATALOGUE_BINDING,
    CandidateProfile,
    ClockKind,
    ClockModel,
    ClockRelation,
    DeferredCandidate,
    DiagnosticChannelPlan,
    DiagnosticPlan,
    FrameKind,
    ObservabilityBinding,
    ObservabilityClass,
    ReferenceFrame,
    SemanticCarrier,
    plan_from_bytes,
    plan_from_record,
)
from scpn_levitated_dipole_core.parameters import (
    STANDARD_GRAVITY_M_S2,
    FloatingCoil,
    LevitationEnvironment,
)
from scpn_levitated_dipole_core.physics import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    ChargingDeclaration,
    HeatingDeclaration,
    Level0Physics,
    OperatingPoint,
    PlasmaDeclaration,
    WindingDeclaration,
    level0_physics,
)
from scpn_levitated_dipole_core.plan_envelope import (
    PlanEnvelope,
    envelope_for_plan,
    envelope_from_bytes,
    envelope_from_record,
    verify_envelope,
)

__version__: Final = "0.1.0.dev0"

__all__ = [
    "APPLICABLE_CANDIDATES",
    "CATALOGUE_BINDING",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "OWNED_CONFIGURATIONS",
    "STANDARD_GRAVITY_M_S2",
    "CandidateProfile",
    "ChargingDeclaration",
    "ClockKind",
    "ClockModel",
    "ClockRelation",
    "ConsistencyFinding",
    "DeferredCandidate",
    "DeviceConfiguration",
    "DeviceConfigurationError",
    "DiagnosticChannelPlan",
    "DiagnosticPlan",
    "DiagnosticPlanError",
    "FloatingCoil",
    "FrameKind",
    "HeatingDeclaration",
    "Level0Physics",
    "LevitationEnvironment",
    "ObservabilityBinding",
    "ObservabilityClass",
    "OperatingPoint",
    "PlanEnvelope",
    "PlasmaDeclaration",
    "ReferenceFrame",
    "RegistryBinding",
    "SemanticCarrier",
    "WindingDeclaration",
    "__version__",
    "configuration_from_bytes",
    "configuration_from_record",
    "envelope_for_plan",
    "envelope_from_bytes",
    "envelope_from_record",
    "level0_physics",
    "plan_from_bytes",
    "plan_from_record",
    "verify_envelope",
]
