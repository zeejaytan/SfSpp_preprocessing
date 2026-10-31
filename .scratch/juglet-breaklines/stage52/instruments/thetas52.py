import sys, os, glob, argparse, re

# ticket 52 theta assembler -- mechanical: read every cell.tsv the run wrote and emit
# out/thetas52.tsv, the ticket's summary table, one row per piece x arm (D/C/X):
#   pipeline_rc, clusters, status_outcome, surf0/surf1 points, paper theta from the log
#   ([SPLITTER-234] theta=), [GROWTH-45] theta, [GROWTH-51] crossing/capped, and the count
# of [GROWTH-52] FALLBACK lines.
# Then the D==C check (theta_check52.tsv): the shipped default (D) must equal the explicit
# request (C) EXACTLY -- chosen theta (post-cap [GROWTH-51] theta) and crossing equal to 5
# decimal places, and surface0/surface1 point counts equal.  A mismatch is a RESULT recorded
# in the table, never a non-zero exit: rc!=0 means only that the table itself could not be
# produced (no cells / unreadable cell.tsv).
ap=argparse.ArgumentParser()
ap.add_argument('--cells',required=True,help='cells-pipeline dir holding <PIECE>_arm{D,C,X}/cell.tsv')
ap.add_argument('--out',required=True)
ap.add_argument('--check-out',required=True)
a=ap.parse_args()

def read_kv(p):
    d={}
    for ln in open(p,encoding='utf-8'):
        ln=ln.rstrip('\n').rstrip('\r')
        if '\t' not in ln: continue
        k,v=ln.split('\t',1)
        d.setdefault(k,v)
    return d

def f5(x):
    try: return '%.5f'%float(x)
    except (TypeError,ValueError): return '-'

rows=[]; bykey={}
cells=sorted(glob.glob(os.path.join(a.cells,'*_arm?','cell.tsv')))
if not cells:
    sys.exit('no cell.tsv under %s -- nothing to assemble'%a.cells)
for c in cells:
    cell=os.path.basename(os.path.dirname(c))
    arm=cell[-1]              # D, C or X
    piece=cell[:-5]
    kv=read_kv(c)
    rc=kv.get('pipeline_rc','na')
    clust=kv.get('pipeline_clusters','-') or '-'
    outcome=kv.get('status_outcome','-')
    p0=kv.get('status_surf0_points','-'); p1=kv.get('status_surf1_points','-')
    paper_log=kv.get('splitter_theta','-') or '-'
    t45=kv.get('growth45_theta','') or '-'
    cross=kv.get('growth51_crossing','') or '-'
    capped=kv.get('growth51_capped','') or '-'
    fb=kv.get('growth52_fallback_lines','0') or '0'
    chosen = kv.get('growth51_theta','') or ('3.4' if arm=='X' else '-')
    r=(piece,arm,rc,clust,outcome,p0,p1,paper_log,t45,cross,capped,fb,chosen)
    rows.append(r); bykey[(piece,arm)]=kv

rows.sort(key=lambda r:(r[0],r[1]))
with open(a.out,'w',encoding='utf-8') as f:
    f.write('piece\tarm\tpipeline_rc\tclusters\tstatus_outcome\tsurf0_pts\tsurf1_pts\tpaper_theta_log\ttheta45\tcrossing_deg\tcapped\tfallback52\tchosen_theta\n')
    for r in rows: f.write('\t'.join(r)+'\n')
print('=== %s ==='%a.out)
print(open(a.out).read())

pieces=sorted(set(p for (p,arm) in bykey if arm in ('D','C')))
lines=['piece\ttheta_D\ttheta_C\ttheta_equal_5dp\tcross_D\tcross_C\tcross_equal_5dp\tsurf0_eq\tsurf1_eq\tD_eq_C']
nmet=0
for p in pieces:
    d=bykey.get((p,'D')); c=bykey.get((p,'C'))
    if not d or not c:
        lines.append('%s\t-\t-\tINCOMPLETE (missing arm)\t-\t-\t-\t-\t-\tREFUTED'%p); continue
    thD=d.get('growth51_theta',''); thC=c.get('growth51_theta','')
    crD=d.get('growth51_crossing',''); crC=c.get('growth51_crossing','')
    s0 = (d.get('status_surf0_points','')==c.get('status_surf0_points',''))
    s1 = (d.get('status_surf1_points','')==c.get('status_surf1_points',''))
    theq = (thD!='' and thC!='' and f5(thD)==f5(thC))
    creq = (crD!='' and crC!='' and f5(crD)==f5(crC))
    ok = theq and creq and s0 and s1
    if ok: nmet+=1
    lines.append('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s'%(
        p,f5(thD) if thD else '-',f5(thC) if thC else '-','MET' if theq else 'REFUTED',
        crD or '-',crC or '-','MET' if creq else 'REFUTED',
        'MET' if s0 else 'REFUTED','MET' if s1 else 'REFUTED','MET' if ok else 'REFUTED'))
with open(a.check_out,'w',encoding='utf-8') as f:
    f.write('\n'.join(lines)+'\n')
print('=== %s (D==C exactness, %d/%d MET) ==='%(a.check_out,nmet,len(pieces)))
print('\n'.join(lines))
