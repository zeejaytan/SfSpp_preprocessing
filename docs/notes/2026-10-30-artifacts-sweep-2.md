# 2026-10-30 — second `artifacts/` sweep (housekeeping check)

**Why.** The conservator's standing ask that tickets close clean and the workspace stay
clean. `python C:/PR/scripts/check_artifacts.py .` reported **needs a sweep**: 7,895 files,
417.0 MB (ceiling 300 MB), 140 uncited geometry files 95.5 MB (ceiling 50 MB), one fetched
tarball over 1 MB. The 2026-10-24 sweep
(`docs/notes/2026-10-24-artifacts-sweep.md`) set the classes; this pass applies them to
what accumulated since.

## Deleted, with the guard each passed

| file | bytes | class | guard |
|---|---|---|---|
| `artifacts/pcdcheck/C01_ours.pcd` | 49,781,270 | uncited geometry | no tracked file cites it; no `.scratch/` ticket cites `pcdcheck/C01` either (grepped); mtime 2026-10-24 23:30 (>24 h); re-derivable on Spartan (`cc_mesh_to_pcd.sh` on `Pot_C_Piece_01_Mesh_DS.obj`) |
| `artifacts/pcdcheck/C01_release.pcd` | 28,000,957 | uncited geometry | same guards; the released cloud itself still lives in the frozen corpus `Point/` tree |
| `artifacts/pota273/C01_bag.pcd` | 30,867 | uncited geometry | same guards; mtime 2026-10-24 04:02 |
| `artifacts/pota293/png.tgz` | 8,537,397 | spent tarball | unpacked beside it (`artifacts/pota293/png/` exists and was read); "delete once unpacked and read" |

Total dropped: **86,350,491 B (82.3 MB)**. The numbers those files backed are already
quoted where they matter (Pot C 01 derived-vs-released comparison in `AGENTS.md`, "Corpus
caveats"; ticket 293's verdicts in `.scratch/pota-repro/issues/293-*`).

## What was deliberately NOT touched

- `artifacts/visual-qa/` and `artifacts/mesh_for_viewing/` — the conservator's eye,
  excluded whole per the 2026-10-24 precedent (≈19 MB of the uncited-geometry count).
- Every cited path (633 cited paths in tracked files) and anything written <24 h.

## After, and the honest remainder

Gate after the sweep: **≈334.7 MB total — still over the 300 MB ceiling; uncited geometry
≈21 MB (under its 50 MB ceiling); zero tarballs.** The overage is the evidence layer the
2026-10-24 sweep chose to keep (overlay PNGs, gate tables, logs from closed `pota-*`
tickets — that sweep ended at 311 MB). Getting under 300 MB now means a decision the
consservator has not made: archive old cited evidence to the Spartan attic, or move the
ceiling. Recorded here so the next sweep starts from a measured state, not a mystery.
