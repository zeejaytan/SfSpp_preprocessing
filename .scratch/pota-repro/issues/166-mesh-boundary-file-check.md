# Mesh-boundary file check: do FAR dots sit on real mesh boundary edges?

GOAL: SETTLE ON THE FILE WHAT THE RENDER LIED ABOUT.

**Answers:** E1

**Blocked by:** 165 CORRECTION (translucent render faked a hole; mesh solid+whole; blue-loop identity open) + 163 (substrate) + 155 (code sites).

**Status:** ready-for-agent

**What to deliver:** (a) On the actual C01 mesh FILE (not a render): is it watertight? Enumerate real boundary-edge loops (open edges) with counts; do the 4 blue loops from 165 exist on the file, and where are they (fracture rims? interior?). (b) Distance from each of the 91 FAR + 86 NEAR veto dots to the nearest real mesh boundary edge -- do FAR dots coincide with mesh boundaries (data-gap rims) or sit mid-surface? (c) Re-render the false-loop region OPAQUE (no translucency) with dots + ORIG + real boundary loops, eye-checked.

**Starting position:** 165 Comments (blue-loop tracing method, dot sets, mesh path); 162/164 Comments (labels). New scratch pota166_repro/; renders artifacts/pota166/.

**Rules:** read-only over tickets 39-165; render-only + file inspection (login-node/mesh tools; laptop-side if fetchable); COMMIT NOTHING; Comments-only ticket edits; OPAQUE renders only; sacct if Slurm used; eye-check renders.

- [ ] watertight verdict + real boundary loops enumerated on the file
- [ ] FAR/NEAR distance-to-mesh-boundary numbers
- [ ] opaque re-render, eye-checked
