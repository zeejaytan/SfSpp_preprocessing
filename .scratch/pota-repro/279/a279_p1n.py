import numpy as np
R=__import__("os").path.dirname(__import__("os").path.abspath(__file__))
rows=[l.rstrip("\n").split("\t") for l in open(R+"/phase1_scan.tsv")]
cols=rows[0]; data=rows[1:]
d={c:i for i,c in enumerate(cols)}
want=("Pot_A_Piece_01","Pot_C_Piece_03","Pot_J_Piece_03")
for r in data:
    if r[0] in want and float(r[d["nsel"]])>3000:
        print("=== %s surface %s" % (r[0], r[1]))
        print("   " + " ".join("%s=%s" % (c, r[d[c]]) for c in cols))
