# One build entry point: `build.sh`

`./build.sh` replaces the copy-a-script-and-tweak-it habit behind the 33 `build_*.sh` files
at the repo root. A build variant is now a named **configuration** (an image plus a set of
`cmake -D` flags), not a copy of the tree and not a bespoke script that rewrites a tracked
file.

## Usage

`bash
./build.sh --target mesh                    # MeshPreprocessingHeadless, variant "default"
./build.sh --target nurbs --variant release # EdgeLineExtractionHeadless, Release flags
./build.sh --target axis                    # AxisExtractionHeadless (see below)
./build.sh --target mesh --container /path/other.sif   # try a candidate image
./build.sh --target mesh --build-dir build/fast-mesh
./build.sh --target mesh --dry-run          # print the container command, run nothing
`

Output always lands in `build/<target>-<variant>/` inside the worktree the script sits in.
The repo root is derived from the script's own location, so a worktree builds itself. The
legacy scripts hardcode `/data/gpfs/projects/punim2657/sfs_preprocessing` and can therefore
only ever build one checkout.

## What it guarantees, and how that is checked

| Guarantee | Mechanism |
|---|---|
| Nothing is written into the source tree | `cmake -S <src> -B <build dir>`; the compiler's cwd is the build dir, never a source dir |
| No tracked file is rewritten | no heredoc writes into the tree; the axis project file is generated **inside** the build dir |
| The tree is still clean afterwards | `git status --porcelain` is captured before and after; any difference exits **3** |
| The compiler runs in the container | `apptainer exec --bind /data:/data <sif> bash -c ...`, as every legacy script did |
| A binary can be traced to its build | `build/<target>-<variant>/build-info.txt` records image, source root, cmake args, make line, timestamp, sha256 |

Ignored paths (`build/`, `*.sif`, `original_nurbs_preprocessing/alglib/`) never appear in
`git status`, so "clean" really means "no source file changed". `build/` is already ignored
by `.gitignore:4`; no ignore edit was needed.

## Variants and targets

| `--variant` | image | extra cmake args |
|---|---|---|
| `default` | `pcl_191_nurbs.sif` | none -- what `build_mesh.sh` did |
| `release` | `pcl_191_nurbs.sif` | `-DCMAKE_BUILD_TYPE=Release` -- what `build_nurbs_preprocessing.sh` wanted |
| `working-pcl112` | `sfs_preprocessing_working.sif` | none -- the legacy PCL 1.12 image, **absent from the cluster today** |

| `--target` | make target | source root |
|---|---|---|
| `mesh` | `MeshPreprocessingHeadless` | `original_nurbs_preprocessing/` |
| `nurbs` | `EdgeLineExtractionHeadless` | `original_nurbs_preprocessing/` (needs `alglib/`, gitignored) |
| `axis` | `AxisExtractionHeadless` | repo root: `axis_extraction_cpp.cpp` |

`--container PATH` overrides the variant's image, which is how a freshly provisioned image is
tried without inventing a variant name for it.

## The 33 legacy scripts, and which ones this replaces

Read mechanically (image, `-D` flags, make targets, and whether the script writes a
CMakeLists). Three groups emerge; only the first is a pipeline build.

### A. Product builds against an existing image -- **replaced by `build.sh`** (8)

| script | image | make targets | equivalent |
|---|---|---|---|
| `build_mesh.sh` (26 l) | `pcl_191_nurbs.sif` | MeshPreprocessingHeadless | `--target mesh --variant default` |
| `build_all.sh` (27 l) | `pcl_191_nurbs.sif` | Mesh + Edge + test_surface_classify test_edge_line_ordering test_boundary_filter, then runs the tests | `--target mesh,nurbs`; the three test targets are not built (see "does not fit") |
| `build_seam.sh` (34 l), `build_seam_inner.sh` (37 l) | `pcl_191_nurbs.sif` | test_edge_line_ordering, EdgeLineExtractionHeadless | `--target nurbs` |
| `build_ticket04.sh` (35 l) | `pcl_191_nurbs.sif` | EdgeLineExtractionHeadless, test_surface_classify | `--target nurbs` (the test is one extra make) |
| `build_with_hook.sh` (97 l) | `pcl_191_nurbs.sif` | EdgeLineExtractionHeadless, then strings/nm proof that the ticket-11 hook is in the binary | `--target nurbs`; the hook check is ticket-specific and stays in that script |
| `build_nurbs_preprocessing.sh` (54 l) | `pcl_191_nurbs.sif` | EdgeLineExtractionHeadless with `-DCMAKE_BUILD_TYPE=Release -DPCL_DIR=/usr/local/lib/cmake/pcl -DCGAL_DIR=/usr/lib64/cmake/CGAL` | `--target nurbs --variant release`; both -D paths are **stale** -- this image ships PCL at `/usr/local/share/pcl-1.9` and CGAL at `/usr/share/cmake/CGAL`, which CMake finds unaided |
| `build_axis.sh` (4 l) | `pcl_191_nurbs.sif` | AxisExtractionHeadless -- **stale**: that target exists in no tracked CMakeLists | `--target axis` (generates its project file in the build dir) |

