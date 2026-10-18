# HANDOFF — pota-repro lane, 2026-10-18 (for a fresh session)

Goal: MATCH AUTHOR'S INPUT — our preprocessing must reproduce the author's perfect-score input (Pot A: gate 15/15 + E2E 8/8+15/15 at k=5/b=3, Table V). Tracked in spec.md + intent/E1-do-our-breaklines-let-sfs-find-joins.md. Read those two files first.

Standing user rule (2026-10-18): ONE ticket at a time — every ticket stops and asks for the user's call before the next is cut. The goal line GOAL: MATCH AUTHOR'S INPUT heads every ticket brief. No auto-chaining tickets.

## Settled (thesis lines, all committed + pushed to origin main)

- Swap is the dominant cross-pot cause (~94/129 rims): our Surface_0/Bl_0 carry the author's Surface_1/Bl_1. Size-desc sort puts the denser exterior wall first; the T04 interior-first guard never ran in the t39 pipe. Cure = slot exchange. Pot F fully seated 6/6+9/9 x3 (ticket 81, jobs 33343950/52/53 + 33344601/615/617).
- Guard recipe (forward-cone + split-then-select + inner-loop select) cures face-hop at source: C01 SEL 16pts/1.18mm/100%/0 jumps (ticket 75).
- C-pair 17.37mm slide = content-shifted overlap valley (search climbs to 45.2% overlap vs 24.3% at GT). Search-side remedies EXHAUSTED over 21+12 runs: SingleOverlap/gates, refinement ablation (76), 4 reweightings (77) — seat never moves. Remaining: rim-shape correction (79 NULL — re-walk reproduces same loop) or new scoring idea.
- 50-pt binary loader gate trips short rims (F06 needed 45->55 densify, ticket 81).
- E_G crash = malformed xyz-only PCD headers from sel78E scripts (reader loads nothing -> segfault at ranking_system.cpp:1113), NOT rim size. v1 restore runs clean but starves beam (0/6); v2 merge seats 0-2/24 (ticket 82).
- Refusal gate: cost>1.40 AND share<0.22 (ticket 18). Strict-vs-GT retired as run gate; binary + snapshots-strict rule (ticket 36/bar ruling).
- 44-asterisk rule: ORIG points never enter fixes; ORIG = ruler only. Visual-evidence lane rule: fresh-vs-author on mesh in visual-qa, Needs-eye lines.

## Open threads (resume in this order)

1. **Roll the swap cure** to remaining swapped pots per ticket-80 census (D 26/29, E 29/31, G 6/7, I 28/30, J 9/12, B 8/9, C 2/4). Recipe: ticket 81 (slot-exchange + 50-pt densify check). Next ticket number: 83.
2. **Pot E merge path**: v2 merge-cure runs clean, 0-2/24. Decide: accept partial + move on, or improve merge (jump handling reintroduces doubling — render honestly shows it).
3. **C-pair slide**: rim-shape (79 null) vs new scoring criterion — user chose rim-shape; still open. Valley numbers in tickets 74/76/77.
4. **Guard roll-out** (78): two-loop check fires B/D/E/F/G/I/J; blocked pieces unblocked by 82's format fix — re-run E_G with cured bundle.

## Vehicle (do not change without cause)

- Assembly: cure-potA @ bffefb6, k=5/b=3, LINK-SHIM-OK + DRIVER-SHIM-OK asserts per job. Prep bundles: /data/gpfs/projects/punim2657/pota{39,78,79,81,82}_repro/. ORIG ruler: sfs_main/original_samples/SfS_pp/. Fresh bundles: pota39_repro/prep/pota39_bundle_{B,C,D,E,F,G,I,J}/.
- Discipline: one-shot subagent per ticket, sacct-direct polling (never scripts/slurm_poll.sh), repeats >=3, no gate relaxation without a mechanism, COMMIT NOTHING from workers (lead lands: 1 ticket = 1 commit).
- Standing user prefs: visual-qa pairs for eye judgments (not flat pictures); ask_user_question tool times out — use plain numbered questions in reply.
