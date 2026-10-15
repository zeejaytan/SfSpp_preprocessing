# 10: Generalise the frozen finder to pots B–J

**What to build:** the proof the finder works beyond the sample — run the frozen (a)-finder over pots B–J and score it where shipped axles exist.

**Answers:** E1

**Blocked by:** 16-sealed-revalidation (frozen finder + Pot A score below). Pot A held-out leg is already spent (05/07/08 scored in 16) — this ticket is cross-pot only.

**Status:** ready-for-agent

**Frozen finder:** `.scratch/pota-repro/p15-stage/axle_finder/` (committed; GM-refine (a)-variant — NOT the rejected (b)-variant in p16-stage). Run it exactly as frozen: no tuning, no per-pot adjustments. If a pot needs a tweak, record the miss and move on — adaptation decisions belong to the successor, not this ticket.

**Standing Pot A score (from 12/14/15/16):** 6/8 direction-pass under the position-conditional bar (direction ≤5° strict everywhere; position ≤2mm where the fragment spans enough shape; P01/P05 at the ~2-3mm material floor). Known misses riding along: P07 count (peel/dedup kills 2 of 3 real modes), P08 landscape (GM prefers a spurious pocket for sh1).

**Per-pot inputs (from ticket 01 census; surfaces face the same pipeline as Pot A):**

| pot | meshes | surfaces | shipped axles (test key) |
|---|---|---|---|
| B | 9 | 18 | 9 |
| C | 7 | 12 | 6 |
| D | 32 | 64 | 32 |
| E | 34 | 68 | 34 |
| F | 7 | 14 | 7 |
| G | 7 | 14 | 7 |
| H | 11 | 22 | 11 |
| I | 30 | 60 | 30 |
| J | 19 | 38 | 19 |

**Rules:** shipped axles are the test key, never finder input. Run pot by pot (largest pots D/E/I may need split jobs); keep steps queued back-to-back. Every sbatch gets a laptop-side poll (`sacct` directly — `slurm_poll.sh` exits immediately) with final State/ExitCode in the ticket.

- [ ] Per-pot table: pieces run, direction errors + radial errors vs shipped, nset vs shipped count, pass/fail under the position-conditional bar
- [ ] Per-pot verdict line: which pots look like Pot A (wall-dominated, direction-passing) vs new failure families (new geometry? multi-axis? base-heavy?)
- [ ] Comments section: cross-pot table + the sentence "the finder generalises beyond the sample: yes/no" with numbers
- [ ] E1 `Where it stands` update proposed in Comments for lead to write into intent/ (worker does not edit intent/)
- [ ] Job IDs + sacct states; no commits; Comments-only ticket edits

**Successor:** cut from the verdict — either per-family repair tickets (if new failure families) or the E2E gate proof (if B–J direction-passes).
