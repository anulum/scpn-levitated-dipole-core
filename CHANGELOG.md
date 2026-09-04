<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Levitated Dipole Core — CHANGELOG
-->

# Changelog

## [Unreleased]

### Added

- The coil set in two states, tessellated and exact (`device_3d_model`,
  `device_cad_model`, ADR 0006). The rollout plan assigned this family a
  **torus primitive**; reading the filed source settled it differently.
  Printed page 2374 describes the floating coil's winding pack as "three
  rectangular sub-coils with aligned vertical centers", and every body of
  this device turns out to be an **annular tube** — a primitive the shared
  library has carried since its own ADR 0002. Nothing printed is a torus,
  and the source's own schematic draws the floating coil as a rectangle in
  section.

  **Two states, two frames, no transformation between them.** The source
  prints the levitation coil's 1.610 m separation from the floating coil
  and prints nothing about the charging coil's, so one frame holding all
  three coils would assert a distance no source gives.

  **The vacuum vessel is not modelled.** One printed number, its 5 m
  diameter, does not fix a shape, and the source draws a faceted body of
  revolution whose profile appears nowhere.

  Four dimensions are declared rather than printed and each carries its
  reading: two sub-coil outer diameters that make the pack continuous, a
  cryostat height that is the circular-cross-section reading of two
  printed diameters, a levitation coil height summed from printed plate
  and tape thicknesses, and a charging offset of zero.

  **Three printed diameters nest** — cryostat 1.140 m, charging station
  1.157 m, charging bore 1.300 m — from three different places in the
  source, and a floating coil too large for the bore is refused. **One
  printed relation nearly closes** and is carried as a number: 2800 turns
  of 0.168 mm tape span 470.4 mm against a printed 455.0 mm, ratio 1.0338.

  Measured on this body set: the B-rep agrees with the analytic forms
  within `1e-14`; the faceting sits between 4.72 % and 11.95 % of its
  bound across the ten body placements; and **the tier-G1 mesh deficit
  equals the inscribed-polygon bound** to twelve significant figures,
  because an annular tube is bounded by two circles of one segment count.
  The tier-G2 mesh check is therefore tight rather than generous, and its
  whole margin is the faceting.

  This repository becomes a consumer of the shared kernel library, pinned
  by public git URL at commit `4095aa8`, which widens the open registry
  finding already reported to the reviewing authority.

- Level-0 device physics (`level0_device_physics`,
  `computational_prototype`, ADR 0005): four declarations of what the
  configuration does not carry — the winding, the inductive charging
  circuit, the electron cyclotron heating and the plasma — and four
  relation modules evaluated on them. Anchored on the freely published
  design paper the repository cites, read off pages rendered at 180 dpi.
  Two printed numbers are recovered from relations they were not fitted
  to: the field a printed heating frequency resonates at, and the
  floating-coil charge a printed pair of inductances and a printed
  charging current produce. One printed figure is recorded as not
  reproduced rather than absorbed, checked at the most favourable
  printed combination and not only at the nominal one. Two printed
  statements that disagree with each other are reported and gated
  nowhere: the source's levitation relation names a symbol that makes it
  differ from the standard loop force balance by exactly a factor of
  two, and the current its printed inductances induce is not the
  operational current it prints elsewhere. The configuration's own
  single-turn levitation estimate is superseded by the winding's, and
  both are reported.

- Diagnostic-plan depth: per-channel signal inventories, frame
  transformations with a fixed kind-admissibility table and connectivity
  rule, and a clock topology partitioning the physical clocks into rooted
  domains with a star of relations to the reference root. Envelope
  `scpn.reactor-diagnostic-plan-envelope.v1` bumped to `1.2.0`; the
  fixture is regenerated from the public surface and re-pinned. All new
  members are declarations: no observation, phase, mapping, or control
  authority is created.

### Fixed

- Added the nullable `timing_uncertainty_s` channel member (always `null`;
  no event-relative candidate is applicable) so the diagnostic-plan
  channel shape matches the portfolio-uniform envelope 1.1.0 contract;
  fixture regenerated and re-pinned.

### Added

- Local gate parity with the wider ecosystem: the pre-commit chain now
  also runs REUSE licensing compliance and a typographical checker
  (`_typos.toml` carries the deliberate reactor vocabulary), and adds
  the upstream YAML, TOML, large-file and private-key guards. Licensing
  and spelling were previously verified only in hosted CI, so a broken
  REUSE annotation — including the aggregate annotation that covers the
  binary header images — could reach a push before being caught.
