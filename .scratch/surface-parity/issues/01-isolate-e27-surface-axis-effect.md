# 01: Isolate E27’s surface-to-axis effect at join 27–28

**What to build:** Show where our E27 and E28 surfaces differ from the authors’ surfaces, and test whether the resulting difference in E27’s axis file is enough to remove or recover join 27–28.

**Answers:** E2

**Blocked by:** none. Uses the saved axis-parity Ticket 19 assembly inputs and Ticket 03 surface and axis evidence.

**Status:** ready-for-agent

**Worker:** unassigned

**Budget:** medium 5

**Hand-over:** DeepSeek V4.1 Flash via DSH Baton. Lead acceptance lives outside the ticket worktree.

[Spec](../spec.md)

## Frozen inputs and files

Edit only this ticket and new experiment files under `.scratch/surface-parity/t01/` in the assigned worktree. Use `surface01.py` for measurement and rendering, `stage01.py` for axis-file staging and hash checks, `cell01.sbatch` for assembly and `report01.py` for summarising saved outputs. Store run outputs on Spartan and fetch only tables, logs and PNGs to the project’s ignored artifacts. Preserve corpus and application source. Follow the workspace run-index and Slurm polling rules. The lead fills the verdict.

On Spartan set `P=/data/gpfs/projects/punim2657`, `T19=$P/SfSpp/runs/20261124-0443_21446b8_t19-decisions`, and `SHIP=$P/SfSpp/runs/20261121-1319_2e951d9_t03-ship`. Load `Pot_E_Piece_27` and `Pot_E_Piece_28` on each surface source via `SHIP/work/t03_lib.py:walls(stem, surfaces)` with `surfaces=own` and `surfaces=authors`. The own source resolves to the Ticket 305 Pot E `.S0` and `.S1` files. The authors’ source resolves through the archived loader to the released surfaces. Use the archived TORA Python and `PYTHONPATH="$SHIP/work/impl_t03:$SHIP/work"`. Log the actual four file paths per sherd, hashes and load dimensions. Do not use the assembler’s mounted walls in place of the estimator’s wall inputs.

## 1. Compare the surfaces

- Work in native coordinates in millimetres. Use the frozen mesh and released pose as independent landmarks for both clouds. Show both faces on the same mesh from the same two views at a 20 mm scale. Check native-frame alignment without ICP or any estimated registration. Record the signed orientation of corresponding normals. Keep same-face and crossed-face comparisons separate. If correspondence or frame is indeterminate, report that and do not attribute any feature difference.
- For each sherd, face and direction between sources, use a same-face nearest-neighbour query. At 1 mm and 2 mm report counts and fractions paired and unpaired. Report point-to-point p50/p95 in mm and within-cloud non-self nearest-neighbour p50/p95 in mm. Keep exact duplicate counts separately and measure spacing on distinct XYZ. For matches within 1 mm report signed normal-angle p50/p95 in degrees, the fraction above 90°, and the count of invalid normals. A zero valid denominator gives a blank metric with a zero count.
- To avoid a dense patch concealing sparse coverage, also report occupied 2 mm XYZ cells on the shared fixed grid `floor(xyz_mm / 2)` per face, with own-only, author-only and shared counts. Use the point correspondence overlay to distinguish a sampling grid effect from a real gap. Render shared and unmatched points separately with fixed colours, and identify any differences near the fixed 27–28 fracture line. These are observations and may remain correlated.
- Compare every saved E27 and E28 candidate in `T19/axes/OWN` and `T19/axes/AUTHOR` and the released `Axes` separately. Row layout is position then direction. Report signed and unsigned angles, row order, and the distance in mm from the pose-derived reference axis anchor to each line. Use reference axes only in the readout. Preserve every packaged axis byte in the assembly trial.

## 2. Test E27 with all other inputs fixed

Stage four axis directories of 31 sherd files. Use exact source bytes from `T19/axes/{OWN,AUTHOR}`. The two hybrids change only `Pot_E_Piece_27_Axis.xyz`. In the own background use the authors’-surface E27 file, and in the authors’-surface background use our E27 file. Call the hybrids `OWN_E27_AUTHOR` and `AUTHOR_E27_OWN`. Preserve E28’s bytes relative to the corresponding background. If the E27 files are identical, report the hashes and do not submit redundant swap arms.

