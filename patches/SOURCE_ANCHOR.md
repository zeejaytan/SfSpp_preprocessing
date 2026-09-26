# Source state anchor — superseded by vendoring

**This file is kept for the record. The state it describes is now in
`main`.** On 2026-09-26 the nested clone was dissolved: its 64 source
files are tracked directly in this repository at
`original_nurbs_preprocessing/`, MD5-verified byte-identical, and the
pipeline was re-verified building and reproducing the known-good bundle
from the tidied tree.

## What replaced it

- `original_nurbs_preprocessing/README-vendored.md` — provenance, what is
  and is not vendored, and why the copy is for patch verification rather
  than building.
- Branch `nested-applied-2026-09-26` (commit `4c0b90b`) held the
  pre-vendoring applied source. It was **deleted on 2026-09-26** once the
  vendored copy was verified. If it is ever needed again, ask git for the
  commit by id — `git branch nested-applied-2026-09-26 4c0b90b` — which
  works as long as the object has not been garbage-collected.
- The old nested `.git` is set aside on the cluster at
  `sfs_preprocessing/nested_git_backup_2026-09-26` (not tracked).

## Why a branch and not `main`

## Why a branch and not `main`

**The nested clone and the parent repo are two divergent histories
pushing at the same GitHub URL.** The nested clone's `zeejay` remote
resolves to `zeejaytan/SfSpp_preprocessing`, whose `main` is the *parent*
lineage (e.g. `92f9712`, a ticket commit), while the nested clone sits on
`3737977`. A plain `git push` to `main` was correctly rejected, and would
have clobbered the repository every script and the laptop clone depend
on. This is the same class of problem as the 2026-07-19 migration noted
in `AGENTS.md`.

**Consequence to keep in mind:** the nested clone's `HEAD` is *not*
reachable from the remote's `main`. Anything recovered from the nested
side must name the branch or the commit id explicitly.

## Verified file anchor (still current, and now enforced by the repo)

The vendored copy in `main` is byte-identical to the pre-vendoring
state, checked on both machines and re-checked by build job 31342607:

```
original_nurbs_preprocessing/edgeline_extraction_headless.cpp
  md5  aecfe83007a7de0b4c115cee577d6e71
  size 137419 bytes, LF line endings (0 CRLF)
  walk K: line 832  int K = std::max(5, std::min(50, boundary_size / 10));
  markers: g_boundary_radius_mm, "keep everything in mm",
           "mm (was meters-assumed)", "do NOT convert"
  absent : SFS_WALK_K_LOCAL   (patch 1, refuted)
mesh_processing_headless.cpp  md5 3f383619ab55b395da5c0e7f8e969602
  markers: GROW-DIAG, "Single-file filter", "Segmentation thresholds"
```

```bash
md5sum original_nurbs_preprocessing/edgeline_extraction_headless.cpp
# expect aecfe83007a7de0b4c115cee577d6e71
```

`vendor_check.sbatch` asserts this and rebuilds; `tidy_verify.sbatch`
re-runs the extraction and diffs against the known-good bundle.

## The problem that is still open

**Breakline segment boundaries are not reliably reproducible.** Re-running
the extraction on identical input with an identical binary reproduced the
known-good bundle byte-for-byte on 8 of 9 pieces; **piece 1's segment
header differed** (ref `1-5, 6-32, 33-94, 95-195, 196-200`; new
`1-6, 7-107, 108-169, 170-196, 197-200`) while its 200 points were
identical to 0.0000 mm. The geometry is stable; the *grouping* is not.

This matters because the segment header (`start_`/`end_` per `LCSIndex`)
is what tells the assembler **which** breakline points to compare, so a
boundary change alters the correspondence set the join gate sees. It is
a candidate contributor to the assembly side's run-to-run pairing
instability (`structure-from-sherds-pp` ticket 08, where a different
candidate pair is proposed on every run). Not proven to be the same
cause — recorded so it is not rediscovered from scratch.

**Not yet actioned:** making the nested sources a first-class part of the
parent repo (vendored copy, or a submodule pinned to a branch we control)
would remove the remaining friction — one checkout, laptop-verifiable
patches, no cluster-only step. Recorded in ticket 02.
