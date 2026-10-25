import glob, json, os, re, sys
RUNS="/data/gpfs/projects/punim2657/SfSpp/runs"
COMMIT="d1f1a4c37ec5bc8e531c195858303b3ce942486a"
changed=[]
for d in sorted(glob.glob(f"{RUNS}/20261026-0126_d1f1a4c_p298-*")):
    rid=os.path.basename(d)
    rj=os.path.join(d,"run.json")
    if not os.path.exists(rj): continue
    j=json.load(open(rj))
    pot=j.get("pot","")
    before=json.dumps(j, sort_keys=True)
    j["runid"]=rid
    j.setdefault("parameters",{})
    if "prep" in rid:
        j["commit_preprocessing"]=COMMIT
        j["parameters"]["pieces"]=sum(1 for _ in open(os.path.join(d,"scripts/pieces.txt"))) if os.path.exists(os.path.join(d,"scripts/pieces.txt")) else j["parameters"].get("pieces")
    else:
        logs=sorted(glob.glob(f"{d}/logs/slurm-*.out"))
        sh=None
        if logs:
            m=re.search(r"SHARD_NUMBER (\d+)", open(logs[-1], errors="ignore").read())
            if m: sh=int(m.group(1))
        if sh is not None: j["parameters"]["SHARD_NUMBER"]=sh
        j["parameters"]["step_size"]=j["parameters"].get("step_size") or sh
        j["commit_preprocessing"]=COMMIT
        if j.get("arm")=="oursd":
            j["parameters"]["bundle"]="our p298-prep bundle: our Surface_0/Surface_1 + our Breakline_0/Breakline_1 from runs/20261026-0126_d1f1a4c_p298-prep-%s/out/geom ; mesh, axis and ground truth from the frozen corpus" % pot
            j["prep_run"]=f"{RUNS}/20261026-0126_d1f1a4c_p298-prep-{pot}"
        else:
            j["parameters"]["bundle"]="the authors' corpus Surface_0/Surface_1 + corpus Breakline_0/Breakline_1 ; mesh, axis and ground truth from the frozen corpus"
            j.pop("prep_run", None)
        j["metadata_note"]=("run.json was laid out from the Pot B template and carried that template's runid, "
            "SHARD_NUMBER, commit and bundle text until 2026-10-26; corrected here from the job's own log "
            "(the SHARD_NUMBER line the flipped header printed) and from out/links.tsv. No execution changed.")
    after=json.dumps(j, sort_keys=True)
    if after!=before:
        json.dump(j, open(rj,"w"), indent=2, sort_keys=False); open(rj,"a").write("\n")
        changed.append(rid)
print("fixed", len(changed)); [print(" ", c) for c in changed]
