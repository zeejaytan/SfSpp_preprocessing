# 01: Emit the fractured surface the assembler reads

**Answers:** E1

**Blocked by:** nothing — measurement and small mesh-stage change

**Status:** ready-for-agent

**Needs-eye:** required before closing. A new file appears in the handoff;
the conservator should see what it contains on one sherd before anything
downstream consumes it.

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
