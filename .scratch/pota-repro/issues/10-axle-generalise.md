# 10: Axle generalisation (held-out pieces, then pots B–J)

**What to build:** the proof the repaired finder works where no reference axles exist — fit on some pieces, test on the rest, then extend across pots.

**Answers:** E1

**Blocked by:** 09-pristine-axle-repair (only a winning repair is generalised; a kill verdict closes this ticket unrun).

**Status:** ready-for-agent (runs when 09 reports a win)

**Pristine-only rule (binding):** same as 09. Shipped axles are the test key, never training input — the finder may not read the answer file for the piece it is estimating.

- [ ] Held-out test on Pot A: repair fitted on ≤4 pieces, tested on the remaining pieces — report per-piece errors; bar: ≤5° and ≤2mm on all held-out pieces
- [ ] Cross-pot extension: run the frozen repaired finder on pots B–J pieces (census counts in ticket 01: 164 meshes total); where shipped axles exist score them, where none exist report Gate per-pair seating at k=5/b=3 as the behavioural check
- [ ] E1 `Where it stands` update proposed in ticket Comments for lead to write into intent/ (worker does not edit intent/)
- [ ] Comments section: held-out table + cross-pot table + the sentence "the finder generalises beyond the sample: yes/no" with numbers
