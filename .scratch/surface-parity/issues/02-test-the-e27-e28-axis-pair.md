# 02: Test whether the axes of sherds 27 and 28 together explain the missing join

**What to build:** Test whether swapping the two neighbouring axis files together changes the missing 27–28 join in either direction. Use the same scanned geometry and archived assembler.

**Answers:** E2

**Blocked by:** None. Surface Parity 01 and axis-parity 19 single-file comparisons are recorded on main.

**Status:** needs-triage — defer while testing surface inputs

**Worker:** unassigned

**Budget:** medium 5

**Hand-over:** DeepSeek V4.1 Flash via DSH Baton. Lead writes private acceptance before dispatch.

## Why this comparison

Surface Parity 01 preserved the 27–28 pass or fail when E27 alone was swapped. Axis-parity 19 preserved the pass when our E28 file went into the authors’ axis set. The next controlled change is both axis files together. Use the direct matching trace to distinguish loss of candidate fracture stretches from loss later in the full assembly.

## Run design

Use Surface Parity 01's frozen non-axis inputs, archived Ticket 19 executable, image, scorer and whole-pot invocation. Stage only the original complete OWN and AUTHOR axis directories and the two reciprocal dual swaps, `OWN_E27_E28_AUTHOR` and `AUTHOR_E27_E28_OWN`. Each swap changes only the packaged E27 and E28 bytes from its corresponding opposite parent, with no row reordering or candidate truncation. Verify both donor files actually differ and halt before submission if either planned two-file contrast degenerates. Verify the actual container-visible manifest, including 31 axis files, with 187 input hashes per arm and the pinned executable hash at both boundaries.

Run two waves of four, OWN, OWN_E27_E28_AUTHOR, AUTHOR, AUTHOR_E27_E28_OWN in wave 1 and the reverse order in wave 2. Each cell uses a fresh Result directory. Poll wave 1 to terminal states before launching wave 2. Retain all jobs and the eight attempted cells in the record. Score only cases that exported 31 nonempty sherd poses, using the completeness gate from ticket 01. Keep the missing IDs, logs and traces for incomplete runs. Do not silently substitute a replacement run. Stage and report under `.scratch/surface-parity/t02/` only, plus this ticket and its ignored evidence. Run measurements on Spartan compute nodes.

Keep the two complete full-set controls contemporaneous. Interpret the reciprocal dual swaps only if AUTHOR scores 62/62 in both complete repeats and OWN misses 27–28 in both complete repeats. Judge the primary join by the pinned scorer and inspect the locked view. Record direct queries, candidate stretches and fit counts with first event IDs, with blank IDs when a count is zero. Report the other two sherd-28 joins and count all 62 joins per usable run to expose losses elsewhere. Preserve the archived single-file comparisons as context and identify their run and repeat in a separate table.

## Acceptance

- [ ] The four packs contain the expected exact bytes. Both reciprocals differ at E27 and E28 alone. The executable, scorer, non-axis inputs and container image are fixed across all arms.
- [ ] Each attempt has recorded terminal Slurm state and exit code, before and after input hashes, scoring eligibility, and provenance for both raw traces. An incomplete attempt is visibly unusable and contributes no scored rows.
- [ ] Report the 62 unique join outcomes per usable cell, with relative rotation, translation component and scorer verdict. Also report a physical displacement on the sherd using the same frozen points transformed into the reference frame. Keep the absolute sherd-score issue separate from the joins. Include the three direct matching traces and locked 27–28 render for every attempt, including missing or off-frame cases.
- [ ] Report whether the control separated and whether either reciprocal result agreed in both usable repeats. One-direction, mixed, incomplete and no-change results remain visible. Keep a per-requirement worker table, separate read-only review, budget and one end state. Leave research interpretation and commits to the lead.

## Comments

### Direction agreed in the 24 November review

Defer this assembly comparison. The same estimator already separates the two surface sources on fixed Pot E inputs. This ticket could localise the effect to a pair of axis files. The immediate E2 question is which property of the surface samples changes the result. Revisit this comparison if the surface controls give a candidate effect and the sherds carrying it still need to be localised.
