import json,sys
o=json.load(open(sys.argv[1]))
g=o["gauge"]
print({k:(type(v).__name__, len(v) if hasattr(v,"__len__") else v) for k,v in g.items()})
print(json.dumps(g, indent=1)[:1200])
