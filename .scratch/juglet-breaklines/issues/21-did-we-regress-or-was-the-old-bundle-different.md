# 21: Did the pipeline regress since late September, or was the old 7-of-9 a different bundle?

**What to build:** the comparison that separates two things a number cannot tell
apart — our code changed and lost surfaces, or the older "7 of 9 produced" was
measured on a different bundle/stage and was never comparable. This is the
measurement-call versus method-call question, and it decides how the Juglet result
is described.

**Answers:** U19

**Blocked by:** none

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-10-27)
**Branch:** 21-did-we-regress-or-was-the-old-bundle-different, in /c/PR/worktrees/sfs/21

## What is already established

- Today's code (commit `d8af9d2`, job **33834939**, run
  `20261027-0055_d8af9d2_p07-juglet-stage1`) produces Surfaces for **4 of 9**
  Juglet sherds: pieces 1, 4, 6, 7. Pieces 2 and 9 give 0 clusters, piece 5 gives 1,
  pieces 3 and 8 give 2 and the merge fuses them to 1.
- The older claim is at
  `C:/PR/SfSpp_preprocessing/.scratch/juglet-breaklines/issues/07-end-to-end-acceptance.md:17-20`:
  "0 of 5 scorable touching pairs pass, 5 touching pairs unmeasurable (**pieces 3
  and 9 produce no surfaces** — single cluster after 30 loosened retries — and skip
  loudly)", from the 2026-09-30 run. That implies the other **7 of 9** did produce
  surfaces, and it names a different pair of absent pieces (3 and 9) than today's
  (2, 3, 5, 8, 9).
- That bundle is **gone**: the 2026-10-24 attic sweep carved the three
  `Juglet_Dataset_*` trees out whole and deleted the geometry; only
  `checkout-bucketc-20261024-record.tar.gz` survives, holding `SfS_pp/Ground Truth/`.
  Its last full write was 2026-09-25 14:37-14:40, three days BEFORE the
  interior/exterior classifier (ticket 04, commit `4513f00`, 2026-09-28; its parent
  is `f27c5e5`).
- Code commits available as replay targets, verified in this clone:
  `a41a91e` (last commit before 2026-09-26, the code that wrote the old bundle) and
  `28e470b` (2026-09-30, the code that produced the "7 of 9 / 0 of 5" reading).
- The nine input meshes are still on disk:
  `/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Juglet/Piece01..09.obj`,
  vertex counts 24294, 2568, 3495, 3651, 6212, 5126, 8421, 4479, 2095.

## The two checks

**A — replay the same nine meshes through the older code.** Build the mesh stage from
`28e470b` first (that is the code behind the "7 of 9" reading), and only if it cannot
build or run, from `a41a91e`. Reconstruct the stage invocation by reading that
commit's own `main()` and `data_path.h` — **not** today's `submit.sbatch`, which
carries the axis gate (ticket 277) and the paper chain (ticket 234) that did not exist
then. Run the nine meshes and report, per piece: point count into clustering, cluster
count and sizes, and whether surfaces were written.

**B — were the inputs the same?** Record the md5 of the nine `Piece0N.obj` today.
Then search for any record of what the old bundle was built from: the repo history
under `.scratch/juglet-breaklines/`, any `run.json` or `index.tsv` row naming the old
bundle, and the attic `checkout-bucketc-20261024-INDEX.txt` / record tarball listing.
If no md5 record survives, say **unknown** — do not infer identity from file names.

## Acceptance

1. A per-piece table, old commit vs today: surfaces produced, cluster count and sizes,
   points into clustering — with the run directory named for each row.
2. A verdict, one of: **(1) regression** — the older code produces more surfaces from
   byte-identical inputs; **(2) comparison artefact** — the old number came from
   different inputs or a different stage, so the two were never comparable; **(3) not
   determined**, with what would decide it. The evidence that decides it, quoted.
3. The input-identity question answered with md5s, or explicitly recorded as unknown
   after the search.
4. If the older code cannot build or run, the exact failure (command, error text) and
   what it would take — do not port fixes forward, do not modify the old tree to make
   it work, and do not fall back to today's code.
5. No tracked source changed (`git diff --stat main..<branch>` shows only this
   ticket), frozen corpus md5 unchanged, geometry deleted with a counted record, index
   rows appended with `verdict` and `human_note` empty, ticket and `Status:` updated.

## Boundaries

- Build the old commit in a private tree inside its own run directory; never build in,
  or dirty, the canonical checkout `/data/gpfs/projects/punim2657/sfs_preprocessing`.
- Env-var and build-target choices only. No source edits, in any commit, at any age.
- Runs on compute nodes only. A scoring or probing step over a bundle runs there too —
  the previous ticket's Pot A gate probe was run on the laptop, which breaks the
  standing rule; do not repeat that.

## What this cannot settle

**Why** the surfaces are lost — that is ticket 20. And whether the Juglet would
reassemble if every sherd produced a surface — stage 2 of ticket 07, paused.