All eight bind `--bind /data:/data`, use the same Apptainer binary
`/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer`,
and run inside a held allocation via `srun --jobid`. They differ only in image, source root,
-D flags and make target -- that is the entire variation.

### B. Image provisioning -- **not replaced, out of scope** (19)

`build_complete_pcl191 build_fallback_tools build_final_working build_focused_nurbs
build_from_working_container build_host_nurbs build_host_nurbs_full build_in_container
build_manual_nurbs build_nurbs_conda build_nurbs_support build_patched_nurbs
build_preprocessing_pipeline build_sfs_prep_fixed build_static_nurbs build_ubuntu20
build_ubuntu20_nurbs build_vtk82_nurbs build_working`

These build PCL 1.9.1 with `-DBUILD_NURBS=ON -DBUILD_ON_NURBS=ON` (plus VTK 8.2/9.1 and
OpenNURBS) and install it into an image, often taking `cache/sfs_prep_from_working.sif`,
`../sfs_main/cache/sfspreproc-base.sif` or `../sfs_main/sfspreproc.sif` as input. Three of
them (`build_sfs_prep_fixed.sh`, `build_ubuntu20.sh`, `build_working.sh`) run
`apptainer build` itself. They produce the `.sif` that `build.sh` consumes; a build entry
point cannot replace them.

Two are not scripts at all but idea notes with a shebang: `build_host_nurbs.sh` (31 l) only
prints a plan and asks "Would you like me to try this host-native approach?", and
`build_patched_nurbs.sh` (21 l) writes `pcl_vtk91_patches.patch` into the current directory
(not gitignored, so running it dirties the tree) and prints a suggestion. Neither builds
anything.

### C. One-off experiment programs -- **not replaced, out of scope** (6)

`build_direct build_enhanced_2024 build_enhanced_2024_fixed build_enhanced_2024_final
build_simple build_working_tools`

These compile a different program -- `test_enhanced_2024`, an "enhanced alternative to NURBS"
experiment, or the PCL fallback tools -- by heredoc-writing a CMakeLists over the tracked root
`CMakeLists.txt`. `build_enhanced_2024_final.sh:17` is the offender the brief names:
`cat > CMakeLists.txt << 'EOF'` ... `project(Enhanced2024Test)`, then it builds in
`build_enhanced_final/` inside `sfs_preprocessing_working.sif`. That is what left the tree
dirty after every build. If that experiment is ever wanted again it belongs as its own target
with its own CMakeLists in a subdirectory, not as a rewritten root file.

## What does not fit the parameterisation

- **The axis target is in no tracked CMakeLists.** Commit `3bd5c10` added
  `add_executable(AxisExtractionHeadless axis_extraction_cpp.cpp)` to the root CMakeLists;
  commit `e34db86` ("Remove incorrect AxisExtractionHeadless C++ build target", 2025-11-18)
  removed it again, saying axis extraction runs via MATLAB (`AxisExtraction/*.m`) -- but
  `axis_extraction_cpp.cpp` is still tracked (450 lines, `int main()` at line 442, Eigen
  only). `--target axis` therefore generates a small project file **inside the build
  directory** and configures it with `-S <build dir> -B <build dir>`. Editing the tracked
  `CMakeLists.txt` -- what `build_axis.sh` relies on and what the heredoc scripts do -- is
  exactly what must not happen. If the axis experiment should become a real target, that is a
  deliberate tracked-CMakeLists change, not a build-script side effect.
