# 205 - Draw 204's D-loops: per-piece triplets vs ORIG

Status: open (lead 2026-10-20: cut per user m04809 -- draw 204's rim work now, same as 200/203, vs author)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Render what the 204 D chain did to every Pot C piece BEFORE the E2E lands, so the eye can judge the repair against the author's answer key while the jobs run. Same panel pattern as 199/200/203.

## Method (laptop-only render leg; COMMIT NOTHING)
1. Inputs: the four 204 D-loops (staged under .scratch/pota204_repro/ + the 204 bundle -- ask the 204 ticket/worker paths; C01 filed md5 matches 197's exactly), the four fresh loops, the four ORIG loops (answer key, draw-only). Mesh: C01 mesh as in 199/203 for the overlay.
2. Per piece (C01, C02, C03, C04): triplet (a) BEFORE = fresh loop on mesh, (b) AFTER = 204 D-loop on mesh, (c) AUTHOR = ORIG loop on mesh. Same viewpoint/scales as 203's triplets so they sit side by side. Plus one overlay panel per piece (fresh + D-loop + ORIG, three colours, as in 203).
3. Per-step panels for ONE piece only (C03 -- the interesting one: split leg holds at ~1.2-1.5mm yet output sits 6.5mm off per 204 worker): densify / split / thin / walk stages overlaid, 199 d/d2/e/f/g pattern.
4. Name-don't-fake: any loop file missing or unreadable is named, never synthesized. 203 already covers C01-both-versions; do not redo it, cite it.
5. Eye-check every PNG yourself (read_image) before reporting: state what changed per piece in one line each (closer to author? new damage? untouched?).

## Acceptance
4 triplets + 4 overlays + C03 per-step strip under artifacts/pota205/, all eye-checked by worker, paths + one-line verdicts per piece in Comments + final output. No E2E, no bundle, no sources touched.

## Required evidence
Ticket Comments + final output: PNG paths, per-piece one-line verdicts (BEFORE vs AFTER vs AUTHOR), any named-missing inputs.

## Comments (worker -- append below, do not edit above)
