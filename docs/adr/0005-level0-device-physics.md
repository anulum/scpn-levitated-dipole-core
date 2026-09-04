<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Levitated Dipole Core — ADR 0005
-->

# ADR 0005 — Level-0 device physics

Status: accepted (2026-09-04). Builds on ADR 0002, which established the
device configuration model this record evaluates.

## Context

The configuration carries a floating coil's mean radius, conductor
current and mass, one levitation field gradient, and a hard requirement
that the coil be superconducting. Its two derived quantities — a
single-turn magnetic moment and an axial force — are documented in their
own module as rough consistency instruments.

The family's filed source is D. T. Garnier et al., *Fusion Engineering
and Design* **81** (2006) 2371, an LDX design and first-results paper
obtained from a laboratory-hosted reprint. It is ten pages and it prints
a great deal: a coil mass, a current-centroid diameter, a turn count, an
operational current, two inductances, two charging currents, two
microwave frequencies and the field one of them resonates at, a plasma
pressure, three betas, an anisotropy ratio, an adiabatic index and a
pressure ratio.

**Every value below was read off pages rendered at 180 dpi**, never off
the PDF text layer, and the source's SHA-256 was verified against the
repository's own papers ledger before anything was read.

## Decision

**Four declarations, one per subsystem the source describes and the
configuration does not carry**, and four relation modules evaluated on
them:

| Declaration | Carries | Why the configuration cannot |
|---|---|---|
| `WindingDeclaration` | turn count | the configuration has no turns field |
| `ChargingDeclaration` | two inductances, charging current | the charging circuit is a separate machine |
| `HeatingDeclaration` | frequencies, total power | heating is not a coil parameter |
| `PlasmaDeclaration` | pressure, beta, anisotropy, adiabatic index, pressure ratio | the plasma is not the device |

The relation modules are `coil` (the ring as a magnet), `levitation`
(what holds it up), `charging` (how current reaches a coil with no
leads) and `plasma` (what the field confines). `level0` composes them.

**A turn count is not required to be an integer.** The source prints
`8388.5` turns for the charging coil, so a fractional winding is
something this family's own source describes and a whole-number
validator would refuse it.

## What is anchored, and it is not merely restated

Two printed numbers come back out of relations they were not fitted to.
That is what makes them anchors rather than transcriptions.

**The electron cyclotron resonance.** The source prints a 6.4 GHz
heating source "resonant at B = 0.23 T". The standard non-relativistic
condition `B = 2 pi m_e f / e` returns **0.228633 T**, which is 0.23 to
the two significant figures the source carries.

**The inductive charge transfer.** The source prints `L_F = 0.389 H`,
`M_CF = 1.69 H` and, separately, that "for a C-coil charge of 300 A,
corresponding to an F-coil charge of 930 kA T". Flux conservation gives
`I_F = (M_CF / L_F) I_C = 1303.34 A`, and at the printed 716 turns that
is **933.19 kA-turns** — 930 at two significant figures. Four printed
numbers from three different pages, one relation, and the fifth comes
out.

**This source rounds; it does not floor.** Worth recording because a
sibling family in this group anchors on a volume measured to floor on
two independent values. Carrying that convention here would have given
0.22 T and disagreed with what this source prints. A printing convention
is a property of a source, not of printed numbers, and a test asserts
the difference so nobody carries it across again.

## What does not reproduce, and what disagrees with itself

**One printed figure does not reproduce.** The source says the conductor
carries "over 1.5 MA turns". Its own printed operational current and
turn count give **1.303 MA-turns**; the printed inductances at the
printed *maximum* charging current give **1.322 MA-turns**. Neither
reaches 1.5, checked at the maximum precisely because a claim that a
figure is unreachable has to be tested where the numbers are largest. It
is named `NOT_REPRODUCED_` and anchors nothing. The same paragraph's
other figure, ">1.2 MA", is consistent with both and is carried as a
floor.

**Two printed statements about one current disagree by 1.4 %.** The
maximum charging current with the printed inductances induces 1846.4 A;
the source prints the operational current as 1820 A. The record reports
the ratio and **gates nothing on it**, because the source does not
reconcile them and a threshold here would be a criterion no source
states.

**The levitation relation's own symbol makes it differ from the standard
force balance by exactly two.** The source prints

    B_r = M_d g / (2 pi a I_d)

and states in the same sentence that `a` is the **average diameter of
the coil**. The force on a current loop in a radial field is `F = I L B`
with `L` the circumference `2 pi R`, giving `B_r = M g / (2 pi R I)`.
Since the diameter is twice the radius, the printed relation read
literally returns **half** what the loop balance requires.

**Both forms are computed, the ratio is a field of the record, and
neither is adjusted.** The source prints no value of `B_r` anywhere, so
nothing anchors either. Both land in the millitesla range — 0.986 mT and
1.973 mT — so neither is absurd and the ambiguity does not resolve
itself. Deciding which the authors meant would be reading intent into a
printed sentence.

## The configuration's own levitation force is superseded, not repeated

`DeviceConfiguration.levitation_force_n()` evaluates `F = m dB/dz` on a
**single turn**, because the configuration carries no turn count. The
source's coil has 716. The record therefore reports both forces and
takes its margin from the winding, and a test asserts that the two
differ by exactly the declared turn count.

This is not a defect in the configuration, which documents itself as a
rough instrument and cannot do better without a field it does not have.
It is what level-0 is for.

## The anchor fixture balances rather than passes

The one quantity the source prints nowhere is the **axial field gradient
at the floating coil's position**. It prints a levitation-coil
separation, an operating field inside that coil's own winding, and the
required-field relation above — no gradient.

The fixture therefore **derives** the gradient that makes `F = m dB/dz`
balance the printed weight exactly, so the anchor configuration sits at
a levitation margin of one. A fixture that declared a comfortable
gradient would make the margin test pass forever while measuring the
choice rather than the relation.

## Consequences

- One capability is declared: `level0_device_physics`, with its own
  `VALIDATION.md` section.
- **No dependency on the shared kernel library.** Level-0 consumes no
  geometry primitive, so this family does not become a library consumer
  here; the pin arrives with the geometry tiers, which need a torus the
  library does not yet build.
- The permeability follows the closest structural sibling's `4e-7 pi`.
  The group also contains a CODATA value elsewhere; they differ by about
  five parts in ten thousand million, which cannot reach a beta the
  source states to two significant figures. Recorded here so the
  divergence is visible rather than discovered.
- 100 % statement and branch coverage of the new package, with no
  suppression and no unreachable handler.
- Every declared bound has a test proving it still refuses something,
  including three floors that are one rather than zero: an anisotropy at
  one is an isotropic plasma, an adiabatic index at one is an isothermal
  gas, and a pressure ratio at one is no gradient at all.
