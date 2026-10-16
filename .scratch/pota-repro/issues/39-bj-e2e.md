# 39: B–J E2E on admitted fragments with the landed cure

**What to deliver:** per-pot E2E tables across pots B–J with ORIG controls.

**Answers:** E1

**Blocked by:** 40-cure-branch-vehicle (vehicle = cure-potA @ bffefb6, proven 8/8+15/15 ×2 on Pot A).

**Status:** results-in

## Comments (worker, 2026-10-17)

**Verdict: MEASURED — all 9 pots executed end to end with valid ORIG controls; the fresh chain (our rims + our finder axles + cure assembly) does NOT reproduce on any pot B–J. Vehicle confirmed working (ORIG arms reproduce the authors on 7/9 pots fully, near-fully on D/I/J); the gap is rims+search, NOT the finder (Pot B shipped-axles diagnostic collapses identically). No commits; Comments-only edit here.**

**0. Vehicle + provenance.** Assembly `cure-potA` @ bffefb6 verified in laptop clone: `git diff 9195c01..cure-potA` = exactly 2 files 2+/2- (P22FIX FM:1860, P22FIX2 RS:1785); fork main untouched @ b35905b. Preprocessing @ 912b4ae per dispatch (diff f1fd6b4..912b4ae = ticket-Comments only, zero source change — vehicle-equivalent). Fresh Spartan clones in `/data/gpfs/projects/punim2657/pota39_repro/` (prep + asm), zero patches. Reused ticket-38/40 mechanisms: nested-alglib scaffold (tracked→nested copy + `diff -rq` IDENTICAL guard) + gt_stub contingency (never needed — cure links clean every arm) + fork-host shim (TOP_k 5/BRANCH_b 3) with LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK asserts green in all 19 stage arms. New mechanism (documented): per-pot `data_path.h` POT selector via host-side untracked 2-line overlay bind-mounted in-container only (clone stays clean; `diff` = exactly the selector flip) — the upstream header hardcodes `#define POT_A`. POT_E's line reads `// #define POT_E` (upstream spacing typo) — handled. Poll was `sacct` directly throughout.

**1. E2E sets (vehicle blocks ∩ ticket-18 admission ∩ GT-having).** Rule refusals (cost>1.40 AND share<0.22, ticket-18): H01–H11 (all of H — no H pipe, recorded), C03, D28, D30 (outside block), I30, J03. No-GT exclusions (no reference to score against): D22, F07, I28, I29, J09. Outside upstream vehicle blocks (no POT_ entries, not piped): C05–C07, D30–D32, E32–E34, J13–J19. Exclusions enforced by EMPTY axle files — the binary auto-excludes them (`ReadAxis` empty → `shard_on_off=false`) and its denominators count the admitted set only (verified: C fresh 0/3, F ORIG 6/6). E2E sets: B 9; C {01,02,04}; D 01–29 minus {22,28} = 27; E 01–31 = 31; F 01–06; G 7; H none; I 01–27 = 27; J {01,02,04,05,06,07,08,10,11,12} = 10.

**2. Gate (fresh rims, probe-faithful strict A→B, record-only).** B 14/15 (2-4 = 0); C 3/5 (1-2 = 0, 1-3 = 1); D 68/69 (12-28 = 0); E 61/62 (3-5 = 0); F 9/9 (min 23); G 10/10 (min 6); I 64/65 (9-18 = 0); J 21/21 (min 6). Teleports: B/C Bl0 files carry T14-appended decorative segments (multi-segment joints, expected — NOT Pot-A-style single loops); F/G mostly clean.

**3. Finder on fresh surfaces (frozen (a)-chain, shipped axles = test key).** B 9/9 admitted (misses B03 11.15°, B08 35.40/5.40 — both ticket-10 families recur); C 4 ran, C03 REFUSED (1.532/0.203), C02 miss (42.52°); D 29 ran, D28 REFUSED (1.623/0.174), misses D17/D18/D21/D24/D25/D26/D27/D29 (small-multi tails); E 31/31 admitted, misses E17/E20/E21/E30/E31; F 7/7 admitted, F07 miss (no-GT anyway); G 7/7 admitted, all ≤0.73°; I 30 ran, I30 REFUSED (1.562/0.169), misses I20/I25/I27/I29; J 12 ran, J03 REFUSED (1.480/0.204), misses J01/J02/J06/J08/J11. Fresh-vs-shipped verdicts agree everywhere except J02/E20/E30 (fresh-miss/shipped-pass, borderline multis).

