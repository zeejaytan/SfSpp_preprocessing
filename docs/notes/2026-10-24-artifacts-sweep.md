# 2026-10-24 — the SfS++ `artifacts/` sweep

**Why.** The conservator asked whether the folder could be cleaned up, and for a rule
saying where each kind of output belongs. The answer to the first was yes: it had become a
second data store. The answer to the second is now
`../docs/agents/workspace-hygiene.md`, "Where each kind of output goes", with
`scripts/check_artifacts.py` as the gate.

## What it held, measured

`C:/PR/SfSpp_preprocessing/artifacts` — **870 MB, 229 entries, 12,903 files**, fetched
per ticket by `scripts/remote/fetch_artifacts.sh` and never swept. The composition was not
a mystery once measured: 90 `.obj` files held 427 MB and 35 `.ply` held 163 MB — mesh and
point-cloud data, which by rule is Spartan's, not the laptop's. The evidence layer that
someone actually cites (536 `.png` overlays, gate tables, logs, ticket scripts) was 95 MB.

## What was deleted, and the guards

```
kind                        paths     by file size
point clouds .pcd            5055           ~72 MB*      (re-fetchable from the run dir)
surfaces .xyz                 239           ~57 MB
meshes .obj                    93          ~427 MB
dense arrays .npy              19           2.4 MB
meshes .ply                     3           ~2 MB
fetch bundles .tgz > 1 MB       2            5.8 MB
pot_a_mesh_all_tmp/           all          ~92 MB       (a temp copy of Pot A meshes)
                                        ---------
total                        5411         637.9 MB
```

Guards, in the order they ran:

1. **Cited paths were read first.** `git ls-files` over the repo, every `artifacts/...`
   path named by a tracked file — 319 exact file paths, 591 path tokens. A file named in a
   ticket, a note or an `intent/` line was exempt from the start.
2. **Anything written in the last 24 hours was exempt** (`-mtime +0`), so a fetch in
   progress could not be caught.
3. **`artifacts/visual-qa/` and `artifacts/mesh_for_viewing/` were excluded whole** — the
   viewer staging area is the conservator's eye, and pruning it is their decision, not a
   sweep's.
4. Two assertions were run before the `rm`, both required to print 0: nothing under the two
   staged areas, and nothing in the cited set.

Per-path record: `.scratch/pota-repro/artifacts-cleanup-20261024.manifest.tsv.gz`
(5411 rows, path and bytes, 33 KB).

**Result: `du` 870 MB -> 311 MB**, 225 entries. What remains is the evidence layer: 536
overlays, the 28 cited geometry files, the gate tables, the logs, the 163 MB of staged
viewer pairs, and the 14 MB `mesh_for_viewing`.

## The finding the gate then made

`python scripts/check_artifacts.py C:/PR/SfSpp_preprocessing` exits 1: **172.9 MB of
geometry no tracked file cites, 88 files** — and every one of the largest is in
`visual-qa/`, stored **twice**: `pota209_P01/pota209_P01_left.ply` beside
`pota209_P01/preview_left.ply`, 8.5 MB each, same pair repeated for eight pieces. The
staging helper writes a copy of the mesh it already has. That is the next 86 MB, and it is
left in place deliberately: only the conservator can say which staged pairs are still being
looked at.

## Lesson, paid for inside this sweep

The deletion list was written to `/tmp` and read back — and `/tmp` was **empty on the
next shell call**, so the per-path record nearly vanished with the files it described. It
survived only because that one shell happened to keep its temp directory. Rule 13's order —
write the record, then delete — is not bookkeeping: the manifest must be written to the
repo, not to a temp directory, *before* the `rm`, and this sweep did it in the wrong order.
