# `original_nurbs_preprocessing/` — vendored source (2026-09-26)

These are **the source files that actually build the pipeline**, vendored
into the main repository so they can be read, reviewed and patch-verified
from the laptop.

## Why this directory exists

The preprocessing pipeline was built inside a **nested git clone** on
Spartan (`sfs_preprocessing/original_nurbs_preprocessing/`), which had
its own history and its own remote pointing at this same GitHub URL. The
main repository could not see it: `git checkout` on those files was a
silent no-op, the compiled code was invisible to the main repo, and the
two histories could not push to `main` without colliding.

That caused two wrong-file patches and six failed job submissions on
2026-09-26 (recorded in `.scratch/juglet-breaklines/issues/02-*.md`).

**This directory is now tracked by the main repository**, replacing a
gitlink that pointed at the nested repo's commit `3737977`.

## What is here, and what is not

**Vendored (64 files):** the pipeline's own source —

- C++: `edgeline_extraction_headless.cpp`, `edgeline_extraction.cpp`,
  `edgeline_extraction_backup.cpp`,
  `edgeline_extraction_curvature_fixed.cpp`, `mesh_processing.cpp`,
  `mesh_processing_headless.cpp`,
  `generate_nurbs_compatible_surface_f.cpp`, `tools/*.cpp`
- headers: `tiny_obj_loader.h`, `data_path.h`
- `CMakeLists.txt`, `Dockerfile`, `setup_container.sh`, `download.sh`
- MATLAB axis extraction: `AxisExtraction/*.m` and the `extract_*.m` /
  `analyze_*.m` helpers
- docs: `README.md`, `PREPROCESSING_FIXES.md`, `LICENSE`

**Deliberately excluded** (present in the nested repo, not vendored here):

| Excluded | Why |
|---|---|
| `alglib/` (36 files) | third-party numerics library, unchanged from upstream |
| `build*/` (74 files) | build output, including compiled binaries and `.o` files |
| `*.pcd`, `*.ply`, `*.xyz`, `Pot_A_Piece_*_Surface_*` | generated data and run outputs |
| `*.err`, `*.out`, `*.log`, `*.flag`, `*.pid` | run leftovers |
| `gen_normals` | a compiled binary, not source |
| `segmentationStats.txt`, `Dataset`, `Temp` | run outputs / symlinks |

## This copy is for reference and patch verification, not for building

**Builds still happen on Spartan**, inside the preprocessing container,
which supplies PCL, Eigen, OpenCV and MATLAB. A laptop checkout cannot
build this — it never could. What the vendored copy buys is the thing
that was missing: **a patch can now be written and checked on the
laptop, against the exact bytes that compile.**

## Provenance and verification

The two files that carry the applied fixes were copied from Spartan and
verified byte-identical by MD5 at the moment of vendoring:

```
edgeline_extraction_headless.cpp   aecfe83007a7de0b4c115cee577d6e71
mesh_processing_headless.cpp       3f383619ab55b395da5c0e7f8e969602
```

The applied state is also preserved in the nested repo's history, pushed
as branch **`nested-applied-2026-09-26`**, commit **`4c0b90b`**, in this
same repository. That branch is the fallback if this vendored copy is
ever found to be wrong; it can be deleted once this is trusted.

## Patch discipline still applies

Patches live in `../patches/`. They are generated against these files and
must keep their **LF line endings** and exact hunk counts — the nested
copy was LF-only, so a CRLF patch silently fails to apply. The nested
repo also has a handy script generator pattern: build the diff from the
file with `difflib` rather than hand-counting hunk headers.
