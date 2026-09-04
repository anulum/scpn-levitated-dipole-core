# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — 3D and CAD model fixtures

"""The coil set as the filed source prints it, and what it does not print.

Every constant below cites the printed page it comes from. The four
values the source does **not** print are named ``DECLARED_`` and each
carries the reading that produced it, so a reader can see exactly where
the record stops repeating the source and starts declaring.

Printed-to-PDF page offset is constant: PDF page = printed page - 2370.
Every value was read from a page rendered at 180 dpi, never from the
PDF text layer.
"""

from __future__ import annotations

from typing import Final

from physics_fixtures import anchor_configuration
from scpn_levitated_dipole_core.configuration import DeviceConfiguration
from scpn_levitated_dipole_core.geometry import Annulus, CoilSet

#: Printed page 2374: "The inner sub-coil has inner diameter of 0.552 m
#: and height of 0.069 m".
PRINTED_INNER_SUBCOIL_INNER_DIAMETER_M: Final = 0.552
PRINTED_INNER_SUBCOIL_HEIGHT_M: Final = 0.069

#: Printed page 2374: "the next has inner diameter of 0.555 m and height
#: of 0.125 m".
PRINTED_MIDDLE_SUBCOIL_INNER_DIAMETER_M: Final = 0.555
PRINTED_MIDDLE_SUBCOIL_HEIGHT_M: Final = 0.125

#: Printed page 2374: "the outer sub-coil has an inner diameter of
#: 0.585 m, outer diameter of 0.764 m, and height of 0.162 m". This is the
#: only sub-coil whose three dimensions are all printed.
PRINTED_OUTER_SUBCOIL_INNER_DIAMETER_M: Final = 0.585
PRINTED_OUTER_SUBCOIL_OUTER_DIAMETER_M: Final = 0.764
PRINTED_OUTER_SUBCOIL_HEIGHT_M: Final = 0.162

#: Printed page 2374: the cryostat's stainless steel vacuum vessel,
#: "inner diameter 0.445 m, outer limiter diameter 1.14 m".
PRINTED_CRYOSTAT_INNER_DIAMETER_M: Final = 0.445
PRINTED_CRYOSTAT_OUTER_DIAMETER_M: Final = 1.140

#: Printed page 2374: the charging station the C-coil surrounds.
PRINTED_CHARGING_STATION_DIAMETER_M: Final = 1.157

#: Printed page 2374: the C-coil winding pack, "height of 750 mm, and
#: inner and outer diameters of 1300 and 1600 mm".
PRINTED_CHARGING_COIL_INNER_DIAMETER_M: Final = 1.300
PRINTED_CHARGING_COIL_OUTER_DIAMETER_M: Final = 1.600
PRINTED_CHARGING_COIL_HEIGHT_M: Final = 0.750

#: Printed page 2376, Table 2: L-coil winding pack inner and outer
#: diameters in millimetres, its turn count, and the tape it is wound
#: from.
PRINTED_LEVITATION_COIL_INNER_DIAMETER_M: Final = 0.410
PRINTED_LEVITATION_COIL_OUTER_DIAMETER_M: Final = 1.320
PRINTED_LEVITATION_COIL_TURNS: Final = 2800
PRINTED_TAPE_HEIGHT_M: Final = 0.168e-3
PRINTED_TAPE_WIDTH_M: Final = 3.1e-3

#: Printed page 2376: the L-coil's centre support plate, "two 1.0 mm thick
#: copper sheets that are epoxy laminated to either side of a 9.5 mm thick
#: stainless steel plate".
PRINTED_SUPPORT_PLATE_STEEL_M: Final = 9.5e-3
PRINTED_SUPPORT_PLATE_COPPER_M: Final = 1.0e-3

#: Printed page 2376, Table 2: L-F vertical separation.
PRINTED_LEVITATION_SEPARATION_M: Final = 1.610

#: DECLARED, not printed. The source gives no outer diameter for the two
#: inner sub-coils. It calls the pack "continuous", and the printed inner
#: diameters of the next sub-coil out are the only values that make the
#: word true, so each sub-coil's outer diameter is declared to be the next
#: one's inner diameter. The record reports the resulting gaps rather than
#: enforcing them, because this reading is ours and not the source's.
DECLARED_INNER_SUBCOIL_OUTER_DIAMETER_M: Final = PRINTED_MIDDLE_SUBCOIL_INNER_DIAMETER_M
DECLARED_MIDDLE_SUBCOIL_OUTER_DIAMETER_M: Final = PRINTED_OUTER_SUBCOIL_INNER_DIAMETER_M

