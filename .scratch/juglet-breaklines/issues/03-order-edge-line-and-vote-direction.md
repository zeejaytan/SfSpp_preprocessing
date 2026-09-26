# 03: Order the edge line along the rim, and vote for the direction

**What to build:** the edge line comes out as a single closed loop that
follows the rim, traversed in a consistent direction, instead of being
assembled by a non-local nearest-neighbour walk.

The paper (§IV-B1) states the edge-line points are "reordered
counter-clockwise using their normals and a voting algorithm". That step
is **not implemented in the released code** at all. The paper names the
voting but does not describe it, and a sweep of all 22 papers in
`papers/text/` found the word "voting" exactly once — in that sentence —
with no paper describing an edge-point ordering method. What follows is
therefore a **reconstruction, not the authors' algorithm**, and is
labelled as such in code and in the ticket.

- *Sequencing*: walk the rim, taking at each step the unused point that
  best continues the local tangent, subject to a maximum step. This
  replaces "first unused point among the 50 nearest", which is non-local
  and truncates on **roughly half the sherd faces of both pots** (8/18
  Juglet faces fully covered, 7/16 Pot_A faces — Pot_A being the control
  that assembles 15/15 correctly). See `08-is-the-defect-juglet-specific.md`.

## BLOCKED as the Juglet's fix — 2026-09-26

This ticket was going to be justified as *"the walk is why the Juglet
proposes no joins."* **Ticket 08 refuted that.** Pot_A suffers the same
truncation and still assembles perfectly, so the truncation does not
discriminate between the pot that works and the pot that doesn't, and
cannot be its cause.

**Keep the ticket; change the claim.** The work is still worth doing — the
walk discards 15–75% of an edge on half of all faces, which is a real
quality defect in its own right, and the paper's ordering step genuinely is
missing from the code. But it must be:

- described as **an independent defect, not the Juglet's cause**;
- judged by whether it improves the coverage *distribution* across all 18
  Juglet and 16 Pot_A faces — not by whether the Juglet's gate score moves,
  since there is no reason it should;
- **not credited in advance with fixing the Juglet.**

Before starting, read the face-selection hypothesis in ticket 08: the
leading candidate for the Juglet's zero joins is that `Surface_0` is the
largest cluster with no interior/exterior test, so 10 of 18 true mates are
inner-vs-outer. That is a face-*selection* problem, in ticket 04's
territory, and is the more likely explanation. This ticket should not be
sequenced as though it were the Juglet's remedy.

## A number in this ticket that does not belong to it

An earlier version carried *"traced length 0.27–2.15× the rim; internal
jumps of 10–24 mm against a 0.3 mm median step"* as evidence of the walk's
failure. **Those were measured on the emitted breakline files**, after
B-spline resampling and 200-point padding — a later stage. They say nothing
about the walk. The walk's own failure is truncation, measured as coverage
(ticket 01). Removed rather than left in place to mislead.
- *Voting*: ordering a closed curve has a one-bit ambiguity — which of
  the two senses of travel is "counter-clockwise". Each point votes on
  the sign of its fracture normal, defined by the paper as the cross
  product of the point's surface normal with its local tangent; the
  aggregate decides.

**Answers:** E1

**Blocked by:** 02 (dedupe first — sequencing on a duplicate-laden cloud
cannot be judged)

**Status:** ready-for-agent

**Needs-eye:** none yet; the witnessed render is in 07.

- [ ] A clean synthetic circle is ordered as one closed loop visiting
      each point once
- [ ] A circle carrying near-duplicates and a gross outlier still yields
      one loop; the outlier is not swallowed into the traversal
- [ ] The traversal direction is the one the vote selects, and reversing
      the input normals reverses it — both asserted
- [ ] No internal step in the result exceeds the maximum step by more
      than a stated factor
- [ ] The reconstruction is marked as such in a code comment, so nobody
      later mistakes it for the authors' algorithm
- [ ] Acceptance probe run before and after, both numbers recorded

## Note

The paper reports the axis-direction sign ambiguity is handled at
*matching* time, by inverting one descriptor and matching twice. This
ticket is not required to solve it, and must not try to.
