<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Levitated Dipole Core — Architecture summary
-->

# Architecture summary

`SCPN-LEVITATED-DIPOLE-CORE` is the device-family owner for
levitated-dipole systems inside the SCPN Reactor Systems Research Group.
The repository is currently `architecture_only`: it defines the device
boundary, its ecosystem contracts, and the validation tooling that enforces
both, and it implements no reactor capability.

The authoritative architecture record is
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). The ownership decision and
its consequences are fixed in
[`docs/adr/0001-repository-boundary.md`](docs/adr/0001-repository-boundary.md).

Boundary in one paragraph: this repository owns levitated-dipole plant and
experiment truth — configuration policy for closed-dipole-field confinement
around a magnetically levitated superconducting coil with
compressibility-governed stability and turbulent inward pinch, lifecycle
semantics spanning cryogenic and plasma phases (cooldown, charge, lift,
levitated operation, de-levitation), dipole flux-coordinate diagnostic and
clock declarations, actuator-response boundaries, safety-envelope
declarations, and the device-owned CONTROL adapter specification. Solver
mathematics stays in `SCPN-FUSION-CORE`; typed semantics stay in
`SCPN-PHASE-ORCHESTRATOR` (review-only); admitted control actions are
formed only by `SCPN-CONTROL`; independent machine protection (including
the levitation-safety chain) keeps the final veto; portfolio presentation
belongs to `SCPN-STUDIO`, towards which this project is `not_federated`.
