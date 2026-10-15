# 03: Header writer fix (emit segment block)

**What to build:** preprocessing emits the fork-style `# nSeg totalPts / # ranges` segment header block on every breakline PCD, so the pristine assembly reader loads 8/8 instead of erroring ×8.

**Answers:** E1

**Blocked by:** 02-swap-test (surfaces must be attributed before edges are re-emitted; avoids re-running on shifted input twice).

**Status:** results-in — fix in fork, sim 8/8, Spartan fresh-run rides ticket 06

- [x] Spike: confirm writer defect at pristine pin (`edgeline_extraction_backup.cpp:2783` plain save vs fork `edgeline_extraction.cpp:1042-1111,2992`) and reader contract (`data_structure.cpp:189-319`, pristine :178 region)
- [x] Fix in fork only; pristine pin `d5ee6865` kept for control binaries on both sides
- [x] Fresh Pot A 8/8 files carry `#` block; pristine reader loads 8/8 with counts ≥1 (no `missing header information`) — shown by sim on laptop; binary fresh-run confirmation rides ticket 06
- [x] Curvature-column garbage (7.09e+33 vs ORIG 1.9e-42) dispositioned: fixed or ticketed separately

## Comments (worker pota-header-fixer, 2026-10-15)

**Verdict: fixed in fork (`edgeline_extraction.cpp` only, +19/−34). Pristine pins untouched.**

### Spike
- Pristine defect: `edgeline_extraction_backup.cpp:2783` is a bare `pcl::io::savePCDFile(pcdFilePath, *cloud_CompleteBreakline)` — no `#` block. The pristine reader (`BreakLine::ReadPCDFileWithInfo`, `data_structure.cpp:189-319`) requires `fileContents[1]` to split to `# nSeg totalPts info` and errors `missing header information` otherwise (the standard-PCD fallback at `:256-312` is a fork addition, absent pristine).
- Fork writer defects found (beyond the missing-block case): (1) `writeBreaklinePCDWithSegments(filename, cloud)` ignored the `index` table built during assembly and re-derived ranges by re-reading `Segments/*.xyz` at full `rows()` — but the cloud loop consumes `rows()-1` per segment, so ends overshoot and `totalPts` ≠ cloud size; (2) rim flags hardcoded `0`, discarding the `isBreaklineSegARim`/axis-stdev flags in `index`; (3) `tmpPtN.curvature` never set (stack garbage → the 7.09e+33 column) while the sibling path at `:928` already zeroes it.
- `original_nurbs_preprocessing/` is a vendored pristine mirror (control), not a build target — deliberately untouched. Stale same-named writer copies there noted, not changed.

### Fix (`edgeline_extraction.cpp`, fork only)
- Writer now takes `const std::vector<std::string>& segmentIndex` and emits the caller's `index` entries verbatim as `# start end rimflag` lines, with `totalPts = cloud.points.size()`; empty-table fallback is one segment covering the cloud. Call site `:2992` passes `index`.
- `tmpPtN.curvature = 0.0f` at fill (covers both segment loops) + `pn.curvature = 0.0f` on the empty-cloud boundary synthesis path. 0 matches ORIG's ~0 placeholder (measured `1.9e-42` uniform on authors' `pot_a_bl` P01B0) and what the reader expects in column 7. No separate curvature ticket needed.

### Check (laptop; no PCL/CGAL toolchain here, so no C++ build — compile check rides the ticket-06 Spartan build)
- Python replica of the pristine strict header parse over 8 Pot A `*_Breakline_0.pcd`: BEFORE (headers stripped = plain-save shape) → **0/8 load, all `missing header information`**; AFTER (fixed-writer logic: verbatim ranges, rim flag preserved) → **8/8 load, counts ≥1, zero missing-header errors**, header arithmetic `nSeg+12` holds.
- Heads (P01B0): before starts `VERSION 0.7 / FIELDS ...`; after starts `# .PCD v0.7 / # 5 208 0 / # 1 38 1 / # 39 119 0 / ...` (rim flag survives verbatim).
- Change set: `edgeline_extraction.cpp` only (+19/−34), one def + one call site, signature-consistent. Fresh-binary 8/8 confirmation belongs to the ticket-06 Spartan rebuild+run.
