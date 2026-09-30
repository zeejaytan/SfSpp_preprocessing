# 06: Resample to the specified spacing and report traced length

**What to build:** edge-line points are spaced as the method specifies
rather than padded to a fixed count, and every breakline file states how
much curve was actually traced.

The paper (§IV-B1): "The filtered points are resampled to generate
equidistant points with a point-to-point distance of d = 1.9mm, an
empirically optimized value." The code instead pads to exactly 200
points. **This is what let a 3.6 mm fragment pass every count-based
check** — a bundle was accepted as sound because each file held 200
points, while one sherd's entire "breakline" spanned less than four
millimetres. Point count has been carrying no information about trace
quality.

**Answers:** E1

**Blocked by:** 05 (resample the filtered, ordered edge line)

**Status:** resolved 2026-09-30 — equidistant resampling live, gate held
on Pot_A (15/15), Juglet unmoved (0/5 scorable). One crash found and fixed
by the change (below); it is part of this ticket, not a new one.

**Needs-eye:** none.

- [ ] Points are spaced at the specified interval, exposed as a
      parameter defaulting to 1.9 mm — not hard-coded, because that value
      was tuned on larger vessels and ours are an order of magnitude
      smaller
- [ ] The fixed 200-point padding is **removed**, not re-tuned
- [ ] Every breakline file reports its traced length, and a seam test
      fails if a length is missing
- [ ] A run whose traced length is a small fraction of the rim it should
      cover is loud in the log, so a fragment cannot again pass silently
- [ ] The header format the assembler reads (segment count, total points,
      per-segment ranges) is unchanged, so no assembly-side change is
      needed; the length is added as a comment line the assembler ignores

## RESOLVED 2026-09-30

- Spacing parameterized (default 1.9, `SFS_RESAMPLE_MM` per-run override);
  clamp and skip-if-dense deleted; mm/m unit lie fixed; traced length +
  loud ≤5-point warning per breakline (`[SFS-T06]`).
- Files now carry honest counts (Juglet Breakline_0: 8–32 pts at 1.9mm —
  the 200-count fiction is gone). One ≤5-pt warning fired in the Juglet
  run. Header format unchanged; length to stdout, not a file comment
  (assembler header parser is position-sensitive — recorded deviation).
- **Crash (exit 139, Juglet piece 2):** 12-pt rims reached segment raw-point
  gathering, whose `nearestKSearch(pt,20)` + hardcoded `i<20` loop read
  past the results on clouds smaller than K. Masked for years by
  clamp-inflation (≥30 pts). Bounded by found count; other three neighbor
  searches audited (all iterate found-size). Theory confirmed by
  intervention: rerun completes all 7 present pieces. Adjacent fix:
  `"Detected segments = " + int` was pointer arithmetic (log showed
  "etected segments = "); streamed properly.
- Pot_A `resample19` 15/15 — all pairs pass (thinnest 2-8 at 2 inliers);
  vote pattern unchanged.
- Juglet 0/5 scorable, 5 unmeasurable, zero copies. Traces moved (6-7
  min_d 3.5→16.9mm); run-to-run variance vs resampling effect
  unattributed (mesh stage is nondeterministic across runs — votes moved
  440v364→444v360); score unmoved, so no regression by the ticket's own
  criterion (a passing pair failing).
- Honest consequence on record: piece 2 (9 pts) and piece 7 (8 pts)
  breaklines now sit below the assembler's 50-point shard threshold —
  the fiction previously kept them above it. The assembler logs that drop
  (fixed earlier); short rims now fail loudly downstream instead of
  passing silently here.

## Note

The paper's dataset has an edge-line perimeter of roughly 9 cm per
fragment, which at 1.9 mm is about 47 points — against the 200 our files
carry. Our output is dense in the opposite direction to the padding
problem, and this ticket corrects both at once by specifying spacing
rather than count.
