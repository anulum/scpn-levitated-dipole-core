<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Levitated Dipole Core — Benchmarks and computation contract
-->

# Benchmarks and computation contract

## Computation contract

The level-0 physics of this package is a set of closed forms evaluated in
IEEE-754 binary64 on the Python floor (SI units; the configuration carries
the conductor current in kiloamperes):

| Module | Kernels | Operations |
|---|---|---|
| `physics/coil.py` | amp-turns, current-centroid diameter, dipole moment `pi r^2 N I` | `* /` |
| `physics/levitation.py` | required radial field (as printed and from the loop force), required field gradient, levitation margin | `* /` |
| `physics/charging.py` | charge-transfer ratio `M / L_F`, induced current, agreement ratio | `* /` |
| `physics/plasma.py` | resonant field `2 pi m_e f / e`, perpendicular and anisotropic beta, field from beta (`sqrt`), marginal pressure ratio `V^gamma` and required expansion | `* /`, `sqrt`, **one real power** |
| `physics/level0.py` | the composed record with canonical bytes and SHA-256 digest | composition, JSON serialisation |

Every input outside its domain is refused with the package error, never
clamped. The square root is correctly rounded by IEEE-754; the real power
(`x ** gamma` and its inverse) is evaluated by the platform `pow`, which
the standard does not require to be correctly rounded. A native backend
that must agree bit for bit would therefore have to use one deterministic
power on both sides, such as the shared library's
`numerics_transcendental` kernel. The constants and their editions are
documented in `physics/constants.py` and bound by tests.

**Backend status.** Python floor only. There is no native crate. Audit
plan Q01 asks for a native path on required numeric paths and allows a
scoped, owner-approved exception for trivial non-hot arithmetic; that
decision is the owner's and is recorded as open in the backlog. The
benchmark marks the native backend as unavailable instead of omitting it.

## Level-0 physics — local workstation (non-isolated)

Artefact: `benchmarks/results/level0_physics.local.json` (schema
`scpn-levitated-dipole-core.level0-physics-benchmark.v1`, generated 2026-10-31T02:13:11.045404+00:00, at commit
`d59a36090777` with the working tree of the landing commit).
Host: 11th Gen Intel(R) Core(TM) i5-11600K @ 3.90GHz, Linux-7.0.0-34-generic-x86_64-with-glibc2.39, Python 3.12.3; load average
at start 5.12 (another test run was active);
cores not isolated, so treat the numbers as a smoke timing, not a
performance measurement. Parameters: 20000 closed-form points and
2000 records, 3 warm-up passes, 20 timed passes.

### `closed_forms` (resonant field, perpendicular beta, marginal pressure ratio, induced current per point)

| Backend | P50 µs/point | P95 µs/point | P99 µs/point | mean µs/point | throughput points/s | status |
|---|---|---|---|---|---|---|
| `python_floor` (public API) | 1.181 | 1.737 | 1.766 | 1.251 | 847059 | measured |
| `rust_native` | — | — | — | — | — | unavailable: no native crate |

### `level0_record` (composed record with canonical bytes per point)

| Backend | P50 µs/record | P95 µs/record | P99 µs/record | mean µs/record | throughput records/s | status |
|---|---|---|---|---|---|---|
| `python_floor` (public API) | 51.829 | 67.925 | 75.915 | 52.858 | 19294 | measured |
| `rust_native` | — | — | — | — | — | unavailable: no native crate |

## Regenerate

```bash
.venv/bin/python benchmarks/level0_physics.py --label local
```

The script writes `benchmarks/results/level0_physics.<label>.json` with the
provenance above. A number from a fixed CI runner or isolated cores would
replace the smoke timing here; none is claimed yet.
