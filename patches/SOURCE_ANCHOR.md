# Known-good source anchor for the untracked nested clone

`original_nurbs_preprocessing/` sources are **not tracked in git** — the
laptop clone has exactly one tracked file in that directory, and the
compiled `edgeline_extraction_headless.cpp` exists only on Spartan.
`git checkout` on it is a silent no-op, so there is no way to reset it
from the repository, and any pipeline result cannot be reproduced from
git alone.

**Verified pre-experiment state (2026-09-26), all patches of 2026-09-25
already applied:**

```
original_nurbs_preprocessing/edgeline_extraction_headless.cpp
  md5  aecfe83007a7de0b4c115cee577d6e71
  size 137419 bytes
  LF line endings (0 CRLF)
  walk K: line 832  int K = std::max(5, std::min(50, boundary_size / 10));
  markers present: g_boundary_radius_mm, "keep everything in mm",
                   "mm (was meters-assumed)", "do NOT convert"
  markers absent : SFS_WALK_K_LOCAL (patch 1 reverted, see ticket 02)
```

`mesh_processing_headless.cpp` carries the three mesh-patch markers
(`GROW-DIAG`, `Single-file filter`, `Segmentation thresholds`).

## Why this file exists

Ticket 02 patch 1 (walk K=2) was applied on top of this state, refuted,
and then reverted by restoring this exact copy. Without an anchor there
would have been no way back: the patch chain is not reversible from git,
and the next experiment would have silently inherited the refuted K=2.

## How to use

Before any experiment, check the anchor and restore if it has drifted:

```bash
cd /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing
md5sum edgeline_extraction_headless.cpp
# expect aecfe83007a7de0b4c115cee577d6e71
```

## The real fix, still open

This file being untracked and unresettable is itself a defect worth its
own ticket: it means a published result cannot be regenerated, and it has
already caused one experiment (patch 1) to be one `git checkout` away
from unrecoverable. Committing the nested sources — or vendoring them as
patches against a tracked pristine copy — would remove the whole class of
problem. Recorded in ticket 02; not yet actioned.
