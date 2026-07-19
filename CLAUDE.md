# CLAUDE.md — SfSpp_preprocessing (project)

Follow the workspace root **`../AGENTS.md`** / **`../CLAUDE.md`** (laptop ↔ GitHub ↔ Spartan) for all shared rules. Same overlay as **`AGENTS.md`** in this folder — the paths table, the unrelated-histories merge note, and the **skip-worktree** convention for the 165 regenerated data files on Spartan live there. Read that before touching `Segments/`, `SegmentsRawPts/`, or `Temp/Data/` on the cluster.

Edit and commit on the laptop; Spartan is pull-only (`git pull --ff-only`) and runs Slurm via `scripts/remote/*`. Heavy data stays on Spartan; `artifacts/` is the local, gitignored rsync landing zone.
