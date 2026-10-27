# Pot A control: how the 15/15 was measured (ticket 07 stage 1, job 33834939)

NO gate probe step ran inside submit.sbatch. The Pot A control number was measured
AFTER the job, on the laptop, from the bundle this job produced. The job's own
product is out/geom/Pot_A_Piece_0N.Bl0.pcd (and .S0/.S1/.Bl0/.Bl1 for all pieces);
the probe is what turns those files into a pass count.

1. Bundle fetched from this run directory:
     ssh spartan 'cd RUN/out && tar czf stage1_out.tgz geom axes boot files.md5 ...'
     md5 of stage1_out.tgz = 0d823524f974d2ac8fe6b0f3428ed007 (11,654,126 bytes)
     extracted to C:/PR/structure-from-sherds-pp/artifacts/p07_stage1/
2. Breakline_0 copies renamed to the canonical names the probe's bundle spec expects:
     for f in geom/Pot_A_Piece_*.Bl0.pcd; do b=$(basename "$f" .Bl0.pcd); cp "$f" "pota_bl/${b}_Breakline_0.pcd"; done
   (a rename by copy: the bytes the probe read are the bytes in out/geom)
3. Probe run, from C:/PR/structure-from-sherds-pp/artifacts/p07_stage1:
     python gate_probe_b0_p07.py p07 > gate_probe_p07.out 2>&1
   exit 0. gate_probe_b0_p07.py is artifacts/juglet_run1/gate_probe_b0.py (md5 below)
   with ONE added BUNDLES entry:
     "p07": (ART + "/p07_stage1/pota_bl/Pot_A_Piece_%02d_Breakline_0.pcd",
             ART + "/pota_gt/Pot_A_Piece_%d_T.txt",
             ART + "/pota_gt/Pot_A_simple_graph.txt", 8),
   no other change to the probe's logic (gates 2.0 mm/0.85 and 20 deg/0.7, _0-only,
   max inlier count over segment pairs, PASS = inliers at 2.0 mm/0.85 > 0).

Files:
  gate_probe_b0.py      md5 c96b108f13a9a72248ecfe213f0b6ccf  (the unmodified probe, from artifacts/juglet_run1)
  gate_probe_b0_p07.py  md5 26f5d8e204e7e47d8d59292ac937e3a9  (with the p07 bundle entry)
  gate_probe_p07.out    the measured output: "p07 mates: 15 (_0-only)", 15 per-pair lines,
                        "STRICT pass rate at GT (_0-only): 15/15"
  checks_p07.py / .out  the ride check (Breakline_0 median distance to Surface_0 vs
                        Surface_1) and the md5-uniqueness check, same bundle

Bundle entries the probe uses for Pot A ground truth (unchanged, on the laptop):
  C:/PR/structure-from-sherds-pp/artifacts/pota_gt/Pot_A_Piece_%d_T.txt
  C:/PR/structure-from-sherds-pp/artifacts/pota_gt/Pot_A_simple_graph.txt
