# 08: Pristine axle failure repro (no fork in the loop)

**What to build:** the honest failure — run the author's axle chain as released on Pot A and score its axles against the shipped Pot A axle files. No fork code, no NURBS, no repaired anything.

**Answers:** E1

**Blocked by:** 07-pristine-potsac-map.

**Status:** ready-for-agent (runs when 07 reports)

**Pristine-only rule (binding):** same as 07. If the released chain cannot run as-is (missing loader, bad paths, crashes), that IS the result — record the exact error + file:line and stop that arm; do not borrow fork helpers to get it moving.

- [ ] Author-chain axles for all 8 Pot A pieces vs shipped axle files: direction error (deg) + radial position error (mm) per piece, median + worst
- [ ] Verdict with numbers: does the released chain reproduce the shipped axles (bar: ≤5° and ≤2mm on 8/8), and if not, which stage in the 07 map introduces the error
- [ ] Each claimed defect pinned to pristine file:line + observed behaviour (log/error/number), not inference
- [ ] Comments section: per-piece table + the single sentence "the author's path reproduces its shipped axles: yes/no" with the numbers attached
