# Spec — paper-compliance closeout (preprocessing side)

**Answers:** E1

**Status:** spec for slicing; nothing implemented yet

## Problem statement

Ticket 16 audited our preprocessing against SfS++ §IV-B1 and found the
pipeline follows the paper's *shape* while differing in *content* at seven
points. Separately, tickets 04 and 14 fixed two of them (classification,
fracture rims) because each moved the gate 7/15 → 11/15 → 15/15 on Pot_A.
The rest were left open with "paper-compliance, not gate remedy" as a
placeholder no one defined.

This spec defines it: **under what conditions a remaining gap gets filled.**
The chain's standing rule — from the GLOMAP episode through ticket 10's
proxy error — is that work is justified by a measured number or an explicit
decision, never by "the paper says so" alone. That rule applies here too,
and it cuts both ways: a gap with no measured effect can still be worth
closing if leaving it open risks a silent failure, but then the ticket must
say which failure and how the fix would be detected.

## Scope decisions (binding on all tickets below)

1. **No duplication.** Tickets 03 (ordering vote), 05 (noise filter), and 06
   (resampling) already exist in `juglet-breaklines/` and stay where they
   are. Tickets here REFERENCE them; they do not re-specify them.
2. **Two acceptance lanes, declared per ticket up front:**
   - *Gate lane:* the change must move a scored number (Pot_A per-pair from
     15/15, Juglet honest 0/10) or recover a named failing pair. Judged on
     the probe, never on a proxy (ticket 10's rule).
   - *Compliance lane:* the change makes the code match the paper with no
     expected gate movement. Requires a no-regression proof (Pot_A 15/15
     held per pair, Juglet unchanged-or-better) AND a stated reason the
     compliance matters (e.g. removes a silent-failure mode, unblocks a
     future ticket). "Matches the paper" alone closes nothing.
3. **Research spike first, in every ticket** (workspace rule: read the guide
   at the pinned version, search how experienced people use it for this
   task, form an opinion before acting). Each ticket's first acceptance box
   is the spike write-up, and work stops if the spike says the gap is
   harmless.
4. **The authors' arm rides along** in every comparison (ticket 11's rule).
   A ticket that cannot name what its change is compared against is not
   ready.

## The gaps and their lanes

| # | gap (ticket 16 ref) | lane | ticket |
|---|---|---|---|
| Surface_F never produced; reconstruction reads it empty (§B) | gate if fracture rims matter beyond piece 2, else compliance (silent-failure removal) | 01 here |
| Rim criterion differs (paper height/radius vs ours plane-fit+axis) (§5) | research first; lane decided by the spike | 02 here |
| Merging single-pass, no convergence loop (§7) | research first; lane decided by the spike | 03 here |
| Region params 4.5/1.5/15–40 vs 4/1.0/10 (§6) | compliance-accept (ticket 12 measured the default optimal) | 04 here |
| Ordering vote (ticket 03), dead filter (05), resample (06) | existing tickets; referenced, not re-specified | — |

## Out of scope

- Assembly-side gaps (descriptors smoothing, NO_BASE_INFO, axis
  precedence): separate feature in `structure-from-sherds-pp`, same
  template. Neither repo specifies the other's work.
- Juglet re-extraction with the new pipeline: ticket 07's territory once
  these land.
- The MATLAB PotSAC-vs-paper comparison: flagged in ticket 16, needs a
  reader of MATLAB + the paper's §IV-B2, not listed here for lack of an
  owner. Say so rather than silently dropping it.

## Done when

- Every row above is resolved (fixed with gate movement, accepted with
  justification, or refuted with measurement) and ticket 16's acceptance
  boxes check in full.
