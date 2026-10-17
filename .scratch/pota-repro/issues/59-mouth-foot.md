# 59: Mouth/foot disambiguation — teach the marker which edge is lip

**What to deliver:** a flagger that marks mouth arcs and spares foot arcs — then F re-piloted at/above the unflagged baseline.

**Answers:** E1

**Blocked by:** 58 (pilot-negative: F fresh 0/6+0/9 ×3 vs unflagged 4/6+3/9; 3 recall losses on E2E pieces + 5 fresh-only flags on ORIG-base/zero edges; LCS masking 136→67 + H_rim veto; B's clean set doesn't replicate) + 46 (ORIG top-sign already encodes rim-vs-base; paper §IV-B1 test ignores it).

**Status:** ready-for-agent

**Starting position:** two gaps: (a) DISAMBIGUATION — ORIG's top-sign column already says mouth vs foot; the paper recipe test ignores it, so foot arcs that pass the geometric test get flagged and poison via masking + veto. Use the sign (honestly computed on OUR outlines, never copied) to spare foot arcs. (b) RECALL — 3 true mouth arcs on E2E pieces too rough fresh to pass; chopped-fragment-tolerant recall (shorter arcs? roughness-tolerant thresholds?) without re-admitting feet. Bundle reference: Spartan pota58_repro/ + pota39 F bundle (read-only); flagger copies p58_flagger.py (copy, never edit p47/p49 originals). Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** land ONLY with F fresh at/above 4/6+3/9 unflagged baseline ×3 same-binary runs + identities + controls green (F ORIG 6/6+9/9, A 8/8+15/15) in same runs + gate green; renders (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [ ] Mouth/foot disambiguation arm(s), one variable each
- [ ] Recall arm(s) on chopped fragments
- [ ] F re-pilot ×3 + identities or measured why-not
- [ ] Job IDs + sacct states

**Successor:** roll-out to C–J per ticket 58 (pilot G second, then rest).
