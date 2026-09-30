# 01: Emit the fractured surface the assembler reads

**Answers:** E1

**Blocked by:** nothing — measurement and small mesh-stage change

**Status:** resolved 2026-09-30 — removal implemented, rebuild clean.
Zero `Surface_F` files exist in either dataset, so the loads were dead;
`IcpFine` (zero callers) now refuses empty frac loudly.

**Needs-eye:** none — this ticket no longer emits any file. (The old
Needs-eye for a `Surface_F` look is withdrawn with the emission lane.)

## Spike outcome: dead expectation, not missing data

- Sole consumer chain (`MakeCorWithSur :701/:749` → `COR_frac` → 
  `P2PConstraint :2109`) is reachable only via `IcpFine`
  (`reconstruction.cpp:2039`), which has **zero call sites** repo-wide.
  The live binary runs `FeatureComp → PairwisePruning → StateManager` —
  none read `sur_frac_` (verified: zero reads in feature_matching,
  ranking_system, filter, axis_estimation, two_phase, optimizer).
- Every empty-cloud op on the dead path is inert (early-return load,
  zero-iteration loops, zero-residual constraint, non-firing emptiness
  check at `:2098-2099` — which is why the failure would be silent, not
  loud, if `IcpFine` ever runs).
- **Populating `Surface_F` files would change zero executed instructions
  in any built binary.** Emission is pure cost, no effect. Ticket premise
  corrected: live code in a dead function, not silent corruption.

## What to build (removal, assembly repo)

1. Delete the `surface_fr` path entries from the ACTIVE `data_path.h`
   blocks (keep legacy BB blocks untouched — different reader).
2. Make the two unconditional 3-arg `LoadSurface` calls
   (`main_headless_correct.cpp:187`, `main.cpp:95`) 2-arg, matching the
   guarded `main_headless.cpp:89-93` pattern — or guard them the same way.
   Keep the `sur_frac_.CalculateLineNormal` guard (`:191-192`) consistent
   with whatever remains.
3. If `IcpFine` stays: add a per-pair `cor.empty()` guard where `:2098`
   assumes non-empty, so re-enabling it without files fails LOUDLY. If it
   goes, its `sur_frac_` reads go with it. Either way, no silent path.
4. Hazards on record (do not re-introduce): one-sided population risks UB
   (`MakeCorWOBuildTree :412-418`); `ReadPCD :887-893` strips 12 header
   lines so headerless `.xyz` emission would drop 12 points; active blocks
   expect `.pcd` while legacy blocks name `.xyz`.

## RESOLVED 2026-09-30 (removal lane, assembly repo)

- `main_headless_correct.cpp:187` + `main.cpp:95`: 3-arg → 2-arg loads;
  `main.cpp` frac-normal call guarded. `main_headless.cpp` already fell
  back (its guard is now the only pattern).
- `IcpFine` per-pair empty-frac refusal (breaks loudly, never a silent
  solve without the fracture term).
- Path tables left alone (fixed-size initializers; inert strings once
  unread) — correction to the spec above, recorded not hidden.
- In-container rebuild exit 0 with the new strings in `Hierarchy-Clear`.
- Per-pair assembly rerun waived with reason (S1 entry): the loads were
  dead on current data (no files exist), so no executed instruction
  changes. The preprocessing probe (per-pair, both pots, authors' arm)
  covers everything that reaches the matcher.

## Acceptance criteria (updated 2026-09-30)

## Why this ticket exists

`data_path.h` points `surface_fr[i]` at `Surfaces/<piece>_Surface_F.pcd`.
Two of three assembler mains load it unconditionally; zero such files exist
in either dataset; `reconstruction.cpp:701/749` runs fractional-surface
correspondence on the resulting empty clouds. The paper segments three
surfaces — interior, exterior, fractured — and we emit two named walls
while the fracture zone sits in `unclustered.ply`, which no `Surface_F`
filename points at. Ticket 16 gap B.

This is not a new observation: it is the same fracture zone ticket 14's
patch rims are mined from, seen from the assembler's side. What is missing
is the file, not the data.

## Research spike (do first, stop if it says harmless)

1. Read `Geom::LoadSurface` 3-arg (`data_structure.cpp:501-511`), `ReadPCD`
   (`:868-929`), and every `sur_frac_` read (reconstruction `:701/749`,
   plus whatever else references it) and write down what an empty vs
   populated `sur_frac_` changes in matching behavior. If the answer is
   "nothing reads it to effect," this ticket becomes removal of dead
   expectations (the `surface_fr` paths and the unconditional loads), not
   emission — which is a smaller, safer change. Record which.
2. If it does matter: define `Surface_F` content precisely. Candidate:
   the unclustered points that pass near the breakline (the ticket-14
   fracture zone), with mesh normals as ticket 14 established. Alternative:
   whatever the paper's fractured surface means operationally — say which,
   with the paper section cited.

## What to build (only after the spike)

- Mesh stage writes `<piece>_Surface_F.pcd` (6-column xyz+normal, same
  conventions as `Surface_0/1.xyz`) for every sherd that has unclustered
  points near its breakline; skips with a logged reason where there are none.
- No change to `Surface_0/1` contents or names. Additive file only.

## Acceptance criteria

- [ ] Spike write-up: what empty `sur_frac_` changes downstream, with
      file:line cites — or the ticket converts to dead-expectation removal
- [ ] Lane declared: gate (which pairs should move, predicted before the
      run) or compliance (Pot_A 15/15 held per pair + which silent failure
      this removes)
- [ ] If gate lane: probe per pair from the current 15/15; any regression
      returns the ticket to open, not to "accepted with notes"
- [ ] If compliance lane: no-regression proof (Pot_A per-pair table
      unchanged, Juglet unchanged-or-better) plus the named failure mode
- [ ] Authors' arm in every comparison (ticket 11's rule)
- [ ] Witnessed look of one `Surface_F` cloud on its sherd before the
      assembler consumes it (Needs-eye above)
