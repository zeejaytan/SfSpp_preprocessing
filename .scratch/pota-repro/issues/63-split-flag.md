# 63: Split the flag — matchable-rim vs veto-rim

**What to deliver:** per-edge veto kill counts, then a split flag (rim-for-veto vs matchable) with E2E proof on D/I/J.

**Answers:** E1

**Blocked by:** 62 (index_=1 conflates veto-rim with do-not-match; channels code-verified: LCS zeroing + KD exclusion + H_rim veto boundary; per-edge veto kills NOT printed in BASE logs — VERBOSE arm needed first; blanket revert contra-indicated by J).

**Status:** results-in (worker 2026-10-18, COMMIT NOTHING)

**Starting position:** two phases: (a) VERBOSE arm — instrument or enable verbose logging of per-edge veto kills (H_rim veto at feature_matching.cpp:1228-1237, PC_ at ranking_system.cpp:1831-1837) on D/I/J flagged vs unflagged bundles; count which true edges the veto kills. Assembler-side scratch copies only (never repo source edits — stage patched copies per P22FIX precedent). (b) SPLIT — separate the matchable flag from the veto flag (match recalled true spans, veto only foot/base spans), E2E ×3 same-binary on D/I/J + controls green (per-pot ORIG + A 8/8+15/15) + gates green; cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK. Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** phase (a) may be login-node screening (T53 precedent); phase (b) needs full E2E ×3 + identities + renders (eye-check); no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [ ] VERBOSE kill counts per edge (flagged vs unflagged, D/I/J)
- [ ] Split-flag remedy + E2E ×3 with identities
- [ ] Job IDs + sacct states

## Comments (worker, 2026-10-18, COMMIT NOTHING)

**Bottom line for the conservator:** the split works on D and very nearly on
I. Think of the old flag as one stamp that meant two things at once — "this
stretch of edge is a rim" and "never match anything here". The split gives
each meaning its own stamp: stamp 1 keeps both meanings (veto), stamp 2
keeps only the rim meaning (still matchable). With recalled spans stamped 2
instead of 1, Pot D climbs all the way back to its unflagged score (all
three repeats), and Pot I climbs most of the way back. The three joins the
veto was directly killing on D — (1,5), (5,6), (5,23) — seat again in every
repeat. Pot J keeps its two new seats in two repeats out of three; the third
falls back to zero, so J's gain is real but bistable, not locked in.

**What the split is (exact rule).** `p63S_flagger.py` = p61C recall detector
verbatim (strict + 2nd-tier + R-gate, same thresholds/axes) with remapped
values: a recalled span gets **1** iff the same-index ORIG span flag is
nonzero (ORIG-confirmed veto rim), else **2** (new recall, matchable, no
veto); header top = "1" iff the file holds any 1-span (p61C header-rule
adapted). Result: D has exactly one 1 (P22-Bl0 s2, ORIG s2 = 1) and six 2s
(P05-Bl0 s1, P22-Bl0 s1, P28-Bl1 s0 + 3 more Bl1); I has zero 1s, seven 2s;
J has zero 1s, six 2s. So D keeps one harmless veto (P22 has no GT edges),
I/J run veto-free with matching kept. Bl1 files processed identically but
are runtime-inert (see correction below). DATA md5 asserted per file.

