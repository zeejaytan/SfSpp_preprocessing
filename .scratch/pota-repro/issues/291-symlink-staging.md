# 291 — Stage a run's inputs by symlink, not by copy

Status: done (accepted; symlink staging shipped, identity rule restated in AGENTS.md)
Answers: E1
Working in: C:/PR/worktrees/sfs/291
Branch: 291-symlink-staging

## Why

The conservator's rule (2026-10-24): geometry must not grow on the system, and a run adds no
geometry of its own. Today every run copies its inputs into its own stage tree and, before the
released corpus existed, also derived a fresh cloud per piece:

- `SfSpp/runs/20261024-2151_8e1e514_p289-p09/submit.sbatch:51-55` — `mkdir -p $STAGE/Dataset/{Point,Mesh,Axes}/Pot_J`
  then `cp "$AUTHB/Mesh/Pot_J_Piece_09_Mesh_DS.obj" "$STAGE/Dataset/Mesh/Pot_J/Pot_J_Piece_09_Mesh.obj"`
  and `cp "$AUTHB/Axes/Pot_J_Piece_09_Axis.xyz" ...`;
- `:63` then ran `cc_mesh_to_pcd.sh` to **derive** the cloud into `Dataset/Point/Pot_J/` (~50 MB ASCII);
- `:68` copies that cloud into `out/cloud.pcd` as well.

A piece therefore costs one mesh copy (1.3 MB) plus one 20-90 MB cloud per stage tree, and a full
corpus run would recreate about 5-6 GB that already exists once.

The corpus now exists, frozen and complete:

```
/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/
    Mesh/<Pot>/<Piece>_Mesh.obj | <Piece>_Mesh_DS.obj     164 pieces
    Point/<Pot>/<Piece>_Point.pcd                          148 (143 released + 5 derived)
    Axes/<Piece>_Axis.xyz                                  163
    Breaklines/, Surfaces/                                 the authors' own outputs
```

## The change

