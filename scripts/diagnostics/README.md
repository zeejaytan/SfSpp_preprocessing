# Edge-line ordering diagnostics

How the edge-line ordering defect was measured, and how to re-measure it.
These scripts are the evidence behind ticket 01; the conclusions they
support are written up in the ticket and in
`original_nurbs_preprocessing/edge_line_ordering.h`.

Run from this directory (`python <script>.py`) — they import each other by
module name, so the working directory matters.

## The fixture

Two scripts need the real Juglet boundary cloud, fetched from Spartan:

```bash
mkdir -p fixtures
scp spartan:/data/gpfs/projects/punim2657/sfs_preprocessing/Temp/Temp_edge/Juglet/boundary.pcd          fixtures/
scp spartan:/data/gpfs/projects/punim2657/sfs_preprocessing/Temp/Temp_edge/Juglet/boundaryImproved.pcd fixtures/
```

`*.pcd` is gitignored project-wide, so these are not committed. A
**copy** of `boundary.pcd` is committed as plain text at
`original_nurbs_preprocessing/tests/data/juglet_boundary_59.txt`, which is
what the C++ seam test reads — so the test itself needs no fixture fetch.

`Temp_edge/` is overwritten per sherd, so the file on the cluster is
whichever sherd ran last. **One sherd of nine, not a summary of the
Juglet.** Re-fetching may give a different sherd; the numbers will differ
and that is expected, not a regression.

## The scripts

| Script | Question | Answer it gave |
|---|---|---|
| `diagnose_walk.py` | What does the walk do to a real cloud? | 59 in, 9 out, 2.1 mm of a 36.8 mm rim. And a faithful Python transcription of the C++, checked against it. |
| `test_saturation_bound.py` | Is the walk bounded near 2K−1? | **Refuted.** Coverage 1.000 at every n and K; a walk pinned at K=8 still covers a rim 32× longer. Kept as the record of the refutation. |
| `find_stall_trigger.py` | Which input property stalls it? | Neither uneven spacing nor off-plane noise alone; **a folded or self-approaching rim** reproduces it. Reads the exact stall: which candidates, which distances, used or free. |
| `test_density_contrast.py` | Is it local density contrast? | **Yes, and exactly.** A ring at 40× contrast, 15% dense, gives 9/59, coverage 0.153, 50 stalls — identical to the real cloud. On the real cloud, 85% of points have ≥K neighbours within K × median spacing. |
| `calibrate_reference_length.py` | What reference length can a test assert against? | MST length tracks true rim length to within 1.7% on circles. Healthy `traced/ref` ∈ [0.46, 1.00]; the real Juglet cloud is 0.058. The gap is ~8×, which is why the 0.3 threshold is measured rather than chosen. |

## Reading the output

Two of these scripts print explanatory prose under their tables. That prose
is **part of the output, not commentary on it** — if a table contradicts a
line of prose, the table is right and the prose is a stale hypothesis.
That happened once already (`test_saturation_bound.py` predicted coverage
would fall; it stayed at 1.000) and the prose was corrected rather than
left to mislead the next reader.

## What these scripts are not

`diagnose_walk.py` is a **transcription** of the C++ in Python, for fast
iteration on a laptop. It is not the artefact under test. The artefact is
`original_nurbs_preprocessing/tests/test_edge_line_ordering.cpp`, which
compiles the same `edge_line_ordering.cpp` the pipeline compiles. Where the
two disagree, the C++ is right and the transcription has a bug.
