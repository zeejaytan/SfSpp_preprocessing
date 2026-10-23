# Ticket 265: strand separation + mesh overlay (which two lines are these?)

**Answers:** E1

**Needs-eye:** conservator to confirm whether the two strands sit on opposite faces of the break (two lips) or on one folded face.

**Status:** results-in
**Working in:**

- [x] Split the P03-Bl1 bag into its TWO strands — **but not inside the 1045**: the G3 filter's 76 dropped dots ARE the second strand (see Comments)
- [x] Stage mesh + strand A + strand B (+ author lane) + export ONE PNG for the chat (visual-qa staging skipped per lead steer 2026-10-23)
- [x] Measure strand separation vs wall thickness; name which face each strand sits on
- [x] Verdict: ONE FOLDED SHEET (both strands on the exterior face), not two lips
- [x] Evidence in ticket Comments + Status results-in; no main commits

## Goal

Answer the lead question with a render: is the P03-Bl1 braid two lips of the break (inner-face edge + outer-face edge, ~one wall thickness apart) or one folded face? Prior art: 2026-10-17 face-hop finding (doubled loop ~5mm apart = walk hopping faces, wall thickness is the fingerprint); breakline slot semantics (slot 0 interior / slot 1 exterior); paper IV-B takes the edge line from the INTERIOR surface boundary only. If two lips: ordering = separate faces, trace the interior one (paper's design) — the out-and-back walk is wrong. If one fold: ordering = out-and-back (263's design) — separation is the fix.

## Boundary

- 248 worktree C:/PR/SfSpp_preprocessing-248 + Spartan sfs-vote-248 (data + mesh live there; 264 G3 filtered set reusable). Edge stage only. No main commits.
- Strand split method is the worker's choice (e.g. cut the FULL chain at its 122.8mm max-jump and verify each half is one coherent line; or split by signed distance to the bag PCA plane). Acceptance decides, not method.
- PICTURE ONLY (lead steer 2026-10-23): skip visual-qa stage_pair/viewer; export ONE static 3D PNG (mesh grey + strand A one colour + strand B another + author black, plus a zoomed panel) to the 248 artifacts for the chat.
- Leftover from the failed first attempt (worker 23eeb4ae died, no message): C:/PR/SfSpp_preprocessing-248/pota265_split.py (162 lines) + pota265_run_split.sbatch. Reuse, extend or discard as you see fit — nothing was confirmed run.

## Constraints

- Spartan git pull --ff-only + STOP on divergence; same node class for md5 comparisons.
- Do NOT rebuild unless the existing binaries (2d435e9f FULL, f3a2bcf5 GUIDED) mismatch md5 — reuse them.
- Judgement stays with lead — stage evidence and STOP. Disk: project fs was 92% in 264 — prune own superseded trees only, keep evidence trees.

## Acceptance

- Two staged strands, each visibly ONE line; strand separation measured (median nearest inter-strand distance) quoted against wall thickness (measure from mesh or thickness detector, state source).
- Each strand named to a face (interior/exterior/same-face) with method stated (mesh normals / surface classification / eye).
- Verdict line: two-lips vs one-fold + the ordering consequence (separate-then-trace-interior vs out-and-back).
- Replication: G3 keep 1045/1121 and strand union == G3 set exactly (no dots lost/added in the split).

## Lead verdict (R6, 2026-10-23)

Checked: ticket Comments, the PNG at C:/PR/SfSpp_preprocessing-248/artifacts/pota265_strands_P03_Bl1.png, and the plotting script pota265_final.py (panels a/b/c draw the chain ORDER as polylines, not point sets — so a straight orange run in the picture is a real chain segment).

