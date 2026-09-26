# Source state anchor — the nested clone, and where the applied patches now live

## Status: tracked and resettable (2026-09-26)

The applied preprocessing source is now **committed and pushed**, so the
pipeline state can be reset and reproduced:

| | |
|---|---|
| Repo | `zeejaytan/SfSpp_preprocessing` (**same URL as the parent repo**) |
| Branch | **`nested-applied-2026-09-26`** — deliberately NOT `main` |
| Commit | **`4c0b90b`** "Juglet 2026-09-25 preprocessing fixes, now committed" |
| Files | `edgeline_extraction_headless.cpp`, `mesh_processing_headless.cpp` |
| Verified on remote | `4c0b90baf2602edfb6faad0cfa94d0b2576f5283` |

That commit holds the seven `juglet_*` patches of 2026-09-25 as applied
source: mm-unit boundary/outlier radii, no write convert, sphere radii in
mm, mesh single-file argv filter, segmentation thresholds, grow
diagnostic. Ticket 02 patch 1 (walk K=2) is **deliberately absent** — it
was refuted and reverted before the commit.

**Reset / reproduce:**

```bash
cd /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing
git fetch zeejay nested-applied-2026-09-26
git checkout 4c0b90b -- edgeline_extraction_headless.cpp mesh_processing_headless.cpp
```

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

## Verified file anchor (belt and braces)

Committed state, for byte-level comparison:

```
original_nurbs_preprocessing/edgeline_extraction_headless.cpp
  md5  aecfe83007a7de0b4c115cee577d6e71
  size 137419 bytes, LF line endings (0 CRLF)
  walk K: line 832  int K = std::max(5, std::min(50, boundary_size / 10));
  markers: g_boundary_radius_mm, "keep everything in mm",
           "mm (was meters-assumed)", "do NOT convert"
  absent : SFS_WALK_K_LOCAL   (patch 1, refuted)
mesh_processing_headless.cpp markers: GROW-DIAG, "Single-file filter",
                                     "Segmentation thresholds"
```

```bash
md5sum original_nurbs_preprocessing/edgeline_extraction_headless.cpp
# expect aecfe83007a7de0b4c115cee577d6e71
```

## What is still not reproducible

The **laptop clone has no `original_nurbs_preprocessing/` at all** — the
nested clone is never fetched here (the parent repo tracks one file in
that directory). So laptop-side verification of these patches still
requires copying the file off Spartan first. The state is now safe and
recoverable; verifying it from the laptop in one step is not.

**Not yet actioned:** making the nested sources a first-class part of the
parent repo (vendored copy, or a submodule pinned to a branch we control)
would remove the remaining friction — one checkout, laptop-verifiable
patches, no cluster-only step. Recorded in ticket 02.
