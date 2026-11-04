import json,glob,sys
for f in sorted(glob.glob(sys.argv[1]+"/score/F20*.json")):
    o=json.load(open(f))
    print(f.split("/")[-1], "keys:", list(o.keys()))
    for k in ("seated_count","right_way_count","seat_bar_mm","mutual_deg","mutual_mm","candidates","n_candidates","seated"):
        if k in o: print("   ",k,"=",o[k])
    if "countresult" in o:
        print("    countresult", {k:(v if not isinstance(v,list) else len(v)) for k,v in o["countresult"].items()})
