import sys, os, glob, argparse, re

# ticket 51 theta assembler -- mechanical: read every cell.tsv the run wrote and emit
# out/thetas51.tsv (the ticket's 12-column table), then TWO REPORT-ONLY checks against the
# committed reference (stage51/instruments/thetas51.tsv):
#   check U  arm-U theta_formula must reproduce t48_theta_formula to 2 dp (same code path,
#            same clouds as t48 arm V)
#   check C  arm-C crossing must land within 1.5 deg of edge50_glue60_k10 where measured
#            (thetaCross51 uses k=11 including self = edge50's 10 neighbours)
# A check miss is a RESULT recorded in the table, never a non-zero exit: rc!=0 means only that
# the table itself could not be produced (no cells / unreadable cell.tsv).
ap=argparse.ArgumentParser()
ap.add_argument('--cells',required=True,help='cells-pipeline dir holding <PIECE>_arm{C,U}/cell.tsv')
ap.add_argument('--ref',required=True,help='committed thetas51.tsv reference')
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

ref={}
for ln in open(a.ref,encoding='utf-8'):
    if ln.startswith('#'): continue
    f=ln.rstrip('\n').split('\t')
    if f[0]=='piece': continue
    if len(f)>=3: ref[f[0]]=(f[1],f[2])

def first2sizes(s):
    # [STATUS-23] sizes=  ->  first two cluster sizes (c0, c1); '-' when absent
    if not s or s=='-': return '-','-'
    nums=re.findall(r'\d+',s)
    if len(nums)<2: return (nums[0] if nums else '-'),'-'
    return nums[0],nums[1]

rows=[]; misses=[]
cells=sorted(glob.glob(os.path.join(a.cells,'*_arm?','cell.tsv')))
if not cells:
    sys.exit('no cell.tsv under %s -- nothing to assemble'%a.cells)
for c in cells:
    cell=os.path.basename(os.path.dirname(c))
    arm=cell[-1]              # C or U
    piece=cell[:-5]
    kv=read_kv(c)
    rc=kv.get('pipeline_rc','na')
    t45=kv.get('growth45_theta','')
    g51=kv.get('growth51_line','')
    cross=kv.get('growth51_crossing','')
    capped=kv.get('growth51_capped','')
    t51=kv.get('growth51_theta','')
    theta_formula=t45 if t45 else '-'
    if arm=='C':
        crossing=cross if cross else ('none' if g51 else '-')
        theta=t51 if t51 else '-'
    else:
        crossing='-'; capped='-'; theta=t45 if t45 else '-'
    outcome=kv.get('status_outcome','-')
    s0,s1=first2sizes(kv.get('final_sizes','-'))
    p0=kv.get('status_surf0_points','-'); p1=kv.get('status_surf1_points','-')
    rows.append((piece,arm,rc,theta_formula,crossing,capped if capped else '-',theta,outcome,s0,s1,p0,p1))
    r=ref.get(piece,('na','na'))
    if arm=='U':
        try:
            d=abs(float(theta_formula)-float(r[0]))
            if d>0.005: misses.append('%s U theta_formula %s vs t48 %s (d=%.4f > 0.005)'%(piece,theta_formula,r[0],d))
        except ValueError:
            misses.append('%s U theta_formula %s not comparable to t48 %s'%(piece,theta_formula,r[0]))
    else:
        if r[1]=='na':
            pass  # edge50 did not measure this piece: nothing to check
        elif crossing=='none':
            misses.append('%s C crossing=none (edge50 glue60 %s)'%(piece,r[1]))
        else:
            try:
                d=abs(float(crossing)-float(r[1]))
                if d>1.5: misses.append('%s C crossing %s vs edge50 %s (d=%.2f > 1.5)'%(piece,crossing,r[1],d))
            except ValueError:
                misses.append('%s C crossing %s not comparable to edge50 %s'%(piece,crossing,r[1]))

rows.sort(key=lambda r:(r[0],r[1]))
with open(a.out,'w',encoding='utf-8') as f:
    f.write('piece\tarm\tpipeline_rc\ttheta_formula\tcrossing\tcapped\ttheta\toutcome\tc0\tc1\tsurface0_pts\tsurface1_pts\n')
    for r in rows: f.write('\t'.join(r)+'\n')
print('=== %s ==='%a.out)
print(open(a.out).read())
with open(a.check_out,'w',encoding='utf-8') as f:
    f.write('piece\tarm\tvalue\treference\tdelta\tcheck\n')
    for r in rows:
        refv=ref.get(r[0],('na','na'))
        if r[1]=='U':
            f.write('%s\tU\t%s\t%s (t48)\tsee thetas51.tsv\ttheta_formula within 2 dp of t48\n'%(r[0],r[3],refv[0]))
        else:
            chk='within 1.5 deg of edge50' if refv[1]!='na' else 'edge50 na: unchecked'
            f.write('%s\tC\t%s\t%s (edge50)\tsee thetas51.tsv\t%s\n'%(r[0],r[4],refv[1],chk))
print('=== reference checks (%d rows) ==='%len(rows))
if misses:
    print('MISSES (results, not failures):')
    for m in misses: print('  '+m)
else:
    print('no reference misses')
