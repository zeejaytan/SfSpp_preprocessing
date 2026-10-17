# 57: NURBS lip-region refit — move the material, don't cut it

**What to deliver:** a refitted B-p2 S1 lip with ORIG-like standoff — valid thickness, honest strengths, E2E lift.

**Answers:** E1

**Blocked by:** 56 (lip-curl NURBS-fit error in ~3mm band, 8× excess hugging material; JOINT bound 66→7 — wall behind outside ray corridor; cut dead; ONLY a refit that moves material qualifies) + 54 (sheets fine off-lip at 0.34mm — refit must preserve the bulk).

**Status:** results-in (worker 2026-10-17, COMMIT NOTHING)

**Starting position:** the refit must (a) exclude the curled lip-band cluster points, (b) refit the lip region from honest neighbouring material (mesh + wall points), (c) preserve the innocent bulk (0.34mm agreement — gate on bulk drift), (d) keep rim spacing untouched (50: matcher keys off raw sampling). This reaches into the surface-fitting stage (RegionGrowing/NURBS pipeline) — work in scratch copies of the fitting chain, not the repo source. Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only. Render references: artifacts/t56_lip.png, artifacts/t56_depth.png.

**Rules:** land ONLY with standoff recovery toward ORIG (2.87) AND/OR valid-thickness recovery toward 97%/med 2.9 AND/OR honest strength lift AND/OR E2E lift ×3 same-binary runs + controls green (B ORIG 9/9+15/15, A 8/8+15/15) in same runs + gates green + bulk-drift gate (off-lip sheet must stay within ~0.5mm of current); renders (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [ ] Lip refit arms, one variable each
- [ ] Standoff/thickness/strength/E2E lift or measured why-not
- [ ] Job IDs + sacct states

**Successor:** cross-pot generalization of the B recipe (C–J share the drowning shape).

## Comments (worker, 2026-10-17, COMMIT NOTHING)

**Bottom line: measured why-not — no lift. Eleven scratch refit variants that MOVE (not cut) the lip-band material all fail the joint ORIG gauge (146/150 valid, med 2.90, standoff 2.87): validity and median move in opposite directions with no ORIG-like joint point, and even TRUE rim positions + refit (the ceiling of "regenerate lip + reseat rim") reach only 74–99 valid. Scratch refit of existing points is exhausted; what remains is a genuine pipeline NURBS refit that ADDS correctly-placed wall material inside the ray corridor, which point moves cannot create.**

**Arms (all OUR-only, zero ORIG points; rim byte-identical throughout; bulk drift 0.0000 beyond blend by construction — bulk gate HELD; gate untouched by construction — Breaklines never written):**
- REFIT-A wall-plane projection (band→inboard plane, R3/5): 124→54 valid, med 1.73→2.19, standoff 0.64→3.44 (overshoot, corridor-escape — move ACROSS rays, same death as excision).
- REFIT-C radial-from-rim push δ 0.8/1.3/2.0 (move ALONG rays): 122/109/91 valid, med 2.03/2.23/2.58 — monotonic validity↔median tradeoff, no joint point.
- REFIT-D lateral snap to ray α 0.5/1.0: 128/145 valid but med 1.79/1.27 — validity without depth.
- REFIT-F per-point local wall-depth extension (honest-neighbor target, in-corridor): 151–159 valid but med 1.25–1.42 — even perfect wall extension gives thin hits: the rim-wall GEOMETRY is wrong, not just shape.
- REFIT-E ray-direction depth remap to OUR-only inboard target (n=18, med 3.50): 163–164 valid, med 3.52, standoff 3.06 — past ORIG on all three, BUT eye-check refutes it: flat uniform 3.4 shelf (128/163 hits in one qbin, Cond4 p2-p1 7.4%→46.9% = veto-silence class T54 proved E2E-dead), a 50mm ray escape, and a visible discontinuity cliff at the blend edge (t57_refit.png idx 155/170/180). Sculpting to the gauge, not a wall.

**Ceiling joints (diagnostic, never fixes): TRUE ORIG rim positions + refit → E 74, F 98, D 99 valid (vs ORIG 146); E tuned to OUR rays collapses from true rays (163→74, overfit signature). Neither side nor both together suffice.**

**E2E/strength:** none spent — no arm presents an ORIG-like joint offline point; T54 STRONG already showed veto-silence (E's class) does not admit the honest 2-1 edge E2E 3/3. Controls/gates N/A (no bundles staged).

**Job IDs + sacct:** none — offline login-node numpy screening only (same basis as T53/T55/T56). No sbatch submitted, nothing to poll. Slurm never touched.

**Renders (eye-checked):** `SfSpp_preprocessing/artifacts/t57_refit.png` (BASE vs REFIT-E xsec — flat orange shelf + blend cliff), `SfSpp_preprocessing/artifacts/t57_depth.png` (E = dead-flat ~3.5 line vs ORIG's structured 1–5mm profile).

**Work dir:** `/data/gpfs/projects/punim2657/pota57_repro/` (refit57*.py, render57.py, S2*.npy, t57 PNGs). Tickets 49–56 + p47/p49 flaggers untouched (read-only reference only).

**Successor:** genuine pipeline NURBS lip-region refit with re-sampled wall (must place NEW material inside the 1mm ray corridor at 1–5mm structured depth — moves of existing points provably cannot); or beam-side rerouting (ticket 43 lane).
