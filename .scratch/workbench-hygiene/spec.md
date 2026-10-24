# Workbench hygiene in SfSpp_preprocessing

**Prior work searched:** GitHub and git's own manual for worktree and skip-worktree practice
(https://git-scm.com/docs/git-worktree, 2026-10-24); the Spartan data-management page
(https://dashboard.hpc.unimelb.edu.au/data_management/, now redirecting). Found: no released
code applies; this is our own workbench, following `../../../docs/agents/workspace-hygiene.md`.

**Answers:** none. This effort carries out this repo's share of the workbench amendments the
conservator agreed on 2026-10-24 ("Workbench amendments against the five habits"): per-machine
data out of git (C2), then the root tidy (2.1, 2.2) and log paths (2.3) as later tickets.

## Tickets

- `issues/01-live-data-out-of-git.md` — amendment C2.
- `issues/02-tidy-the-root.md` — One CMakeLists and one build script; root batch scripts and notes into folders.
- `issues/03-log-paths.md` — Slurm logs go to the run directory, never the checkout.
- `issues/04-review-unmerged-branches.md` — Decide each of the 22 unmerged branches: merge, keep as a named rescue, or delete.
- `issues/05-retire-spartan-worktrees.md` — Retire the three worktrees on Spartan once their tickets close.
