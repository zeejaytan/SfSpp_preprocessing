
## Lead verdict (2026-10-24)

**DO NOT ROLL OUT — accepted, and the pre-registered rule was honoured exactly (2/10, 0/4 controls).** No retuning, no cherry-picking a family. The 214-lane table stays the only rollout evidence, and it describes theta=4 + greedy, not the shipped code.

**Stop the line on Pot_C_01.** The shipped defaults segfault the edge stage on a real piece, reproducibly, on the source tree's own sheets and on three independent sheet draws. A default that crashes on a piece in the benchmark cannot ship, whatever its scores are. This outranks every score in this ticket.

**The stop rule is the prime suspect for the four collapses, not yet convicted.** Its own log names the mechanism: `[STOP-267] CHAIN-END step=88 of 1000 ... left=911 dots unvisited` -> `resampled=14 (L=25.7448mm)`. A rule built to refuse one 124 mm final-closure jump is refusing a mid-rim step where the local dot spacing happens to exceed 12 mm. It was tuned on six lanes from three pots (P03/P22/P01) whose worst guard step was 4.69 mm; Pot C and Pot J were never in that set. That is a sampling error in the rule's evidence base, and it is mine — the margin was measured on lanes that could not have shown the failure.

**It may not need fixing at all.** The rule was written for the P03-Bl1 bag that carried a 76-dot satellite at 47 mm. Ticket 271's theta=3.4 removed that lip from the surface; the bag the rule was built for may no longer exist. If theta=3.4 + full walk + stop OFF still puts P03-Bl1 at bar, the rule is a cure for a symptom that no longer occurs, and retiring it is better than guarding it.

**Mesh non-reproducibility is confirmed and now blocks gates.** Same piece, same env, same input cloud: Pot_H_01 and Pot_C_01 give different sheets run to run; Pot_J_01 reproduces bit-for-bit. So `mesh_processing_headless.cpp:1526-1527` (unseeded `std::random_device`) makes a fixed-tolerance gate partly a measurement of draw noise. Every lane in the next ticket reuses ONE frozen sheet pair per piece, and the md5 goes in the row.

**Corrections accepted and recorded:** (a) shipped default is vote-order ON at `edgeline_extraction_headless.cpp:1320`; the OFF line came from `a8e1f715` on the 248 worktree, where the arm was still opt-in. (b) Job 33731308 is not strip evidence — its mesh lanes ran `maxIterations=30` instead of `SFS_SINGLE_SHOT=1`'s 1 (P01 Surface_0 120,907 vs 16,650 points). On the 271 sheets the new binary reproduces the accepted 271 table exactly, so the strip itself remains behaviour-neutral.

**Family read-out, kept as written:** Pot H half cured (P01 100.0, P03 91.8); P02/P10 stall at ~73 % = extent, needs its own mechanism. C C03 moved 12.21 -> 2.01 mm but cov 48.4 %. Tails not fixed anywhere. Nothing here supports a rollout.

**Next: ticket 273** — crash trace first, then the stop rule's attribution and the retire-or-guard decision, all on frozen sheets. Overlay PNGs remain owed (Needs-eye stays open).
