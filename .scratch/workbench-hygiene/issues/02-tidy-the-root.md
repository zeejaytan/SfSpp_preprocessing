# 02: One CMakeLists and one build script; root batch scripts and notes into folders

**What to build:** The 515-file root becomes a short one: one `CMakeLists.txt` with options and one `build.sh --build-dir`, the 83 batch scripts in `hpc/`, the 42 notes in `docs/notes/`, the 6 `.pid` files deleted and `*.pid` ignored.

**Answers:** none (workbench routine).

**Blocked by:** 01 (same clone; run after it).

**Status:** ready-for-agent

Amendments 2.1, 2.2, 4.4. The variant `CMakeLists_*.txt` and 34 `build*.sh` are code edits standing in for build options. Fold each variant into an option only where a current job uses it; move the rest to the attic. Check references with `git grep` and the batch scripts' composed paths (hygiene trap: composed paths).

- [ ] One `CMakeLists.txt`, one build script; every current job still builds
- [ ] Root batch scripts and notes moved; no stale reference
- [ ] `.pid` files gone and ignored
