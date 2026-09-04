# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — physical constants of the level-0 models

"""Physical constants shared by the level-0 models, in SI units.

Nothing here describes a device.

**On the permeability.** Two values are in use across this repository
group: the pre-2019 exact ``4e-7 pi`` and the CODATA measured value
``1.25663706212e-6``. They differ by about five parts in ten thousand
million. This module uses the first, matching the closest structural
sibling in the group, and the choice cannot reach any result here: the
only printed quantity it touches is a plasma beta the source states to
two significant figures.
"""

from __future__ import annotations

import math
from typing import Final

#: Vacuum permeability ``4e-7 pi``.
MU0: Final = 4.0e-7 * math.pi
#: Electron rest mass in kilograms (CODATA).
ELECTRON_MASS_KG: Final = 9.1093837139e-31
#: Elementary charge in coulombs (exact SI 2019 value).
ELEMENTARY_CHARGE_C: Final = 1.602176634e-19
#: ``pi`` as the correctly rounded double.
PI: Final = math.pi
#: Amperes in a kiloampere. The configuration carries the conductor
#: current in kiloamperes and every relation here is stated in amperes.
AMPERES_PER_KILOAMPERE: Final = 1.0e3