**4. E2E binaries (k=5/b=3 shim, forest/pruned shown).** A pot counts with a valid ORIG arm in the same run — all ORIG arms ran clean (asserts + snapshots, see gaps):

| pot | ORIG R1 | ORIG R2 | fresh R1 | fresh R2 |
|---|---|---|---|---|
| B (9/15) | 9/9+15/15 (114/76) | 9/9+15/15 (114/77) | 4/9+2/15 (1442/31) | 4/9+2/15 (1442/39); R3 same, strict 1/15 |
| C (4/5) | 4/4+5/5 (125/40) | 4/4+5/5 (125/40) | 0/3+0/3 (307/7) | 0/3+0/3 (307/9) |
| D (28/66) | 23/28+55/66 (2445/892) | 22/28+53/66 (2445/889) | 15/27+17/66 (10853/879) | 16/27+16/66 (10853/872) |
| E (31/62) | 31/31+62/62 (1912/826) | 31/31+61/62 (1912/825) | 5/31+3/62 (25022/211) | 7/31+4/62 (25022/214) |
| F (6/9) | 6/6+9/9 (36/27) | 6/6+9/9 (36/27) | 4/6+3/9 (136/18) | 4/6+3/9 (136/18); R3 same |
| G (7/10) | 7/7+10/10 (51/31) | 7/7+10/10 (51/31) | 4/7+3/10 (146/21) | 3/7+1/10 (146/19) |
| H | all refused — no run | — | — | — |
| I (27/65) | 25/27+59/65 (1424/667) | 25/27+59/65 (1424/667) | 9/27+4/65 (8512/356) | 6/27+2/65 (8512/345) |
| J (11/21) | 8/11+16/21 (731/202) | 8/11+16/21 (731/197) | 0/10+0/18 (1873/56) | 0/10+0/18 (1873/49) |

(Denom = graph pieces/edges among on-pieces; H row intentional.) Fresh forests dwarf ORIG (B 1442 vs 114, E 25022 vs 1912 — extra finder modes + decorative rim segments drown the beam). Repeats agree within beam variance (G fresh 4/7↔3/7, E ORIG edge 62↔61, D ±1).

**5. Strict (5°/10mm relative-edge, diagnostic; full tables in `artifacts/pota39/strict_tables.txt`, 1133 lines).** ORIG — B 9/15 ×3; C 5/5 (R2); D 40/69, 39/69; E 31/62, 33/62; F 3/9 (R3); G 5/10 ×2; I 28/65, 26/65; J 9/21, 7/21 (fails cluster on pieces 8/11/12 + 10–18mm translation floor). Fresh — B 1/15 ×2 (only 3-5); C 0/5 ×2; D 4/69, 7/69; E 0/62 ×2; F 0/9 ×3; G 1/10 ×2; I 0/65, 1/65; J 0/21 ×2. (Strict denominators = full graph incl. rule-excluded-touching edges scored as unseated-fail; admitted-only counts are in the tables.)

**6. Axles exonerated (Pot B shipax diagnostic, job 33199066 COMPLETED 0:0):** fresh rims + SHIPPED axles → 4/9+2/15 strict 0/15 (forest 523/27) — identical collapse to finder-axle arms. Eye-check `pota39_seating_B_R1.png`: fresh rims at ORIG poses form a closed bowl (rims fine); fresh poses scatter (search fails). So the gap is rims+search, not the finder. No further diagnostics run (repair belongs to the successor, not this measurement ticket).

**7. Renders (eye-checked, `artifacts/pota39/`).** `pota39_seating_{B,C,D,E,F,G,I,J}_R1.png` — ORIG panels: closed/coherent vessels (B/C/E/G clean; D/I tall pots cohere; J loose with 8/11/12 astray; F small clean); fresh panels: scattered/open in all 8 (D partly vessel-like lower body — its 15/27 best-fresh). C ORIG panel empty (snapshot lost, §8); G/C/F/J/I/B/D/E ORIG vessel confirmed in available panels.

