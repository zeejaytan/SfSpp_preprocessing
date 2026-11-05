import io
p=r"C:/PR/worktrees/sfs/310/sfs_axes/potsac.py"
s=io.open(p,encoding="utf-8").read()
blk=io.open(r"C:/PR/worktrees/sfs/310/.scratch/pota-repro/310-stage/warrant_block.txt",encoding="utf-8").read()
key="def run_potsac_union("
assert s.count(key)==1
assert "The union rule, one warrant per term" not in s
s=s.replace(key, blk+key)
io.open(p,"w",encoding="utf-8",newline="\n").write(s)
print("inserted", len(blk))
