#!/usr/bin/env python3
"""Ticket 301 -- write / update ONE run directory's run.json.

The run record is the unit of record (workspace AGENTS.md, "Runs, worktrees and the attic"):
parameters, inputs, the commit and the tag. This script writes that file twice per run:

  --phase start   immediately before the arm runs: what the run IS -- the commit it builds
                  from, the job id, the pot, the role (ctrl or swap), the target piece, the
                  pinned assembler and image, the frozen corpus, the start time.
  --phase end     after the arm: what the run DID -- the arm's exit code, the assembler's own
                  printed counts read back out of out/summary.txt, the input fingerprint, the
                  assembler-binary md5, the corpus md5 chain (before/after/unchanged) and, for a
                  swap run, the swap provenance p301_mkswap.py wrote when it staged the file.

Nothing here computes geometry; it only records what the arm already left on disk. Every field
names the file it came from, so a reader can check the run.json against the run directory.
"""
import argparse, hashlib, json, os, re, socket, sys, time

def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()

def read_kv_md5(path):
    """md5sum output ("<md5>  <path>") -> {path: md5}."""
    d = {}
    if not os.path.exists(path):
        return d
    with open(path) as fh:
        for line in fh:
            parts = line.split()
            if len(parts) >= 2 and re.fullmatch(r"[0-9a-f]{32}", parts[0]):
                d[parts[-1]] = parts[0]
    return d

