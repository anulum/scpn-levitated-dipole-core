# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — level-0 physics anchors

"""Anchors of the level-0 physics, and what is declared instead.

Reproducing a printed value is an anchor, never a claim about that
machine.

Every ``PRINTED_`` constant below appears in the filed source
``docs/internal/external_papers/Garnier_2006_LDX_design_FED81_2371.pdf``,
SHA-256 ``4e3015fd...``, and each names the printed page and the PDF page
it was read from. **They were read off pages rendered at 180 dpi**, never
off the PDF text layer. The printed-page to PDF-page offset is constant
in this source at minus 2371 plus 1, and is given per constant anyway.

**Two things this source anchors are relations, not restatements**, and
they are the reason this family has real anchors at all:

- the electron cyclotron resonance, where the source prints a frequency
  and the field it resonates at, and the standard relation returns the
  printed field;
- the inductive charge transfer, where the source prints two
  inductances, a charging current and the ampere-turns that combination
  produces, and the relation returns the printed ampere-turns.

**One printed value does not reproduce** and is named ``NOT_REPRODUCED_``
for it. **Two printed statements are in tension with each other** and
both are carried, because the source does not reconcile them and neither
do we.
"""

from __future__ import annotations

import math
from typing import Final

from scpn_levitated_dipole_core.configuration import (
    DeviceConfiguration,
    RegistryBinding,
)
from scpn_levitated_dipole_core.parameters import (
    STANDARD_GRAVITY_M_S2,
    FloatingCoil,
    LevitationEnvironment,
)
from scpn_levitated_dipole_core.physics.level0 import (
    ChargingDeclaration,
    HeatingDeclaration,
    PlasmaDeclaration,
    WindingDeclaration,
)

# --- The floating coil, printed p. 2372-2374 / PDF p. 2-4 ---
#: Mass of the floating coil. Printed p. 2373 / PDF p. 3: "The 560 kg
#: floating coil (F-coil)"; repeated p. 2376 / PDF p. 6.
PRINTED_FLOATING_COIL_MASS_KG: Final = 560.0
#: Diameter of the current centroid. Printed p. 2372 / PDF p. 2: "a
#: relatively small, 0.68 m diameter (current centroid), superconducting
#: ring". This is the one dimension of the winding the source states as a
#: single number rather than as sub-coil bounds.
PRINTED_CURRENT_CENTROID_DIAMETER_M: Final = 0.68
#: Turn count of the floating-coil winding pack. Printed p. 2374 / PDF
#: p. 4: "wound in a hybrid single pancake/double layer fashion to form a
#: continuous winding pack (716 turns) without internal joints".
PRINTED_FLOATING_COIL_TURNS: Final = 716.0
#: Operational conductor current of the floating coil. Printed p. 2374 /
#: PDF p. 4: "charge the F-coil inductively to its operational current of
#: 1820 A".
PRINTED_FLOATING_COIL_CURRENT_A: Final = 1820.0

# --- The charging circuit, Table 1 printed p. 2375 / PDF p. 5 ---
#: F-coil self-inductance, Table 1: "F-coil self-inductance, L_F (H)".
PRINTED_FLOATING_COIL_SELF_INDUCTANCE_H: Final = 0.389
#: Mutual inductance, Table 1: "Mutual inductance, M_CF (H)".
PRINTED_MUTUAL_INDUCTANCE_H: Final = 1.69
#: Charging-coil maximum operating current, Table 1.
PRINTED_CHARGING_COIL_MAX_CURRENT_A: Final = 425.0
#: The charging current of the source's own worked case. Printed
#: p. 2376 / PDF p. 6: "For a C-coil charge of 300 A".
PRINTED_WORKED_CASE_CHARGING_CURRENT_A: Final = 300.0
#: The ampere-turns that worked case produces, printed in the same
#: sentence: "corresponding to an F-coil charge of 930 kA T".
PRINTED_WORKED_CASE_FLOATING_COIL_CHARGE_KA_TURNS: Final = 930.0

# --- The heating, printed p. 2372-2373 and p. 2378 ---
#: The two injected microwave frequencies. The higher is printed
#: p. 2373 / PDF p. 3 ("the 6.4 GHz heating frequency source"); both are
#: labelled in Fig. 1 (p. 2372 / PDF p. 2) and named together p. 2378 /
#: PDF p. 8 ("equal amounts from 2.45 and 6.4 GHz sources").
PRINTED_HEATING_FREQUENCIES_HZ: Final = (2.45e9, 6.4e9)
#: Field at which the higher frequency resonates. Printed p. 2373 /
#: PDF p. 3: "the 6.4 GHz heating frequency source (resonant at
#: B = 0.23 T)".
PRINTED_RESONANT_FIELD_T: Final = 0.23
#: Total injected microwave power. Printed p. 2378 / PDF p. 8: "5 kW of
#: total ECRH microwave power was applied".
PRINTED_TOTAL_HEATING_POWER_KW: Final = 5.0

