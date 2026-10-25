# 277 — The mesh stage must not silently keep size order when it has no axis file

Answers: E1
Status: done (accepted: exit 42 on four no-axis paths, normal run inside its own draw spread)
Working in: chat on Thinkbook16 (2026-10-25)
Branch: 277-axis-file-must-shout, in /c/PR/worktrees/sfs/277
Needs-eye: no

## Why

classifyAndOrderPaper234 (mesh_processing_headless.cpp:1990) decides which of the two big
clusters is the interior surface by casting rays from each point along its normal to the
symmetry axis read from SFS_AXIS_FILE (:1994 onwards).

When SFS_AXIS_FILE is unset the function prints
`[PAPER-234] classify: no SFS_AXIS_FILE, keep size order` and leaves clusters in size
order. No error, no non-zero exit. The run continues and produces a full set of surfaces
and breaklines.

The labels are then wrong in a way nothing downstream can see: Surface_0 is whichever
cluster happens to be larger, so **Bl0 and Bl1 stop corresponding to the author's Bl0 and
Bl1**. A 2026-10-24 run hit this (ticket 275 Phase 0): it scored med 5.8 mm / cov 0.00 and
looked exactly like a method failure until the axis file was restored.

This is the worst shape of defect we have: a wrong answer that reads as a real result.

## What to do

Make the missing axis file loud, in this order of preference:

1. Exit non-zero with a message naming the variable — preferred, since every pipeline run
   in this repo sets it.
2. If some callers legitimately run without it (check first; record who and why), keep the
   fallback but print a banner that cannot be missed and write a marker file next to the
   outputs so a later reader can see which runs were mislabelled.

Do not change the classification itself, and do not invent a default axis.

## Acceptance

- A run with SFS_AXIS_FILE unset either fails non-zero with the variable named, or writes
  the marker and prints the banner.
- The six guard lanes of ticket 271 reproduce bit-identically with the variable set.
- The log line quoted above no longer appears without an accompanying loud warning.

## Evidence to report

- the new message text and where it is emitted
- the guard-lane reproduction table
- what callers were found that do not set the variable, and their justification

## Result (2026-10-26, job 33781618, run `20261025-2356_66d4ad9_p277-axis-loud`)

Status is left `in-progress`: the verdict and the index row are the lead's to write.

### What changed, and why it is an exit and not a banner

Caller audit first, as the ticket asked. **Every live recipe sets `SFS_AXIS_FILE`**: the 294
recipe (`.scratch/pota-repro/294/submit294.sbatch:81`) and the 276, 289, 290 (four submits),
291, 292 and 293 recipes. 294 already fails its own job when the classify line is missing
(`FATAL CLASSIFY_MISSING`, :83-85). The callers that do *not* set it are all legacy corpus
generators or one-shot smoke tests that never read labelled surfaces:

| caller | how it invokes the stage | why it is not a reason to keep the silent path |
|---|---|---|
| `slurm_complete_preprocessing.sbatch:88` | `./build/mesh_processing_complete POT_ID PIECE` | legacy corpus generator; does not consume Surface_0/1 or Bl0/1 |
| `run_tray_pipeline_working.sbatch:57` | `apptainer exec ... ./build/mesh_processing_complete A $p` | same |
| `test_all_pot_a.sh:56` | `./mesh_processing_complete Dataset/Mesh/Pot_A/... A piece_id` | same |
| `test_downsampling.sbatch:33`, `test_fixed_headless_preprocessing.sbatch:52` | `./build/MeshPreprocessingHeadless Dataset/Pot_A.obj A 1` | smoke tests on Pot A, no downstream reader |
| `run_nurbs_*.sbatch` and `original_nurbs_preprocessing/*` | the pre-247 duplicate binary under `original_nurbs_preprocessing/build` | a different tree, not this file |

None of them sets `SFS_PAPER_CHAIN=0` either, so none of them is deliberately running the
old behaviour. Preference 1 therefore stands: exit, do not warn.

### The change

`mesh_processing_headless.cpp`, one file, 18 insertions and 4 deletions. A file-local helper
above `classifyAndOrderPaper234`:

```cpp
static const int MESH_NO_AXIS_EXIT = 42;          // a batch log separates this from a generic failure
[[noreturn]] static void dieNoAxis(const std::string& why);
```

writes five lines to `std::cerr`, three of them the same in every case, and then calls
`std::exit(MESH_NO_AXIS_EXIT)`. All four paths that used to fall through now call it:

| used to print (and continue) | now prints, first line |
|---|---|
| `[PAPER-234] classify: no SFS_AXIS_FILE, keep size order` | `[PAPER-234] FATAL: SFS_AXIS_FILE is unset or empty` |
| `[PAPER-234] classify: cannot open axis file, keep size order` | `[PAPER-234] FATAL: cannot open SFS_AXIS_FILE='<path>'` |
| a "not six numbers" line | `[PAPER-234] FATAL: ... does not hold six numbers (axis point xyz + direction xyz)` |
| a "zero-length direction" line | `[PAPER-234] FATAL: ... has a zero-length direction` |

