# Pot A re-gate with no veto in path

GOAL: KNOW WHETHER THE REFERENCE CURE SURVIVES ITS MECHANISM BEING WRONG.

**Answers:** E1

**Blocked by:** 170 (worktree + binaries; sequence AFTER it lands -- same relay worktree, no parallel builds), 153/155 (veto-cured Pot A 8/8 now unexplained under user ruling 2026-10-20: veto dropped for all, mechanism wrong), 169 (snap med 2.19 on-rim; veto destroys vs moves).

**Status:** ready-for-agent (170 landed 2026-10-20 -- unblocked).

**User ruling (2026-10-20):** a logically wrong mechanism cannot be kept because it produces the right result on one example. Re-gate Pot A veto-free and watch the 8/8 together.

**What to deliver:** Pot A pairs + Pot G slot-swap controls (155 recipe) rebuilt/run with NO veto stage (neither dead reload-over read-out nor live Ticket-05 filter) in the walked path; same-binary ORIG control alongside or void. Score pairs seated/8 + controls 15/15-equivalent vs the veto-cured numbers (8/8 + 5 unique seats, 155 Comments).

**Bar:** EITHER veto-free Pot A holds 8/8 (user right, veto never load-bearing -- veto programme closed) OR it regresses with per-pair owners (veto was load-bearing on clean meshes -- per-piece policy returns to the table with numbers). Both are landings; only an ungated claim is a failure.

**Starting position:** 155 Comments (recipe, pair counts, worktree + build); 153 Comments (veto patch); 169 Comments (veto-loss numbers). Scratch pota171_repro/; renders artifacts/pota171/.

**Rules:** dataset read-only; relay worktree restore byte-identical; COMMIT NOTHING; tickets 39-170 read-only; Comments-only ticket edits; sacct recorded; eye-check renders.

- [x] Pot A veto-free pairs + controls, gated vs veto-cured numbers
- [x] hold-or-regress verdict with per-pair owners on regress
- [x] Verdict + render paths

## Comments (worker, 2026-10-20 -- NOVETO relay run; COMMIT NOTHING)

**Verdict: REGRESS with per-pair owners -- the veto is load-bearing on intact-mesh Pot A. Per-piece policy is back on the table with numbers. The ticket's 8/8 bar is ungated as written: no veto-cured Pot A 8/8 exists in 153/155 Comments (those hold pair counts + relay record only; 8/8+15/15 live in the 145 assembly table, a different repo lane), and no Pot_G inputs exist in the relay worktree (Dataset/Breaklines + Point + Mesh hold Pot_A + Juglet only), so Pot G slot-swap controls are unrunnable in this lane. The gate actually run: same staged surfaces, veto-cured (155) vs veto-free (171) pair counts + eye-checked overlays. Same-binary ORIG control VOID (no ORIG breaklines for Pot A in this lane; dataset read-only forbids importing them); substituted with three pipeline-validity controls below.**

0. CONTROLS (all GREEN). (a) In-state control: current Breaklines == pair_cure/ 8/8 Bl_0 SAME (bit-identical) before and after -- frozen veto-cured state entered and restored. (b) NOVETO-proof lines in run_noveto.log: 16x [FACE VETO] kept==all dropped==0 (thresh 2.0), 16x [POTA171-NOVETO] T05 bypass, SPLIT-WALK sequencer active (32 lines), NOVETO-RUN-EXIT:0. (c) Restore: worktree diff md5 e546596c90f8552ed9a40db34c5c2a4b == baseline, veto binary 19397aab41908acc15f640c7a44aff55 restored, Breaklines content-identical to backup (5886758985a81de635c737cdccca7e66), 29 status lines == baseline, no pota171 spill. sacct: build 33447936 COMPLETED 0:0 el 51s; run 33448009 COMPLETED 0:0 el 57s. Tickets 39-170 untouched (read-only); relay worktree entered only for build+run, production checkout never touched; dataset read-only.

1. PAIR COUNTS (pcd lines, 155 convention; dots = -11). Veto-free Bl_0 moves back toward BASE on exactly the 4 pieces where the veto bit hardest in 155: P02_0 181 vs 97 (base 743), P03_0 167 vs 80 (base 502), P04_0 162 vs 103 (base 259), P05_0 166 vs 97 (base 343). Plus P01_1 337 vs 190 (base 210) and P06_0 160 vs 129. HOLD everywhere else (deltas 0..+10, within the +/-7 resample band 155 measured on P01_0). Full table: .scratch/pota171_repro/p171_evidence.txt. Honesty note: this arm bypasses veto+T05 together per the ticket verbatim, so deltas are the combined vetoless-path effect; vs-BASE comparison is confounded by the sequencer (BASE = production binary with old greedy sequencer; 171 = new split-walk), so CURE-under-new-sequencer is the gate reference.

2. OVERLAYS (all 6 eye-checked). P02_0: veto-free traces the FULL closed rim loop, cured keeps only the bottom arc -- the second-face loop the veto was built to kill is back. P03_0: same, full outer loop returns. P01_1: veto-free admits a full extra outer loop the cured cloud lacks -- not an anomaly, the same veto effect on the Bl_1 side. P01_0 / P08_0: dot-for-dot identical loops -- HOLD confirmed visually. Renders: artifacts/pota171/p171_counts.png + p171_<stem>.png (5 overlays, top XY + side XZ).

3. PER-PAIR OWNERS. REGRESS: P02_0 (+84), P03_0 (+87), P04_0 (+59), P05_0 (+69), P01_1 (+147), P06_0 (+31 mild). HOLD: P01_0, P02_1, P03_1, P04_1, P05_1, P06_1, P07_0, P07_1, P08_0, P08_1. So 6/16 pairs need the veto, 10/16 do not -- the veto is load-bearing exactly where 155 showed it biting, and dead weight on clean rims. That is the per-piece policy input: keep the veto for P02/P03/P04/P05-class double-face geometry, drop it where the admission cloud is already single-face.

**What would overturn this:** a veto-free run on the same staged surfaces that keeps P02_0/P03_0/P04_0/P05_0/P01_1 at cured counts with the loops closed -- i.e. a single-face admission mechanism that is not the veto; or a showing that the returned outer loops seat better downstream (assembly lane, not this one). E2E seating is out of scope here by lane boundary.

Status: results-in.
