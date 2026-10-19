# Apply, build, re-extract — switch the cure on

GOAL: FALSE DOTS FILTERED AT THE SOURCE IN PRODUCTION.

**Answers:** E1

**Blocked by:** 153 (patch staged in .scratch/pota153_repro/: face veto @ :954-965 + DELETE :1032 reload-over + walker split/guard + GridX veto; veto field decided ORIG-free; build instructions staged; repo sources untouched)

**Status:** results-in

**What to deliver:** (1) apply the staged hunks to the prep working tree (fuzz/anchor notes in the staged files; backup/non-headless copies stay untouched); (2) get it built — login-node/laptop means first, Spartan container recipe per the staged instructions if needed; if the build needs a Spartan relay beyond your reach, stage the applied tree + exact build commands and STOP (lead relays); do NOT submit Slurm jobs yourself; (3) re-run the Pot_C_Piece_01 C-base extraction with the new binary and score vs the 182/195 baseline with 148/150 counters (bar: outer ~1, inner 88/88) — full [FACE VETO]/[SPLIT-WALK] counter lines in Comments.

**Starting position:** .scratch/pota153_repro/ (diffs + build instructions + ORIG-free note), 150 §1 (file:line). New scratch pota154_repro/; renders under laptop artifacts/pota154/.

**Rules:** ORIG Bl_0 ruler-only; no ORIG-derived constants in applied code — mesh-observable gates only; worker COMMIT NOTHING (lead reviews diff and lands); tickets 39-153 read-only; Comments-only ticket edits.

- [ ] Hunks applied in working tree (applied-diff vs staged-diff reconciliation)
- [ ] Build result (binary path or staged-tree + relay commands)
- [ ] Re-extraction scored vs 182/195 (or staged for relay)
## Comments (worker, 2026-10-19 -- cure applied, staged for relay; COMMIT NOTHING)

Verdict: CURE APPLIED IN WORKING TREE, BUILD+RE-EXTRACT STAGED FOR RELAY (no laptop toolchain).

1. Hunks applied (reconciliation 4/4 MATCH vs staged). edgeline_extraction_headless.cpp @ 73c3e9e via anchored applier .scratch/pota154_repro/apply_patch.py (CRLF-preserving): hunk 0 includes; hunk 1 face veto @ :954-965 verbatim (FACE_ALIGN_VETO=0.5, in-function surfCentroid, FACE-VETO log); hunk 2 DELETE :1032 reload-over (context-verified); walker :806-892 replaced verbatim (86-line old span asserted, signature unchanged). git diff --stat: 1 file +135/-65; backup and non-headless copies untouched. Brace delta -1 is prose in the staged header comment (code braces balance); GridX SURF-C1 has no prep target (nothing to apply). Relay copy: .scratch/pota154_repro/applied.diff (vs 73c3e9e). Full record: .scratch/pota154_repro/relay_and_reconciliation.md.

2. ORIG-free recheck: PASS. Added-line grep for ORIG/Bl_0/author = 3 hits, all comment prose from staged text; no ORIG geometry in code; gates stay 0.5/5mm/6mm mesh-observable literals.

3. Build: STAGED-FOR-RELAY. No cmake/gcc/PCL on laptop (verified); Temp/Data Pot_A only. No compile, no Slurm. Read-only Spartan probe: login2 alive, REMOTE_ROOT at a5d9ccd (BEHIND laptop, lead reconciles), remote tree DIRTY (modified non-headless copy + untracked Juglet dirs) -- worker touched nothing remote. Exact relay commands in relay_and_reconciliation.md section 3.

4. Re-extraction: STAGED (not run). Counters to beat (150 baseline: C-base 270, inner 88, outer 182, share 182/195=0.933; bars outer red>=0.90, inner 88/88) + FACE-VETO/SPLIT-WALK log watches in relay note.

5. Renders: NONE fresh (relay produces artifacts/pota154/ plots). Tickets 39-153 untouched; COMMIT NOTHING done.
