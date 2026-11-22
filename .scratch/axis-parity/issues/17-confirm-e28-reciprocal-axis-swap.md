# 17: Does the E28 axis file account for Pot E's three lost joins?

**What to build:** Swap only the full E28 axis file in both directions on frozen Pot E, using one byte-identical assembler for every launch. Report whether 13–28, 27–28 and 28–31 recover and disappear with the swap.

**Answers:** E1
**Blocked by:** None. Use saved Ticket 03 inputs.
**Status:** in-progress
**Working in:** DSH: SfS++ axis-parity Ticket 17 (2026-11-23)
**Branch:** 17-confirm-e28-reciprocal-axis-swap, in /c/PR/worktrees/sfs/17
**Worker:** DeepSeek
**Budget:** medium 5
**Hand-over:** DeepSeek, one-shot diagnostic. Return worker self-compliance and a separate read-only review.

## Frozen inputs and the four arms

On Spartan, let `BASE=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9`, `T03E=${BASE}_t03-potE` and `SHIP=${BASE}_t03-ship`. Use `FIXED="$T03E/trees/E_K3R1/E/MM"` for all non-axis data. The original own input scored 59/62 twice and the released-axis control 62/62 twice. All three own failures touch E28. The released-axis control motivates the test and is distinct from the author-wall selector control in this ticket.

Construct four small axis directories from `$SHIP/out/axes03_own` and `$SHIP/out/axes03_tri`. Copy exactly the 31 source axis files named in `$FIXED/Axes`; preserve file bytes, row order, line count and signs (E28 own one line, author-wall two). Require the whole own set to match the frozen staged axes byte for byte. `OWN` uses axes03_own, `AUTHOR` uses axes03_tri. `FORWARD` is OWN with only `Pot_E_Piece_28_Axis.xyz` copied from AUTHOR. `REVERSE` is AUTHOR with only that file copied from OWN. No released or GT axis may enter any arm. Publish relative path/file SHA-256 for every input file, including the fixed non-axis inputs, separately from the aggregate manifest digest. Check inputs before and after execution.

## Exact build and bind recipe

Use Ticket 13's resolved section **Required build and launch recipe (revision 2)** verbatim for the guard, CMake flags, compiler flags and link substitution, with only these prescribed substitutions: `T12/work/patch_guard67.py` and `T12/work/mk_inc.py` become `$T03E/work/patch_guard67.py` and `$T03E/work/mk_inc.py`; `inc_J` becomes `inc_E`; last argument to mk_inc is `E`; `shim_t13`, `link_t13` and `Hierarchy-T13` become `shim_t17`, `link_t17` and `Hierarchy-T17`. Keep SIF, shim/guard MD5 checks, release flags and floor 50. Record the hash of the SIF and scorer. Compile only once, hash the executed file before every launch, and abort before scoring on any mismatch. Save the compiler and link logs. `git` provenance must name the pinned assembler/shim from the frozen recipe. Do all builds and runs on compute nodes.

For each arm set `AXIS_DIR="$RUN/axes/$ARM"` and `RESULT="$RUN/out/${ARM}_${REP}"`. Create the empty mount layout once (`mkdir -p "$RUN/mount"/{Axes,Breaklines,Surfaces,Mesh,'Ground Truth',Result}`); create each result directory with `mkdir "$RESULT"` so accidental reuse fails. Do not copy the non-axis tree. Bind the same four fixed source directories read-only and each arm's axes and result at the same container paths:

```bash
for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)' || true); do unset "$v"; done
"$APT" exec --writable-tmpfs --bind "$MAIN:/workspace" --bind "$WORK:/panel:ro" \
  --bind "$RUN/mount:/Dataset/SfS_pp:ro" \
  --bind "$FIXED/Breaklines:/Dataset/SfS_pp/Breaklines:ro" \
  --bind "$FIXED/Surfaces:/Dataset/SfS_pp/Surfaces:ro" \
  --bind "$FIXED/Mesh:/Dataset/SfS_pp/Mesh:ro" \
  --bind "$FIXED/Ground Truth:/Dataset/SfS_pp/Ground Truth:ro" \
  --bind "$AXIS_DIR:/Dataset/SfS_pp/Axes:ro" \
  --bind "$RESULT:/Dataset/SfS_pp/Result" --env OMP_NUM_THREADS=8 "$SIF" bash -euc '
    sha256sum -c /panel/logs/executable.sha256
    exec /panel/build/Hierarchy-T17 31
  ' > "$RUN/logs/run_${ARM}_${REP}.log" 2>&1
```