ACCEPTED:
- FACE MEMBERSHIP VERDICT — one folded sheet, not two lips. Strand A d->Surface_1 med 0.000, strand B med 0.542, author med 0.246, all against Surface_0 med 10.855/24.981/14.683. Exact set membership, three independent routes (slot naming, sphere radius S0 47.2 < S1 63.8, 0.000 mm). The interior/exterior-lips hypothesis (lead's, 2026-10-23) is DISPROVEN.
- TRAP RECORDED: closest approach 5.364 mm and thinnest wall 5.270 mm coincide within 0.1 mm. The 2026-10-17 face-hop thickness fingerprint would have answered WRONG here; only face membership settles it.
- Departure from the brief accepted as correct: 1045 cannot be partitioned into two strands (122.846 mm cut yields 1042 + 3 identical duplicates from the exhaustive fallback at edgeline_extraction_headless.cpp:897-900; PCA splits leave 60.7-136.5 mm internal jumps). True rows are 1045 + 76 = 1121, and the union check is done against 1121, not 1045.

CORRECTIONS THE LEAD RECORDS AGAINST ITS EARLIER READING OF 264:
- "G3 removed junk and kept both strands" is WRONG. The 76 dropped dots lie on the author's rim (panel b: cyan tracks black within ~2 mm while orange runs alongside and then departs), so the 3 mm gate deletes genuine rim. 264's own "satellite = removable noise" reading inherits this error.
- "Second row" is loose language: median satellite-to-loop spacing is 14.451 mm (p90 22.38), not ~5.4 mm; only the closest stretch is row-like. Better: a second arc that hugs the author's rim where it matters.
- Worker's "separation is the fix" is NOT adopted as this ticket's conclusion. Panel (a)+(b) show the 1045 chain ORDER leaping straight across the loop (that is the maxjump=122.846 mm segment), on a set whose neighbour structure the worker's own lag test says is a single traversal. Ordering, not separation, is therefore the open question and needs its own test.

Nothing landed to main from this ticket's work beyond the ticket file itself; 264's guided filter stays default-OFF and must NOT be enabled on this lane (it removes rim).

## Required evidence to report

- Ticket Comments + results-in; visual-qa stage path + PNG path; separation number + wall number + face names; verdict line; job IDs + sacct; self-contained completion message.

## Comments

### Headline

**The 1121 → 1045 GUIDED filter removed the braid's SECOND ROW.** The G3 bag is not "both strands kept, satellite
gone" — it is one row kept and the *other row* discarded. Consequence: the 1045 dots cannot be split into two
strands, because they are a single simple closed loop.

### Verdict line

> **ONE FOLDED SHEET — not two lips of one break.** Both rows lie on the **exterior** sheet (Surfaceslot 1); the
> interior sheet is 24.7 mm from the satellite and >= 5.27 mm from the main loop, so neither row can be the
> interior lip. Ordering consequence: out-and-back (263's design) is the right ordering and **separation is the
> fix** — there is no interior boundary in this bag to trace instead.

### Which face each strand sits on, and how decided

Method — **exact set membership, not eye or normals**: the outline dots are literally sample points of the
extracted face sheets, so a dot's face is read off by its distance to each sheet. The two verdicts are separated by
a factor of ~46 (0.54 mm vs 25 mm), so there is no ambiguity to adjudicate.

| curve | n | d -> Surface_1 (exterior) | d -> Surface_0 (interior) | face |
|---|---|---|---|---|
| strand A (main loop) | 1045 | min 0.000, med **0.000** | min 5.270, med 10.855 | exterior |
| strand B (satellite) | 76 | min 0.283, med **0.542** | min 24.744, med 24.981 | exterior |
| author breakline | 343 | min 0.015, med **0.246** | min 5.377, med 14.683 | exterior |

Slot semantics (slot 0 interior / slot 1 exterior) and a sphere fit of the piece agree independently:
centre (1.98, 34.88, 504.6), mean radius Surface_0 = 47.2 mm < Surface_1 = 63.8 mm, so the smaller-radius
(concave) sheet Surface_0 is the interior. All three routes — slot naming, curvature, and 0.000 mm membership —
put the strands on the exterior face.

### The two numbers, with method

- **Inter-strand separation: closest approach 5.364 mm, median spacing 14.451 mm.**
  Method: per-dot nearest distance from each of the 76 satellite dots to the 1045-dot main loop (p90 = 22.38 mm);
  closest approach is symmetric (5.364 mm both directions).
- **Wall thickness: 5.270 mm thinnest, 10.855 mm median.**
  Source: distance from each outline dot to the extracted **interior** surface sheet (Surface_0). Because the dots
  themselves lie on the exterior sheet at d = 0.000, this is a genuine face-to-face wall, not a fitted guess.
  Cross-check: Surface_0 <-> Surface_1 restricted to within 8 mm of the loop gives median **6.658 mm** (n = 6467),
  consistent.

**Warning for the fingerprint heuristic:** closest approach (5.364 mm) and thinnest wall (5.270 mm) coincide to
within 0.1 mm, which is exactly the "doubled loop ~5 mm apart = wall thickness = walk hopping faces" signature of
2026-10-17. Here that reading is **wrong**: a face hop would put one row on each face, and the satellite is
24.7 mm from the interior sheet. The numeric coincidence is a trap; only the face membership separates the two
hypotheses.

### Why the 1045 bag has no second strand (replication + the test that settles it)

Faithful replication of the FULL walk (pure nearest-neighbour, which is the real behaviour — the POTA-263 heading
guard at edgeline_extraction_headless.cpp:889 is overwritten by the unconditional NN loop at :892-896) reproduces
the binary's own numbers exactly:

- input cloud is the **snapped** boundary, `boundaryImproved.pcd` (n=1121, md5 b79c25b051fadba82e1772a50754584b),
  not `boundary.pcd`. At gap 5 mm it splits into exactly **2 components, largest 1045** — matching the logged
  `[GUIDED-264] dist<=3mm kept 1045/1121 (ref loop 4576 from largest 1045/1121)`.
- the satellite's nearest approach to the main loop is **5.364 mm > the 3 mm guided gate**, so no satellite dot can
  be kept; hence filtered set == main component exactly (no assumption needed).
- chain maxjump **122.846 mm** — identical to the logged `[FULL-263] chain=1045 maxjump=122.846mm`.
- the 122.846 mm "strand B" the old plan expected is **3 points at ONE unique coordinate**
  ([-35.33, -30.00, 474.95]), i.e. duplicates picked up by the exhaustive fallback — degenerate, not a strand.

**The single-loop proof:** distance between dots at half-loop lag (L = 522) has median **125.4 mm**, the loop's own
diameter. If the 1045 were two rows traversed out-and-back, that quantity would be the row offset (a few mm). The
lag-distance curve rises monotonically (10.7 mm at L=20 to 125.4 mm at L=522) with no dip at any lag, so the walk
traverses the rim **once**.

Both candidate split methods named in Boundary were tried and both fail:

| method | result | why it fails |
|---|---|---|
| cut at the 122.846 mm max jump | 1042 + 3 | the 3-point "strand" is one repeated coordinate |
| split by sign of distance to bag PCA plane | 511/534, 572/473, 545/500 on axes 0/1/2 | a plane through a closed loop cuts it twice, so each side is 2 arcs: internal jumps of 60.7-136.5 mm |

No non-arbitrary partition of a simple closed loop into two coherent strands exists; a partition would need two
arbitrary cut points. Reported rather than forced.

### What this implies for the lever (lead's call, not decided here)

The two rows are 5.364 mm apart, so **any guided gate below 5.364 mm deletes the second row**. G3's 3 mm gate
therefore guarantees exactly the bag we are trying to analyse. If the lead wants both rows in one bag, the gate
must exceed 5.364 mm (SFS_GUIDED_DIST > 5.4) — but note that changes what "filtered" means, and per the face
finding the second row is *not* the interior lip, so recovering it does not by itself give paper IV-B its interior
edge line.

### Artefacts

- PNG (laptop): `C:/PR/SfSpp_preprocessing-248/artifacts/pota265_strands_P03_Bl1.png` (2310x1627)
- PNG (Spartan): `/data/gpfs/projects/punim2657/sfs-vote-248/artifacts/pota265_strands_P03_Bl1.png`
- working tree: `/data/gpfs/projects/punim2657/pota265_strands/` (pota265_final.log, pota265_summary.json)
- panel key: (a) full oblique 3D, mesh grey, strand A orange, strand B cyan, author black; (b) 52 mm zoom at the
  closest approach; (c) through-wall cross-section showing both strands inside the exterior-sheet band and the
  interior sheet ~11.6 mm away; (d) row spacing vs wall thickness.

### Baselines

- local `C:/PR/SfSpp_preprocessing-248` and Spartan `sfs-vote-248` both at **4887348**, unchanged before and after;
  nothing committed. Binaries reused unmodified (FULL md5 2d435e9f6a2b6e78ede480b326861da5,
  GUIDED md5 f3a2bcf5cdd1e90744034eef599695ce) — no rebuild.
- Slurm 33708248 (COMPLETED 0:0, spartan-bm176) first geometry pass; final figure and diagnostics ran as short
  interactive computes on the same node class. No other pots and no existing evidence trees touched.
