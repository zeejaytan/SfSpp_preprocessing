# Re-extract Juglet breaklines so a 2 mm / agreeing-normal join gate can pass

## Why

The SFS++ assembler decides two sherds join by asking whether a point on
one sherd's breakline lies within ~2 mm of a point on its neighbour's,
with the two surface normals agreeing. It passes 15/15 on the pot it was
developed on, and **0/18** on the Juglet — including when the assembler is
handed the exact ground-truth placement of a genuinely-touching pair
(assembly ticket 06, 2026-09-26, validated by a Pot_A control on the same
harness).

Something we produce is not consumable. This feature finds out what, fixes
it, and proves the fix with a test that can fail.

## What "proved" means

`gate_probe_b0.py` (lives in the assembly repo) places a bundle's
breaklines at ground truth and counts how many true mates clear the
assembler's own gate. Today: Pot_A 15/15, Juglet 0/18. **A change to the
extractor is done when that number moves and Pot_A stays at 15/15.**
Not when a render looks plausible — the whole finding so far is that
plausible-looking curves failed.

## Shape of the work

1. **Measure before changing.** Per sherd, per segment: which wall face
   (inner/outer/both) did it come from, and does it span the GT contact
   point? Two candidate causes, currently undistinguished: traces on
   opposite faces of a 1.8 mm wall, and traces that miss the seam.
2. **One variable per experiment,** in `patches/juglet_*.patch` as
   established. A bundle of changes teaches us nothing about which one
   worked.
3. **Re-measure with the same probe** after each experiment.
4. **Render** the extracted curve on both sides of a real seam through
   `visual-qa/` before claiming anything.

## Out of scope

- Assembler changes. If a good breakline still gets rejected, that is a
  finding to hand back, not a thing to fix here.
- The Juglet's axis extraction (a separate, already-closed line of work).
- Early Kurgan material — no answer key, not yet.

## Honesty requirements

- **Pot_A is the control and must not regress.** A change that helps the
  Juglet and breaks Pot_A is not a fix; it is a Juglet-only special case
  and must be labelled as one.
- **Report the remainder.** If 12/18 pass afterwards, that is the result.
  Do not report "fixed."
- **A pass rate is not a shape.** The number must be accompanied by a
  witnessed render, and the render must resolve the millimetre scale
  being claimed.
