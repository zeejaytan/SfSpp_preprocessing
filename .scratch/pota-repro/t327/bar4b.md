

### Bar 4b — the sign probe: the residual is per-point, not a per-piece convention

**Why this probe.** Bar 4's two failures are not on the piece whose wall I swapped. `Bl1`'s stored normal sign is
inward on 1/2/6/9 but outward on 3/4/5/7/8 (`phases` in `blnormals327.py`), so I built three more trees from
`juglet_SWAP` on the same copies — `juglet_SWAPneg` (Bl0 normals negated on 2, 6, 9), `juglet_SWAPneg7`
(negated on 7 only), `juglet_SWAPnegall` (all four) — negating only PCD columns 4-6 and leaving every coordinate
byte-identical (verified: the x y z digest of P6 Bl0 is `40e34751ab7414f45de503bb7a186250` before and after).
Job **34690603** on the same run dir, 18 s, **COMPLETED 0:0** (it finished before the withdrawal I sent landed;
its outputs are the three `out/diag_jug_NEG*.txt` in `artifacts/pota327/swap/`, parser
`.scratch/pota-repro/t327/parse_bar4b.py`).

| pair | ctrl | swap (as is) | NEG (2,6,9) | NEG7 | NEGALL |
|---|---|---|---|---|---|
| 1-2 | −0.896/10 | **+0.704/13** | −0.704/13 | +0.704/13 | −0.704/13 |
| 1-4 | +0.786/9 | +0.786/9 | +0.786/9 | +0.786/9 | +0.786/9 |
| 1-8 | +0.971/19 | +0.971/19 | +0.971/19 | +0.971/19 | +0.971/19 |
| 1-9 | −0.945/8 | **−0.039/7** | +0.039/7 | −0.039/7 | +0.039/7 |
| 2-5 | −0.991/1 | **+0.948/1** | −0.948/1 | +0.948/1 | −0.948/1 |
| 2-9 | +0.991/4 | +0.971/4 | +0.971/4 | +0.971/4 | +0.971/4 |
| 3-5 | +0.987/3 | +0.987/3 | +0.987/3 | +0.987/3 | +0.987/3 |
| 6-7 | +0.106/16 | **−0.183/15** | +0.183/15 | +0.183/15 | −0.183/15 |
| 7-9 | −0.674/4 | **+0.708/3** | −0.708/3 | −0.708/3 | +0.708/3 |

`dot_med_d3/n_d3`. `gap_min` is **identical in all four variants** on every pair (1-2 0.514, 1-9 0.998,
2-5 1.539, 6-7 0.809, 7-9 0.945), which is the control that the negation touched only signs, and it also shows
the correspondence set is geometric (`MakeCorWOBuildTree`, `reconstruction.cpp:341-366`: kd-nearest on points,
normals only read), so a per-piece flip can only mirror the median.

- **No per-piece sign convention can pass 1-9 or 6-7.** Every variant lands on ±0.039 and ±0.183 — the
  reflection of the same mixed set, 3-4 of 7 and 5-10 of 15 correspondences on the wrong side. The three pairs
  that pass pass with the **unnegated** swapped tree, so the swapped-in walks of 2 and 9 already carry the right
  sign for those pairings (negating them breaks 1-2, 2-5 and 7-9 — a useful control, not an improvement).
- So the residual is **spatially varying sign inside one line**, not a convention per piece or per bundle: on
  piece 9's swapped-in walk the section mating with piece 7 is consistently inward, the section mating with
  piece 1 is not (local n·r̂ −0.74..+0.07 across eleven tested points, `pairprobe327.py`), and the same walk is
  17% outward overall. That is what storing the sampled *surface* normal per point does when a walk runs along a
  rim: the normal's relation to the cavity turns along the loop, and nothing in the writer re-signs it against
  the wall it is supposed to face.
- For 6-7 neither piece's sign fixes it (5 of 15 disagree whichever side is flipped), so on that pair the two
  lines' normals differ at the mating section for a reason the wall side no longer explains — the next thing to
  measure there is whether either walk runs on a chamfer/rim rather than the flat of its wall.

**What this means for the fix, stated as narrowly as the evidence allows.** The wall-side filing is confirmed
as a real defect (bars 1-3) and as causally load-bearing (bar 4: 3/5 pairs, all five moved). It is **not
sufficient**: a line whose stored normals are mixed along its own loop will still fail a normal-agreement gate
after the wall is right. Ticket 328 should carry both halves: file by the wall, and re-sign (or re-derive) the
exported line normals per point against that wall instead of storing the sampled surface normal.
