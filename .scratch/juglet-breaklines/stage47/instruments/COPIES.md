# stage47/instruments -- COPIES.md

Nothing byte-copied from stage46: ticket 47 is corpus-only (no C++ build, no cells, no
container), so the instrument set is new and small.  The conventions are stage46's:
the submitter comes out of the pushed commit (git archive), the job md5-compares its
instruments against that commit and fails on any difference, and the run directory
shape is the project convention.

| file | what it does |
|------|--------------|
| submit47.sh | renders submit47.sbatch.tmpl, gates it (CRLF, py_compile, unrendered-placeholder, expansion-count), writes the run directory + run.json, submits. |
| submit47.sbatch.tmpl | the job: phase 0 record + verify (converter bytes from the commit, corpus tree + md5s before), 1 convert the nine meshes with cc_mesh_to_pcd.sh defaults-only into staging, 2 gates (frame vs mesh vertices vs GT frame, density ~840k, median spacing), 3 attic move of the nine vertex dumps with manifest + read-back proof, install of the nine clouds + _cc.log + MANIFEST_JUGLET_CC.tsv, 4 the J2 before/after figure, 5 corpus-confined proof + run-meta; index row appended with verdict and human_note empty; trap on TERM/INT closes the record. |
| gates47.py | per piece: parses the _cc.log (sampled count, Global Shift lines) and the PCD header (FIELDS/POINTS), streams the cloud for bbox/centroid/max-abs and first rows, reads the OBJ vertices (and faces for area), computes the median NN spacing on a seeded 250k subsample, and emits gates47.tsv (frame/density PASS-FAIL) and manifest_rows.tsv (the freeze-manifest fields: piece / points / md5 / cc-log / date / command / spacing / mesh md5). |
| figure47.py | the conservator's eye picture: J2 before (shipped vertex dump) vs after (the cc draw) over the mesh outline on the two largest-extent axes, mm axes, equal aspect, counts and pts/mm^2 in the caption. |
| .gitattributes | byte-copy of stage46/instruments/.gitattributes (LF everywhere). |

The converter itself is NOT an instrument and is never copied into this directory: the job
extracts cc_mesh_to_pcd.sh from the pushed commit's repo root (git archive <commit>
cc_mesh_to_pcd.sh), records its md5, and runs exactly those bytes, defaults only -- the
corpus converter stays byte-frozen (ticket 47 records its known gaps, MAX_REMOVAL_PERCENT
never enforced and the unseeded sampler, and fixes neither).
