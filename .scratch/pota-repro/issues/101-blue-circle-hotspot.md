# Blue-circle hotspot — the top overshoot on C01 (user-marked)

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** Numbers on the user-circled spot at the top of the C01 sherd (left panel of artifacts/pota100/C100_C01_mesh_overlay.png, blue circle: red walk overshoots the green ORIG loop and tangles near the top of the lip). Which fresh file indices pass through the circled region, their step sizes along file order, off-mesh distances, distance to ORIG Bl_0, and which routine fired each leap there (greedy nearest-pick edge_line_ordering.cpp:92-103 vs SFS-T13 second-chance jump :162-187, from pota39_C/edgeline_stage.log line 23's 4 jumps if they fall here).

**Answers:** E1

**Blocked by:** 97 + 99 (run map, step-across points) + 100 (overlay render)

**Status:** results-in

## Comments (worker, 2026-10-18 — COMMIT NOTHING; lead to commit)

**Verdict: circled hotspot measured.** The blue circle holds a two-pass overshoot hump at the top of the lip: the file-head nub F0–F9 (orange) riding 3.3–4.3mm off the ORIG top arc (nearest O104–O113) with the fresh topmost points at Z=90.0 (+2.9mm above ORIG max Z 87.1 at O101), and the run tail F182–F190 (blue) peeling off the ORIG loop (vsORIG 1.2→3.6 from F180) and kissing the nub start at the (0,190) 1.90mm touch before the 190→191 teleport. Adopted region (hand circle has no 3D coords): sphere r=18mm about the touch midpoint C=(10.6,15.6,90.0) GT — members F0–9 (dC 1.0–17.6) + F182–190 (dC 15.2–1.0); spur F10+ (dC≥58.6) and post-teleport F191+ (dC≥104.5) excluded; F180/181 (dC 18.7/17.0) noted as peel-off transition.

**Numbers (GT-seated; off-mesh = nearest mesh vertex; vsORIG = nearest ORIG Bl_0 point):** nub steps all 1.85–1.90mm, off-mesh 0.14–0.95 (on-surface), vsORIG 3.33–4.27; tail steps all 1.85–1.90mm, off-mesh 1.67–2.17 mid-tail (lifting) settling to 0.29–0.85 at F188–190, vsORIG 2.82–3.96; bounding teleports 9→10 56.82mm and 190→191 105.02mm; full table in artifacts/pota101/p101_numbers.txt (19 member rows + transition).

**Routine per leap (with log evidence):** no walk routine fired *between* consecutive circled indices — every interior step is 1.85–1.90mm = SFS-T06 uniform-resample interpolation (pota39_C/edgeline_stage.log: "resampling 166 -> 402 points at ~1.9mm"). The two bounding teleports are walk-discontinuity echoes attributable to the SFS-T13 second-chance global-nearest jump (edge_line_ordering.cpp :162–187, the `if (!advanced)` global scan) by elimination: greedy :92–103 only steps to unvisited points inside the K=34 window of a ~1.08mm-spacing cloud and stalls rather than jumps (log line 23: coverage 0.271137 → 0.690962, 237/343, 4 jumps — the stall is the proof), so 56.8/105mm spans can only be second-chance globals. Caveat: the log records the 4 walk jumps without coordinates, so the file-echo ↔ walk-jump mapping is by elimination, not coordinate match; one of the 4 walk jumps has no >5mm file echo (only 3 file jumps: 9→10, 38→39, 190→191 — sphere-marching smoothed one over).

**Render:** artifacts/pota101/C101_C01_bluecircle_hotspot.png (eye-checked; left: adopted circle + labelled hump over mesh; right: per-leap log profile showing uniform interior steps vs teleport spikes). Script + numbers mirrored at artifacts/pota101/; Spartan scratch pota101_repro/ (4 scripts + PNG). Zero ORIG points; bundles read-only untouched; login-node numpy only — no Slurm, no E2E, no gate; nothing committed.

**Starting position:** Fresh C01 Bl_0 (402 pts) + ORIG C01 Bl_0 (211 pts) + mesh from the t39-pipe C bundle; edgeline_stage.log. Login-node numpy only — no Slurm, no E2E, no gate. Renders under laptop artifacts/pota101/.

**Rules:** read-only (zero ORIG points, bundles md5-guarded); COMMIT NOTHING; Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); one question only — do not re-diagnose the whole walk.

- [ ] Indices + steps + off-mesh + vs-ORIG numbers inside the circled region
- [ ] Routine attribution per leap (greedy vs second-chance, with log evidence)
