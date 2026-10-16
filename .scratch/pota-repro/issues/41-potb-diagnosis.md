# 41: Pot B diagnosis — where do fresh true joins die?

**What to deliver:** the kill site, with numbers — not a fix.

**Answers:** E1

**Blocked by:** nothing (runs alongside ticket 39; read-only vs 39's lanes).

**Status:** ready-for-agent

**Starting position:** Pot B R1 (fetch_B_R1, 2026-10-17): ORIG 114/76 → 9/9+15/15 (vehicle valid on B); fresh 1442/31 → 4/9+2/15. Fresh generates 12× the graphs and keeps a third of ORIG's count — true joins die in filtering. Pot C repeats the shape (fresh 307/7 → 0/3; ORIG 125/40 → 4/4+5/5).

**Steps (diagnose ONLY — no source edits, no commits except this ticket's record):**
1. Gate our B rims: teleport scan per breakline (ticket-26 method), min-pair check (ticket-06 gate). Are B rims clean like A's?
2. Axle errors per admitted B fragment (finder axle vs shipped, ticket-10 record): any >5°/failures among admitted?
3. Kill-site instrumentation (ticket-25/26 pattern): which stage kills GT-true B edges — RP overlap, CheckGraph@150, SingleOverlapTest@100, profile veto? Counts per site, fresh vs ORIG.
4. Verdict in the three-category frame: genuinely-failed method / broken measurement (ours) / wrong reference — with the number that decides.

**Acceptance:** kill site named with per-site fresh-vs-ORIG counts; gate + axle tables; verdict category + deciding number; job IDs + sacct states.

**Successor:** fix ticket per verdict (not cut here).
