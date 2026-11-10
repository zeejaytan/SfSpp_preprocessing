
## Comments (lead, 2026-11-10)

**Why the lead is writing here.** Both dispatched workers died before reporting: `ea7da6de-bca6-4a5d-8530-9b63d7adaa09` (glm-5.3, stopped ~15:00) and `e263b1ef-20fc-409f-9451-d643d578b11f` (qoder-global/dfmodel, failed 15:58 — provider quota). Neither wrote a closing message, so this ticket has no worker report. The conservator's instruction is to continue without redoing finished work, so the lead is finishing the remaining bars and records them here, labelled as lead measurements. Nothing already produced is re-run: the worktree, the identity run 34648716, the measure run 34647797 and the two workers' submit scaffolding are reused as they stand.
Scratch-writer check (AGENTS.md rule 12) run 16:47 with `--quiet-for-hours 1`: every remaining sign is one of the two dead workers' files (newest 15:53:53, `t325/tmpl/potJ.sbatch`); no live writer.

### Bar 5 pre-registration (written before submitting, as the ticket requires)

Claim type: *the method's output is usable*, purely geometric — no reference answer is involved, so this cannot be a reference-is-wrong result.

- **Arms, K = 3 lines per piece, FLOOR = 20, NP = 9, two repeats each:**
  - `O` — `Dataset/Axes/Juglet` (our own September output, the shipped baseline);
  - `K3` — this ticket's axes, `runs/20261110-1450_22151d0_t325-axes/out/axes325`, top 3 lines per piece;
  - `GT` — `Dataset/Juglet_GT/Juglet_Piece_N_Axis.xyz` used directly (the oracle control).
- **Success** = on **both** repeats, at least **1 of the 18 breakline joins seated** and at least **2 of the 9 pieces placed**. Partial success is reported per repeat, never averaged.
- **What each outcome will mean.** `K3` succeeds and `GT` succeeds: the axes are good enough to seat a 33 mm vessel. `K3` fails and `GT` fails: the blocker is downstream of the axis finder (breaklines or the assembler's scale), not this ticket's gates — reported as such, not patched around. `K3` fails while `GT` succeeds: the axis finder is the blocker, and the axis-error table says which pieces.
- **Baseline to beat, recorded before the run:** job 34623404 (`20261110-0740_d628fc0_t323-juglet`, axes323) scored **0/9 pieces and 0/18 edges on all four arms** — `score/acc.tsv`: F20O_r1 0/9 0/18, F20K3_r1 0/9 0/18, F20O_r2 0/9 0/18, F20K3_r2 0/9 0/18.
