import numpy as np
R=__import__("os").path.dirname(__import__("os").path.abspath(__file__))
rows=[l.rstrip("\n").split("\t") for l in open(R+"/boundary_test.tsv")][1:]
m=[r for r in rows if r[3]==r[4]]
print("matched pairs (lane==surface): %d" % len(m))
for name,sel in (("lane0->S0",[r for r in m if r[4]=="0"]),("lane1->S1",[r for r in m if r[4]=="1"]),("mismatched",[r for r in rows if r[3]!=r[4]])):
    g=np.array([float(r[6]) for r in sel]); fr=np.array([float(r[7]) for r in sel])
    print("%-10s n=%3d med_maxgap p10/p50/p90=%.1f/%.1f/%.1f frac_lanes_med>100=%.3f mean_dots>100=%.3f"%(
        name,len(sel),np.percentile(g,10),np.percentile(g,50),np.percentile(g,90),(g>100).mean(),fr.mean()))
print("worst matched lanes (lowest median maxgap):")
for r in sorted(m,key=lambda r: float(r[6]))[:8]:
    print("   %-22s S%s lane%s n=%s med=%.1f frac>100=%.2f"%(r[0],r[3],r[4],r[5],float(r[6]),float(r[7])))
print("the three disc pieces:")
for r in m:
    if r[0] in ("Pot_A_Piece_01","Pot_C_Piece_03","Pot_J_Piece_03"):
        print("   %-22s S%s lane%s n=%s med=%.1f frac>100=%.2f"%(r[0],r[3],r[4],r[5],float(r[6]),float(r[7])))