Use fixed scorer `"$PY" "$T03E/work/score305.py" "$RESULT" "$GT" E "$PIECES" "$RUN/score/${ARM}_${REP}.tsv" "${ARM}_${REP}"`, with `GT="$FIXED/Ground Truth"` and `PIECES="$T03E/trees/E_K3R1/arm_pieces_E.tsv"`. Record raw output and the scorer's 20.05°/50 mm gates. Never use an absolute pose/shard tally to adjudicate a seam.

## Runs and decision

Two interleaved repeats in one run directory, with fixed threads and settings: repeat 1 OWN, FORWARD, AUTHOR, REVERSE; repeat 2 AUTHOR, REVERSE, OWN, FORWARD. Separate output roots. Record uncontrolled randomness state honestly. Report all 62 reference seams per arm using the pinned scorer thresholds and flag 13-28, 27-28 and 28-31 separately. The strong single-file contrast is met if in both repeats all three fail on OWN, pass on FORWARD and AUTHOR, and fail on REVERSE, with no other join lost in the forward comparison. Otherwise report the exact paired changes and whether the control reproduced the target seam contrast. The test also has a valid negative outcome and must never backfill a missing arm from an older run.

Render each of the three joins at identical camera, scale and colours for the four arms in repeat 1, plus any arm in repeat 2 where the seam verdict changes. Apply the actual saved native-to-assembled transforms, using the Ticket 13 corrected renderer's transform convention and Pot E fixed walls. Set the locked frame from the matching reference pair and use a mm scale bar. Mark missing or out-of-frame sherds explicitly, with a paired zoom/overview if needed. Save existing rendered screenshots and metric tables, not geometry, to the laptop.

## Acceptance and return

- `replay.tsv`: arm (OWN/FORWARD/AUTHOR/REVERSE), repeat (1/2), executable_sha256, joins (integer numerator), sherds (assembler count). `seams.tsv`: arm, repeat, seam (lower-ID-first with hyphen), angle_deg, translation_mm, pass (0/1). Include all 62 rows per cell; for unscorable/missing poses use blank angles and pass 0 with a reason field or notes.
- `inputs.tsv`: arm, repeat, path (relative to dataset root, slash separators), before_sha256, after_sha256. Include all loaded inputs per cell, one row per file, with 31 axis paths rooted in Axes/. `donor.tsv`: source (own/author), path, sha256, lines for the two E28 upstream files. `renders.tsv`: arm, repeat, seam, camera, path (relative evidence path). Include `jobs.tsv` (job_id, run_id, state, exit_code, polled, indexed; use sacct State/ExitCode and 1/0 flags) and matching nonempty `corpus_before.md5` / `corpus_after.md5`. Keep exact profiling provenance, run code, assembly geometry and job logs on Spartan. Fetch small records into `C:/PR/artifacts/axis-parity-17/`.
- Run existing scorer with the exact arguments above on compute nodes as the experiment's check. Poll each Slurm job and record terminal accounting. In the ticket provide a factual requirement / status / file:line self-compliance table and exactly one End state. Have a separate read-only DeepSeek reviewer return its own table and actually inspect seam renders. Leave only the ticket write-back modified locally. No production edits, commit, merge, close or research verdict.

## Comments

One-shot diagnostic. [SfS++ §IV-C.1](https://arxiv.org/html/2502.13986v1#S4.SS3.SSS1) describes the axis-based matching stage. Ticket 13 establishes the reciprocal-swap and single-executable method on J01.
