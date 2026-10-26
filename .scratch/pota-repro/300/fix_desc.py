import json
from pathlib import Path
base = Path(r"C:/PR/visual-qa/viewer/pairs")
for name in ("pota300_potC_arms.json", "pota300_potC_c01.json"):
    p = base / name
    d = json.loads(p.read_text())
    fn = d["frame_note"]
    if fn.endswith("unchanged."):
        d["frame_note"] = fn[:-1] + "; "
    elif fn.endswith("fit."):
        d["frame_note"] = fn[:-1] + "; "
    else:
        print("UNCHANGED tail:", repr(fn[-40:]), "-> leaving as is" if fn.endswith("; ") else "-> CHECK")
        continue
    p.write_text(json.dumps(d, indent=1) + "\n")
    print("patched", name, "->", repr(d["frame_note"][-30:]))
