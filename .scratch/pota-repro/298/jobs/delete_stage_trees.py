import glob, os, shutil, subprocess
RUNS="/data/gpfs/projects/punim2657/SfSpp/runs"
preps=sorted(glob.glob(f"{RUNS}/20261026-0126_d1f1a4c_p298-prep-Pot_*"))+sorted(glob.glob(f"{RUNS}/20261026-0046_63cf615_p298-prep-Pot_*"))
tot_files=tot_bytes=0
rows=[]
for d in preps:
    st=os.path.join(d,"stage")
    if not os.path.isdir(st): continue
    files=0; nbytes=0; ext={}
    for root,dirs,fs in os.walk(st):
        for f in fs:
            p=os.path.join(root,f)
            try:
                sz=os.path.getsize(p) if not os.path.islink(p) else 0
            except OSError:
                sz=0
            files+=1; nbytes+=sz
            e=os.path.splitext(f)[1].lower() or "(none)"
            e2,n2=ext.get(e,(0,0)); ext[e]=(e2+1,n2+sz)
    geom=os.path.join(d,"out","geom")
    gf=sum(len(fs) for _,_,fs in os.walk(geom)); gb=sum(os.path.getsize(os.path.join(r,f)) for r,_,fs in os.walk(geom) for f in fs)
    rec=os.path.join(d,"out","GEOMETRY_DELETED.txt")
    with open(rec,"w") as f:
        f.write(f"# ticket 298 Phase 2 cleanup, {os.path.basename(d)}\n")
        f.write(f"deleted_tree\truns/{os.path.basename(d)}/stage\n")
        f.write(f"files_deleted\t{files}\nbytes_deleted\t{nbytes}\n")
        for e in sorted(ext): f.write(f"kind\t{e}\t{ext[e][0]}\t{ext[e][1]}\n")
        f.write(f"kept\tout/geom\t{gf} files\t{gb} bytes\t(the deliverable bundle)\n")
        f.write("why\tstaged/intermediate clouds of one prep run; the frozen corpus is untouched and the bundle in out/geom is kept\n")
    shutil.rmtree(st)
    rows.append((os.path.basename(d), files, nbytes, gf, gb))
    tot_files+=files; tot_bytes+=nbytes
print("prep runs cleaned", len(rows), "files", tot_files, "bytes", tot_bytes)
for r in rows: print(r[0], r[1], r[2], "| kept geom", r[3], r[4])
