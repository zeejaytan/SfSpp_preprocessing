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

## Corpus caveats — read before scoring

The conservator reports two pieces that are not watertight, and on both the gap is in the
**interior** surface only — the exterior is intact. The pipeline reads that gap as **a second broken
edge the sherd does not have**, so lanes derived from the interior surface (Bl0) are measured against
a reference that includes an edge we invent: their scores are evidence about the input, not about the
method, and they can neither convict nor exonerate a change. Lanes derived from the exterior surface
(Bl1) are not explained by the gap and stay usable.

- **Pot C 01** — interior Bl0 25 dots / 51.62 mm / cov 0.0 at the shipped defaults, its 986-dot bag
  in four pieces; exterior Bl1 81 dots / 41.06 mm / cov 0.0.
- **Pot J 01** — interior Bl0 47 dots / 29.27 mm on the theta-3.4 rebuild (25 / 32.05 shipped), its
  832-dot bag in four pieces (580 / 127 / 75 / 50); exterior Bl1 82 dots / 23.31 mm.

Both exterior lanes are stub failures on intact input, so they remain evidence for the walk-seed
change (ticket 275), alongside Pot B 01. Recorded from the conservator, 2026-10-24; the full record,
the competing causes and the open measurements are in
`.scratch/pota-repro/issues/285-pot-c-01-scan-gap.md`.

### A reference can be the broken thing (read this before quoting any score)

**Pot J 09 — do not score against the authors' breaklines on this piece** (conservator's ruling, 2026-10-24,
ticket 289). Their interior line runs 1-2 mm inside the sherd's real edge; their exterior line leaves the
edge for about 41 mm and crosses the flat of the face, up to 10.4 mm from ours. Both of our lines follow the
broken edge, read on an on-mesh overlay against `Pot_J_Piece_09_Mesh_DS.obj`. Both lanes are **excluded
from the bar tally**: the piece is neither a pass nor a miss. Pot J is 20 of 22 valid lanes at bar; the
corpus is 265 of 294.

This is the third of the workspace's three kinds of claim — the reference is wrong — and it is not a licence
to explain away misses: ticket 279 measured that on 163 of 163 pieces a reference line is the boundary of
the authors' own kept surface, and 265 lanes sit within 2 mm of these references, so one piece is wrong, not
the standard.

### Which pieces are in the corpus, and which the authors left out

The released datasets carry **exactly the pieces the paper reports** (Table V) — A 8, B 9, C 4,
D 29, E 31, F 6, G 7, H 11, I 27, J 11 = **143** — while the samples tree on Spartan holds **164
meshes and 163 pieces with breaklines**. The 21 extra pieces are not lost data; they are the ones the
authors excluded on purpose (`C:/PR/papers/text/sfspp-2502.13986v1.md:329`): "we exclude very small
fragments comprising fewer than 50 points in the respective surface edge lines (with a perimeter of
approximately 9cm) and special parts such as the handle, nose, or ornament. This results in removing
1 piece from pot C, 2 pieces from pot D, 4 pieces from pot E, 2 pieces from pot F, 3 pieces from pot I,
and 8 pieces from pot J." That is 20 removals and our tree reproduces the total exactly — 20 pieces
carry the authors' own breaklines, axis and both surfaces but have no released cloud. Their per-pot
split differs from ours by one on C, D, E and F, so treat the paper's list as approximate and the total
as the reliable figure.

Consequences before quoting a score:

- **Five scored pieces were excluded by the authors**: Pot F 07, Pot I 28, Pot I 29, Pot I 30, Pot J 12.
  Their scores are ours alone and cannot be set against the paper's evaluation.
- **Pot C 07** has no author artefacts at all — a mesh only. It was never processed.
- The frozen clouds live in `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Point/`:
  143 released (binary, ~1,000,000 points each) plus 5 derived from the mesh (ASCII, ~841,000), with
  `MANIFEST_released.tsv` and `MANIFEST_derived.tsv` beside them.

**A derived cloud is not a second-class one — measured, not assumed** (Pot C 01, the one piece that has
both): nearest-neighbour distance to the released cloud median **0.091 mm** ours→release and **0.110 mm**
release→ours (p99 0.23 / 0.36, max 0.39 / 0.94); signed offset along the released normal median
**0.000 mm** (p5 -0.010, p95 +0.009); normals agree at |dot| **0.999** median (p5 0.987); point spacing
0.084 mm against their 0.092. Ours carries 16% fewer points (840,835 against 1,000,026) because
`cc_mesh_to_pcd.sh` applies a statistical outlier removal the release does not. The only real
difference is that the sampler is unseeded, so a rebuild is a different draw of the same surface — the
spread measured between two draws is 0.14-0.16 mm on the median, about one sample spacing.

## Repo history note (2026-07-19 migration)

The pre-migration fork on GitHub and the cluster checkout had **unrelated histories**: the cluster repo re-created upstream's commits with different hashes, then added ~20 research commits. Migration merged the fork lineage into the cluster lineage with `-s ours` (fork content was verified byte-identical to its cluster mirror commit `ad6f415`, so nothing was lost). History contains ~1GB of committed Pot A dataset revisions — cloning is slow; that is expected.