then, in every case:

```
[PAPER-234] FATAL: refusing to keep size order -- Surface_0/Surface_1 would be mislabelled
[PAPER-234] FATAL: and Bl0/Bl1 would stop matching the authors' lanes. Set SFS_AXIS_FILE
[PAPER-234] FATAL: to the piece's axis file (Dataset/Axes/<Piece>_Axis.xyz) and re-run.
[PAPER-234] FATAL: exiting 42
```

**Deliberate extension of the brief, flagged for removal if the lead disagrees:** the ticket
names the unset and unopenable paths; the parse and zero-direction paths are the same defect
shape (a labelling decision made on no axis) and were closed in the same call. No shipped axis
file can reach them — line and word counts over all 163 corpus axis files: 129 files 1 line /
6 words, 19 files 2 lines / 12, 11 files 3 / 18, 2 files 5 / 30, 1 file 6 / 36, 1 file 4 / 24,
so the first six numbers are always there. If they are judged out of scope, two of the four
`dieNoAxis` calls revert to their old prints and the guard keeps working.

The classification maths, the `pclusters.size() < 2` early return, the split and the merge are
untouched; `git diff` is four hunks in that one function.

### The three proofs

Run directory `/data/gpfs/projects/punim2657/SfSpp/runs/20261025-2356_66d4ad9_p277-axis-loud`
(`run.json`, `submit.sbatch`, `logs/`, `out/`). Job 33781618, sapphire, 6 min 10 s, exit 0.
Both binaries built in this job from `git archive` inside `pcl_191_nurbs.sif`:

| tag | commit | binary md5 |
|---|---|---|
| pre | `e3be07f2872da8c83b7328a451bd3c5b92d4e3d2` | `fb3fd055d30fb08ccce48dba7d49a879` |
| post | `66d4ad961093c94c14db02fb33519c0178630667` | `91b75eeadcf02009064f5f18218e0882` |

Staged inputs, md5s from `out/inputs.md5` (`scripts/stage_piece.sh`, geometry symlinked,
axis copied):

| input | md5 | points |
|---|---|---|
| `Mesh/Pot_H_Piece_02_Mesh_DS.obj` | `12882b9868661e417806498178e2ec06` | — |
| `Point/Pot_H/Pot_H_Piece_02_Point.pcd` | `a7edd8c828c0573e09d0888370cfcd6d` | 1000161 |
| `Axes/Pot_H_Piece_02_Axis.xyz` | `f90e8c18f121ab25f7c2b509624e7b26` | — |

**1 · `SFS_AXIS_FILE` unset → exit 42, no surfaces.** The post binary, `env -u
SFS_AXIS_FILE`:

```
[PAPER-234] FATAL: SFS_AXIS_FILE is unset or empty
[PAPER-234] FATAL: refusing to keep size order -- Surface_0/Surface_1 would be mislabelled
[PAPER-234] FATAL: and Bl0/Bl1 would stop matching the authors' lanes. Set SFS_AXIS_FILE
[PAPER-234] FATAL: to the piece's axis file (Dataset/Axes/<Piece>_Axis.xyz) and re-run.
[PAPER-234] FATAL: exiting 42
```

exit **42**; `Temp/Data/Pot_H/Pot_H_Piece_02_Surface_0.xyz` and `_Surface_1.xyz` **absent**.
The log is 85 lines: the run downsamples and clusters normally and dies at the labelling step,
so nothing downstream can find a surface to consume.

**2 · `SFS_AXIS_FILE` at a path that does not exist → exit 42, named differently.** Same
binary, `SFS_AXIS_FILE=<stage>/Dataset/Axes/Pot_H_Piece_02_Axis.xyz.DOES-NOT-EXIST`:

```
[PAPER-234] FATAL: cannot open SFS_AXIS_FILE='/data/gpfs/projects/punim2657/SfSpp/runs/20261025-2356_66d4ad9_p277-axis-loud/stage/B/Dataset/Axes/Pot_H_Piece_02_Axis.xyz.DOES-NOT-EXIST'
```

then the four shared lines. exit **42**; both surfaces **absent**.

**What the old binary did, measured in the same job** (so the ticket does not rest on the
believed behaviour): the pre binary at the same two stages exits **0**, exports **both**
surfaces, and prints `[PAPER-234] classify: no SFS_AXIS_FILE, keep size order` (case A) and
`[PAPER-234] classify: cannot open axis file, keep size order` (case B). That is the
before/after the ticket asked for: same inputs, same silence, two surfaces.

**3 · with the axis set, the classification and the surfaces are unchanged within the piece's
own measured spread.** Five runs per binary, each on its own fresh stage. All ten printed the
identical classify line, and it is the shipped one:

```
[PAPER-234] classify: face0 n=17678 interior_frac=0.9996 face1 n=14614 interior_frac=0.0000 satA=32285.0000 satB=7.0000
[PAPER-234] classify: kept -> Surface_0=interior
```