Use the archived `$T19/work/t19/build/Hierarchy-T19` with SHA-256 `0ba6d10fa6885a67a92a92bb37ec7c138f25f32622368bfcafb5bfae3fa637c9`. There is no build step. Fork the archived `$T19/work/t19/cell19.sbatch` into `cell01.sbatch`. Set `WORK="$T19/work/t19"`, `WANT_SHA` to the hash above, and `RUN` to the new run directory. Use the original Ticket 03 Pot E fixed tree `$P/SfSpp/runs/20261121-1319_2e951d9_t03-potE/trees/E_K3R1/E/MM` for `DATA` and its `Ground Truth` for `GT` in all cells. Bind `$RUN/axes/$ARM` read-only as the sole input that varies. Keep the archived Apptainer executable, SIF, `/panel` bind, input binds, environment, container hash check, `exec /panel/build/Hierarchy-T19 31` and scorer invocation. Set `T18_TRACE=/Dataset/SfS_pp/Result/t18_raw.jsonl` and `T19_TRACE=/Dataset/SfS_pp/Result/t19_decisions.jsonl`. Retain fresh writable Result and logs per cell. Change archived error exits to nonzero for duplicate result directories, input hash failures, missing poses, container failures and scorer failures. No scored rows for unusable cells. Use exact commands below from the prepared run directory and poll every returned ID:

```bash
for arm in OWN OWN_E27_AUTHOR AUTHOR AUTHOR_E27_OWN; do sbatch --parsable "$RUN/submit.sbatch" "$arm" 1; done
# Poll wave 1 to terminal states before submitting wave 2.
for arm in AUTHOR_E27_OWN AUTHOR OWN_E27_AUTHOR OWN; do sbatch --parsable "$RUN/submit.sbatch" "$arm" 2; done
```

Verify a stable positive AUTHOR control (62/62 twice) and that OWN loses 27–28 twice before interpreting the hybrids. Keep the released Ticket 19 62/62 twice as a benchmark record. For each cell read 27–28’s direct-query, first emitted interval and pair-fit events from the raw trace, and score the exported pose with the pinned scorer. Include the other two E28 joins as secondary rows and tally all 62 outcomes to identify collateral changes. Report no interval as a count of zero and leave its event ID blank. A final scoring result can be valid when a direct interval never forms. If a control fails, retain all evidence and label the experiment inconclusive. Do not report graph-pruning attribution.

## Acceptance

- [ ] Both walls on E27 and E28 have input hashes, matched/unmatched and valid/invalid denominators, same-frame surface measurements, candidate comparisons and inspected locked renders.
- [ ] Each executed cell records terminal Slurm State/ExitCode, a matching host and container executable hash, complete before/after input manifests, and its scorer status. Reciprocals differ from their parent at E27 alone. Failed controls or identical donor bytes are visible, and neither can be presented as a successful isolation.
- [ ] `replay.tsv` records arm, repeat, executable hash, execution status, scored joins and sherds. `seams.tsv` records the 62 distinct reference joins per scored cell with relative rotation error in degrees, offset in millimetres and scorer flag. `matching.tsv` gives query, interval and fit counts and first event IDs for the three target joins. `surfaces.tsv`, `axes.tsv`, `inputs.tsv`, `jobs.tsv`, `renders.tsv` and the raw traces carry the provenance above. Render scored 27–28 poses from each repeat against the fixed reference with a locked camera and a scale bar, including missing or off-frame cases. Judge the score using the pinned scorer, with the image for physical inspection.
- [ ] Write a per-requirement self-compliance table with met/not met and file:line evidence in this ticket. Obtain a separate read-only DeepSeek review with its own compliance table, including inspection of the surface and join renders. End with one end state from the delegation guide. Report the facts and the budget used. Leave interpretation, commits and closure to the lead.

**Worker checks:** `python -m py_compile .scratch/surface-parity/t01/surface01.py .scratch/surface-parity/t01/stage01.py .scratch/surface-parity/t01/report01.py`; `bash -n .scratch/surface-parity/t01/cell01.sbatch`; from the workspace root `python scripts/check_intent_links.py`. Run research measurements on Spartan compute nodes.

## Comments
