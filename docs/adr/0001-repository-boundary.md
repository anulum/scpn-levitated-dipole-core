<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Levitated Dipole Core — ADR 0001: repository boundary
-->

# ADR 0001 — Repository boundary and ownership

**Status:** accepted (2026-08-30)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The SCPN reactor portfolio assigns every built-in configuration of the SCPN
Phase Orchestrator reactor registry (version `1.0.0`, 32 configurations) to
exactly one device-family repository. The levitated dipole shares the
`magnetic_open` registry family with mirrors and the cusp yet confines on
closed dipolar field lines around a floating internal coil; a boundary
decision was needed on whether it shares a repository with any neighbour.

## Decision

1. `SCPN-LEVITATED-DIPOLE-CORE` owns exactly one registry configuration:
   `levitated_dipole` (closed dipole field).
2. The repository owns device-level truth only: dipole configuration
   policy, levitation-system semantics (cooldown, charge, levitation
   hand-off, catcher boundary), lifecycle definitions spanning cryogenic
   and plasma timescales, dipole flux-coordinate diagnostic and clock
   declarations, actuator-response model boundaries, the safety-envelope
   declaration, and the device-owned CONTROL adapter specification.
3. Solver mathematics remains in `SCPN-FUSION-CORE` until an exact surface
   passes the family migration gate. No solver code is copied here.
4. Typed semantics remain in `SCPN-PHASE-ORCHESTRATOR` (review-only).
   Admission and `ControlAction` formation remain exclusively in
   `SCPN-CONTROL`. Machine protection remains independent with the final
   veto. Presentation remains in `SCPN-STUDIO`; this project is
   `not_federated`.
5. The repository starts, and remains until evidenced otherwise, at
   `architecture_only` with empty capability and claim inventories.

## Alternatives considered

- **Folding the dipole into the mirror repository** (same registry
  family): rejected — the dipole has no axial loss cone; its confinement
  is on closed field lines with compressibility-governed stability, its
  driver is a levitated internal superconducting coil, and its lifecycle
  is dominated by cryogenic levitation phases (surfaces 1, 2, and 3 all
  differ).
- **Treating the dipole as a toroidal closed-field device** alongside
  tokamaks: rejected — there is no external toroidal-field circuit, no
  driven current, and no comparable shot lifecycle; only the closed-line
  property is shared.
- **Absorbing solver code at scaffold time**: rejected — violates the
  migration gate.

## Consequences

- Downstream consumers get one stable identity for the levitated-dipole
  configuration and a manifest to bind against.
- The validator fails on any capability or claim entry while maturity is
  `architecture_only`.
- Boundary changes require a portfolio-level map change first; a future
  ADR records any such change here.
