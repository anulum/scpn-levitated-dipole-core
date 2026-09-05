<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Levitated Dipole Core — ADR 0006
-->

# ADR 0006 — The coil set in two states, tessellated and exact

Status: accepted (2026-09-04). Adds the capabilities `device_3d_model`
(tier G1) and `device_cad_model` (tier G2), and the repository's first
dependency on the shared kernel library.

## Context

The rollout plan assigned this family a **torus primitive** and deferred
it. Reading the filed source settled that differently, and the
measurement is worth stating because it is the fourth time in this
rollout that a planned primitive turned out not to be the one a family
needs.

Printed page 2374 of the filed source describes the floating coil's
winding pack as "three rectangular sub-coils with aligned vertical
centers" and gives an inner diameter and a height for each. Page 2374
gives the charging coil a height and two diameters; page 2376, Table 2,
gives the levitation coil two diameters. **Every body of this device is
an annular tube**, a primitive the shared library has carried since its
ADR 0002. Nothing printed is a torus of circular cross-section, and the
schematic in the source's own Fig. 1 draws the floating coil as a small
rectangle in section.

The source does use the word "toroidal", once, for the cryostat's helium
pressure vessel. What it prints for that body is an inner diameter and an
outer limiter diameter and no height at all.

## Decision

1. Both tiers are built, tier G1 in `geometry/model.py` and tier G2 in
   `geometry/cad.py`, from the library's `annular_tube` and
   `annular_tube_brep`. No geometry is implemented here.
2. **The device is modelled in two states and no transformation between
   them exists in this repository.** A levitated dipole is one machine in
   two arrangements: charging, with the floating coil lowered into the
   charging station inside the charging coil, and levitated, with the
   floating coil at the centre of the vessel and the levitation coil
   above it. The source prints the levitation coil's separation from the
   floating coil — 1.610 m, Table 2 — and prints **nothing** about the
   charging coil's. One frame holding all three coils would assert a
   distance no source gives, so there are two frames and the absence
   between them is structural rather than documentary. This follows the
   pattern a sibling family established for two schemes in two frames.
3. **The vacuum vessel is not modelled.** The source prints one number
   for it, its 5 m diameter, and draws a faceted body of revolution whose
   profile appears nowhere. A sphere or a cylinder of that diameter would
   be a substitute for a shape that is not stated. The record's
   non-claims say the vessel is absent and why.
4. **Four dimensions are declared rather than printed, and each carries
   the reading that produced it.**
   - The two inner sub-coils have no printed outer diameter. The source
     calls the pack "continuous", and the only values that make the word
     true are the printed inner diameters of the next sub-coil out, so
     each outer diameter is declared to be the next inner one. The
     resulting radial gaps are **reported and never gated**, because that
     reading is ours.
   - The cryostat has no printed height. A body of circular cross-section
     with its two printed diameters is 0.3475 m tall, and that is what is
     declared. **The model still builds an annular tube**; what the
     toroidal wording contributes is the missing height and nothing else.
   - The levitation coil has no printed height. The source prints a
     9.5 mm steel plate faced with two 1.0 mm copper sheets and pancakes
     wound to either side from a tape 3.1 mm wide; one tape width per
     side is the thinnest arrangement those sentences allow, giving
     17.7 mm.
   - The charging coil has no printed vertical offset from the floating
     coil. Zero, the coaxial and co-centred reading, is declared.
5. **Three printed diameters nest, and that is a real check rather than a
   restatement.** The cryostat's outer limiter diameter is 1.140 m, the
   charging station's is 1.157 m and the charging coil's bore is 1.300 m.
   They are printed in three different places and the machine could not
   be assembled if they did not nest. The constructor refuses a set in
   which the floating coil could not enter the charging coil, and a test
   asserts the nesting and the 17 mm and 80 mm clearances it implies.
6. **One printed relation nearly closes and is carried as a number.**
   Table 2 prints 2800 turns, a tape 0.168 mm high and inner and outer
   diameters of 410 and 1320 mm. Laid side by side the turns span
   470.4 mm against a printed radial span of 455.0 mm, a ratio of
   **1.0338**. The source calls the winding a double pancake, which would
   predict two radial stacks rather than one. The record reports the
   ratio and resolves nothing.
7. The kernel library is pinned by **public git URL at commit
   `c83745c6011d9b0ea6c413cf0b7d607c724090e7`**, declared in the manifest
   with the inventory digest
   `46dc34f9a3c7f498c454bd3219c0233848a71405371ee947d4ab79cf2f5d63f8` and
   the eight kernels this family reaches. The tier-G2 back-end is an
   optional `cad` extra naming the same commit, because it pulls about a
   gigabyte and every other capability works without it.

## Consequences

**This repository becomes a consumer of the kernel library, which widens
an open audit finding.** Sixteen repositories now pin that library across
eight distinct commits while its own consumer registry lists ten and
carries no commit field at all. That finding is declared here, has been
reported to the reviewing authority, and is **not** fixed locally: the
registry's schema is a group decision.

Measured on this body set rather than reused from a sibling:

| Quantity | Measured |
|---|---|
| B-rep agreement with the analytic forms | within `1e-14` relative |
| faceting deficit as a fraction of its bound | **0.0472 to 0.1195** across the ten body placements |
| tier-G1 mesh deficit against the polygon bound | **equal**, to twelve significant figures |

The last row is the one that matters for anyone reading the evidence.
Every body here is bounded by two circles of the same segment count, so
both radii shrink by the same polygon ratio and the volume scales by
exactly that ratio: the inscribed-polygon bound is **attained**, not
approached. The whole margin of the tier-G2 mesh-difference check is
therefore the B-rep faceting being finer than tier G1, which makes that
check tight rather than generous. A reader who assumed slack there would
be wrong.

The spread in the faceting fraction is not noise either: the bound falls
as a body's inner radius grows while the mesher's actual deviation does
not, so the widest-bore body sits at more than twice the fraction of the
narrowest. A single number quoted for the family would have hidden that.

**The torus primitive is deferred, not refused.** Nothing in this family
needs it, and the one body the source calls toroidal is specified by data
that is annular. If a later family or a later reading requires a circular
cross-section, the primitive is still the right thing to build.
