<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Levitated Dipole Core — Architecture
-->

# Architecture

## Purpose and evidence state

`SCPN-LEVITATED-DIPOLE-CORE` is the device-family owner for
levitated-dipole systems in the SCPN Reactor Systems Research Group
portfolio. The
repository owns two implemented capabilities at
`computational_prototype` in `src/scpn_levitated_dipole_core/`: the device
configuration model (design record ADR 0002, evidence record
`VALIDATION.md#device-configuration-model`) and the diagnostic and
clock semantics model (design record ADR 0003, evidence record
`VALIDATION.md#diagnostic-and-clock-semantics`). Every other
section below describes boundaries and contracts. The claim inventory is
empty; capability and claim inventories are generated and drift-checked.

## The five-surface boundary

1. **Governing confinement physics** — the `levitated_dipole` (closed
   dipole field): plasma confined in the dipole field of a magnetically
   levitated superconducting internal coil. Field lines are closed, and
   stability follows compressibility rather than average curvature:
   interchange-marginal profiles satisfy an entropy-like invariant, and
   turbulence can drive an inward particle pinch that sustains centrally
   peaked density without driven current. The registry places the
   configuration in the `magnetic_open` family; the device-defining
   distinction from mirrors (axial loss cones) and cusps (sheath-aperture
   losses) is confinement on closed dipolar field lines around a floating
   internal conductor. External-coil toroidal systems fail the sharing
   test through their driver, lifecycle, and diagnostic surfaces.
2. **Primary driver and energy delivery** — the levitated superconducting
   coil (inductively charged, cryogenically buffered) establishing the
   dipole field, a levitation coil with feedback keeping it floating, and
   radio-frequency heating with gas fuelling building the plasma.
3. **Plant and shot lifecycle** — a lifecycle dominated by the internal
   coil: cooldown, inductive charge, lift and levitation hand-off,
   plasma operation (long-pulse, bounded by the coil's cryogenic
   endurance), controlled de-levitation onto the catcher, and recool.
   Device-level hazard semantics cover levitation-control excursions,
   coil-quench boundaries, and catcher engagements.
4. **Diagnostic, reference-frame, and clock model** — dipole
   flux-coordinate conventions, flux-tube-volume labels for
   interchange-marginality declarations, interferometry and edge probe
   layouts, levitation-state channels, and clock identities spanning slow
   cryogenic and fast plasma timescales.
5. **Solver, evidence, and control-contract boundary** — versioned seams
   towards `SCPN-FUSION-CORE`, review-only semantics towards
   `SCPN-PHASE-ORCHESTRATOR`, and the device-owned CONTROL adapter
   specification towards `SCPN-CONTROL`.

## Position in the SCPN ecosystem

```text
SCPN-LEVITATED-DIPOLE-CORE (device truth: dipole/levitation policy,
                            lifecycle, flux-coordinate diagnostics,
                            safety envelope, adapter spec)
   │  optional versioned solver seams (none active)
   ├──────────────► SCPN-FUSION-CORE      (solver mathematics, evidence)
   │  typed review-only semantics
   ├──────────────► SCPN-PHASE-ORCHESTRATOR (semantics, comparability)
   │  device-owned adapter (specification only; no implementation)
   ├──────────────► SCPN-CONTROL          (admission; sole ControlAction author)
   │  derived portfolio descriptor (not_federated)
   └──────────────► SCPN-STUDIO           (catalogue, evidence UI, gating)

SCPN-CONTROL ──admitted ControlAction──► independent machine protection
                                          (final veto) ─► plant actuators
```

## Repository layout

| Path | Role |
|---|---|
| `reactor-domain.json` | portable source of project identity and contracts |
| `studio/portfolio-descriptor.json` | derived Studio descriptor, `not_federated` |
| `capability-inventory.json` | generated, truthfully empty inventory |
| `docs/CONTROL_ADAPTER_SPECIFICATION.md` | device-owned adapter contract |
| `docs/THREAT_MODEL.md` | assets, trust boundaries, misuse paths |
| `docs/adr/0001-repository-boundary.md` | boundary decision record |
| `tools/` | validators, derivation tools, preflight orchestrator |
| `tests/` | statement- and branch-complete tests for `tools/` |
| `.github/workflows/` | read-only CI definitions (no publication) |

## Contract surfaces and versioning

- `reactor-domain.json` follows schema `scpn.reactor-domain.v1`; unknown
  schemas are rejected by consumers.
- The Studio descriptor is derived deterministically and embeds the
  manifest's SHA-256; manual edits are detected as drift.
- The CONTROL adapter contract is specification-only at `0.1.0-spec`.
- SPO binding is fixed to reactor registry `1.0.0`, digest
  `786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090`.

## What would change this architecture

Acceptance of a FUSION solver seam through the family migration gate,
ratification of an SPO `ControlIntent`-class contract, or Studio federation
after a real capability passes producer and consumer gates — each recorded
as a versioned contract change in a new ADR.
