# 214 - Pot D preprocessing + per-sherd edgeline gate (NO assembly yet)

Status: ready-for-agent (PRECONDITION: starts only after 213 lands -- lead dispatches then)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User order (2026-10-20): run Pot D (29 pieces, biggest pot) on the 213-cured
pristine line, then STOP: score every generated edgeline against the
author's and send one overlay picture per sherd (our lanes vs author lanes
on OUR mesh). The user says go / no-go per sherd before ANY assembly is
ticketed. Pot D is the cure's proving ground (195: worst non-regression by
numbers, half the pot lost).

## Boundary
Starts after 213 lands, on whatever line 213 lands to (lead names the
branch + worktree + Spartan dir at dispatch). Fresh Spartan experiment copy
for D (never the live main checkout, never the 2 pre-E2E stashes, never
210/211/212/208 dirs). Scope ends at the gate table + pictures -- NO
assembly, NO seating, NO bundle swap. Touch NO tracked file except this
ticket. COMMIT NOTHING (lead commits).

## Constraints
Preprocessing: full pipe (mesh + edge, 208 pattern) with the 213-cured
binary, same-binary author-bundle control (self-match sanity). Scoring:
209 pattern per sherd -- slot matrix first (per-piece 209-pattern check per
standing ledger-B rule: slots may flip per piece, P01 precedent -- never
blanket-swap), then matched-lane med / %<2mm / max + point counts.
Pictures: one overlay per sherd, 209 lane-rule style (our mesh, matched
lanes drawn, counts in title); pictures suffice per standing decision.
Present big + foot/base pieces first in the gate table (interior-loop watch
from 211). Standing submit sign-off covers pipe + scoring jobs; held
allocation for iterative work, sbatch only for long unattended runs with
laptop-side poll.

## Acceptance
29/29 sherds scored + 29 overlay pictures + one gate table (per sherd:
slot verdict, both-lane numbers, picture path, lead-readable one-line
read). User verdict recorded here before any assembly ticket is written.

## Required evidence
Comments: pipe job IDs + sacct states, control result, gate table, picture
paths, any per-piece slot flips. Final report: same, self-contained, plus
the explicit go/no-go request. Do NOT flip to done -- the USER flips this
one with their verdict; lead records it.

## Lead R6 (2026-10-20) -- gate VERIFIED, awaiting USER verdict
Worker could not locate this ticket file (searched wrong tree); full write-back arrived via message and is recorded here. Numbers rechecked EXACT on laptop (P01 0.48/99.7 + 0.66/96.3; P16 0.80/76.2 + 1.45/51.8); all 3 jobs sacct-COMPLETED 0:0 (build 2:17, sample 0:43, pipe 14:56); source md5 verified (LF-normalised worktree file = 21fbb6b5 = exact 213-cure source; binary differs only by build-dir path); 29/29 overlays + 58+58 lane files + gate_table.csv on disk. Eye-checked P01 (both lanes coincide, one negligible stray squiggle) and P16 (both lanes deviate: orange cuts interior shortcut, red leaves blue on upper arc -- genuinely the worst sherd). Provenance note: no Pot_D Point PCDs exist anywhere; inputs synthesised by sampling ORIG meshes at legacy Pot_A density (36.24 pts/mm2, mesh-observable only) -- accepted, documented in ticket. Worker recommendation: GO on 23 clean, flag 6 mixed (P12/P15/P16/P22/P25/P27). Status stays ready-for-agent -- the USER closes this one with go/no-go.

## Comments (worker)
