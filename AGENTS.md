# AGENTS.md — SfSpp_preprocessing (project)

Follow the workspace root **`../AGENTS.md`** (laptop ↔ GitHub ↔ Spartan) for all shared rules. This file only adds project-specific paths and domain notes.

## Paths

| Role | Value |
|------|--------|
| GitHub fork (`origin`) | `zeejaytan/SfSpp_preprocessing` |
| Upstream | `DominicoRyu/SfSpp_preprocessing` |
| Spartan checkout (`REMOTE_ROOT`) | `/data/gpfs/projects/punim2657/sfs_preprocessing` |
| SSH | `Host spartan`, user `zhuojiat` |
| Remote helpers | `scripts/remote/pull_and_sbatch.sh`, `job_status.sh`, `fetch_artifacts.sh` |

This is the **preprocessing** stage (axis extraction, breaklines, NURBS surfaces) feeding the SFS++ **assembly** repo (`zeejaytan/structure-from-sherds-pp`, at Spartan path `sfs_main/sfspreproc-docker` — misleading name, see that repo's AGENTS.md).

## Repo history note (2026-07-19 migration)

The pre-migration fork on GitHub and the cluster checkout had **unrelated histories**: the cluster repo re-created upstream's commits with different hashes, then added ~20 research commits. Migration merged the fork lineage into the cluster lineage with `-s ours` (fork content was verified byte-identical to its cluster mirror commit `ad6f415`, so nothing was lost). History contains ~1GB of committed Pot A dataset revisions — cloning is slow; that is expected.

## Spartan-side data (skip-worktree)

On the Spartan checkout, **165 tracked data files** (`Segments/*.xyz`, `SegmentsRawPts/*`, `Temp/Data/Pot_A/*`, ~817MB) hold locally regenerated pipeline outputs that differ from the committed versions and are deliberately **not** committed. They are flagged with `git update-index --skip-worktree` on Spartan so the tree reads clean.

- If a future pull touches those paths, git will error — resolve by un-flagging (`git update-index --no-skip-worktree <file>`), stashing the data aside, pulling, and deciding which version wins. Do not blind-checkout over them: they may be the live inputs of the current assembly runs.
- List the flagged files with: `git ls-files -v | grep ^S`

Heavy untracked data (datasets, `.sif` containers, logs, `axis_output/`) stays on Spartan; `artifacts/` is the local rsync landing zone.

Typical loop:

```bash
git push origin HEAD
./scripts/remote/pull_and_sbatch.sh generate_complete_dataset_v2.sbatch
./scripts/remote/job_status.sh
./scripts/remote/fetch_artifacts.sh logs ./artifacts/
```
