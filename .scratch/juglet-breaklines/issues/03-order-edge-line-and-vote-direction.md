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
  and is the direct cause of the stalled and derailed walks measured on
  the Juglet (traced length 0.27-2.15x the rim it should cover; internal
  jumps of 10-24 mm against a 0.3 mm median step).
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
