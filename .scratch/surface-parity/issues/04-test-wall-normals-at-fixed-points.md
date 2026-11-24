# 04: Test whether wall normals move the Pot E axes

**What to build:** Test whether changing the local direction of the pottery wall, at the same sample points, changes the axis candidates for Pot E sherds 27 and 28.

**Answers:** E2

**Blocked by:** None. Surface Parity 01 verified that the corresponding walls are in the same scan frame. The two-file assembly swap in Ticket 02 is deferred. Ticket number 04 keeps the existing axis-parity worktree in slot 03 intact.

**Status:** ready-for-agent

**Worker:** unassigned

**Budget:** medium 5

**Hand-over:** DeepSeek V4.1 Flash via DSH Baton. Lead verification is outside the worker's worktree.

## Frozen estimator and scope

Use the two saved inner and outer wall arrays of E27 and E28 loaded by `t03_lib.walls(stem, surfaces=own/authors)` from the archived run `/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship` (SHIP). The corresponding own files are from Ticket 305; the authors' files are `Surface_0/1.xyz`. Use the archived TORA Python `/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3` and `SFS_IMPL=$SHIP/work/impl_t03`. Read the original extraction wrapper and submit environment. Reuse `t03_lib.draw_pool(C, seeds=10, step=10)`, `t03_extract.select_lines(..., 6, None)`, and `t03_extract.write_lines` on the frozen shipped joint-selector path with its original environment. Record the effective stride and drawn sample count. Form C by concatenating face 0 then face 1. Reference axes are for readout only.

Changes are limited to this ticket and four new files under `.scratch/surface-parity/t04/`: `normals04.py` (matching, perturbation and small fixtures), `extract04.py` (worker wrapper, tables and rendering), `submit.sbatch` (Spartan) and `check04.py` (public evidence validation). Use a fresh run directory and existing Slurm polling. Use a held compute allocation for fixture/debug iteration. Preserve all source, frozen inputs, estimator, configured seed list, selector, candidate cap and assembly inputs. Do not run the assembler or change extraction defaults in this ticket.

## Reciprocal surface change

For each sherd, run OWN and AUTHOR native controls, one sham repeat each that passes copied native arrays through the same experimental wrapper, and both transfers OWN_AUTHOR_NORMALS and AUTHOR_OWN_NORMALS. Run the transfers separately per sherd. Each target column keeps its position, index, face and multiplicity. Replace only its last three values with the raw donor normal of the closest valid donor point on the same face, in the native frame. Use a 1.000 mm inclusive Euclidean distance cut. A valid normal has finite components and norm greater than 1e-9. Invalid target normals are kept unchanged and counted separately. If no valid donor lies within the cut, keep the original target normal. Ties go to the first donor row in archive order. Preserve donor signs and lengths. Preserve target row order even where XYZ repeats. Report transferred and numerically changed rows separately. No registration, fits, point removal, reordering, resampling, deduplication, normal estimation or normal flipping.

The four native files must reproduce their paired sham files byte-for-byte. Compare each native file with its source in the archived Ticket 19 OWN or AUTHOR axis pack `20261124-0443_21446b8_t19-decisions`. Keep both sets and report hashes and ordered numeric differences. If bytes differ, accept the archived-control gate only when candidate counts and ranks agree and every ordered serialized component agrees within absolute 1e-9 and zero relative tolerance. A failed gate is an inconclusive experiment. Preserve its evidence and stop interpreting the transfer. If an arm cannot return finite candidate rows, record the stage and reason and keep the empty or missing output explicit, without inventing geometric distances.

## Evidence and acceptance

- [ ] `inputs.tsv` has 24 rows with `sherd,arm,face,points,xyz_sha256,normals_sha256,matched,changed,invalid_target,unmatched,source_sha256`. Hash the in-order little-endian contiguous float64 Nx3 XYZ and normal matrices separately. For transfers, matched + invalid_target + unmatched equals target points and changed is at most matched. For natives and shams, transfer counts are zero. Record a source file manifest with loader and estimator code hashes. The run keeps full match indices, distances and classifications under evidence; fetch only short tables, summary and renders.
- [ ] `runs.tsv` has 12 rows with `sherd,arm,status,k,axes_sha256,archive_ok,effective_stride,drawn_points`. Use status `ok` or `no_axis`; k=0 for no axis, with a reason in an additional column. For native and sham, archive_ok is 1 or 0; leave it blank for transfers. Keep raw estimator output and all ranks as emitted. `axes.tsv` has `sherd,arm,rank,oriented_deg,line_deg,anchor_mm` and six serialized components, plus costs when available. Rank starts at 1. Measure oriented angle in 0–180 degrees, the sign-independent line angle in 0–90 degrees and distance from the same pose-derived reference anchor to each line in mm. Show whether number, order, tilt or position of the candidate lines changes relative to the same geometry's native arm.
- [ ] `fixtures.tsv` records PASS for `inclusive_cut`, `outside_cut`, `same_face`, `invalid_target`, `invalid_donor`, `tie_first`, `duplicates_preserved`, `normal_sign` and `identity_order`. Run fixtures on Spartan. On all archived inputs, verify matching partitions, XYZ hash identity for every native/sham/transfer trio, and exact retention for unmatched or invalid target rows. Report the fraction transferred on each wall so a sparse intervention is visible.
- [ ] `renders.tsv` lists one locked two-view baseline/transfer comparison PNG per sherd, each with a 20 mm scale, both wall faces, changed normals and native and transferred axis lines. Make sampled arrows legible, retain the full geometry comparisons on Spartan and inspect the figures.
- [ ] `jobs.tsv` records every submitted Slurm ID, terminal state and exit code. Keep the lead verdict blank in the run index. Report facts, budget used and one end state. Write a per-requirement compliance table and get a separate read-only DeepSeek review that checks the tables and opens the two figures. Leave interpretation, commits and closure to the lead.

Named checks: compile the three Python files, `bash -n .scratch/surface-parity/t04/submit.sbatch`, run fixtures and `check04.py` on the compute node, and `git diff --check` scoped to the ticket.
