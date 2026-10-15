# 12: Reverse-engineered axle finder (fit 01–04, prove on 05–08)

**What to build:** our finder, not their patch — reverse-engineered from three sources: the paper's method (§IV-B2), the shipped Pot A inputs+axles as the answer key, and the pristine code as clues. Starts from 09's working scaffold; closes the 1/8 → 8/8 gap with new variables 09 named.

**Answers:** E1

**Blocked by:** 09-pristine-axle-repair (kill verdict above).

**Status:** ready-for-agent

**Starting position (inherited, re-verify what you touch):** 09 leaves a working chain — loader shim, vote fix (direction ≤1.3° on pieces 01–04), from-paper LM refinement, validated scorer — that still scores 1/8: position stalls 3–5mm in a flat cost basin, small/multi-axis pieces fail on direction (worst 56°/200mm). Cost diagnostic proved the shipped axles ARE the GM-cost minimum but the basin around them is flat. Spartan scaffold to reuse: `/data/gpfs/projects/punim2657/Temp/potsac-p09-run/` (shim/, r2fix/, r3fix/refine_axis.m, score_vs_shipped.m). Paper: `C:\PR\papers\text\sfspp-2502.13986v1.md:169-177`. Pristine clone: re-clone upstream `DominicoRyu/SfSpp_preprocessing @ d5ee6865` yourself.

**The three unknowns (in this order, one variable at a time):**
1. **Point weighting** — what weighting of surface points makes each shipped axle the *unique sharp* minimum instead of a flat basin (rim vs wall balance, normal-confidence, radius arms).
2. **Search + de-dup** — what candidate generation and pruning finds small-sherd and multi-axle answers (pieces 07 has 3 shipped axes, 08 has 2; current dedup keeps only the top-1 neighbourhood).
3. **Rim/base handling** — what the small pieces need that the big ones don't (see 07's rim map + 08's toolbox notes).

**Rules:** fit on pieces 01–04 ONLY; pieces 05–08 stay sealed until the final frozen validation. Shipped axles are the test key, never finder input. New code lives in a new `axle_finder/` package (never edit `sfs_axes/` — quarantined — nor any fork pipeline file). Pristine files stay read-only (overlay, don't fork-edit). Kill branch: if weighting + search + rim work move the fitted score by nothing, stop and report — do not add a fourth variable on your own.

- [ ] Fit (01–04): per-piece direction + position errors after each variable, reported against the ≤5° / ≤2mm bar
- [ ] Frozen validation (05–08, run once, no tuning after unsealing): per-piece errors + pass count; bar for the ticket: 8/8 across fit + held-out reported separately as 4/4 + x/4
- [ ] Design note in Comments: for each variable, what was tried, what the paper says, what the shipped answer implies, what won — so a cold reader can re-derive it
- [ ] Job IDs + sacct states; no commits; Comments-only ticket edits

**Successor:** ticket 10 (generalise B–J) runs on the frozen finder from this ticket.
