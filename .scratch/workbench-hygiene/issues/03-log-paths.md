# 03: Slurm logs go to the run directory, never the checkout

**What to build:** Every batch script writes its Slurm output to an absolute path (the run's `logs/`), so no log lands in the source tree.

**Answers:** none (workbench routine).

**Blocked by:** 02.

**Status:** ready-for-agent

Amendment 2.3. Today `--output=name_%j.out` drops logs wherever `sbatch` ran: that is how 336 to 570 logs ended up in each removed tree.

- [ ] No relative `--output` or `--error` left
- [ ] One job run through `new_run.sh` shows its log in `<run>/logs/`
