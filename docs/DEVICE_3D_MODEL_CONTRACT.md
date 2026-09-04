<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Levitated Dipole Core — device 3D model contract
-->

# Device 3D model contract

What a consumer of `device_3d_model` and `device_cad_model` may rely on,
and what it may not. Design record: `docs/adr/0006-device-3d-and-cad-models.md`.

## The bodies

Five per state, all annular tubes, named and ordered:

| Body | Inner diameter | Outer diameter | Height |
|---|---|---|---|
| `floating_coil_inner_subcoil` | 0.552 m printed | **declared** | 0.069 m printed |
| `floating_coil_middle_subcoil` | 0.555 m printed | **declared** | 0.125 m printed |
| `floating_coil_outer_subcoil` | 0.585 m printed | 0.764 m printed | 0.162 m printed |
| `floating_coil_cryostat` | 0.445 m printed | 1.140 m printed | **declared** |
| `charging_coil_winding_pack` | 1.300 m printed | 1.600 m printed | 0.750 m printed |
| `levitation_coil_winding_pack` | 0.410 m printed | 1.320 m printed | **declared** |

The charging state places the first four and the charging coil; the
levitated state places the first four and the levitation coil.

## The two states

The floating coil's mid-plane is `z = 0` in **both** states, which is the
one placement the source supports in each: the three sub-coils have
aligned vertical centres, printed, and the cryostat encloses them.

- `levitated`: the levitation coil sits at **+1.610 m**, printed.
- `charging`: the charging coil sits at a **declared** offset, zero by
  default, because the source prints none.

**There is no transformation between the two states anywhere in this
repository.** A consumer that needs one has to state its own, and the
record's non-claims say the same.

## What is declared and what each declaration rests on

| Declared value | Reading |
|---|---|
| inner sub-coil outer diameter, 0.555 m | the pack is called continuous, so it meets the next sub-coil |
| middle sub-coil outer diameter, 0.585 m | the same |
| cryostat height, 0.3475 m | a circular cross-section with the two printed diameters |
| levitation coil height, 0.0177 m | 9.5 mm plate, two 1.0 mm sheets, two 3.1 mm tape widths |
| charging offset, 0.0 m | coaxial and co-centred |

## What the record reports and never gates

- the two radial gaps of the winding pack, zero under the declaration;
- the cryostat's radial clearance over the pack, 0.188 m;
- the cryostat's clearance inside the charging bore, 0.080 m;
- the levitation coil's turn stack against its printed radial span,
  ratio 1.0338.

## What is gated

- every dimension is finite and strictly positive, and every outer
  diameter exceeds its inner one;
- the three sub-coils are radially ordered;
- the floating coil's cryostat fits inside the charging coil's bore;
- a record's body set matches the state it claims;
- in tier G2, the B-rep measures agree with the analytic forms, the
  faceting stays inside its bound, and the faceted body agrees with the
  tier-G1 mesh within the inscribed-polygon bound.

## What neither tier claims

The vacuum vessel is absent. No body carries a material, a temperature or
a structural property. No clearance is a design margin. The tier-G1
meshes are inscribed, so every tier-G1 volume is an underestimate by
exactly the inscribed-polygon deficit of its segment count. The B-rep
back-end is a pinned third-party dependency and is not the bit-exact
floor of this group.
