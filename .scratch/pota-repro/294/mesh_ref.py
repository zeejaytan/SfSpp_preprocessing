#!/usr/bin/env python3
"""Distance from each authors' breakline to the authors' own DS mesh triangles.

Read-only on the corpus. No geometry written.
"""
import os, sys, json, struct

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
PIECES = [
 ("Pot_C","Pot_C_Piece_03"), ("Pot_D","Pot_D_Piece_22"), ("Pot_D","Pot_D_Piece_27"),
 ("Pot_E","Pot_E_Piece_16"), ("Pot_H","Pot_H_Piece_02"), ("Pot_H","Pot_H_Piece_10"),
 ("Pot_I","Pot_I_Piece_06"), ("Pot_I","Pot_I_Piece_13"), ("Pot_I","Pot_I_Piece_25"),
]

def mesh_path(piece):
    for cand in (os.path.join(CORPUS,"Mesh",piece+"_Mesh_DS.obj"),
                 os.path.join(CORPUS,"Mesh",piece+"_Mesh.obj")):
        if os.path.exists(cand):
            return cand
    return None

def read_obj(path):
    V=[]; F=[]
    with open(path, "r", errors="ignore") as fh:
        for line in fh:
            if line.startswith("v "):
                p=line.split()
                V.append((float(p[1]),float(p[2]),float(p[3])))
            elif line.startswith("f "):
                idx=[]
                for tok in line.split()[1:]:
                    idx.append(int(tok.split("/")[0])-1)
                for k in range(1,len(idx)-1):
                    F.append((idx[0],idx[k],idx[k+1]))
    return V,F

def read_xyz_list(path):
    pts=[]
    with open(path,"r",errors="ignore") as fh:
        for line in fh:
            p=line.split()
            if len(p)>=3:
                try: pts.append((float(p[0]),float(p[1]),float(p[2])))
                except ValueError: continue
    return pts

def read_pcd_xyz(path):
    """ASCII or binary PCD; honours the FIELDS order (authors' files put normals first)."""
    fields=None; size=None; typ=None; count=None; npts=0; data="ascii"; off=0
    with open(path,"rb") as fh:
        while True:
            line=fh.readline()
            if not line: break
            off=fh.tell()
            s=line.decode("ascii",errors="replace").strip()
            k=s.split()
            if not k: continue
            key=k[0].upper()
            if key=="FIELDS": fields=k[1:]
            elif key=="SIZE": size=[int(x) for x in k[1:]]
            elif key=="TYPE": typ=k[1:]
            elif key=="COUNT": count=[int(x) for x in k[1:]]
            elif key=="POINTS": npts=int(k[1])
            elif key=="DATA": data=k[1].lower(); break
        fh.seek(off)
        if data=="ascii":
            pts=[]
            for line in fh:
                v=line.split()
                if len(v)<3: continue
                ix,iy,iz=fields.index("x"),fields.index("y"),fields.index("z")
                pts.append((float(v[ix]),float(v[iy]),float(v[iz])))
            return pts
        # binary
        if count is None: count=[1]*len(fields)
        ncol=sum(count)
        rec=sum(s*c for s,c in zip(size,count))
        fmts={"F":"f","U":"I","I":"i"}
        tags=[]
        for t,c,sz in zip(typ,count,size):
            base=fmts[t]
            tags.append(str(c)+base if c>1 else base)
        st=struct.Struct("".join(tags))
        raw=fh.read(npts*rec)
        pts=[]
        ix,iy,iz=fields.index("x"),fields.index("y"),fields.index("z")
        for r in st.iter_unpack(raw):
            pts.append((float(r[ix]),float(r[iy]),float(r[iz])))
        return pts

def dist_point_tri(P, A, B, C):
    """Vectorised closest distance from one point P to many triangles. Ericson, regions."""
    import numpy as np
    AB=B-A; AC=C-A; AP=P-A
    d1=(AB*AP).sum(1); d2=(AC*AP).sum(1)
    BP=P-B; d3=(AB*BP).sum(1); d4=(AC*BP).sum(1)
    CP=P-C; d5=(AB*CP).sum(1); d6=(AC*CP).sum(1)
    va=d3*d6-d5*d4; vb=d5*d2-d1*d6; vc=d1*d4-d3*d2
    denom=va+vb+vc
    denom=np.where(np.abs(denom)<1e-20,1e-20,denom)
    v=vb/denom; w=vc/denom
    out=np.empty((A.shape[0],3))
    # region tests
    m=(d1<=0)&(d2<=0); out[m]=A[m]
    m=(d3>=0)&(d4<=d3); out[m]=B[m]
    m=(d6>=0)&(d5<=d6); out[m]=C[m]
    m=(vc<=0)&(d1>=0)&(d3<=0); t=np.where((d1-d3)==0,0,d1/(d1-d3)); out[m]=(A+t[:,None]*AB)[m]
    m=(vb<=0)&(d2>=0)&(d6<=0); t=np.where((d2-d6)==0,0,d2/(d2-d6)); out[m]=(A+t[:,None]*AC)[m]
    m=(va<=0)&((d4-d3)>=0)&((d5-d6)>=0); t=np.where(((d4-d3)+(d5-d6))==0,0,(d4-d3)/((d4-d3)+(d5-d6))); out[m]=(B+t[:,None]*(C-B))[m]
    m2=~((d1<=0)&(d2<=0))&~((d3>=0)&(d4<=d3))&~((d6>=0)&(d5<=d6))&~((vc<=0)&(d1>=0)&(d3<=0))&~((vb<=0)&(d2>=0)&(d6<=0))&~((va<=0)&((d4-d3)>=0)&((d5-d6)>=0))
    out[m2]=(A+v[:,None]*AB+w[:,None]*AC)[m2]
    return out

def stats(vals):
    import numpy as np
    a=np.asarray(vals,dtype=float)
    if a.size==0: return {}
    return dict(n=int(a.size), median=round(float(np.median(a)),3),
                p95=round(float(np.percentile(a,95)),3), max=round(float(a.max()),3),
                share_gt2=round(100.0*float((a>2.0).mean()),2))

def main():
    import numpy as np
    print("piece lane pts  mesh_tris  median_mm p95_mm max_mm share_gt2mm")
    rows=[]
    for pot,piece in PIECES:
        mp=mesh_path(piece)
        if not mp:
            print("MISSINGMESH", piece); continue
        V,F=read_obj(mp)
        A=np.asarray(V,dtype=float); idx=np.asarray(F,dtype=int)
        T1=A[idx[:,0]]; T2=A[idx[:,1]]; T3=A[idx[:,2]]
        for lane in (0,1):
            bp=os.path.join(CORPUS,"Breaklines",piece+"_Breakline_%d.pcd"%lane)
            if not os.path.exists(bp):
                print("MISSINGLINE",piece,lane); continue
            pts=read_pcd_xyz(bp)
            d=[]
            for p in pts:
                P=np.asarray(p,dtype=float)
                Q=dist_point_tri(P,T1,T2,T3)
                d.append(float(np.sqrt(((Q-P)**2).sum(1)).min()))
            s=stats(d)
            print("%s %d %d %d %.3f %.3f %.3f %.2f" % (piece,lane,s["n"],T1.shape[0],s["median"],s["p95"],s["max"],s["share_gt2"]))
            rows.append(dict(piece=piece,pot=pot,lane=lane,mesh=os.path.basename(mp),tris=int(T1.shape[0]),**s))
    with open(os.path.join(os.environ.get("OUT","."),"authors_to_mesh.json"),"w") as fh:
        json.dump(rows,fh,indent=1)
    print("[DONE] rows=%d" % len(rows))

main()
