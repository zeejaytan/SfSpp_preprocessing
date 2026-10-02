# 18: Breakline_0 carries face-crossing traces (witnessed on Pot_A piece 2)

**Answers:** E1

**Blocked by:** nothing — measurement + small edgeline change

**Status:** resolved 2026-10-02 — REFUTED by measurement (see spike).
No code changes; the lines are true seams in the wrong look context.

**Needs-eye:** the originating look (`pota_12`, witnessed 2026-10-01) is
done and stands; no re-stage (nothing changes).

**Needs-eye:** the originating look (`pota_12`, witnessed 2026-10-01) is
done and stands; closing needs no second look unless the fix changes what
red draws — then re-stage, since the eye is the only instrument that sees
this class (the gate passed WITH the pollution present).

## What the eye found (verbatim, `annotations_manifest_pota_12.jsonl`)

*"they seem to go well together. the red run on seam, most of the time,
however there is gaps. also on the blue sherd: there are straight lines
run across the sherds, these are not the seam"*

## What measurement said 2026-10-01 (SUPERSEDED — see spike outcome below;
kept so the retraction is auditable)

- "Go well together": CONFIRMED (stands — thinnest pass genuine).
- "Red on seam with gaps": consistent with coverage (stands).
- "Straight lines": CONFIRMED REAL as geometry (stands — tubes are
  per-segment, no streaks) BUT misattributed: "most likely appended
  decorative/patch rims" was stated before measuring and is WITHDRAWN.
  The segs are <30pts (append floor excludes them); they trace the 2-8
  seam (0.07–0.13mm). The "false-positive surface / pollution" framing
  below is withdrawn with it — there is no known false-positive surface
  in any passing bundle at this time.

## SPIKE OUTCOME 2026-10-02: premise refuted — the lines are true 2-8 seams

Attribution by the ticket's own rule (≥30pts + T14 log lines for appends;
byte comparison where applicable):

- Piece 2's small segs (5/19/21 pts) are all BELOW the 30-pt append floor
  (`kMinPatchRimPoints`) — they CANNOT be ticket-14 appends. (The e2e
  rebuild's T14 log confirms the mechanism working as designed: 114+119pt
  appends logged with file positions, sub-30 fragments skipped loudly.)
- At GT against ALL of piece 2's mates (correct Pot_A transforms this
  time — an earlier pass used Juglet transforms and produced garbage
  200–600mm figures, discarded, not trusted):
  s0 → 0.13mm from piece 8; s2 → 0.07mm from piece 8; wall → 0.09–0.13mm
  from pieces 1, 4, 5 AND 8 (the full loop passes every seam).
- So s0/s2 trace the **2-8 seam** — genuine seam content, invisible in a
  look that shows only sherds 1+2. The eye read them correctly ("not the
  seam" = not the 1-2 seam); the defect inference was the agent's, from
  a context-limited look, and it is withdrawn. Duplicate seam coverage
  (wall + fragments all on 2-8) is harmless to the gate (more inliers).
- s1 (19pts, nearest 9.8mm from piece 8): near-seam fragment, minor,
  unexplained — recorded, not chased (one fragment, no gate impact).
- CORRECTION of the 2026-10-01 same-round reply: "most likely appended
  decorative/patch rims" was wrong — stated before measuring, against
  this ticket's own spike rule. Retracted with the numbers above.

1. Attribute seg 24-44 (and 0-4/5-23): decorative append, patch-rim
   append, or wall-rim branch (interior ring)? Read the append call order
   vs Integration Point #1 and the `Decorative_*.pcd` contents for piece
   2 — `cmp` bytes, don't eyeball.
2. Then separate or label: flag per segment in the file, a second file,
   or a matcher-side weight — whichever is smallest such that a bundle
   with face-crossing content either drops it or declares it. Removing
   patch rims outright is NOT the default: they recovered pairs 2-4/2-5
   (ticket 14, +4 measured). The fix must keep what joins while labeling
   what doesn't trace a seam.
3. Re-measure per pair both pots + authors' arm; re-stage `pota_12` if red
   changes (the eye must confirm the lines are gone, numbers can't).

## Acceptance criteria

- [x] Spike: seg-level attribution — DONE (not appends: <30pts floor
      excludes + T14 log corroborates; 2-8 seam traces at 0.07–0.13mm)
- [x] No unlabeled face-crossing trace exists — VACUOUS (duplicate 2-8
      coverage is wall loop + corner-split fragments of the same seam)
- [x] Pot_A 15/15 untouched (no code changed); Juglet unmeasured (nothing
      to measure — no change)
- [x] Re-stage NOT NEEDED (nothing changes)
- [x] Ticket 14's +4 pairs unaffected (append mechanism exonerated)
