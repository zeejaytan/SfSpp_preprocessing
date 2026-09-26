# 08: Is the ordering defect Juglet-specific, or general?

**Answers:** E1

**Blocked by:** 01-establish-cpp-test-seam (needs the diagnosis to be
established before it can be tested elsewhere)

**Status:** ready-for-agent

**Needs-eye:** none — this is a measurement, not a geometry claim.

## Why this is a separate ticket

Ticket 01 established *what* breaks the edge-line ordering. It did not
establish *where*. The three failure classes in `../AGENTS.md` must not be
blurred, and right now the honest statement is narrower than the one the
Juglet invites:

> The walk truncates on a boundary cloud whose local point spacing varies
> by ~20×, or whose points scatter further off the rim than the local
> spacing.

Both are properties of the *input geometry*, not of the Juglet
specifically. That leaves two very different findings open:

- **the method is sound and the Juglet is awkward material** — rough,
  hand-made, densely and unevenly sampled edges; or
- **the method is broken for any sherd edge that is not near-uniformly
  sampled**, and Pot_A survives by luck of sampling, not by merit.

These lead to opposite decisions about how much to trust the method on the
rest of the corpus. Reporting the first as the second would be the exact
error this workspace has already paid for once.

## The prediction that can be broken

Pot_A is the control: it produces 15/15 correct joins. The mechanism
predicts Pot_A's boundary clouds are **near-uniformly sampled**, so the walk
covers their rims. That is a prediction, not an observation, and it is
falsifiable: if a Pot_A boundary cloud also shows large spacing variation
and still gets full coverage, the mechanism is wrong and the diagnosis in
ticket 01 needs revisiting before any fix is built on it.

## What to do

1. Run the edge-line stage once on Pot_A, keeping the per-sherd
   `boundary.pcd` intermediates. `Temp_edge/` is overwritten per sherd, so
   a normal run leaves only the last one — snapshot each as it is written.
2. For each Pot_A boundary cloud, measure the same quantities ticket 01
   measured on the Juglet: nearest-neighbour spacing min/median/max, the
   max/min ratio, the fraction of points with ≥K neighbours inside
   K × median spacing, and the walk's coverage.
3. Report both arms side by side with the same units and the same
   definitions. Nine Juglet sherds against however many Pot_A has; state
   the counts.

## Acceptance criteria

- [ ] At least one Pot_A boundary cloud is measured, with the spacing
      statistics and the walk coverage reported
- [ ] The comparison states explicitly whether Pot_A's spacing variation is
      materially smaller than the Juglet's
- [ ] The finding is recorded as one of: *the defect is Juglet-specific
      material*, *the defect is general and Pot_A survives by sampling luck*,
      or *the mechanism is wrong* — with the measurement that decides it
- [ ] If the mechanism is wrong, ticket 03 is blocked and ticket 01 is
      reopened. Do not build a fix on a refuted diagnosis.

## Note

One Pot_A sherd is a lead, not a conclusion. Pot_A is a single pot; if the
spacing statistics are uniform across its sherds that is consistent with
the mechanism but does not establish it for the corpus. Say which of the
two it is.