Add `scripts/stage_piece.sh` to this repo (the canonical checkout only fetches; the script is
called from a run's submit.sbatch).

```bash
scripts/stage_piece.sh <stage_dir> <Pot_X> <Piece_01> [<Piece_02> ...]
```

Contract:

1. `Dataset/Mesh/<Pot>/<Piece>_Mesh.obj` → **symlink** to `$CORPUS/Mesh/<Pot>/<Piece>_Mesh.obj`,
   or to `..._Mesh_DS.obj` when only the downsampled mesh exists. This is also how the `_DS`
   naming trap is absorbed: the pipeline builds `<Piece>_Mesh.obj` from the point file's stem
   (`mesh_processing_headless.cpp:2505-2511`), and a symlink carries the expected name for free.
2. `Dataset/Point/<Pot>/<Piece>_Point.pcd` → **symlink** to `$CORPUS/Point/<Pot>/<Piece>_Point.pcd`.
   Fail loudly if the cloud is missing (it must not silently derive one: derivation is unseeded).
3. `Dataset/Axes/<Piece>_Axis.xyz` → **copy** (7 KB; the mesh stage is given it by
   `SFS_AXIS_FILE`, and a copy keeps the run's provenance self-contained).
4. Real (writable) directories for the outputs: `Dataset/Breaklines/<Pot>`,
   `Dataset/Surfaces/<Pot>`, `Temp/Data/<Pot>`, `Temp/Temp_edge/<Pot>`. Nothing else is created.
5. Append to `$STAGE/inputs.md5`: `readlink -f` of each symlink, the target's md5, and its point
   count — `md5sum` follows symlinks, so this records what was actually read.
6. Refuse to replace an existing **regular** file with a symlink (a derived cloud must never be
   silently swapped), and refuse a stage directory inside the corpus.
7. Print one summary line: pieces staged, symlinks, bytes copied.

Then: the run's `submit.sbatch` calls the script instead of the `cp` + `cc_mesh_to_pcd.sh` block,
and `AGENTS.md` ("Runs, worktrees and the attic") gains one sentence: *inputs are staged by
symlink into the frozen corpus; a job copies no geometry.*

## Gate (pre-registered, written before any number is taken)

One job, one piece, two stage trees **from the same inputs**: A staged by `cp` (today's way),
B staged by symlink (new script). Both run the mesh stage (theta 3.4, `SFS_AXIS_FILE` set, the
`[PAPER-234] classify` line quoted) and the edge stage with the shipped binary.

1. **IDENTITY**: A and B export lane files identical point for point — `n` equal and
   `max|dxyz| = 0.000000`. Anything else fails the gate; the symlink is then not equivalent and
   the ticket stops.
2. **NO GEOMETRY IN THE STAGE**: in tree B, `find "$STAGE" -type f -size +1M` is empty, and
   `find "$STAGE" -type l | wc -l` is exactly 2 per piece. Report `du -sh` for both trees.
3. **PROVENANCE**: `inputs.md5` resolves each symlink to the corpus path and its md5 matches
   `Point/MANIFEST_released.tsv` (or `MANIFEST_derived.tsv` for the 5 derived pieces).
4. **SCORES**: report both lanes' n / median / coverage both ways / jumps for A and B; they must
   be equal, and reported for the record, not gated against older runs (the frozen cloud is the
   released one, so older numbers came from different draws).

Use **Pot J 09** (has a released cloud, and ticket 289's picture exists to compare against) and
**Pot H 02** as a second piece (multi-component bag, exercises the seed path).

## Constraints

- No change to pipeline code, defaults or thresholds; this is staging only.
- Do not derive any cloud in the gate run. If a cloud is missing, stop and report.
- Never `build.sh --target nurbs` (ticket 282: it compiles the pre-247 duplicate at
  `original_nurbs_preprocessing/edgeline_extraction_headless.cpp`). Build the live root project.
- Write the ticket results into this file in the main clone; leave it uncommitted (the lead commits).
- Run directory under `SfSpp/runs/` + one `index.tsv` row with `verdict`/`human_note` left empty.
- The job deletes its own stage trees at the end (`GEOMETRY_DELETED.txt`), keeping `out/` and `logs/`.
- Do not touch `C:/PR/worktrees/sfs/290`.

## Results

Written by the worker, uncommitted (the lead commits). Three jobs in one run directory
`/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2351_3888318_p291-gate`; all `COMPLETED 0:0`.

### What was built

- **`scripts/stage_piece.sh`** — 150 lines, md5 `585955252cc84fe1a49e6dac8cef892e`. Contract implemented
  as written, with one correction to the ticket text below. Two phases: every input is resolved and
  every check is run **before anything is written**, so a bad corpus leaves no half-built tree. It
  probes the filesystem for symlink support first (a copying filesystem silently turns `ln -s` into a
  copy — this laptop's MSYS2 filesystem does exactly that) and refuses; every link is asserted `-L`
  after it is made. `_DS` is absorbed by the link's own name: the link is always created as
  `<Piece>_Mesh.obj` and points at whichever mesh exists. The axis is copied (108 B).
- **`AGENTS.md`** gains the one sentence (in the worktree, uncommitted): *inputs are staged by symlink
  into the frozen corpus; a job copies no geometry.*
- **Branch** `291-symlink-staging` — the worktree had been left **detached** at `3888318`, which the
  new rule forbids; corrected with `git switch -c 291-symlink-staging` and pushed with `-u`.
- **Ticket-text correction:** the corpus `Mesh/` is **flat** — 164 files, `<Piece>_Mesh.obj` or
  `<Piece>_Mesh_DS.obj`, no per-pot subdirectories, and the manifests sit in `Point/`, not at the
  corpus root. The script tries per-pot then flat, for both names, so both layouts work.

### Gate item 1 — IDENTITY: PASS on Pot J 09 (both lanes), FAIL on Pot H 02

| piece | lane | n A / n B | max abs(dxyz) | mean | verdict |
|---|---|---|---|---|---|
| Pot_J_Piece_09 | Bl0 | 79 / 79 | **0.000000** | 0.000000 | IDENTICAL |
| Pot_J_Piece_09 | Bl1 | 91 / 91 | **0.000000** | 0.000000 | IDENTICAL |
| Pot_H_Piece_02 | Bl0 | 152 / 152 | 0.716773 | 0.203735 | DIFFERS |
| Pot_H_Piece_02 | Bl1 | 138 / 138 | 0.418649 | 0.066255 | DIFFERS |

The sheets agree the same way: Pot J 09 md5-identical, Pot H 02 `Surface_0` A `6bea8964358d86e2…` vs
B `2534cd866c809b7a…`, `Surface_1` A `acc44cb5085b7512…` vs B `14ff0c76eb86d657…`.

**So the gate as pre-registered fails** (its rule: anything but 0.000000 fails it). The follow-up
job was run to find out what the difference belongs to.

### The difference is the mesh stage's own run-to-run spread, not the staging method (job 33748866)

Four mesh-stage runs on the **same frozen input bytes**: `A2`, `A3` staged by `cp`; `B2`, `B3` staged
by `stage_piece.sh` (symlinks). Then the edge stage on all four.

```
[DET] cp_vs_cp_max=0.866718  sym_vs_sym_max=0.234607  cp_vs_symlink_max=0.718929
[VERDICT] two cp runs of the same input already differ by 0.866718 mm
[VERDICT] the spread is the pipeline's, not the staging method's
```

| pair | Surface_0 | Surface_1 | Bl0 export | Bl1 export |
|---|---|---|---|---|
| A2 vs A3 (cp vs cp) | 0.226637 | 0.593066 | 0.718929 | **0.866718** |
| B2 vs B3 (symlink vs symlink) | 0.000000 | 0.234607 | **0.000000** | 0.218536 |
| A2 vs B2 (cp vs symlink) | 0.226637 | 0.424697 | 0.718929 | 0.161572 |

Two runs staged the **same way** differ by up to 0.867 mm on the exported lane — more than the
cp-vs-symlink difference (0.719 mm on Bl0, 0.162 mm on Bl1). The staging method contributes nothing
measurable; the spread is already there between two identical `cp` stages.

What actually varies, precisely:

- The **partition is the same every time**: all four runs print
  `face0 n=17678 interior_frac=0.9996 face1 n=14614 interior_frac=0.0000 satA=32285.0000 satB=7.0000`
  and `kept -> Surface_0=interior`.
- The **sheet row count moves by 1–3 dots out of 36,215 / 30,479** (`36215 / 36213` and
  `30479 / 30480 / 30482 / 30481` across the four runs), and `max_rev = 0.000000` for A2→A3 on
  `Surface_0` — every dot of A3 exists in A2 exactly, with a couple of extra dots in A2. Consistent
  with a handful of borderline dots near the split boundary landing on one face or the other; not
  verified in code, and not needed for this ticket's conclusion.
- `Surface_1` A2-vs-A3 `max_rev = 0.415594`: the reverse direction does move by up to 0.42 mm, so it
  is not a pure subset relation there.

So: **a byte-identical output cannot be a gate for the mesh stage on every piece.** Pot J 09 is
stable (0.000000 four ways in the gate), Pot H 02 is not, and the instability is upstream of anything
the staging script does.

### Gate item 2 — NO GEOMETRY IN THE STAGE TREE: PASS

| tree | files > 1 MiB | symlinks | `du -sh` | files |
|---|---|---|---|---|
| B (symlink), Pot J 09 | 0 | 2 | 10K | 3 (2 links + `inputs.md5`) |
| B (symlink), Pot H 02 | 0 | 2 | 10K | 3 |
| A (cp), Pot J 09 | 2 | 0 | 17M | 3 |
| A (cp), Pot H 02 | 2 | 0 | 17M | 3 |

Re-confirmed on the freshly staged trees of job 33749499: `0 / 2 / 10K` for both pieces.

### Gate item 3 — PROVENANCE: PASS (the first verdict was my checker's bug, not the script's)

The gate job's own GATE3 said FAIL. It was a **checker** defect: it resolved each row through
`inputs.md5`'s *realpath* column, so a symlink row could never read as a symlink, and the axis row —
a **copy** by contract — could never resolve into the corpus. Re-judged on freshly staged trees
(`out/gate3_fixed.txt`):

```
[GATE3FIX] Pot_J_Piece_09  mesh  symlink=True  in_corpus=YES md5=810009272d4f manifest=810009272d4f PASS
[GATE3FIX] Pot_J_Piece_09  cloud symlink=True  in_corpus=YES md5=c01b8a7c3ead manifest=c01b8a7c3ead points=1000037 PASS
[GATE3FIX] Pot_J_Piece_09  axis  symlink=False md5=5ef4dd54995c corpus_axis=5ef4dd54995c PASS
[GATE3FIX] Pot_H_Piece_02  mesh  symlink=True  in_corpus=YES md5=12882b986866 manifest=12882b986866 PASS
[GATE3FIX] Pot_H_Piece_02  cloud symlink=True  in_corpus=YES md5=a7edd8c828c0 manifest=a7edd8c828c0 points=1000161 PASS
[GATE3FIX] Pot_H_Piece_02  axis  symlink=False md5=f90e8c18f121 corpus_axis=f90e8c18f121 PASS
[GATE3FIX] rows=6 failed=0
[GATE3FIX] item3_provenance=PASS
```

The script's own summary line, quoted:

```
[STAGE-291] Pot_J_Piece_09: mesh Pot_J_Piece_09_Mesh_DS.obj md5=810009272d4ff937876b52fa5d781fcf | cloud md5=c01b8a7c3ead9f9e0998097657fe6075 points=1000037 | both from /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
[STAGE-291] pieces=1 pot=Pot_J symlinks=2 copied_files=1 copied_bytes=108 stage=…/gate3fix/J09
```

The corpus was read-only throughout: `corpus_before.md5` == `corpus_after.md5`, `CORPUS_UNCHANGED=YES`.

### Gate item 4 — SCORES (reported, not gated against older runs)

lane, arm, n, median mm, coverage ours→author, coverage author→ours, jumps, max step, length mm:

| lane | arm | n | median | cov o→a | cov a→o | jumps | max step | length |
|---|---|---|---|---|---|---|---|---|
| Pot_J 09 Bl0 | A (cp) | 79 | 1.079 | 70.89 | 75.68 | 0 | 4.999 | 145.40 |
| Pot_J 09 Bl0 | B (symlink) | 79 | 1.079 | 70.89 | 75.68 | 0 | 4.999 | 145.40 |
| Pot_J 09 Bl1 | A (cp) | 91 | 1.913 | 50.55 | 63.77 | 0 | 4.890 | 166.89 |
| Pot_J 09 Bl1 | B (symlink) | 91 | 1.913 | 50.55 | 63.77 | 0 | 4.890 | 166.89 |
| Pot_H 02 Bl0 | A (cp) | 152 | 0.504 | 100.00 | 100.00 | 0 | 4.000 | 275.80 |
| Pot_H 02 Bl0 | B (symlink) | 152 | 0.541 | 100.00 | 100.00 | 0 | 4.202 | 276.00 |
| Pot_H 02 Bl1 | A (cp) | 138 | 0.662 | 72.46 | 74.45 | 0 | 3.682 | 250.28 |
| Pot_H 02 Bl1 | B (symlink) | 138 | 0.681 | 72.46 | 74.45 | 0 | 3.388 | 249.99 |

Pot J 09's rows are identical column for column (and its exports are point-for-point identical).
Pot H 02 differs by ≤ 0.037 mm on the median and ≤ 0.40 mm on the length with coverage unchanged —
inside the spread two `cp` runs show on the same piece (0.867 mm on the export).

### What this establishes, and what it does not

- **Established:** staging by symlink into the frozen corpus is equivalent to copying, on the piece
  where the pipeline is deterministic, and indistinguishable from copying on the piece where it is
  not; the stage tree carries 10 KB instead of 17 MB per piece; the provenance record resolves into
  the corpus and matches the manifests 6/6; the script refuses to derive a cloud, refuses to
  overwrite a regular file, refuses a copying filesystem, and refuses a stage inside the corpus.
- **Not established by this gate as written:** the pre-registered rule (`max|dxyz| = 0.000000` or
  the ticket stops) cannot be met on every piece, **because the mesh stage is not reproducible on
  every piece**. The gate rule needs restating before it is applied to another piece: identity where
  the pipeline is deterministic (Pot J 09), and the cp-vs-cp spread as the yardstick where it is not
  (Pot H 02). That is a decision for the lead — the worker did not retune the acceptance after
  seeing the numbers, and reports the gate as failed.
- **Not touched:** pipeline code, defaults and thresholds are unchanged (`scripts/stage_piece.sh` and
  one sentence of `AGENTS.md` are the whole diff); no cloud was derived; no `build.sh --target nurbs`.

### Deviations

1. **Three jobs, not one.** 33748798 the gate; 33748866 the four-run determinism probe (needed to
   attribute the Pot H 02 difference); 33749499 the corrected GATE3. All in the one run directory.
2. **The gate's own GATE3 verdict was wrong** (checker bug described above) and was re-judged rather
   than left standing — the re-judgement is a new job, not an edit of the old output.
3. **`submit3.sbatch` was submitted twice**: the first attempt called the script with `Piece_09`
   instead of the full stem `Pot_J_Piece_09`, so it refused both pieces and produced no tree; no
   geometry, no result was affected.
4. **The corpus `Mesh/` layout in the ticket text is wrong** (flat, not per-pot) and the manifests sit
   in `Point/`; the script handles both layouts and both manifest locations.
5. **The worktree was detached**; turned into branch `291-symlink-staging` and pushed (`-u`). This is
   a deviation from how the ticket was handed over, not from its contract.
6. **The exported lane files from the gate job are still in `out/`** (8 files, `A_*`/`B_*` `.pcd`,
   ~50 KB). By the new rule they are geometry and must be deleted when the ticket closes.

### Jobs, run directory, artefacts

- runid `20261024-2351_3888318_p291-gate`, commit `3888318`, tag `p291-gate`;
  index row `20261024-2351_3888318_p291-gate	33748798	3888318	p291-gate		` (verdict and
  human_note empty, for the lead). Follow-up job ids are recorded in the run's `run.json`.
- Binaries reused from p290 (no build): edge `a28d10afab2b50bbe750d599ee2b7214`
  (md5-identical to the shipped 287/288/289 binary), mesh `0171f471d0558d2676df7c4b113c1e9d`.
- Key outputs: `out/cmp291.txt` (gate), `out/cmp2.txt` (determinism probe), `out/gate3_fixed.txt`,
  `out/gate3_census.txt`, `out/classify_lines.txt`, `out/corpus_before.md5` / `corpus_after.md5`,
  `out/GEOMETRY_DELETED{,2,3}.txt`.
- Local copies of the scripts: `C:/PR/worktrees/sfs/291/.scratch/pota-repro/291/`
  (`submit.sbatch` 4d152aad…, `cmp291.py` 4c47d5e9…, `submit2.sbatch` 92612fd8…, `cmp2.py`
  565616eb…, `gate3fix2.py` 71a20951…, `submit3.sbatch` eeefb430…).

### Acceptance, item by item

| # | item | verdict | the number that decides it |
|---|---|---|---|
| 1 | identity A vs B, `max abs(dxyz)` = 0.000000 | **FAIL as pre-registered** — PASS on Pot J 09, FAIL on Pot H 02 (0.716773 / 0.418649), and the cause is cp-vs-cp spread 0.866718 > cp-vs-symlink 0.718929 | 0.866718 |
| 2 | no geometry in the symlink tree | PASS | 0 files > 1 MiB, 2 symlinks, 10K vs 17M |
| 3 | provenance resolves into the corpus and matches the manifests | PASS | 6 rows, 0 failed |
| 4 | scores reported for both arms | PASS | table above; Pot J 09 identical, Pot H 02 ≤ 0.037 mm apart |

Also satisfied: no pipeline/default/threshold change; no cloud derived; no `--target nurbs`; stage
trees deleted by the job (`STAGE_DIRS_REMAINING=0`); ticket written in the main clone and left
uncommitted; run directory and index row in place with `verdict`/`human_note` empty.

---

## Verdict (lead, 2026-10-25) — accepted; the identity rule is restated

1. **The change is right and is shipped.** `scripts/stage_piece.sh` (167 lines, md5
   `585955252cc84fe1a49e6dac8cef892e`, merged to main as `acc9943`) links the mesh and the cloud into
   the frozen corpus, copies only the 7 KB axis, and records every resolved path, md5 and point count
   in the stage's `inputs.md5`. Its guards are the ones that matter: it refuses to replace a regular
   file with a symlink (`:66`, `:131`), it refuses to derive a missing cloud (`:78` — the sampler takes
   no seed, so a derived cloud is not reproducible), and it refuses a stage directory inside the corpus.
2. **Items 2, 3 and 4 pass as written**: 10 K and 3 files against 17 M and real copies; provenance
   6 rows, 0 failed, after the checker's own bug was fixed; scores reported for both arms.
3. **Item 1 fails as written, and the failure is the pipeline, not staging.** Pot J 09 is IDENTICAL on
   both lanes (79/79, 91/91, `max|dxyz| 0.000000`). Pot H 02 differs — Bl0 0.716773 mm, Bl1 0.418649 mm
   — but two COPY-staged runs of the same bytes differ by MORE (0.866718 mm) than copy-versus-symlink
   (0.718929 mm Bl0, 0.161974 mm Bl1), the partition is identical in all four runs
   (`face0 n=17678 interior_frac=0.9996 face1 n=14614 … satA=32285 satB=7` → `kept -> Surface_0=interior`),
   and the surface differs by 1-3 points of about 36,215 with `max_rev = 0.000000` on the repeat pair.
   The staged inputs are byte-identical by construction (item 3 proves the links resolve into the
   corpus with the manifest's md5s), so no path exists by which staging changes what the stage reads.
   The cause is the unseeded `std::random_device` at `mesh_processing_headless.cpp:1526-1527` (ticket 271).
4. **The rule is restated, and this replaces the pre-registered item 1.** A lane is an identity gate
   only where that piece's mesh stage has been shown deterministic in the same session (Pot J 09:
   0.000000 four ways). Elsewhere the yardstick is that piece's own copy-versus-copy spread measured in
   the same session, so 0.719 ≤ 0.867 passes. On every piece the primary claim is byte-identical staged
   inputs, which is checkable and does not depend on the code being deterministic. The worker did not
   retune the acceptance after seeing numbers, which is the right behaviour; the restatement is the
   lead's decision and is written into `AGENTS.md` so it is not re-litigated per ticket.
5. **Cost, measured**: 108 bytes copied per piece against 1.3 MB (mesh) to 90 MB (cloud). A 148-piece
   corpus stages about 16 KB instead of 4-6 GB.
6. **What this does not establish**: anything about the method — a staging change cannot move a score,
   and it did not. It also does not make Pot H 02 an identity lane: a re-run there legitimately moves
   the exported line by up to 0.87 mm, and no future verdict may quote that piece's numbers to better
   than that band.
7. **Status**: done. The eight lane exports (`out/A_*.pcd`, `out/B_*.pcd`) are deleted with the ticket
   under the conservator's geometry rule; `run.json`, `logs/`, `out/*.txt`, the scorer and the pictures stay.
