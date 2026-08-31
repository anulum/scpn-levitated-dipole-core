<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Levitated Dipole Core — ROADMAP
-->

# Roadmap

Planned work and implemented capability are kept strictly separate. Anything
listed under "Planned" carries no implementation, no code, and no claim in
this repository until it appears in the capability inventory with evidence.

## Implemented (repository infrastructure, not reactor capability)

- Domain manifest (`reactor-domain.json`) with validator.
- Derived Studio portfolio descriptor (`not_federated`) with drift check.
- Generated capability inventory (truthfully empty) with drift check.
- CONTROL adapter specification (contract only, no implementation).
- Local and workflow gate definitions (lint, typing, tests, coverage,
  REUSE, security audit, SBOM, documentation checks).

- **Device configuration model** (landed 2026-08-31) — validated
  floating-coil and levitation objects for `levitated_dipole` with the
  hard superconducting-coil invariant, the dipole-moment/force-balance
  levitation advisory (LDX-class; Garnier et al. 2006), canonical
  digests, and the SPO registry data pin; `computational_prototype`
  (ADR 0002, `VALIDATION.md#device-configuration-model`). Heating
  inventory remains future work under the same capability.

## Planned (no implementation exists; ordering is not a commitment)
1. **Diagnostic and clock semantics** — declared dipole flux-coordinate
   conventions, flux-tube-volume labels, levitation-state channels, and
   dual (cryogenic/plasma) clock identities aligned with the SCPN Phase
   Orchestrator semantic profile.
2. **Safety-envelope declaration** — machine-readable operational envelope
   (coil, levitation, and density bounds) consumed by the CONTROL adapter
   contract.
3. **CONTROL adapter implementation** — device-owned adapter against the
   published specification, with replay fixtures and HIL evidence,
   targeting `control_research_ready` only after replay and HIL
   acceptance.
4. **Solver seam consumption** — versioned consumption of exact
   `SCPN-FUSION-CORE` seams for interchange-marginality and pinch
   transport surfaces, strictly after the family migration gate proves
   exact replacement; no solver code is copied.
5. **Facility-data correlation** — preregistered acceptance contracts
   against identified facility or published experimental data, targeting
   `experiment_correlated` per capability.

## Not planned in this repository

Magnetic mirrors, magnetic-cusp devices, toroidal external-coil systems,
pinches, inertial and magneto-inertial systems, electrostatic devices,
generic controller mathematics, machine-protection logic (including the
levitation-safety chain), and any direct actuation path.