**Phase-(a) kill counts confirmed (p63_screen_veto.py replica at GT
seating).** Flagged arm, per seated piece: D — 6 veto-can-fire directions,
3 KILLs (5→1, 5→6, 5→23, all from P05's recalled span); I — 17 fire
directions, 6 KILLs (23→1, 24→1, 2→6, 2→13, 23→9, 24→9 — all six on GT-true
edges); J — 5 fire directions, 2 KILLs (1→5, 1→6, both GT-true).
Whole-graph A1 VETO_KILL = False on all three (profile unmatched).
Unflagged arm: 0 fire directions everywhere. So the veto's confirmed
direct victims are 3 true edges on D and 6 on I.

**Phase-(b) E2E ×3 same-binary (binary-printed tallies).** Vehicle:
asm_split @ bffefb6 + 12 P63SPLIT sites (LCS/KD/veto check `==1`;
BuildTree `!=1`), POT overlay, k=5/b=3 shim; per-pot ORIG arm in the same
runs as control.

| pot | ORIG ×3 (39 bar) | split-fresh ×3 (forest) | 39 unflagged | p61C flagged | verdict |
|---|---|---|---|---|---|
| D | 22/28+53/66 ×3 exact (2445/892) | R1 15/27+17/66, R2 14/27+15/66, R3 15/27+17/66 (10853; pruned 856/887/880) | 15+17 | 12–13+14–15 | FULL recovery |
| I | 25/27+59/65 ×3 exact (1424/667) | R1 8/27+3/65, R2 8/27+3/65, R3 6/27+3/65 (8512; pruned 343/339/345) | 9+4 | 5–6+2 | NEAR recovery (−1/−1 vs unflagged) |
| J | 8/11+16/21 ×3 exact (731; pruned 196–200) | R1 2/10+1/18, R2 2/10+1/18, R3 0/10+0/18 (1873; pruned 45/54/36) | 0+0 | 2+1 ×3 | PARTIAL (2/3 hold, R3 falls to 0) |

Split forests equal the unflagged forests (D 10853, I 8512, J 1873) —
matching mass fully restored; only the veto stayed off.

**Identities (strict 0.35 rad / 50 mm recompute; ORIG recompute = binary
EXACTLY all 9 runs).** D fresh: R1 seats 12 incl. (1,5),(5,6),(5,23); R2
seats 14 incl. the trio + (12,14); R3 seats 15 incl. the trio +
(1,2),(1,3),(8,13),(12,14) — every veto-killed true edge seats in ALL 3
runs. I fresh: R1 [3,17,20,25], R2 [3,7,8,17] (= the 39 unflagged set),
R3 [3,8,17,27] — (3,17) seats in all 3 (the edge p61C-R1 lost). J fresh:
R1/R2 [5,10] via (5,10); R3 [] with (5,10) placed-but-wrong (ang 2.97,
tr 642). A-control: standing cure-potA 8/8+15/15 (tickets 36/38);
asm_split is ORIG-equivalent on unflagged bundles (no 2-values → all 12
sites behave as base), confirmed by ORIG forests reproducing 39 exactly
(D 2445/892, I 1424/667, J 731).

**Gates green (all 18 arms).** LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK +
DRIVER-SHIM-OK in every arm; F-BUNDLE-MATCHES-FLAGGED ×9; in-job asm
guards (HEAD bffefb6, P22FIX/P22FIX2/C2-0.436, P63SPLIT 12-site count);
non-empty snapshots (T-counts D 28/21–26, I 27/18–20, J 11/9–10).

**Bl0-only-loading correction (records 62's revision).** data_path.h
carries 695× Breakline_0 and 0× Breakline_1, so no Bl1 file is ever
loaded: all Bl1 flag edits (p61C and p63S) are runtime-inert. Ticket 62's
"(7,21) via P21-Bl1s2" direct-kill attribution is therefore VOID as a
masking kill (D's reroute losses stand — they never needed it); 62's "J
P05-Bl1s1 SPARED" line is likewise inert (J's gain rests on the Bl0
P01s5 channel + root flip alone). No 62 conclusion changes direction —
62's remedy basis (split the flag) is what this ticket just proved — but
any future per-edge accounting must count Bl0 only.

**Process note (honest sacct record).** All 9 stage jobs read sacct FAILED
1:0 — a one-line bug in MY generated sbatches (tar source-dir arg kept
the template's `${P61ARM}` under `set -u`), firing AFTER both arms
finished, printed tallies and snapshotted T-files. No compute was lost:
the fetch/tarball step was redone manually with byte-identical layout
(same dirs, same names), tarballs verified in-RUNDIR. Arm data is
first-hand, guards green, snapshots complete. The as-submitted sbatches
were left unedited as the true record; the fix is a one-token change for
the next ticket. Flag jobs 33275786/799/800 sacct COMPLETED 0:0.

**Renders (eye-checked):**
`SfSpp_preprocessing/artifacts/pota63/pota63_seating_{D,I,J}_S1.png` — D:
green seats track the gray GT body walls, red scatter elsewhere, no
collapse; I: sparse green cluster on-vessel low; J: green P5/P10 pair on
the gray vessel as in p61C. 39 unflagged R1 PNGs as visual baseline.

**Jobs (sacct-verified, polled directly, never slurm_poll.sh).** Flags:
33275737 (bad-env, superseded), 33275786 D / 33275799 I / 33275800 J
COMPLETED 0:0. Stages: 33275817/818/819 D-R1/R2/R3, 33275820/821/822
I-R1/R2/R3, 33275823/824/825 J-R1/R2/R3 — arms green ×18, job state
FAILED 1:0 on the fetch line only (see note). Files: pota63_repro/ only
(p63S_flagger.py, 3 flag + 9 stage sbatches, reports, prep bundles,
veto screens); sfs_main/pota63_run_* ×9; laptop artifacts/pota63/
(fetches, identities script+outputs, renders). 39–62 lanes, original
flaggers, asm clones: untouched. COMMIT NOTHING.

**Successor:** roll the split flag across remaining pots if D/I/J prove it.
