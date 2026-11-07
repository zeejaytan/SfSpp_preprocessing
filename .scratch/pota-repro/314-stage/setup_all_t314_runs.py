import os
import shutil
import re

runs_root = "/data/gpfs/projects/punim2657/SfSpp/runs"
ax_314_dir = "/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0415_e4329a7_t314a-axes/out/axes314"
commit = "e4329a7"
timestamp = "20261107-0420"

run_configs = [
    {
        "src_tag": "20261106-1330_fe906ab_t313b-kladder-E",
        "tag": f"{timestamp}_{commit}_t314b-kladder-E",
        "job_name": "t314b-kladder-E",
        "pot": "E",
        "named": 31,
        "np": 31,
        "floor": 50,
        "stage": "B: Pot E K-ladder",
    },
    {
        "src_tag": "20261106-1330_fe906ab_t313c-pota",
        "tag": f"{timestamp}_{commit}_t314c-pota",
        "job_name": "t314c-pota",
        "pot": "A",
        "named": 8,
        "np": 8,
        "floor": 50,
        "stage": "C: Pot A non-regression gate",
    },
    {
        "src_tag": "20261106-1330_fe906ab_t313c-potb",
        "tag": f"{timestamp}_{commit}_t314c-potb",
        "job_name": "t314c-potb",
        "pot": "B",
        "named": 9,
        "np": 9,
        "floor": 50,
        "stage": "C: Pot B non-regression gate",
    },
    {
        "src_tag": "20261106-1330_fe906ab_t313c-potd",
        "tag": f"{timestamp}_{commit}_t314c-potd",
        "job_name": "t314c-potd",
        "pot": "D",
        "named": 28,
        "np": 28,
        "floor": 50,
        "stage": "C: Pot D non-regression gate",
    },
    {
        "src_tag": "20261106-1330_fe906ab_t313c-potg",
        "tag": f"{timestamp}_{commit}_t314c-potg",
        "job_name": "t314c-potg",
        "pot": "G",
        "named": 7,
        "np": 7,
        "floor": 50,
        "stage": "C: Pot G non-regression gate",
    },
    {
        "src_tag": "20261106-1330_fe906ab_t313c-poti",
        "tag": f"{timestamp}_{commit}_t314c-poti",
        "job_name": "t314c-poti",
        "pot": "I",
        "named": 26,
        "np": 30,
        "floor": 50,
        "stage": "C: Pot I non-regression gate",
    },
]

for cfg in run_configs:
    src_dir = os.path.join(runs_root, cfg["src_tag"])
    dst_dir = os.path.join(runs_root, cfg["tag"])
    os.makedirs(dst_dir, exist_ok=True)
    os.makedirs(os.path.join(dst_dir, "logs"), exist_ok=True)
    os.makedirs(os.path.join(dst_dir, "out"), exist_ok=True)
    os.makedirs(os.path.join(dst_dir, "score"), exist_ok=True)

    # Copy work/ directory
    dst_work = os.path.join(dst_dir, "work")
    if os.path.exists(dst_work):
        shutil.rmtree(dst_work)
    src_work = os.path.join(src_dir, "work")
    
    # We only copy the python scripts, bash scripts, and helper configs
    os.makedirs(dst_work, exist_ok=True)
    for fname in os.listdir(src_work):
        if fname.endswith(".py") or fname.endswith(".sh") or fname.endswith(".txt"):
            shutil.copy2(os.path.join(src_work, fname), os.path.join(dst_work, fname))

    # Update code_commit.txt
    with open(os.path.join(dst_work, "code_commit.txt"), "w") as f:
        f.write(commit + "\n")

    # Update run.json
    run_json = {
        "runid": cfg["tag"],
        "ticket": "314",
        "stage": cfg["stage"],
        "commit": commit,
        "pot": cfg["pot"],
        "named": cfg["named"],
        "np": cfg["np"],
        "floor": cfg["floor"],
        "axes_314": ax_314_dir,
    }
    import json
    with open(os.path.join(dst_dir, "run.json"), "w") as f:
        json.dump(run_json, f, indent=2)

    # Read and adapt submit.sbatch
    with open(os.path.join(src_dir, "submit.sbatch"), "r") as f:
        sbatch_text = f.read()

    # Replacements in submit.sbatch
    sbatch_text = sbatch_text.replace(cfg["src_tag"].split("_")[-1], cfg["job_name"])
    sbatch_text = sbatch_text.replace("t313", "t314")
    sbatch_text = sbatch_text.replace("313", "314")
    # Restore correct path for AX_314
    sbatch_text = re.sub(
        r"AX_314=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-1316_fe906ab_t314a-axes/out/axes314",
        f"AX_314={ax_314_dir}",
        sbatch_text
    )
    # Ensure any AX_313 line is replaced
    sbatch_text = re.sub(
        r"AX_313=[^\n]+",
        f"AX_314={ax_314_dir}",
        sbatch_text
    )

    with open(os.path.join(dst_dir, "submit.sbatch"), "w") as f:
        f.write(sbatch_text)

    print(f"Configured {dst_dir}")
print("ALL RUNS CONFIGURED.")
