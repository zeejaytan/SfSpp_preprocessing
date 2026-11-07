import glob
import os

jobs = [
    ("t314b-kladder-E", "/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314b-kladder-E"),
    ("t314c-pota", "/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314c-pota"),
    ("t314c-potb", "/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314c-potb"),
    ("t314c-potd", "/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314c-potd"),
    ("t314c-poti", "/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314c-poti"),
]

for tag, run_dir in jobs:
    print(f"=== {tag} ===")
    logs = sorted(glob.glob(os.path.join(run_dir, "logs", "run_*.log")))
    for log in logs:
        base = os.path.basename(log)
        try:
            with open(log, "rb") as f:
                size = os.path.getsize(log)
                f.seek(max(0, size - 1500))
                tail = f.read().decode("latin1", errors="replace").strip().splitlines()
                lines = [l.strip() for l in tail if l.strip()]
                last_3 = " | ".join(lines[-3:]) if lines else "empty"
                print(f"  {base} ({size}B): {last_3}")
        except Exception as e:
            print(f"  {base}: error {e}")
