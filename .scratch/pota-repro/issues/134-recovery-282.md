# Recovery gate on 282 — tell honest density from stuck

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 133 (3 dots junk 0 visited on-road, but greedy ratio 116/282=0.4113 trips T13's absolute 0.40 gate and suppresses recovery; forced-T13 probe 209/gate 4.3001/uncovered 8 NOT banked; key-space refusal at far-arc dot, 208 unique keys of 282 slots) + 126 rule-form (derive from the bag, never port; a per-bag constant is a port — the gate must be a FUNCTION of bag/walk state)

**Status:** ready-for-agent

**What to deliver:** a recovery rule that fires on the 282 bag. Constraint (ORIG-free, stated before running): the trigger must be a function of walk/bag state, not a re-tuned constant — name the feature that distinguishes honest-density ratio (dots sequencing on-road, coverage falling) from stuck ratio (no visits, coverage flat) and gate recovery on THAT. Candidates: visits-per-N-steps, coverage-delta-per-N-steps, unique-key exhaustion rate — worker's choice, stated first with the honest-vs-stuck evidence from the 133 freeze. Test on 282: walk + gate vs both marks (verbatim 116-strand AND forced probe 209/4.3001/8 — match-or-beat the probe honestly; beating it banks the recipe, matching it confirms the mechanism). Success bar: walk >=206 AND gate at/below 4.3107 AND uncovered below 15 AND 0 jumps >=40mm AND the trigger feature stated with its honest/stuck separation. If no state-function separates them, refute with the distributions — that says recovery-gating is bag-specific and the 282 walk stays probe-class.

**Starting position:** .scratch/pota133_repro/ (282 bag, forced probe, ratio/key evidence), pota116_repro/ (recovery tier reference). Login-node numpy only — no Slurm, no E2E. New scratch pota134_repro/; render under laptop artifacts/pota134/ (trigger-feature distributions honest-vs-stuck, walk vs 279/282, gate).

**Rules:** control reproduces 133's two marks first (verbatim strand 116 + forced probe numbers quoted, probe NOT re-run as control... no: reproduce the strand, quote the probe from file) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; NO re-tuned constants.

- [ ] Strand reproduced + trigger feature stated with separation
- [ ] Recovery walk vs both marks
- [ ] Verdict + recipe or bag-specific refutation
