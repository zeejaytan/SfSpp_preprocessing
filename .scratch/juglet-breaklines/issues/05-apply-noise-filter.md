# 05: Apply the noise filter the method specifies

**What to build:** the edge-line noise filter is actually applied, rather
than computed, written to disk, printed, and then thrown away.

The paper (§IV-B1) specifies: "Using a K-D tree-based search, points near
the edge line are identified and filtered to remove noise and outliers."
The code does all of that — and then reloads the **unfiltered** boundary
cloud over the filtered one before sequencing, so the filter's output is
never used. On the Juglet it made no difference anyway (it kept 59 of 59
points), which is why this sat unnoticed; on a noisy scan it would
silently do nothing.

**Answers:** E1

**Blocked by:** 04 (filter the edge line once it is known which surface
it belongs to)

**Status:** ready-for-agent

**Needs-eye:** none.

- [ ] The filter runs after the improved surface/edge-line selection and
      its result is the cloud that gets ordered — verified by a test that
      fails if the unfiltered cloud is ever reloaded
- [ ] The reload of the unfiltered boundary is gone, and a comment
      records that it was there and why it was wrong
- [ ] The filter radius and neighbour count are derived from the cloud's
      own spacing rather than fixed in millimetres, so the stage behaves
      the same on a 65 mm juglet and a 300 mm pot
- [ ] The number of points removed is logged; a filter that removes
      nothing and a filter that removes almost everything are both
      visible in the log
- [ ] A synthetic boundary with a gross outlier loses that outlier, shown
      by a test

## Note

Small ticket, and easy to judge wrongly: if the acceptance number does
not move, that is expected and is not evidence the change was pointless.
Its value is that the code now does what the method says, and that the
behaviour is covered by a test.
