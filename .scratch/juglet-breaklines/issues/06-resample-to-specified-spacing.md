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

**Status:** ready-for-agent

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

## Note

The paper's dataset has an edge-line perimeter of roughly 9 cm per
fragment, which at 1.9 mm is about 47 points — against the 200 our files
carry. Our output is dense in the opposite direction to the padding
problem, and this ticket corrects both at once by specifying spacing
rather than count.
