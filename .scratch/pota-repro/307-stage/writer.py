import json, sys
p, jobid, runid = sys.argv[1], sys.argv[2], sys.argv[3]
o = json.load(open(p))
o["runid"] = runid
o["jobid"] = jobid
o["slurm_submit_out"] = jobid
json.dump(o, open(p, "w"), indent=1)
open(p, "a").write("\n")