## Spartan-side data (skip-worktree)

On the Spartan checkout, **165 tracked data files** (`Segments/*.xyz`, `SegmentsRawPts/*`, `Temp/Data/Pot_A/*`, ~817MB) hold locally regenerated pipeline outputs that differ from the committed versions and are deliberately **not** committed. They are flagged with `git update-index --skip-worktree` on Spartan so the tree reads clean.

- If a future pull touches those paths, git will error — resolve by un-flagging (`git update-index --no-skip-worktree <file>`), stashing the data aside, pulling, and deciding which version wins. Do not blind-checkout over them: they may be the live inputs of the current assembly runs.
- List the flagged files with: `git ls-files -v | grep ^S`

Heavy untracked data (datasets, `.sif` containers, logs, `axis_output/`) stays on Spartan; `artifacts/` is the local rsync landing zone, **not a store**. Where every other kind of output goes, and how long each one lives, is `../docs/agents/workspace-hygiene.md`, "Where each kind of output goes"; check this folder with `python ../scripts/check_artifacts.py .` (exit 0 = still a landing zone).

## Runs, worktrees and the attic

**The canonical checkout is `/data/gpfs/projects/punim2657/sfs_preprocessing`.** It only
fetches; nothing is edited or committed on Spartan, and it carries no worktrees. Ticket
branches live in a laptop worktree (`C:/PR/worktrees/sfs/<ticket>`), are pushed, and a job
builds from the pushed commit in a checkout it makes and deletes itself
(`../docs/agents/workspace-hygiene.md`, "One ticket, start to finish"). There are no
numbered copies of the tree, and a parameter is never varied by copying the tree.

A run records itself as a directory under the shared run root:

```
/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/
    run.json        parameters, inputs, the commit and tag in the directory name
    submit.sbatch   the exact batch script submitted
    logs/           Slurm output and the job's own logs
    out/            whatever the run produced
```

- The append-only index is `/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv`, header
  exactly `runid\tjobid\tcommit\ttag\tverdict\thuman_note` (tab-separated). `verdict` and
  `human_note` are written by a person or the coordinating session, never by the job.
- `logs/` and `out/` are pruned after **90 days**; `run.json` and the index row stay forever.
- Removed trees live in `/data/gpfs/projects/punim2657/SfSpp/attic/` -- one directory per
  tree, each with `manifest-path-size.txt.gz` and `skipped.txt`, plus a tarball where one was
  made. `/data/gpfs/projects/punim2657/SfSpp/bundles/` holds only `README.txt`.
- **The run directory is the unit of record, not the variation.**
- **Tidying this repo follows one written procedure:** `../docs/agents/workspace-hygiene.md`
  (scan, classify, prove provenance against this canonical checkout, harvest by named
  classes, prove the harvest, delete in guarded passes, record in the attic). Deletion
  follows `../AGENTS.md` rule 13. Measured 2026-10-24: 44 trees and 17 clones became 3
  and 1.

## Agent skills

Configured here so this repo works when opened on its own, not only from the `C:\PR`
umbrella. The full text of each convention lives at the workspace root; these are the
parts an agent needs before it can act.

- **Issue tracker — local markdown.** One feature per directory: the spec at
  `.scratch/<feature>/spec.md`, tickets one per file at
  `.scratch/<feature>/issues/<NN>-<slug>.md`, numbered from `01` in dependency order.
  Every ticket carries an **`Answers:`** line naming the question in `intent/` it exists
  to settle — `E1` for this project, `U`-numbers for the workspace, or `none` for
  routine work. Conventions and the ticket template: `../docs/agents/issue-tracker.md`.
- **Triage labels.** `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`,
  `wontfix`, recorded as a `Status:` line near the top of the ticket. Details:
  `../docs/agents/triage-labels.md`.
- **Domain docs — single-context.** Three different things, kept apart: **this file** is
  how to work here and the traps; **`CONTEXT.md`** at the repo root is the glossary, and
  `/domain-modeling` creates it lazily when the first term is actually resolved — do not
  create it empty; **`../docs/glossary.md`** is the cross-project measurement vocabulary
  (`part_acc`, chamfer distance, best-of-N) and outranks any local redefinition. ADRs go
  under `docs/adr/`. Details: `../docs/agents/domain.md`.
- **Intent.** [`intent/`](intent/) holds what we are trying to establish and what would
  settle it -- prefix **`E`**, permanent, numbers never reused. `/to-intent` opens a
  question or writes a finished ticket's result back into one. Check the loop is wired
  with `python ../scripts/check_intent_links.py`.

**Do not run `/setup-matt-pocock-skills` in this repo.** It would replace the above with
its own defaults, and its ticket template has no `Answers:` line -- tickets would stop
being connected to the question they exist to answer, silently.

Typical loop:

```bash
git push origin HEAD
./scripts/remote/pull_and_sbatch.sh generate_complete_dataset_v2.sbatch
./scripts/remote/job_status.sh
./scripts/remote/fetch_artifacts.sh logs ./artifacts/
```
