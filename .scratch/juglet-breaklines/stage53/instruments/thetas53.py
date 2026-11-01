import sys, os, glob, argparse

# ticket 53 theta assembler -- mechanical: read every cell.tsv the run wrote and emit
# out/thetas53.tsv, the ticket's summary table, one row per piece x arm (W/C/X):
#   pipeline_rc, clusters, status_outcome, surf0/surf1 points, the theta the pipeline
#   actually grew with ([SPLITTER-234] theta=), [GROWTH-45] theta, [GROWTH-51]
#   crossing/capped, and the walk's own [GROWTH-53] theta_split / theta_ship / fallback.
# Then theta_check53.tsv -- the ticket's prediction-1 check, per piece:
#   W reproduce: the pipeline's paper-grow thetaDeg must equal the walk's theta_ship to
#     5 decimal places (the pipeline grows at the theta the walk chose);
#   W ship==0.9*split to 5 dp unless FALLBACK (theta_ship=3.4 then);
#   C and X must carry NO [GROWTH-53] line (the walk is armed only by SFS_GROWTH_WALK).
# A mismatch is a RESULT recorded in the table, never a non-zero exit: rc!=0 means only
# that the table itself could not be produced (no cells / unreadable cell.tsv).
ap=argparse.ArgumentParser()
ap.add_argument('--cells',required=True,help='cells-pipeline dir holding <PIECE>_arm{W,C,X}/cell.tsv')
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
    arm=cell[-1]              # W, C or X
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
    tsplit=kv.get('growth53_theta_split','') or '-'
    tship=kv.get('growth53_theta_ship','') or '-'
    fb=kv.get('growth53_fallback','-') or '-'
    chosen = kv.get('growth53_theta_ship','') if arm=='W' else (kv.get('growth51_theta','') if arm=='C' else '3.4')
    r=(piece,arm,rc,clust,outcome,p0,p1,paper_log,t45,cross,capped,tsplit,tship,fb,chosen)
    rows.append(r); bykey[(piece,arm)]=kv

rows.sort(key=lambda r:(r[0],r[1]))
with open(a.out,'w',encoding='utf-8') as f:
    f.write('piece\tarm\tpipeline_rc\tclusters\tstatus_outcome\tsurf0_pts\tsurf1_pts\tpaper_theta_log\ttheta45\tcrossing_deg\tcapped\ttheta_split\ttheta_ship\tfallback\tchosen_theta\n')
    for r in rows: f.write('\t'.join(r)+'\n')
print('=== %s ==='%a.out)
print(open(a.out).read())

# ---- prediction 1 + wiring checks, per piece
pieces=sorted(set(p for (p,arm) in bykey if arm=='W'))
lines=['piece\tW_ship\tW_split\tpipeline_thetaDeg\tship_eq_pipeline_5dp\tship_eq_0.9split\tfallback\tC_no_53\tX_no_53\tall_ok']
nmet=0
for p in pieces:
    w=bykey.get((p,'W')); c=bykey.get((p,'C')); x=bykey.get((p,'X'))
    if not w:
        lines.append('%s\t-\t-\t-\tINCOMPLETE (missing arm W)\t-\t-\t-\t-\tREFUTED'%p); continue
    ship=w.get('growth53_theta_ship','')
    split=w.get('growth53_theta_split','')
    fb=w.get('growth53_fallback','no')
    # the pipeline's own grow theta: [PAPER-234] paper grow thetaDeg=<v>
    pgt=''
    pgf=w.get('paper_grow_first','')
    if 'thetaDeg=' in pgf:
        pgt=pgf.split('thetaDeg=')[1].split()[0]
    eq_pipe = (ship!='' and pgt!='' and f5(ship)==f5(pgt))
    if fb=='yes':
        eq_ship='n/a FALLBACK'
        eq_pipe_ok = (ship!='' and pgt!='' and f5(ship)==f5(pgt) and f5(pgt)=='3.40000')
    else:
        eq_ship = (ship!='' and split!='' and f5(ship)==f5(0.9*float(split)))
        eq_pipe_ok = eq_pipe
    c_no = (not c) or (c.get('growth53_line','')=='')
    x_no = (not x) or (x.get('growth53_line','')=='')
    ok = eq_pipe_ok and (fb=='yes' or eq_ship) and c_no and x_no
    if ok: nmet+=1
    def yn(b): return 'MET' if b else 'REFUTED'
    lines.append('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s'%(
        p, f5(ship) if ship else '-', f5(split) if (split and split!='none') else '-',
        pgt or '-', yn(eq_pipe) if fb!='yes' else yn(eq_pipe_ok),
        eq_ship if fb=='yes' else yn(eq_ship), fb,
        yn(c_no), yn(x_no), 'MET' if ok else 'REFUTED'))
with open(a.check_out,'w',encoding='utf-8') as f:
    f.write('\n'.join(lines)+'\n')
print('=== %s (W ladder==pipeline theta 5dp + wiring, %d/%d MET) ==='%(a.check_out,nmet,len(pieces)))
print('\n'.join(lines))