- **The nurbs build needs a gitignored vendored library.**
  `original_nurbs_preprocessing/edgeline_extraction_headless.cpp:93` includes
  `alglib/src/dataanalysis.h` (and uses `namespace alglib` at lines 2507 and 2640). `alglib/`
  is gitignored (19 MB), so a fresh worktree never has it. `build.sh` checks for it and stops
  with the `cp -a` command instead of letting the compiler emit dozens of errors. Provisioning
  it into the worktree keeps the tree clean -- it is ignored -- but two worktrees are not equal
  until both have it. The mesh target does not need alglib.
- **The three test targets** (`test_edge_line_ordering`, `test_surface_classify`,
  `test_boundary_filter`) that `build_all.sh` builds are not pipeline products, so they are
  not `--target` values. After any nurbs build they are one command away in the same build
  directory:
  `apptainer exec --bind /data:/data <sif> make -C build/nurbs-default test_surface_classify`.
  `build_all.sh` also *runs* those tests; running a test is not building, and expectations set
  by ticket 04 do not belong in a build entry point.
- **`build_with_hook.sh` proves a symbol is present** (strings/nm, plus that
  `SFSPP_BOUNDARY_RADIUS_MM` survives into the container). That is ticket-11 acceptance
  evidence, not a build. Keep it.
- **`build_nurbs_preprocessing.sh` passes two -D paths that no longer exist** in the image.
  `--variant release` intentionally keeps only `-DCMAKE_BUILD_TYPE=Release`: passing
  `-DPCL_DIR=/usr/local/lib/cmake/pcl` would now fail at configure time.

## Verifying a change to this script

`bash
bash -n build.sh                      # syntax
./build.sh --help
./build.sh --target mesh --dry-run    # prints the exact container command
git status --porcelain                # must be unchanged by the above
`

The acceptance run for the script itself is: fresh worktree, `git status --porcelain` empty,
build in a compute-node job, `git status --porcelain` still empty, and the binary compared
against the legacy script's output.
## What the first cluster runs showed (2026-10-24)

Two compute-node runs on fresh worktrees: job `33733032` (spartan-bm171, first attempt,
failed on axis) and job `33733113` (spartan-bm169, after the axis quoting fix; every number
below is from this one). Both used the worktree
`/data/gpfs/projects/punim2657/sfs_preprocessing.wt/buildsh-20261024`.

- **The image is not inside a worktree.** `pcl_191_nurbs.sif` is gitignored, so a fresh
  worktree has no image at all: pass
  `--container /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif`.
  Copying 312 MB into every worktree is not worth it.
- **mesh is byte-identical to the legacy script.** `build_mesh.sh` (a staged copy with ROOT
  repointed at the worktree) produced sha256
  `2f27e110a3947c3527ef6ebf06f2d22f258d99d8b2dc1c6e82e9b2fceebd206c`, 5 721 408 bytes;
  `./build.sh --target mesh --variant default` produced the same hash, the same size and the
  same link line (`cmp` silent). Both compile the same source directory with the same flags
  (`-std=gnu++17 -Wno-old-style-cast -march=native -msse4.2 -mfpmath=sse -frounding-math`),
  and a binary does not record which directory it was built in.
- **nurbs needs `alglib/` provisioned once** (see above), then builds:
  `EdgeLineExtractionHeadless`, 11 490 848 bytes, sha256
  `7c4b87aa9d3ab57dd926350527182d3518531c68bb01a08062f80fc4a51f5390`.
- **`--target axis` cannot build today, and the reason is the source, not the script.** The
  project file is generated and configures cleanly -- that part works, which is what the flag
  proves -- and then the compile stops at
  `axis_extraction_cpp.cpp:21: error: 'Vector6d' in namespace 'Eigen' does not name a type`.
  Eigen has no `Vector6d` (its fixed sizes stop at 4) and the identifier appears 11 times in
  the file; it arrived with `ff40fc9`. No `AxisExtractionHeadless` binary exists in either
  build directory on the cluster, so it has never compiled there -- which fits commit
  `e34db86` removing the target as "incorrect". Fixing it means editing the pipeline source
  (a local `typedef Eigen::Matrix<double,6,1> Vector6d;`, or `VectorXd`), a change this
  script must not make on the way past. Open a ticket against the file; the `axis` flag
  stays because the interface names it.
- **Neither build dirtied the tree.** `git status --porcelain` had 0 lines before and 0
  after (the two files identical), with `build/`,
  `original_nurbs_preprocessing/build/` and `original_nurbs_preprocessing/alglib/` appearing
  only as ignored (`!!`). The three target directories held 293 files / 28 MB in total.

