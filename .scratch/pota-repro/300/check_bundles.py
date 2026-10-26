import sys, json
import numpy as np
from pathlib import Path
sys.path.insert(0, r"C:/PR/visual-qa/viewer")
from view_juglet import manifest_loader, registry
for name in ("pota300_potC_arms", "pota300_potC_c01"):
    p = Path(r"C:/PR/visual-qa/preview") / f"manifest_{name}.json"
    print("=== MANIFEST", name)
    print(json.dumps(json.loads(p.read_text()), indent=1)[:1200])
    pv = manifest_loader(p)
    print("--- loaded keys:", sorted(pv.keys()))
    for k, v in pv.items():
        if hasattr(v, "geometry"):
            g = v.geometry
            print("   ", k, "objects", sorted(g), "faces",
                  sum(len(m.faces) for m in g.values()),
                  "finite", all(np.isfinite(np.asarray(m.vertices)).all() for m in g.values()))
    print("--- registry match:", [k for k in registry() if "Pot C" in k])
