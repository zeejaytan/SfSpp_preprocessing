# 05: Retire the three worktrees on Spartan once their tickets close

**What to build:** the Spartan canonical checkout carries no worktrees, so
`check_spartan_checkouts.sh` reads ok for SfSpp_preprocessing.

**Answers:** none (workbench routine; amendment 1.2).

**Blocked by:** tickets 275 and 276 (the worktrees' own work) being resolved; 01.

**Status:** ready-for-human

On 2026-10-24 `check_spartan_checkouts.sh` (run in the Spartan thread) found three detached
worktrees off `/data/gpfs/projects/punim2657/sfs_preprocessing`: `sfs_preprocessing.wt/275`
(1308298), `.wt/276` (0ab0935), `.wt/buildsh-20261024` (a147c59). Ticket 276 was committed
today, so these are live work under the old layout: do not remove them while their tickets
are open. When they close: prove each worktree's HEAD is on an `origin/*` branch from the
canonical checkout (rule 13), check `squeue` for jobs inside, harvest any untracked record
files, then `git worktree remove`. Removing anything on Spartan needs the conservator's yes,
hence `ready-for-human`.

- [ ] Each HEAD proved on GitHub, or rescued as `rescue/<name>` via the laptop
- [ ] Untracked record files harvested and proved
- [ ] Worktrees removed; `check_spartan_checkouts.sh` shows 1 worktree for this checkout