- Generated repository header artwork: `docs/assets/generate_header.py`
  renders three deterministic 1280x640 images from the repository's own
  domain surface (the floating ring in its computed dipole field used
  by the README, the levitation force gate, and the closed-field map).
- Modular hosted-workflow surface per the ecosystem workflow-modularity
  standard: `ci.yml` reduced to a coordinator with a stable fail-closed
  `gate` job, single-responsibility reusable workflows for static
  analysis/repository policy and for tests, a versioned machine-readable
  inventory (`.github/workflow-inventory.json`,
  `scpn.workflow-inventory.v1` `1.0.0`), and a fail-closed modularity
  guard (`tools/audit_workflows.py`) enforced locally (preflight gate,
  pre-commit hook) and in hosted CI. The duplicate documentation-links
  step was removed from the CI chain; `docs.yml` remains the single
  owner of documentation validation.

- Typed reference frames, clock synchronisation relations (synthetic
  bounds only; no correlation evidence claimed), and per-channel
  acquisition windows and element counts in the diagnostic model;
  hardened decoders (recursive exact-key, duplicate-member, and
  byte-canonical refusal in both codecs); envelope `1.1.0` adding
  `manifest_sha256` over the committed canonical `reactor-domain.json`
  (fixture regenerated; byte hash re-pinned in tests).

- Portable diagnostic-plan envelope
  (`src/scpn_levitated_dipole_core/plan_envelope.py`,
  `scpn.reactor-diagnostic-plan-envelope.v1` version `1.0.0`): a
  producer-owned, canonically serialised wrapper carrying project
  identity, exact owned configurations, capability and maturity,
  synthetic/review-only/non-actuating statements, both SPO registry
  pins, the inner plan's SHA-256, the producer revision, and fixed
  no-observation/no-control non-claims; strict parsers refuse unknown,
  duplicate, and non-finite members, and an immutable committed fixture
  exercises the exchange end to end.

- Diagnostic and clock semantics model
  (`src/scpn_levitated_dipole_core/observability.py`), the second implemented
  capability at `computational_prototype`: frozen clock, channel,
  deferral, and plan objects aligned fail-closed with the pinned SPO
  observability-profile catalogue (candidate applicability, carrier
  admissibility, exact class-fixed evidence vocabularies, clock-kind
  compatibility, Nyquist bounds); cited advisory band checks; canonical
  serialisation with SHA-256 digests and strict NaN-rejecting round-trip
  parsing (design record `docs/adr/0003-diagnostic-clock-semantics.md`).

- Device configuration model (`src/scpn_levitated_dipole_core/`), the first implemented
  capability at `computational_prototype`: validated frozen parameter
  objects with device-specific invariants and documented, cited
  consistency estimates; canonical serialisation with SHA-256 digests
  and strict NaN-rejecting round-trip parsing; a data-only pin to the
  SPO reactor registry; and the reactor-domain validator branch
  enforcing populated capability inventories with the ADR 0002
  evidence-maturity ceiling rule (design record
  `docs/adr/0002-device-configuration-model.md`).

- Architecture-only repository scaffold: governance, security, licensing,
  REUSE metadata, contribution and support policies, and citation metadata.
- Machine-readable domain manifest `reactor-domain.json` binding the project
  to SCPN Phase Orchestrator reactor registry `1.0.0`
  (configuration `levitated_dipole`).
- Device-owned CONTROL adapter specification and threat model.
- Derived Studio portfolio descriptor (`not_federated`) and generated
  capability inventory (zero implemented capabilities).
- Validation tooling: domain-manifest validator, descriptor derivation and
  inventory generation with drift checks, and a fail-closed preflight
  orchestrator, each with statement- and branch-complete tests.
- Continuous-integration, code-scanning, security-audit, documentation,
  SBOM, pre-commit, and Scorecard workflow definitions (read-only
  permissions; no publication or deployment workflows).

### Changed

- Studio portfolio descriptor schema ratified at version 1.1.0 after
  downstream review, before any consumer adoption (1.0.0 superseded
  unconsumed): canonical JSON Schema published in-repository with a strict
  unknown-field policy, explicit source repository, nullable lifecycle
  evidence pointer, nullable versioned control-intent reference, ratified
  capability item shape, and a machine-protection object (independent
  final-veto owner with availability `not_assessed`) replacing the former
  boolean flag.
