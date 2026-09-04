# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — device geometry package

"""Tessellated and B-rep models of the coil set. Design record: ADR 0006."""

from __future__ import annotations

from scpn_levitated_dipole_core.geometry.model import (
    BODY_NAMES_BY_STATE,
    CHARGING_BODY_NAMES,
    LEVITATED_BODY_NAMES,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_UNITS,
    STATE_CHARGING,
    STATE_LEVITATED,
    STATES,
    Annulus,
    CoilSet,
    DeviceModel3D,
    build_model,
)

__all__ = [
    "BODY_NAMES_BY_STATE",
    "CHARGING_BODY_NAMES",
    "LEVITATED_BODY_NAMES",
    "MODEL_NON_CLAIMS",
    "MODEL_SCHEMA",
    "MODEL_UNITS",
    "STATES",
    "STATE_CHARGING",
    "STATE_LEVITATED",
    "Annulus",
    "CoilSet",
    "DeviceModel3D",
    "build_model",
]
