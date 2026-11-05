import io
p=r"C:/PR/worktrees/sfs/310/sfs_axes/potsac.py"
s=io.open(p,encoding="utf-8").read()
head,sep,tail=s.rpartition("return reps[:, order[:max_candidates]]")
assert sep and tail.strip()=="", (sep, repr(tail[:40]))
s=head+"return reps[:, order]"
io.open(p,"w",encoding="utf-8",newline="\n").write(s)
print("ok", repr(s[-40:]))
