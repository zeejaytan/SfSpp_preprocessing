import json,glob,sys,statistics
for f in sorted(glob.glob(sys.argv[1]+"/score/F20*.json")):
    o=json.load(open(f))
    g=o.get("gauge")
    if isinstance(g,list):
        d=[x.get("gauge_deg") for x in g if isinstance(x,dict) and x.get("gauge_deg") is not None]
        m=[x.get("gauge_mm") for x in g if isinstance(x,dict) and x.get("gauge_mm") is not None]
        print(f.split("/")[-1],"gauge n=%d median_deg=%.2f median_mm=%.2f"%(len(d),statistics.median(d) if d else -1,statistics.median(m) if m else -1))
    else:
        print(f.split("/")[-1],"gauge type",type(g))
