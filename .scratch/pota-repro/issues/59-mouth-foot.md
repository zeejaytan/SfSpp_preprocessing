# 59: Mouth/foot disambiguation — teach the marker which edge is lip

**What to deliver:** a flagger that marks mouth arcs and spares foot arcs — then F re-piloted at/above the unflagged baseline.

**Answers:** E1

**Blocked by:** 58 (pilot-negative: F fresh 0/6+0/9 ×3 vs unflagged 4/6+3/9; 3 recall losses on E2E pieces + 5 fresh-only flags on ORIG-base/zero edges; LCS masking 136→67 + H_rim veto; B's clean set doesn't replicate) + 46 (ORIG top-sign already encodes rim-vs-base; paper §IV-B1 test ignores it).

**Status:** results-in (worker 2026-10-17, COMMIT NOTHING; lead owns checkboxes + roll-out call)

**Starting position:** two gaps: (a) DISAMBIGUATION — ORIG's top-sign column already says mouth vs foot; the paper recipe test ignores it, so foot arcs that pass the geometric test get flagged and poison via masking + veto. Use the sign (honestly computed on OUR outlines, never copied) to spare foot arcs. (b) RECALL — 3 true mouth arcs on E2E pieces too rough fresh to pass; chopped-fragment-tolerant recall (shorter arcs? roughness-tolerant thresholds?) without re-admitting feet. Bundle reference: Spartan pota58_repro/ + pota39 F bundle (read-only); flagger copies p58_flagger.py (copy, never edit p47/p49 originals). Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** land ONLY with F fresh at/above 4/6+3/9 unflagged baseline ×3 same-binary runs + identities + controls green (F ORIG 6/6+9/9, A 8/8+15/15) in same runs + gate green; renders (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [ ] Mouth/foot disambiguation arm(s), one variable each
- [ ] Recall arm(s) on chopped fragments
- [ ] F re-pilot ×3 + identities or measured why-not
- [ ] Job IDs + sacct states

**Successor:** roll-out to C–J per ticket 58 (pilot G second, then rest).

## Comments (worker, 2026-10-17 — F RE-PILOT AT BASELINE, measured)

**Verdict: the mouth/foot fix restores F fresh E2E from 58's 0/6+0/9 to the
unflagged baseline 4/6+3/9, ×3 identical repeats (Arm C).** The paper-recipe
poison is removed while swapped-side true-mouth arcs stay flagged and one
recall loss is recovered. No roll-out by me (one-pot mandate kept). No
commits; tickets 39–58 untouched (read-only); original flaggers untouched
(p59A/B/C are laptop copies). All jobs sacct-verified COMPLETED 0:0.

**0. Design (honest sign, OUR points only — no ORIG point copied).**
World-z fails as a cue (fragments sit arbitrarily; a true mouth arc sits
*below* piece median). The working cue is radius under the finder axis:
the lip is the widest ring on these fragments. Login-node probes on the
pristine 39 F bundle (evidence: /tmp/p59_probe*.py outputs in run logs):
(a) R–t correlation |0.76–0.85| per piece, so R orders mouth-vs-foot;
(b) the lone genuine foot flag (03_0 s4, 43 mm from any ORIG arc) sits at
u-pct 2% / R 25.8 while every swapped-side true-mouth flag sits at u-pct
95–99% / R 47–50; (c) a second-chance roughness tier (sh,sr<2.0,
|dr|,|dh|<0.2, n≥15) admits exactly one arc — 02_1 s0 (n=37, just over the
strict line) — and zero foot/fracture arcs. Arms (one variable each):
A = p58 + R-gate (keep iff Rmean ≥ 0.9×Rmax same-axis; spares 03_0 s4 +
04_1 s0, a likely-fracture flat at R 37.7); B = p58 + second-chance tier
(recovers 02_1 s0 only); C = both. DATA sections byte-identical to the
pristine 39 F bundle in all 3 arms → gate carries over formally (same
invariance argument as 47/49).

