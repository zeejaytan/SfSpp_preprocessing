import json
from pathlib import Path
base = Path(r"C:/PR/visual-qa/viewer/pairs")
for name in ("pota300_potC_arms.json", "pota300_potC_c01.json"):
    p = base / name
    d = json.loads(p.read_text())
    d["view_up"] = "+z"
    p.write_text(json.dumps(d, indent=1) + "\n")
    print("view_up set:", name)