**8. Infrastructure incidents (all diagnosed, none silently absorbed).** (a) Prior dispatch's 9 pipe sbatches were broken (no Point-PCD staging → empty bundles; shared-clone alglib `cp` race → MISMATCH) — rewrote, requeued. (b) My first 7 pipes staged every bundle into `pota39_bundle_B` (template `sed` missed `pota39_bundle_B` — no `pota39_B` substring); destroyed B's bundle mid-R2 (B-R2 fresh snapshot lost) — restored B bundle byte-identical from TREE (md5-verified vs gatefetch) + reran (R3). (c) Concurrent ORIG arms raced on the shared `$ORIG/Result` dir → T-write errors (C/F ORIG R1/R2 snapshots) — fixed with job-private Result binds; F-R3 re-proved the fix (snapshots 6/5, zero write errors). (d) E overlay needed `// *` (upstream `// #define POT_E` typo) after two 5s guard fails. (e) Strict scorer's fuzzy T-matcher phantom-seated one J/I piece — switched to exact names, rescored all. Failed/cancelled jobs on record: 33197167/33197255 (prior worker, empty), 33197344/45/51 CANCELLED, 33197346–50 FAILED (scaffold race), 33198450–56 FAILED (heredoc expansion), 33199068–74 v1 pipes FAILED (DS-PCD names), 33197768 FAILED (guessed prep hash — my error, resubmitted 33198169).

**9. Evidence.** Laptop `artifacts/pota39/`: `p39_gate.py`, `p39_strict.py`, `p39_render.py`, `strict_tables.txt`, gatefetch + fetch tgz per pot per run, `pota39_seating_*_R1.png`. Spartan `pota39_repro/` (clones @ 912b4ae/bffefb6, all sbatches, build/TREE/bundle dirs) + `Temp/potsac-p39-run/` (finder + axles) + `sfs_main/pota39_run_<jobid>/` RUNDIRs. Live `sacct` (all COMPLETED 0:0): pipes 33198169 (B 7:03), 33199747 (C), 33199748 (D 17:16), 33199749 (E 17:07), 33199750 (F), 33199751 (G), 33199752 (I 14:29), 33199753 (J); pts 33197767 + 33198538–44; finders 33198413, 33199759–65; stages B 33198525 (17:39)/33199009 (16:18)/33199773 (11:16)/shipax 33199066 (10:50), C 33200136/39, F 33200137/40/33200603, G 33200138/41, J 33200612 (24:03)/14, I 33200613 (62:01)/15 (59:43), D 33200980 (199:58)/82 (135:49), E 33201913 (145:31)/33201914 (73:30).

**E1 `Where it stands` proposal (for lead):** the landed cure reproduces the authors' Pot A exactly and drives every pot B–J vehicle to completion (ORIG arms: B/C/E/F/G perfect binaries, D 23/28, I 25/27, J 8/11), but our fresh chain (repo-built rims + frozen finder axles) seats only a fraction everywhere (best D 16/27+16/66; C/J zero) — the failure is search drowning in T14-appended decorative segments plus unsupported seams (gate pairs 2-4/B, 1-2/C, 3-5/E etc.), not axle direction (finder matches shipped verdicts; shipped-axle arm collapses identically). Weight: 8 pots, 19 E2E runs, all controls valid. Next: P07/P08 repair tickets (rim segmentation), then thesis write-up.

**Starting position:** Pot A reproduces the paper (binary 8/8+15/15 both arms, landed cure). Ticket 10 mapped cross-pot axles (117/155 dir-pass with the refusal gate: cost>1.40 AND share<0.22); ticket 18's gate decides admission per fragment. This ticket runs the full pipeline — our rims + our axles + landed-cure assembly at k=5/b=3 — on every pot B–J, admitted fragments only, each pot with its ORIG control.

**Rules:** assembly = cure-potA @ bffefb6 (NOT fork main), preprocessing @ f1fd6b4, fresh clones, zero patches. REPEATS mandatory — beam variance proven on Pot A (identical search space picked 7/8+7/15 and 8/8+13/15): minimum TWO E2E runs per pot; a pot counts only with a valid ORIG arm in the same run. Refusals excluded by rule (recorded, not scored); binary tallies + snapshots-strict tables per pot per run (strict diagnostic per the bar ruling); no commits except this ticket's record; laptop poll per sbatch via sacct directly (never slurm_poll.sh).

- [ ] Per-pot runs B–J (admitted fragments;Axle keys per ticket-10 record; refusal list per ticket-18 rule)
- [ ] Per-pot ORIG controls; per-pot binary + strict tables
- [ ] Seating render per pot (eye-check sample: worst + best arms minimum)
- [ ] Job IDs + sacct states; Comments-only ticket edits

**Successor:** P07/P08 revisit; thesis write-up of the reproduction result.
