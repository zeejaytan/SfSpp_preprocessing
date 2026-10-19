# BetterWalk without the veto on Pot C — can the walker alone do it

GOAL: KNOW WHETHER THE WALKER NEEDS THE VETO.

**Answers:** E1

**Blocked by:** 156 (veto misfires on C01: kept=223 dropped=141 ate the true rim; gate 27.68mm/0%) + 155 (split-walk + half-plane guard ported, proven on Pot A relay).

**Status:** ready-for-agent

**What to deliver:** Pot C piece 01 extraction with veto DISABLED but the 155 sequencer (split-walk + half-plane guard) KEPT, gated the 98 way (cured-Bl_0 vs ORIG loops, pose cancels). Build a NOVETO variant in the relay worktree (veto bypass that keeps every admitted dot -- e.g. threshold to keep-all or env-gated skip; sequencer untouched), run on 156's staged Pot C inputs, gate vs fresh (5.61/22.9) and vs 156-cured (27.68/0). Verdict: does BetterWalk alone beat fresh on Pot C?

**Starting position:** 156 evidence (pota156_repro scripts, pota156_C tree, job scripts, gate scripts p156_gate.py/control/probe/render); 155 Comments (worktree, build commands, binary paths). New scratch pota158_repro/; renders artifacts/pota158/.

**Rules:** same-binary ORIG control alongside or void; veto-disable must not touch the sequencer code path (prove: SPLIT-WALK lines present, FACE VETO kept==all/dropped==0); COMMIT NOTHING (worktree-local build only); tickets 39-157 read-only; Comments-only ticket edits; sacct recorded; eye-check renders.

- [ ] NOVETO binary built (veto keeps all, sequencer intact -- proof lines)
- [ ] Pot C P01 run + gate vs fresh and vs 156-cured
- [ ] Verdict (walker-alone vs fresh) + render paths