# --- The plasma, printed p. 2372 and p. 2378 ---
#: Perpendicular pressure at the pressure peak of the quoted discharge.
#: Printed p. 2378 / PDF p. 8: "p_perp = 750 Pa".
PRINTED_PEAK_PERPENDICULAR_PRESSURE_PA: Final = 750.0
#: The combined beta of that discharge. Printed p. 2378 / PDF p. 8:
#: "maximum local beta of beta = (2 beta_perp + beta_par)/3 = 21%".
PRINTED_COMBINED_BETA: Final = 0.21
#: Pressure anisotropy assumed for it, printed in the same sentence:
#: "p_perp/p_par = 5".
PRINTED_PRESSURE_ANISOTROPY: Final = 5.0
#: The two betas the source reports for a displaced pressure peak,
#: printed p. 2378 / PDF p. 8: outward by 5 cm gives 23%, inward by 4 cm
#: gives 18%. Carried so the quoted 21% is visibly one of three.
PRINTED_DISPLACED_BETAS: Final = (0.23, 0.18)
#: Adiabatic index of the interchange criterion. Printed p. 2373 /
#: PDF p. 3: "p_0/p_sol < (U_sol/U_0)^gamma where gamma = 5/3".
PRINTED_ADIABATIC_INDEX: Final = 5.0 / 3.0
#: Core-to-edge pressure ratio the source states is reachable. Printed
#: p. 2373 / PDF p. 3: "this ratio can be made very large, i.e.
#: p_0/p_sol > 10^3".
PRINTED_ACHIEVABLE_PRESSURE_RATIO: Final = 1.0e3

# --- Printed elsewhere in the source, carried for context, unused ---
#: Vertical separation of the levitation and floating coils. Table 2,
#: printed p. 2376 / PDF p. 6: "L-F vertical separation (m) 1.610";
#: stated as "~1.61 m above the floating coil" p. 2373 / PDF p. 3.
PRINTED_LEVITATION_SEPARATION_M: Final = 1.610
#: Vacuum vessel diameter. Printed p. 2372 / PDF p. 2: "levitated within
#: a 5 m diameter vacuum vessel".
PRINTED_VACUUM_VESSEL_DIAMETER_M: Final = 5.0

# --- What the source prints and its own numbers do not reproduce ---
#: Printed p. 2373 / PDF p. 3: the floating coil is "comprised of a
#: single 1.5 km length conductor carrying over 1.5 MA turns in a
#: persistent mode". The printed operational current and the printed
#: turn count give 1.303 MA-turns, and the printed inductances at the
#: printed maximum charging current give 1.322 MA-turns. Neither reaches
#: 1.5, so this figure anchors nothing.
NOT_REPRODUCED_AMPERE_TURNS_A: Final = 1.5e6
#: Printed in the same paragraph and consistent with both: the coil's
#: "very large operating current (>1.2 MA)".
PRINTED_OPERATING_CURRENT_FLOOR_A: Final = 1.2e6

# --- Synthetic, pinning nothing ---
SYNTHETIC_REGISTRY_VERSION: Final = "1.0.0"
SYNTHETIC_REGISTRY_DIGEST: Final = (
    "786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090"
)

# --- Derived from the printed values above, never typed ---
#: Mean radius of the current centroid, half the printed diameter. The
#: configuration carries a radius and the source prints a diameter; this
#: is the only place the two meet in the fixtures.
DERIVED_COIL_RADIUS_M: Final = PRINTED_CURRENT_CENTROID_DIAMETER_M / 2.0
#: Conductor current in the kiloamperes the configuration carries.
DERIVED_COIL_CURRENT_KA: Final = PRINTED_FLOATING_COIL_CURRENT_A / 1.0e3
#: Ampere-turns at the printed operational current and turn count.
DERIVED_AMPERE_TURNS_A: Final = (
    PRINTED_FLOATING_COIL_CURRENT_A * PRINTED_FLOATING_COIL_TURNS
)