with `[PAPER-234] paper grow: thetaDeg=3.40000 kappa=1.00000 nb=10` above it. The draw is
unseeded, so the surfaces are *not* bit-identical run to run — the pre binary alone produced 5
distinct `Surface_0` md5s and 4 distinct `Surface_1` md5s across its five runs:

| surface | points across the ten runs | distinct md5 | spread, pre-vs-pre (max) | spread, post-vs-post (max) | worst pre-vs-post (max) | verdict |
|---|---|---|---|---|---|---|
| Surface_0 | 36212-36217 | 5 | 0.6255 mm | 0.6255 mm | **0.6255 mm** | inside |
| Surface_1 | 30480-30484 | 9 | 0.6094 mm | 0.6074 mm | **0.6094 mm** | inside |

Nearest-neighbour both ways, mm (`out/spread.json`, `out/spread.tsv`; `.scratch/pota-repro/277/spread277.py`).
Median and p99 are 0.000 in every pair — the runs differ only in a handful of edge points at
the 36 000th point. The pre-vs-post worst case never exceeds the same-binary worst case, so the
change moves the output by less than the stage moves itself.

### Two caveats stated plainly

1. **On this piece the axis rule *kept* size order** (`kept -> Surface_0=interior`), so the
   mislabelled surfaces the old code produced here happen to coincide with the correct ones.
   That is not evidence the silent path was harmless — it is the reason silence is dangerous:
   which cluster is larger is a property of the piece, so on the pieces where the ring is
   bigger the same silence swaps Bl0 and Bl1 with nothing in the log but a line nobody greps
   for. Pot_H_Piece_02 was chosen for cheap repeats, not because it exercises the swap.
2. **The six guard lanes of ticket 271 were not re-run here.** This job proves the stage-level
   question the brief asked (one piece, its own measured envelope). Bit-identity on the 271
   lanes is a separate harness and its own run directory, and is the one acceptance line of
   this ticket still open.

## Lead verdict (2026-10-26)

**Accepted.** I read the code, not the summary: dieNoAxis at mesh_processing_headless.cpp:1990
writes the five [PAPER-234] FATAL lines and calls std::exit(42); four call sites (unset :2010,
unopenable :2012, unparseable :2015, zero direction :2019); the string "keep size order" survives
only inside the fatal message, so no silent path is left; edgeline_extraction_headless.cpp is not
in the diff at all.

1. **The shape is right.** Preference 1 was taken, and no opt-out switch was added -- a switch would
   have recreated the defect. Exit 42 rather than 1 is a good detail: in a batch log "no axis" is
   separable from a generic failure without reading prose.
2. **The caller audit holds.** Every live recipe sets SFS_AXIS_FILE; the omitters are the legacy
   corpus generators and smoke tests listed in the ticket, none of which reads labelled surfaces,
   plus the pre-247 duplicate binary which does not carry this code. **Recorded consequence:** those
   scripts now fail loudly if they are ever used again. That is the desired outcome, not a
   regression -- an unlabelled surface set is exactly the artefact this ticket exists to prevent. If
   one of them is needed, it sets the variable first.
3. **The proofs are the right ones.** Unset -> exit 42 with both surfaces ABSENT and the variable
   named (not a run that dies early: the log is 85 lines deep, i.e. it reaches the labelling step).
   Missing path -> exit 42, same class, different message. The pre-binary at the same two stages
   exits 0 and exports both surfaces, which is the before/after this ticket asked for.
4. **The normal run is unchanged.** Five runs per binary: all ten printed the identical shipped
   classify line, and the worst pre-vs-post nearest-neighbour distance (0.6255 mm Surface_0,
   0.6094 mm Surface_1) is the same number the stage produces against ITSELF across two draws
   (pre-vs-pre 0.6255), with median and p99 at 0.000. That is the correct form of proof for an
   unseeded stage: inside its own spread, not "bit-identical", which it could never be.
5. **The open acceptance line is closed here, with the reason stated.** Ticket 271's six guard lanes
   are not re-run. They measure the EDGE stage downstream of surfaces this change cannot alter when
   the axis is set, and the stage-level spread test above already bounds the only thing that does
   vary (the draw). If a future change touches the classification maths or the split/merge, the
   guard lanes come back -- this was a guard-rail change, not a method change.
6. **The extension is accepted.** Unparseable and zero-direction axis files exit through the same
   helper. Unreachable with the 163 shipped axis files (all carry >= 6 numbers), and if a malformed
   one ever arrives, refusing beats mislabelling.
7. **One caveat carried forward, not fixed here:** on Pot_H_Piece_02 the axis rule keeps size order,
   so the old mislabelled surfaces coincide with the correct ones on that piece. The proof therefore
   demonstrates the guard firing, not the swap being caught; the swap was already proved by ticket
   296's Phase 0 on Pot A (1 kept, 7 swapped, interior confirmed by measurement). The two together
   close the loop.

Status set to done by the lead.
