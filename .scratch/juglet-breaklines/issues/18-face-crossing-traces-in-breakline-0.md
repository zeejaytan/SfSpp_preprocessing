# 18: Breakline_0 carries face-crossing traces (witnessed on Pot_A piece 2)

**Answers:** E1

**Blocked by:** nothing — measurement + small edgeline change

**Status:** ready-for-agent

**Needs-eye:** the originating look (`pota_12`, witnessed 2026-10-01) is
done and stands; closing needs no second look unless the fix changes what
red draws — then re-stage, since the eye is the only instrument that sees
this class (the gate passed WITH the pollution present).

## What the eye found (verbatim, `annotations_manifest_pota_12.jsonl`)

*"they seem to go well together. the red run on seam, most of the time,
however there is gaps. also on the blue sherd: there are straight lines
run across the sherds, these are not the seam"*

## What measurement says (2026-10-01, same-round reply)

- "Go well together": CONFIRMED. The thinnest pass (1-2) is genuine at
  sherd level. The 15/15 stands, now witnessed on its most fragile member.
- "Red on seam most of the time, with gaps": consistent with the coverage
  data (ticket 07 diagnosis). No action.
- "Straight lines across the blue sherd": CONFIRMED REAL, not a staging
  artifact (tubes are per file segment; the first-header skip is fixed —
  no streaks). Piece 2's `Breakline_0` (resample19, 4 segments) at GT:
  segs 0-4 and 5-23 hug the 574-pt wall rim (≤2mm — the red-on-seam the
  eye saw); seg 24-44 (21 pts, 38mm arclen) lies ON the mesh face
  (≤0.93mm) wandering up to 15.9mm from the wall rim. A 38mm trace across
  the face, inside the file that claims to be the rim.

## Why it matters (and why the gate didn't see it)

`Breakline_0` mixes the seam rim with face-crossing traces — most likely
ticket-14 appended decorative/patch rims (piece 2 owns 4+ `Decorative`
files of 75–119 ordered pts in the same run tree; exact attribution of
seg 24-44 is this ticket's spike, not assumed here). The gate scores per
segment pair and passes on the wall-rim portion, so the pollution is
invisible to it: on Pot_A every pair is a true mate, so extra segments
only add opportunities. On non-mate material the same content is
false-positive surface — the exact shape ticket 06 was created to kill
(a fragment passing as rim), re-entering through the append path. The
finer the gate gets, the more this class matters: it is currently the
only known false-positive surface in a passing bundle.

## What to build (spike first)

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

- [ ] Spike: seg-level attribution with byte evidence (which append, which
      call order)
- [ ] `Breakline_0` carries no unlabeled face-crossing trace, or the
      label + consumer exist and are tested
- [ ] Pot_A per-pair from 15/15 (no regression), Juglet 0/5-or-better,
      authors' arm alongside
- [ ] If red changes on piece 2: `pota_12` re-staged and re-witnessed
- [ ] Ticket 14's +4 pairs accounted for (kept or explicitly re-diagnosed)
