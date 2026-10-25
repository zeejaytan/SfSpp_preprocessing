import json, os, shutil, subprocess, datetime
ROOT="/data/gpfs/projects/punim2657/SfSpp/runs"
ST="/data/gpfs/projects/punim2657/SfSpp/298-stage/jobs"
COMMIT="d1f1a4c"  # git7 of the pushed Phase 1 commit; full hash passed to jobs
POTS=[("A",8),("C",4),("D",29),("E",31),("F",7),("G",7),("H",11),("I",30),("J",19)]
ts=datetime.datetime.now().strftime("%Y%m%d-%H%M")
POTB_PREP="20261026-0046_63cf615_p298-prep-Pot_B"
tmpl_prep=json.load(open(f"{ROOT}/{POTB_PREP}/run.json"))
tmpl_oursd=json.load(open(f"{ROOT}/20261026-0052_63cf615_p298-Pot_B-oursd/run.json"))
tmpl_authb=json.load(open(f"{ROOT}/20261026-0052_63cf615_p298-Pot_B-authb/run.json"))
made=[]
for letter,shard in POTS:
    pot=f"Pot_{letter}"
    prepid=f"{ts}_{COMMIT}_p298-prep-{pot}"
    hosts={}
    for arm,tmpl in (("oursd",tmpl_oursd),("authb",tmpl_authb)):
        rid=f"{ts}_{COMMIT}_p298-{pot}-{arm}"
        d=f"{ROOT}/{rid}"
        for sub in ("logs","out","scripts","dataset"): os.makedirs(f"{d}/{sub}",exist_ok=True)
        shutil.copy(f"{ST}/p298_arm.sbatch",f"{d}/submit.sbatch")
        shutil.copy(f"{ST}/p298_inside.sh",f"{d}/scripts/p298_inside.sh")
        shutil.copy(f"{ST}/pieces_Pot_{letter}.txt",f"{d}/scripts/pieces.txt")
        s=json.dumps(tmpl,indent=2)
        s=s.replace("p298-Pot_B-"+arm,"p298-"+pot+"-"+arm).replace(POTB_PREP,prepid)
        s=s.replace("Pot_B",pot).replace("Phase 1 pilot","Phase 2 campaign")
        open(f"{d}/run.json","w").write(s+"\n")
        hosts[arm]=rid
    d=f"{ROOT}/{prepid}"
    for sub in ("logs","out","scripts","bin"): os.makedirs(f"{d}/{sub}",exist_ok=True)
    shutil.copy(f"{ST}/p298_prep.sbatch",f"{d}/submit.sbatch")
    shutil.copy(f"{ST}/pieces_Pot_{letter}.txt",f"{d}/scripts/pieces.txt")
    s=json.dumps(tmpl_prep,indent=2)
    s=s.replace(POTB_PREP,prepid).replace("Pot_B",pot).replace("Phase 1 pilot","Phase 2 campaign")
    open(f"{d}/run.json","w").write(s+"\n")
    made.append((prepid,hosts["oursd"],hosts["authb"]))
for m in made: print("\t".join(m))