#: DECLARED, not printed. The source gives the cryostat two diameters and
#: no height, and calls its pressure vessel "toroidal shaped". A body of
#: circular cross-section with those two diameters has a height equal to
#: half their difference, and that is the value declared here. **The model
#: still builds an annular tube**, because the printed data is annular;
#: what the toroidal wording contributes is the missing height and nothing
#: else.
DECLARED_CRYOSTAT_HEIGHT_M: Final = (
    PRINTED_CRYOSTAT_OUTER_DIAMETER_M - PRINTED_CRYOSTAT_INNER_DIAMETER_M
) / 2.0

#: DECLARED, not printed. The source gives the L-coil no height. It prints
#: a 9.5 mm steel plate faced with two 1.0 mm copper sheets, and pancakes
#: wound "to either side" of it from a tape 3.1 mm wide. One tape width
#: per side is the thinnest arrangement those sentences allow, and that is
#: what is declared.
DECLARED_LEVITATION_COIL_HEIGHT_M: Final = (
    PRINTED_SUPPORT_PLATE_STEEL_M
    + 2.0 * PRINTED_SUPPORT_PLATE_COPPER_M
    + 2.0 * PRINTED_TAPE_WIDTH_M
)

#: DECLARED, not printed. The source says the charging coil surrounds the
#: charging station the floating coil is lowered into, and prints no
#: vertical offset between them. Zero is the coaxial, co-centred reading.
DECLARED_CHARGING_OFFSET_M: Final = 0.0

#: Circumferential segments the fixtures build at.
FIXTURE_SEGMENTS: Final = 32


def anchor_coil_set() -> CoilSet:
    """Return the coil set of the filed source, printed where printed.

    Returns
    -------
    CoilSet
        The three sub-coils, the cryostat, the charging coil and the
        levitation coil, with the four declared values named above.
    """
    return CoilSet(
        inner_subcoil=Annulus(
            inner_diameter_m=PRINTED_INNER_SUBCOIL_INNER_DIAMETER_M,
            outer_diameter_m=DECLARED_INNER_SUBCOIL_OUTER_DIAMETER_M,
            height_m=PRINTED_INNER_SUBCOIL_HEIGHT_M,
        ),
        middle_subcoil=Annulus(
            inner_diameter_m=PRINTED_MIDDLE_SUBCOIL_INNER_DIAMETER_M,
            outer_diameter_m=DECLARED_MIDDLE_SUBCOIL_OUTER_DIAMETER_M,
            height_m=PRINTED_MIDDLE_SUBCOIL_HEIGHT_M,
        ),
        outer_subcoil=Annulus(
            inner_diameter_m=PRINTED_OUTER_SUBCOIL_INNER_DIAMETER_M,
            outer_diameter_m=PRINTED_OUTER_SUBCOIL_OUTER_DIAMETER_M,
            height_m=PRINTED_OUTER_SUBCOIL_HEIGHT_M,
        ),
        cryostat=Annulus(
            inner_diameter_m=PRINTED_CRYOSTAT_INNER_DIAMETER_M,
            outer_diameter_m=PRINTED_CRYOSTAT_OUTER_DIAMETER_M,
            height_m=DECLARED_CRYOSTAT_HEIGHT_M,
        ),
        charging_coil=Annulus(
            inner_diameter_m=PRINTED_CHARGING_COIL_INNER_DIAMETER_M,
            outer_diameter_m=PRINTED_CHARGING_COIL_OUTER_DIAMETER_M,
            height_m=PRINTED_CHARGING_COIL_HEIGHT_M,
        ),
        levitation_coil=Annulus(
            inner_diameter_m=PRINTED_LEVITATION_COIL_INNER_DIAMETER_M,
            outer_diameter_m=PRINTED_LEVITATION_COIL_OUTER_DIAMETER_M,
            height_m=DECLARED_LEVITATION_COIL_HEIGHT_M,
        ),
        levitation_separation_m=PRINTED_LEVITATION_SEPARATION_M,
        charging_offset_m=DECLARED_CHARGING_OFFSET_M,
    )


def anchor_device_configuration() -> DeviceConfiguration:
    """Return the configuration the models are built for."""
    return anchor_configuration()
