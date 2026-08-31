<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Levitated Dipole Core — ADR 0002: device configuration model
-->

# ADR 0002 — Device configuration model and evidence-maturity semantics

**Status:** accepted (2026-08-31)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The repository was established architecture-only (ADR 0001). The first
capability lane is the device configuration model for the single
registry configuration this repository owns (`levitated_dipole`). The
claim boundary and repository-level `evidence_maturity` semantics
follow the family pilot.

## Decision

1. The package `scpn_levitated_dipole_core` implements the device
   configuration model as frozen, strictly typed value objects: the
   floating coil (radius, current, mass, superconducting flag) and the
   levitation environment (axial field gradient at the floating-coil
   position).
2. Claim boundary — identical to the family pilot: internal-consistency
   validation, cited textbook estimates with documented bounds,
   canonical serialisation with SHA-256 digest, and the data-only SPO
   registry pin. No claim about any real machine; every exercised
   parameter set is a synthetic test fixture.
3. Hard invariant: the floating coil is superconducting — persistent
   current without leads is what makes levitated-dipole confinement
   possible (LDX-class design; D. T. Garnier et al., Fusion Eng. Des.
   81 (2006) 2371).
4. Derived quantities with citations: the coil magnetic moment
   ``m = pi R^2 I`` and the axial force on a dipole in a field
   gradient ``F = m dB/dz`` (standard magnetostatics). Advisory
   finding, reported by `consistency_report()` and never clamped: a
   levitation force below the coil weight ``M g`` — levitated
   equilibrium is not expected there.
5. Repository-level `evidence_maturity` = the highest state claimed by
   any capability entry; per-capability states are the authoritative
   claim surface.
6. Everything else is unchanged: review-only/non-actionable SPO
   profile, no adapter implementation, empty solver seams,
   `not_federated` Studio state, independent machine-protection veto,
   all non-claims.

## Consequences

- The Studio descriptor's `capabilities` array carries its first item
  (schema 1.1.0 data change only).
- The reactor-domain validator gains the populated-capabilities branch
  with the ceiling rule.
- Later lanes (dipole flux-coordinate diagnostic semantics, safety
  envelope) build on these types; maturity advances per capability only
  with the evidence the family standard requires.
