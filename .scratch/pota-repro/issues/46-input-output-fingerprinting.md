# 46: Cross-pot input↔output fingerprinting — reverse-engineer the author's preprocessing

**What to deliver:** the author's method, inferred from their data — or the measured proof that it can't be inferred.

**Answers:** E1

**Blocked by:** nothing (read-only analysis; runs alongside 45).

**Status:** ready-for-agent

**Starting position:** for every pot A–J we hold BOTH ends: source meshes (original_samples/SfS_pp Mesh OBJs + NURBS drivers) and the perfect-score inputs (ORIG Breaklines/Surfaces/Axes). Our chain reproduces A but not the rest — trial-and-error per pot won't scale. The author's pipeline is unpublished in detail (pristine mesh_processing.cpp + edgeline_extraction.cpp exist but the exact recipe that produced the shipped inputs is unknown).

**Method — fingerprint, then infer (never assume):**
1. Per piece, per pot: tabulate ORIG rim fingerprints — point counts, spacing distribution (uniform? adaptive?), ordering (teleports? segment structure?), segment counts + gap sizes, curvature profile along rim, normal behavior, profile rows, rim length vs GT edge length, header/index conventions.
2. Same fingerprints for OUR rims (fresh chain output) on the same pieces.
3. Diff the two tables: WHERE do they diverge systematically (spacing? termination? selection? ordering?), and do the divergences share one shape across pots?
4. From the ORIG fingerprints alone, infer the likely method family (e.g. uniform resampling at fixed step? curvature-thresholded selection? normal-consistency filter? fixed-count vs length-proportional?) — each hypothesis must PREDICT an as-yet-unchecked ORIG property; then check it.
5. Translate the confirmed inferences into concrete recipe changes for our chain (parameters, walk rules, selection rules), ordered by expected generality (all pots first, pot-specific last).

**Rules:** read-only over shipped/reference data (ORIG inputs are evidence, never material to copy into our outputs — the ticket-44 asterisk rule); no prep/assembly code changes (analysis + tables only); every claimed fingerprint carries pot/piece/numbers; every method hypothesis carries its prediction AND the check result; no commits; sacct-direct polling for any compute (held allocation or short jobs; this is mostly laptop-side table work on fetched PCDs — fetch small samples only, never bulk-copy HPC data trees); Comments-only ticket edits.

- [ ] ORIG fingerprint table (all pots, per piece)
- [ ] Fresh-vs-ORIG divergence table (systematic shapes, cross-pot)
- [ ] Method hypotheses with prediction→check pairs
- [ ] Ranked recipe changes for our chain
- [ ] Job IDs + sacct states (if any compute)

**Successor:** implement the top-ranked recipe change (new ticket per change); ticket 45 continues as the B-p2 instance.
