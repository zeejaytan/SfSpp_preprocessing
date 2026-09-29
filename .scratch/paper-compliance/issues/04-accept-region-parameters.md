# 04: Accept the region-growing parameters as measured-good

**Answers:** E1

**Blocked by:** nothing — record decision, no code change

**Status:** resolved 2026-09-29 — accepted with justification, no code change

**Needs-eye:** none — no geometry changes, no new claims about any sherd.

## Why this ticket exists

Paper (§IV-B1): τθ=4, τκ=1, nb=10. Ours: 4.5°/1.5, 15–40 neighbors,
adaptive cluster sizes (`mesh_processing_headless.cpp:1717-1727`, defaults
`:2174`). Ticket 16 gap 6. Ticket 12 measured the neighborhood exhaustively
on Pot_A: default optimal; tighter crashes the pipeline (2.0/3.0/3.5°);
looser degrades monotonically (5.0 ties 7/15, 6.0→6/15, 8.0→4/15, 15° crash,
25° mesh-stage fail).

There is nothing to build. This ticket exists so the deviation is *accepted
with justification* rather than left as an unexamined gap the next audit
re-reports. The justification is the ticket-12 sweep table, not preference.

## Acceptance criteria

- [x] This file records: values differ from the paper AND the ticket-12
      sweep shows the default optimal on Pot_A with both directions hurt or
      crash — so the values stand, and any future proposal to change them
      must beat the sweep table, not the paper text
- [x] The `SFS_SMOOTHNESS_DEG` / `SFS_CURVATURE_THRESH` env overrides stay
      (they are how the sweep was run; removing them would make the result
      unreproducible)
- [x] Ticket 16 gap-6 row updated to "accepted, see ticket 04 here" —
      or rather ticket 16's acceptance box for this row checked with this
      ticket cited (edit that file, don't duplicate the table)

Resolved 2026-09-29 with no code change: the sweep table (ticket 12 round
1+2: default 7/15, 5.0 ties, all other values worse or crash) is the
justification. No gate movement claimed or needed.
