import json,glob,sys,statistics
for f in sorted(glob.glob(sys.argv[1]+"/score/F20*.json")):
    o=json.load(open(f))
    pp=o["tables"]["per_piece"]
    d=[x["gauge_deg"] for x in pp]
    m=[x["gauge_mm"] for x in pp]
    print(f.split("/")[-1],"n=%d median_deg=%s median_mm=%s"%(len(d), round(statistics.median(d),2) if d else "-", round(statistics.median(m),2) if m else "-"))
