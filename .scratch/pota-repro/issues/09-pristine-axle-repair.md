# 09: Pristine axle repair (smallest fix that finds the shipped axles)

**What to build:** the smallest change to the author's chain that makes it find the shipped Pot A axles — one repair variable at a time against the frozen 08 baseline, in the pristine tree (fork patch ported only by hand-read lines, never by copying fork files).

**Answers:** E1

**Blocked by:** 08-pristine-axle-repro.

**Status:** ready-for-agent (runs when 08 reports)

**Pristine-only rule (binding):** work in a pristine-tree copy. Fork files stay unread; a repair idea that needs a fork line re-derive it from the paper + pristine code or drop it.

- [ ] Repairs tried one at a time, each with before/after per-piece direction + position errors vs shipped axles (same metric as 08)
- [ ] Stop rule: first repair set reaching ≤5° and ≤2mm on 8/8 wins; report it exactly (file:line diff). No second variable while the first is unmeasured
- [ ] Kill branch: if three single-variable repairs move nothing, stop and report the numbers — the path is then declared unfixable-by-repair and the finding routes to a redesign ticket (lead's call, not the worker's)
- [ ] Comments section: repair table (change → median/worst before → after) + winning diff or kill verdict