#: Declared axial field gradient at the floating coil, in tesla per
#: metre. **Not printed anywhere in the filed source**, which gives a
#: levitation-coil separation, an operating field inside that coil's own
#: winding and a required-field relation, and no gradient at the floating
#: coil's position. It is derived here as the gradient that makes
#: ``F = m dB/dz`` exactly balance the printed weight, so the anchor
#: configuration sits at a levitation margin of one rather than at a
#: number chosen to look comfortable — and so that a test asserting the
#: margin is exercising the relation rather than the choice.
DECLARED_FIELD_GRADIENT_T_PER_M: Final = (
    PRINTED_FLOATING_COIL_MASS_KG * STANDARD_GRAVITY_M_S2
) / (math.pi * DERIVED_COIL_RADIUS_M**2 * DERIVED_AMPERE_TURNS_A)


def two_significant_figure_round(value: float, exponent: int) -> float:
    """Round a value to two significant figures at a known exponent.

    Parameters
    ----------
    value
        Value to round.
    exponent
        Decimal exponent of the value's leading digit.

    Returns
    -------
    float
        The value rounded to two significant figures.

    Notes
    -----
    **This source rounds; it does not floor.** That is worth stating
    because a sibling family in this group anchors on a volume that
    floors, measured on two independent values there. A convention
    established in one source is not a property of printed numbers, and
    carrying it across would have been an error here: the resonance
    relation gives 0.2286 T and the source prints 0.23 T, which is the
    rounded value and not the floored one.
    """
    scale = 10.0 ** (1 - exponent)
    return round(value * scale) / scale


def registry_binding() -> RegistryBinding:
    """Build the registry pin the fixtures share.

    Returns
    -------
    RegistryBinding
        The pin this repository's manifest declares.
    """
    return RegistryBinding(
        version=SYNTHETIC_REGISTRY_VERSION,
        digest_sha256=SYNTHETIC_REGISTRY_DIGEST,
    )


def anchor_configuration() -> DeviceConfiguration:
    """Build the configuration the anchors are evaluated on.

    Returns
    -------
    DeviceConfiguration
        The printed floating coil of the filed source. The levitation
        gradient is **declared**, not printed: the source prints a
        levitation coil separation, an operating field in that coil's
        own winding and a required-field relation, and no gradient at
        the floating coil's position anywhere.
    """
    return DeviceConfiguration(
        identifier="levitated_dipole",
        coil=FloatingCoil(
            coil_radius_m=DERIVED_COIL_RADIUS_M,
            coil_current_ka=DERIVED_COIL_CURRENT_KA,
            coil_mass_kg=PRINTED_FLOATING_COIL_MASS_KG,
            superconducting=True,
        ),
        levitation=LevitationEnvironment(
            field_gradient_t_per_m=DECLARED_FIELD_GRADIENT_T_PER_M
        ),
        registry=registry_binding(),
    )


def anchor_winding() -> WindingDeclaration:
    """Build the winding the source prints.

    Returns
    -------
    WindingDeclaration
        The printed 716-turn winding pack.
    """
    return WindingDeclaration(turns=PRINTED_FLOATING_COIL_TURNS)


def anchor_charging() -> ChargingDeclaration:
    """Build the charging circuit at its printed maximum.

    Returns
    -------
    ChargingDeclaration
        The two printed inductances and the printed maximum charging
        current. The source's own worked case at 300 A is exercised
        separately, because that is where it prints the result.
    """
    return ChargingDeclaration(
        charging_coil_current_a=PRINTED_CHARGING_COIL_MAX_CURRENT_A,
        floating_coil_self_inductance_h=(PRINTED_FLOATING_COIL_SELF_INDUCTANCE_H),
        mutual_inductance_h=PRINTED_MUTUAL_INDUCTANCE_H,
    )


def anchor_heating() -> HeatingDeclaration:
    """Build the heating system the source prints.

    Returns
    -------
    HeatingDeclaration
        Both printed frequencies and the printed total power.
    """
    return HeatingDeclaration(
        frequencies_hz=PRINTED_HEATING_FREQUENCIES_HZ,
        total_power_kw=PRINTED_TOTAL_HEATING_POWER_KW,
    )


def anchor_plasma() -> PlasmaDeclaration:
    """Build the plasma state of the source's quoted discharge.

    Returns
    -------
    PlasmaDeclaration
        The printed perpendicular pressure, combined beta and
        anisotropy of one published discharge, with the printed
        adiabatic index and the printed achievable pressure ratio.
    """
    return PlasmaDeclaration(
        peak_perpendicular_pressure_pa=(PRINTED_PEAK_PERPENDICULAR_PRESSURE_PA),
        combined_beta=PRINTED_COMBINED_BETA,
        pressure_anisotropy=PRINTED_PRESSURE_ANISOTROPY,
        adiabatic_index=PRINTED_ADIABATIC_INDEX,
        core_to_edge_pressure_ratio=PRINTED_ACHIEVABLE_PRESSURE_RATIO,
    )
