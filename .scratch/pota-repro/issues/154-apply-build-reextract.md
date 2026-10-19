# Apply, build, re-extract — switch the cure on

GOAL: FALSE DOTS FILTERED AT THE SOURCE IN PRODUCTION.

**Answers:** E1

**Blocked by:** 153 (patch staged in .scratch/pota153_repro/: face veto @ :954-965 + DELETE :1032 reload-over + walker split/guard + GridX veto; veto field decided ORIG-free; build instructions staged; repo sources untouched)

**Status:** ready-for-agent

**What to deliver:** (1) apply the staged hunks to the prep working tree (fuzz/anchor notes in the staged files; backup/non-headless copies stay untouched); (2) get it built — login-node/laptop means first, Spartan container recipe per the staged instructions if needed; if the build needs a Spartan relay beyond your reach, stage the applied tree + exact build commands and STOP (lead relays); do NOT submit Slurm jobs yourself; (3) re-run the Pot_C_Piece_01 C-base extraction with the new binary and score vs the 182/195 baseline with 148/150 counters (bar: outer ~1, inner 88/88) — full [FACE VETO]/[SPLIT-WALK] counter lines in Comments.

**Starting position:** .scratch/pota153_repro/ (diffs + build instructions + ORIG-free note), 150 §1 (file:line). New scratch pota154_repro/; renders under laptop artifacts/pota154/.

**Rules:** ORIG Bl_0 ruler-only; no ORIG-derived constants in applied code — mesh-observable gates only; worker COMMIT NOTHING (lead reviews diff and lands); tickets 39-153 read-only; Comments-only ticket edits.

- [ ] Hunks applied in working tree (applied-diff vs staged-diff reconciliation)
- [ ] Build result (binary path or staged-tree + relay commands)
- [ ] Re-extraction scored vs 182/195 (or staged for relay)
