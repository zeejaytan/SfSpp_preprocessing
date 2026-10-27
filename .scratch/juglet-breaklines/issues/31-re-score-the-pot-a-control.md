# 31 — Re-score the Pot A control on a compute node

**Status:** ready-for-agent
**Answers:** none (a verification debt, not a research question)
**Blocked by:** none
**Blocks:** quoting the 15/15 Pot A control anywhere

## Why this exists

Ticket 07's stage-1 job (33834939, run `20261027-0055_d8af9d2_p07-juglet-stage1`) produced the
Juglet surfaces and, beside them, a **Pot A control**: the same pipeline, the same batch, with
the authors' breaklines taken straight from the corpus. The probe that scored it
(`gate_probe_b0_p07.py`, one added bundle entry over the unmodified
`gate_probe_b0.py`) was then run **on the laptop**, against the fetched bundle
`out/stage1_out.tgz`, md5 `0d823524f974d2ac8fe6b0f3428ed007`, 11 654 126 B.

It reported `STRICT pass rate at GT (_0-only): 15/15`. The number is probably right — but it
was measured on the laptop, and the workspace rule is that heavy work and every re-score run on
compute nodes. Until that is done, nobody can quote the 15/15 without the caveat, and it is the
control every Juglet claim is read against.

The bundle is still on the cluster with the same md5, so this is a port, not a re-run.

## What to build

1. **A numpy-only port of the probe.** The original imports `scipy.spatial.cKDTree`; the cluster's
   `python3` is 3.11 with **numpy 2.4.6 and no scipy**. Replace the nearest-neighbour query with a
   chunked brute-force search (chunk the query points so peak memory stays bounded; the clouds
   are thousands of points, not millions). **Change nothing else**: same bundle spec, same two
   gates (2.0 mm / 0.85 and 20° / 0.7), same `_0`-only restriction, same "max inlier count over
   segment pairs", same PASS rule (inliers at 2.0 mm / 0.85 > 0).
2. **An equivalence test against the laptop's own output**, which is the point of the port. The
   laptop's `gate_probe_p07.out` holds `p07 mates: 15 (_0-only)`, fifteen per-pair lines with
   raw and absolute inlier counts, and the pass line. The port must reproduce **the same fifteen
   pass/fail verdicts and the same inlier counts**, pair by pair. If any pair differs, that is a
   finding to report with both numbers — not something to tune away.
3. **The scoring job**, on a compute node: extract `out/stage1_out.tgz` into `$TMPDIR`, rename
   `geom/Pot_A_Piece_*.Bl0.pcd` to `<piece>_Breakline_0.pcd` (a copy, as the README's step 2
   did — the bytes read are then the bytes in `out/geom`), point the port's bundle entry at those
   files and at the corpus ground truth
   (`/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Ground Truth/Pot_A_Piece_%d_T.txt`
   and `Pot_A_simple_graph.txt`), and run it.

Both the laptop's `gate_probe_p07.out` and the port's output go side by side in the run
directory, so the comparison is readable by someone who was not here.

## What is being verified, in plain terms

The authors' own measurements say 15 of Pot A's 15 touching edges are found by our breaklines at
their correct relative positions. "At their correct relative positions" is a rigid-motion test:
take two pieces' breakline curves, put them where the answer key says they go, and count how many
of one curve's points have a partner within 2 mm that also agrees in direction within about 31°
(cos 0.85). The number 15/15 has been quoted repeatedly; this ticket makes it quotable without a
laptop asterisk.

## Acceptance criteria

1. The port exists under `.scratch/juglet-breaklines/stage31/` with a `--selftest` or equivalent
   that shows the brute-force nearest-neighbour agrees with a small direct computation.
2. The port's output reproduces the laptop's fifteen per-pair verdicts and inlier counts exactly,
   or the differences are listed pair by pair with both numbers.
3. The job ran on a compute node (`sacct` state and node name), one run directory, one
   `index.tsv` row with `verdict` and `human_note` EMPTY.
4. `out/` holds both outputs and a short `COMPARE.md` stating the equality or the differences.
5. The corpus and the canonical checkout are unchanged: md5 listing before and after, compared
   and quoted. `/opt/sfs-pristine` recorded as ABSENT if it is (do not create it).
6. Geometry deleted with a counted record (manifest written before the delete); the two outputs,
   the tables and the logs are kept.
7. Nothing outside `.scratch/juglet-breaklines/stage31/` changed — no C++, no pipeline image, no
   corpus.

## Evidence to return

1. Job id, `sacct` state, node name, wall time.
2. The port's full output, pasted.
3. The comparison: fifteen rows, laptop count and port count side by side.
4. The self-test line(s).
5. Corpus md5 before/after paths and the equality statement.
6. The deletion manifest path and its totals.
7. The pushed branch sha, and anything not done with the command that stopped it.

## Rules for the worker

- Work only in `C:/PR/worktrees/sfs/31`; write outside it only to the run directory and the
  run index.
- Compute nodes only. **At most three jobs.**
- Check every submitted script for CRLF before submitting.
- **Report evidence, not verdicts.** Whether the control holds is the lead's call.
- If the port disagrees with the laptop, that is the most valuable thing you can return. Do not
  adjust the port to agree.

## What this cannot settle

- It re-scores one bundle on one pot. It does not re-run the pipeline, so it says nothing about
  whether today's code still produces those breaklines.
- It does not touch the Juglet, and it does not make the end-to-end run's stage 2 any less paused.
- A port that agrees exactly is evidence that the port is faithful; it is not evidence that the
  original probe measured the right thing.