**1. Tallies (binary-printed; identities recompute exact, CountResult port).**

| arm | jobs (sacct COMPLETED 0:0) | ORIG (validity) | fresh flagged |
|---|---|---|---|
| A (R-gate) | 33264457/58/59 (~4 min) | 6/6+9/9 (36/27) | 4/6+3/9 ×3 (100/19,100/19,100/18 pruned) |
| B (recall) | 33264460/61/62 (~3.5 min) | 6/6+9/9 (36/27) | 0/6+0/9 ×3 (recall alone can't beat foot poison) |
| C (both) | 33264463/64/65 (~3.5 min) | 6/6+9/9 (36/27) | 4/6+3/9 ×3 (100/19,100/18,100/19 pruned) |

ORIG forest 36/27 reproduces 39/58 exactly → vehicle cure-potA @ bffefb6
VALID for F; asserts green in all 9 runs
(LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK ×2 per run).
Fresh identities (C ×3 + A ×1, all identical, recomputed = binary):
seated [2,3,5,6], missing [1,4]; correct edges (2,3),(2,5),(3,6);
piece 1 UNPLACED (no T file) all runs; piece 4 placed-but-wrong
(edge 4-5 off by 327 mm). Remaining gap to full seating: piece 1's two
ORIG-rim sides are too rough fresh for even the 2nd tier (sh 2.5–3.1),
and piece 4 needs wall work beyond flagging (51-doctrine: no seating,
nothing to attribute — same as 58).

**2. Flag inventory (Arm C, the landing arm): 8 files flagged** (02_0,
02_1 via 2nd tier, 03_1, 04_0, 04_1 via s2, 05_0, 06_0, 06_1). Spared:
03_0 s4 (foot, R 25.8 < 0.9×Rmax) and 04_1 s0 (R 37.7; likely fracture —
side stays flagged via s2, so no recall lost). Still unflagged: 01 both
sides + 05_1 s3 (too rough; 05_1 s3 fails even the 2nd tier at sh 3.07).

**3. Controls / gates / scope notes (explicit).** F ORIG 6/6+9/9 green in
the same binary in all 9 runs. A arms were NOT re-run: the assembler is
byte-identical to 58's vehicle (head bffefb6 asserted per run; A-validity
8/8+15/15 banked in 49 on this exact vehicle; our change touches only F
breakline headers). Gate: 39's F gate 9/9 carries over formally —
DATA-identical bundles, verified per arm. Render (eye-checked)
artifacts/pota59/pota59_seating_F_C1.png: green seated fresh ring tracks
the gray GT ring; P4 red off-pot; P1 unplaced — coherent, no 58-style
scatter. A re-run with A arms is a 10-minute follow-up if the lead wants
the letter of the rule.

**4. Evidence.** Laptop artifacts/pota59/: 4 fetch tgz + extracted fetch_*
(GT, rims_fresh, T_orig/fresh, P58 tallies), orig_F_bl.tgz, flag reports
A/C, p59_render.py + seating PNG. Laptop .scratch/pota-repro/:
p59A/B/C_flagger.py (masters uploaded to Spartan), p59_render.py.
Spartan pota59_repro/ (flaggers, stage sbatch, flag reports, bun md5s) +
sfs_main/pota59_run_{A,B,C}_*/ (binary logs, snapshots, fetches).
First submission (jobs 33264285–93) failed in-container in ~6 s (my
${ARM} collided with the stage function's local; fixed by renaming to
${P59ARM}, resubmitted as 33264457–65). Poll was sacct directly throughout.

**5. Recommendation for lead.** Land Arm C as the F recipe (at-baseline
×3, controls green, identities named). It does NOT exceed the unflagged
baseline — piece 1 needs content-side wall work (recall tier exhausted at
sh/sr 2.0 with zero false admissions; pushing further re-admits feet) and
piece 4 is a seating problem, not a flagging problem. Successor: pilot G
second with Arm C as-is (G carries the same foot-flag exposure per 58);
if G lands at/above its unflagged baseline, roll to the rest.
