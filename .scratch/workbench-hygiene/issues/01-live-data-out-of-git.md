# 01: Take Spartan's live pipeline data out of git

**What to build:** the Spartan checkout reads clean because nothing per-machine is tracked,
not because a flag hides it. Pipeline outputs that differ between machines live in the
working area, are ignored by git, and `AGENTS.md` says so instead of describing the old
skip-worktree arrangement.

**Answers:** none (workbench routine; amendment C2, conservator's choice 2026-10-24:
"Move the data out of git").

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

## State when written (2026-10-24)

- Spartan canonical checkout `/data/gpfs/projects/punim2657/sfs_preprocessing`: **0**
  skip-worktree flags left (were 361 earlier today), **91** lines of `git status --porcelain`
  (not yet read: modified tracked files, untracked outputs, or both).
- On `origin/main` (e2aa11e): `Temp/` is already untracked and ignored (`.gitignore` line 32).
  Still tracked: `Segments/1.xyz`, `Segments/2.xyz`, `SegmentsRawPts/1_rawPts.xyz`,
  `SegmentsRawPts/2_rawPts.xyz`.
- `AGENTS.md` "Spartan-side data (skip-worktree)" still describes 165 flagged files: stale.

## Steps

1. **Read, via the Spartan thread:** the 91 status lines, grouped by top directory and by
   code (` M`, `??`, ` D`), and whether the checkout is level with `origin/main`. Read-only.
2. **Decide (lead):** which of those are pipeline outputs (go out of git) and which are
   source or committed inputs (stay). The four tracked `.xyz` files are the likely outputs.
3. **Harvest before anything moves (rule 13):** tar Spartan's live copies of every output
   path into `/data/gpfs/projects/punim2657/SfSpp/attic/sfspp-live-data-<date>.tar.gz` with
   an INDEX and a manifest, extract and `cmp` every member, `gzip -t`. These may be the live
   inputs of current assembly runs: check `squeue` for jobs reading them first.
4. **Laptop commit:** `git rm --cached` the output paths, add them to `.gitignore`, rewrite
   the `AGENTS.md` section to say where the live data lives and why it is not tracked.
5. **Spartan:** `git pull --ff-only`; the files stay on disk as ignored. `git status
   --porcelain` should then show no output paths.

- [ ] 91 status lines read and classified
- [ ] Live copies archived and the archive proved
- [ ] Output paths untracked and ignored; `AGENTS.md` section rewritten
- [ ] Spartan checkout pulled; status clean of output paths; layout gate check 6 passes
