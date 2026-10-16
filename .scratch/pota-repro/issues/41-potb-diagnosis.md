# 41: Pot B diagnosis — where do fresh true joins die?

**What to deliver:** the kill site, with numbers — not a fix.

**Answers:** E1

**Blocked by:** nothing (runs alongside ticket 39; read-only vs 39's lanes).

**Status:** results-in — DIAGNOSED (kill site: SingleOverlapTest@100 eats 8/15 GT-true edges at GT seating on teleport-corrupted fresh Bl_0 rims; p1 Bl_0 garbage unseats piece 1; 2-4 has zero rim support; ORIG 0/15 kills through the same gate — rims are the defect, search is exonerated)

## Comments (worker, 2026-10-17)

**Verdict: category 1 — the method genuinely failed (fresh preprocessing rims), with the search/assembly, the reference, and our measurement all exonerated.** Fresh Pot B rims carry the ticket-26 ordering defect at larger scale (mid-run teleports in 8/9 Bl_0 files, up to 90mm) plus a garbage p1 Bl_0 (1069 pts, ~12mm off either shipped side). At GT seating, 8 of 15 GT-true edges report overlap areas 168–4927 against the SingleOverlapTest gate of 100, while shipped rims report 2–8 on all 15 and assemble 9/9+15/15 through the same binary in all four jobs. The threshold is satisfiable by good rims — the rims are wrong, not the gate. No commits; laptop tree untouched except this file + gitignored `artifacts/pota41_B/`; live prep checkout's tracked files untouched (read-only greps only); ticket-39 run dirs read-only.

**0. Method notes (read before the numbers).** Assembly loads ONLY `Breakline_0.pcd` per piece into `edge_line_` (`data_path.h` POT_B file list; confirmed read-only in `pota39_repro/asm`) — so all kill-site probes below use Bl_0 only. Overlap numbers come from a faithful numpy port of `OverlapCheck_3d` (`MakeCorWOTree`+`DetectIntersection`+`SortRegion`, incl. region<10 and centroid<5 rules) at GT seating — the same port ticket 26 validated against instrumented job-B single-ov kills on Pot A. `SingleOverlapTest` body read (not edited): `OverlapCheck_3d(shard[j].edge_line_, shard[c_node].edge_line_, area, size, 100)` per placed member — matches the port. Per-site RP/CheckGraph/profile-veto counts are NOT in the standard binary logs (only "Total number/pruned" print) and need P26DIAG-pattern prints — barred by this ticket's no-source-edits rule; proposed as successor instrumentation below. Boundary-aware teleport scan: `# s e f` runs are 1-based inclusive; a >5mm jump is boundary iff it lands on a run edge.

**1. Gate table (fresh Bl_0 at GT; A->B strict d<2mm & |n.n|>0.85).**

| piece | Bl_0 n (fresh/ORIG) | mid-run jumps>5mm fresh (max) | ORIG jumps |
|---|---|---|---|
| p1 | 1069/210 | 24 (90.0mm) | 0 |
| p2 | 358/150 | 10 (28.3mm) | 0 |
| p3 | 230/143 | 4 (27.3mm) | 0 |
| p4 | 281/136 | 7 (73.2mm) | 0 |
| p5 | 219/131 | 15 (56.0mm) | 0 |
| p6 | 138/104 | 8 (61.8mm) | 0 |
| p7 | 99/104 | 0 | 0 |
| p8 | 161/101 | 3 (63.0mm) | 0 |
| p9 | 173/75 | 4 (48.2mm) | 0 |

Fresh Bl_1: only p2 has 1 mid-run jump (43.2mm); all other Bl_1 clean both arms. ORIG: zero jumps in all 18 files. Per-edge gate (Bl_0, fresh vs ORIG): 1-2: 31/40; 1-3: 4/37; 1-4: 20/38; 1-5: 12/35; 1-8: 12/14; 1-9: 0/23; 2-4: 0/12; 2-8: 26/31; 3-5: 17/23; 3-7: 21/24; 4-6: 32/31; 5-8: 23/24; 6-7: 14/12; 6-9: 2/18; 7-9: 26/27. Fresh Bl_0 gates 13/15 (zeros: 2-4, 1-9; weak: 6-9=2, 1-3=4); ORIG Bl_0 15/15 (min 9). Full-rim p39 gate: 14/15 (2-4=0). Mixed-rim 2-4 attribution: fresh2-ORIG4 = 0, ORIG2-fresh4 = 0 (either fresh rim alone breaks the seam; ORIG-ORIG = 12).

**2. Axle table (all 9 B admitted — ticket-18 refusal list of 16 contains no B piece; record from ticket 10, job 33109949).** B03 derr 9.12° rerr 37.24 (landscape fail, P08-family); B08 derr [31.37, 5.41] (multi fail); direction-pass with position-over: P01 (rerr 3.15), P06 (3.88), P07 (3.15°/11.19), P09 (2.94°/8.20); clean passes P02/P04/P05. Axles EXONERATED as the driver: the shipped-axle arm (job 33199066, true axes) scores identically 4/9+2/15 with forest 523/27 — same outcome with perfect axles.

**3. Kill-site counts (GT-true edges, fresh; stages as named in the ticket).**
- Forest/prune (binary logs, all four jobs): fresh forest 1442 vs ORIG 114 (12.6× junk admitted by pairwise stages); prune survivors fresh 31/39/27/34 vs ORIG 76/77/77/77 (fresh keeps 2–3%, ORIG 67%). Per-site RP-overlap / CheckGraph@150 / profile-veto splits unavailable without instrumentation (see §0) — the GT-seating replication below is the per-site evidence for the terminal gate.
- SingleOverlapTest@100 at GT seating, Bl_0 (fresh kill?/area vs ORIG area): 1-2 T/926 vs 2; 1-3 F/24 vs 6; 1-4 T/2525 vs 8; 1-5 T/4927 vs 8; 1-8 T/1511 vs 6; 1-9 F/0 vs 0; 2-4 F/0 vs 2; 2-8 T/168 vs 2; 3-5 F/32 vs 2; 3-7 F/2 vs 0; 4-6 T/306 vs 4; 5-8 T/325 vs 8; 6-7 F/6 vs 2; 6-9 T/389 vs 6; 7-9 F/16 vs 8. **Fresh kills 8/15 (areas 168–4927); ORIG kills 0/15 (areas 0–8).**
- Upstream rim deaths: p1 Bl_0 garbage → piece 1 unseated in E2E snapshots (fresh seats 8/9; its 6 edges never place); 2-4 zero rim support at GT (gate 0, overlap region empty both arms-fresh).
- E2E strict (5°/10mm, R1 snapshots): fresh 1/15 (only 3-5 passes; 6 edges UNSEATED via p1; seated-but-flung errors 55–175°, 324–686mm) vs ORIG 9/15 strict with 9/9 seated (all rotations ≤2.85°; the 6 strict-fails are 10.8–15.8mm translations over the 10mm bar). Binary: fresh 4/9+2/15 = R1/R3/repeat/shipax alike.
- Render (eye-checked): `artifacts/pota41_B/pota41_p5_teleports.png` — p5 fresh Bl_0 at GT crisscrossed by 15 red teleport chords vs ORIG same-side clean loop (same triangle, broken order).

**4. Verdict in the three-category frame: (1) genuinely-failed method.** The fresh preprocessing chain cannot produce Pot B rims: ordering teleports (8/9 Bl_0) + p1 content garbage + 2-4 seam gap. The deciding number: **8 of 15 GT-true edges exceed the SingleOverlapTest@100 gate at GT seating on fresh rims (areas 168–4927, i.e. 1.7–49× the gate) while shipped rims exceed it on 0 of 15 (areas 0–8)** — same poses, same code, same threshold. Exonerated with numbers: search (ORIG 9/9+15/15 binary ×4 same binary/m same job), reference (GT+graph seat ORIG fine), our measurement (port validated on Pot A; Bl_0-only semantics verified in source), axles (shipax identical outcome). NOT claimed: per-site RP/CheckGraph/profile splits (need instrumentation), or whether the Bl_0/Bl_1 label swap (below) contributes beyond the teleports.
- Side finding (not the killer): fresh Bl_0 ≈ shipped Bl_1 side on all 9 B pieces (cross-nn 0.5–1.4mm swapped vs 2–12mm same-label; p1 Bl_0 garbage on both; p2 noisy ~2.5mm either way), while Pot A labels match (same-side 0.5–2.2mm). The swap is exonerated as the kill mechanism — shipped Bl_1 pairs gate every edge as well as Bl_0 (ORIG11≈ORIG00: e.g. 2-4: 9 vs 12; all edges 9–40 both sides) — but the per-pot label flip is a pipeline nondeterminism the fix ticket should close deliberately.

**Jobs (sacct State/ExitCode, all COMPLETED 0:0 incl. batch/extern):** 33198525 p39_runB (=R1: ORIG 114/76→9/9+15/15, fresh 1442/31→4/9+2/15); 33199009 p39_runB (repeat: ORIG 114/77, fresh 1442/39→4/9+2/15); 33199066 p39_runBs (shipax: ORIG 114/77, fresh 523/27→4/9+2/15); 33199773 p39_runB (=R3: ORIG 114/77, fresh 1442/34→4/9+2/15). No new Spartan jobs cut (all evidence laptop-side + read-only log/source greps). Spartan leftovers: only `/tmp/pota41_fetch/orig_B_breaklines.tgz` (own scratch, 70KB). Laptop probes: `artifacts/pota41_B/p41_B.py` (teleport+gate+agreement+overlap), `p41_render.py`, unpacked ORIG B breaklines (18 files).

**Successor proposal for lead:** rim-content fix ticket (Bl_0 ordering repair incl. p1 content + 2-4 seam; pin the Bl_0/Bl_1 side convention Pot-A-parity), then gate + E2E rerun; optional P26DIAG-pattern instrumentation on Pot B first if the lead wants measured RP/CheckGraph/profile-veto splits before the fix lands. Do NOT relax SingleOverlapTest@100, RP axis/score gates, or CheckGraph-150 — the ORIG arm proves all gates passable.

**Starting position:** Pot B R1 (fetch_B_R1, 2026-10-17): ORIG 114/76 → 9/9+15/15 (vehicle valid on B); fresh 1442/31 → 4/9+2/15. Fresh generates 12× the graphs and keeps a third of ORIG's count — true joins die in filtering. Pot C repeats the shape (fresh 307/7 → 0/3; ORIG 125/40 → 4/4+5/5).

**Steps (diagnose ONLY — no source edits, no commits except this ticket's record):**
1. Gate our B rims: teleport scan per breakline (ticket-26 method), min-pair check (ticket-06 gate). Are B rims clean like A's?
2. Axle errors per admitted B fragment (finder axle vs shipped, ticket-10 record): any >5°/failures among admitted?
3. Kill-site instrumentation (ticket-25/26 pattern): which stage kills GT-true B edges — RP overlap, CheckGraph@150, SingleOverlapTest@100, profile veto? Counts per site, fresh vs ORIG.
4. Verdict in the three-category frame: genuinely-failed method / broken measurement (ours) / wrong reference — with the number that decides.

**Acceptance:** kill site named with per-site fresh-vs-ORIG counts; gate + axle tables; verdict category + deciding number; job IDs + sacct states.

**Successor:** fix ticket per verdict (not cut here).
