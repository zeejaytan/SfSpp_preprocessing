# 39: B–J E2E on admitted fragments with the landed cure

**What to deliver:** per-pot E2E tables across pots B–J with ORIG controls.

**Answers:** E1

**Blocked by:** 38-land-cure-set (needs the landed, repo-built cure).

**Status:** ready-for-agent

**Starting position:** Pot A reproduces the paper (binary 8/8+15/15 both arms, landed cure). Ticket 10 mapped cross-pot axles (117/155 dir-pass with the refusal gate: cost>1.40 AND share<0.22); ticket 18's gate decides admission per fragment. This ticket runs the full pipeline — our rims + our axles + landed-cure assembly at k=5/b=3 — on every pot B–J, admitted fragments only, each pot with its ORIG control.

**Rules:** same-binary ORIG control per pot (a pot counts only with a valid ORIG arm); refusals excluded by rule (recorded, not scored); binary tallies + snapshots-strict tables per pot (strict diagnostic per the bar ruling); no commits except this ticket's record; reuse the ticket-38 repo-built binaries; laptop poll per sbatch via sacct directly.

- [ ] Per-pot runs B–J (admitted fragments;Axle keys per ticket-10 record; refusal list per ticket-18 rule)
- [ ] Per-pot ORIG controls; per-pot binary + strict tables
- [ ] Seating render per pot (eye-check sample: worst + best arms minimum)
- [ ] Job IDs + sacct states; Comments-only ticket edits

**Successor:** P07/P08 revisit; thesis write-up of the reproduction result.
