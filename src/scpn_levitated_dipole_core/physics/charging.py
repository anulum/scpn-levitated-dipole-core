# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Levitated Dipole Core — putting current into a coil with no leads

"""How current reaches a coil that has no electrical contacts.

The floating coil is charged **inductively**: it is closed into a
persistent loop and the charging coil around it is discharged, driving
current into it through their mutual inductance. There are no
high-current leads to make and break, which is what allows the ring to
float free.

For a closed superconducting loop the flux linkage is conserved, so
discharging the charging coil from ``I_C`` to zero leaves

    I_F = (M_CF / L_F) I_C

in the floating coil. The two inductances and the charging current are
all printed by the filed source, and so is the ampere-turn figure the
relation produces for one worked case — which makes this the one place
in this family where a printed number is recovered from three other
printed numbers through a relation, rather than merely restated.

Nothing here is integrated in time. Whether the transfer completes, how
fast, and what the coupling loses are questions this record does not
ask.
"""

from __future__ import annotations

from scpn_levitated_dipole_core.parameters import require_positive


def charge_transfer_ratio(
    mutual_inductance_h: float, floating_coil_self_inductance_h: float
) -> float:
    """Return the flux-conserving current transfer ratio.

    Parameters
    ----------
    mutual_inductance_h
        Mutual inductance between the charging and floating coils, in
        henries; strictly positive.
    floating_coil_self_inductance_h
        Self-inductance of the floating coil, in henries; strictly
        positive.

    Returns
    -------
    float
        ``M_CF / L_F``, dimensionless: the floating-coil current per
        unit of charging-coil current.

    Raises
    ------
    DeviceConfigurationError
        If either inductance leaves its documented interval.
    """
    require_positive("mutual_inductance_h", mutual_inductance_h)
    require_positive("floating_coil_self_inductance_h", floating_coil_self_inductance_h)
    return mutual_inductance_h / floating_coil_self_inductance_h


def induced_current_a(
    charging_coil_current_a: float,
    mutual_inductance_h: float,
    floating_coil_self_inductance_h: float,
) -> float:
    """Return the conductor current induced in the floating coil.

    Parameters
    ----------
    charging_coil_current_a
        Charging-coil current before its discharge, in amperes;
        strictly positive.
    mutual_inductance_h
        Mutual inductance between the coils, in henries; strictly
        positive.
    floating_coil_self_inductance_h
        Self-inductance of the floating coil, in henries; strictly
        positive.

    Returns
    -------
    float
        ``I_F = (M_CF / L_F) I_C`` in amperes.

    Raises
    ------
    DeviceConfigurationError
        If any input leaves its documented interval.
    """
    require_positive("charging_coil_current_a", charging_coil_current_a)
    return charging_coil_current_a * charge_transfer_ratio(
        mutual_inductance_h, floating_coil_self_inductance_h
    )


def current_agreement_ratio(induced_a: float, declared_a: float) -> float:
    """Return the induced conductor current over the declared one.

    Parameters
    ----------
    induced_a
        Current the transfer relation gives, in amperes; strictly
        positive.
    declared_a
        Current the configuration declares, in amperes; strictly
        positive.

    Returns
    -------
    float
        ``I_induced / I_declared``, dimensionless.

    Raises
    ------
    DeviceConfigurationError
        If either input leaves its documented interval.

    Notes
    -----
    **Reported, never gated.** Both currents are printed by the filed
    source — one as the charging coil's maximum operating current
    together with the two inductances, the other as the floating coil's
    operational current — and the source does not reconcile them. A
    threshold here would be a criterion no source states, so the record
    carries the ratio and says what it is.
    """
    require_positive("induced_a", induced_a)
    require_positive("declared_a", declared_a)
    return induced_a / declared_a