def parse_summary(path):
    """The assembler's own printed lines -> counts. Source: class/main.cpp prints these."""
    out = {"lines": [], "sherds_seated": None, "sherds_on": None, "sherds_pct": None,
           "joins_seated": None, "joins_on": None, "joins_pct": None,
           "pair_hypotheses": None, "pair_hypotheses_pruned": None}
    if not os.path.exists(path):
        return out
    with open(path) as fh:
        lines = [l.rstrip("\n") for l in fh if l.strip()]
    out["lines"] = lines
    for line in lines:
        m = re.match(r"\s*Total number\s*:\s*(\d+)", line)
        if m and out["pair_hypotheses"] is None:
            out["pair_hypotheses"] = int(m.group(1))
        m = re.match(r"\s*Total number pruned\s*:\s*(\d+)", line)
        if m:
            out["pair_hypotheses_pruned"] = int(m.group(1))
        m = re.search(r"Sherd accuracy\s*:\s*(\d+)\s*/\s*(\d+)\s*\(([0-9.]+)", line)
        if m:
            out["sherds_seated"], out["sherds_on"], out["sherds_pct"] = int(m.group(1)), int(m.group(2)), float(m.group(3))
        m = re.search(r"Edge accuracy\s*:\s*(\d+)\s*/\s*(\d+)\s*\(([0-9.]+)", line)
        if m:
            out["joins_seated"], out["joins_on"], out["joins_pct"] = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--phase", required=True, choices=["start", "end"])
    ap.add_argument("--role", required=True, choices=["ctrl", "swap"])
    ap.add_argument("--target", type=int)
    ap.add_argument("--runid")
    ap.add_argument("--tag")
    ap.add_argument("--commit")
    ap.add_argument("--job-name")
    ap.add_argument("--sibling", help="the other half of this pair (ctrl<->swap run id)")
    a = ap.parse_args()

    run = os.path.abspath(a.run_dir)
    out = os.path.join(run, "out")
    path = os.path.join(run, "run.json")
    rec = {}
    if os.path.exists(path):
        with open(path) as fh:
            rec = json.load(fh)
    now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    if a.phase == "start":
        rec.update({
            "runid": a.runid or os.path.basename(run),
            "tag": a.tag or os.path.basename(run).split("_", 2)[-1],
            "ticket": "301-d-axis-swap",
            "question": ("Pot D pieces 18/25/26/28/29 fail to seat and their released axis files "
                         "disagree with their released reference poses by 10-75 deg. Is the AXIS FILE "
                         "the broken artefact, or the REFERENCE POSE? ctrl and swap differ in one "
                         "piece's axis direction and in nothing else."),
            "role": a.role,
            "arm": ("every piece gets the authors' corpus axis verbatim (the ticket 298 authb arm)"
                    if a.role == "ctrl" else
                    "every piece gets the authors' corpus axis except the target, which gets a real "
                    "staged file whose direction fields are +/- R_GT^T . a_world (p301_mkswap.py); "
                    "axis point columns, line count and field order untouched"),
            "target_piece": a.target,
            "sibling_runid": a.sibling,
            "pot": "Pot_D",
            "shard": 29,
            "commit": a.commit,
            "jobid": os.environ.get("SLURM_JOB_ID", ""),
            "job_name": a.job_name or os.environ.get("SLURM_JOB_NAME", ""),
            "host": socket.gethostname(),
            "started": now,
            "parameters": {
                "assembler_tree": "/data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker",
                "image": "/data/gpfs/projects/punim2657/sfs_main/sfs_pristine_assembly.sif",
                "apptainer": "/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer",
                "corpus": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp",
                "bundle": ("authors' Surfaces + Breakline_0 (corpus), frozen corpus Mesh, frozen corpus "
                           "ground truth; pot selected in a throwaway copy of the pinned tree"),
                "changed_between_arms": "one piece's axis direction, nothing else",
            },
        })
    else:
        rec["finished"] = now
        rec["inputs"] = {
            "file": "out/inputs.md5",
            "n_entries": (sum(1 for l in open(os.path.join(out, "inputs.md5")) if l.strip())
                          if os.path.exists(os.path.join(out, "inputs.md5")) else 0),
            "md5_sum": md5(os.path.join(out, "inputs.md5")) if os.path.exists(os.path.join(out, "inputs.md5")) else None,
        }
        asm = read_kv_md5(os.path.join(out, "assembler_inputs.md5"))
        rec["assembler_md5"] = asm
        before = os.path.join(out, "corpus_axes_md5_before.txt")
        after = os.path.join(out, "corpus_axes_md5_after.txt")
        rec["corpus_axes_md5"] = {
            "before_file": "out/corpus_axes_md5_before.txt",
            "after_file": "out/corpus_axes_md5_after.txt",
            "n_axes": len(read_kv_md5(before)),
            "diff": open(os.path.join(out, "corpus_unchanged.txt")).read().strip() if os.path.exists(os.path.join(out, "corpus_unchanged.txt")) else "",
            "before": read_kv_md5(before),
            "after": read_kv_md5(after),
        }
        rec["corpus_axes_md5"]["unchanged"] = (rec["corpus_axes_md5"]["before"] == rec["corpus_axes_md5"]["after"])
        for name in ("target_axis_source.txt", "corpus_target_md5_before.txt", "corpus_target_md5_after.txt"):
            p = os.path.join(out, name)
            if os.path.exists(p):
                rec.setdefault("target_axis", {})[name] = open(p).read().strip()
        prov = os.path.join(out, "swap_provenance.json")
        if os.path.exists(prov):
            with open(prov) as fh:
                rec["swap"] = json.load(fh)
        ex = os.path.join(out, "arm_exit.txt")
        code = open(ex).read().strip() if os.path.exists(ex) else None
        rec["result"] = {"arm_exit": code, "summary_file": "out/summary.txt",
                         "summary": parse_summary(os.path.join(out, "summary.txt"))}
        rt = os.path.join(out, "Result")
        if os.path.isdir(rt):
            files = sorted(os.listdir(rt))
            rec["result"]["result_dir"] = {"path": "out/Result", "n_files": len(files),
                                           "transforms": len([f for f in files if re.fullmatch(r"T_\d+to_\d+\.txt", f)])}
    with open(path, "w") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("run.json", a.phase, "->", path)
    return 0

if __name__ == "__main__":
    sys.exit(main())
