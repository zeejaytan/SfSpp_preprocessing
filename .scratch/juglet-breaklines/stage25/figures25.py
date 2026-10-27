#!/usr/bin/env python3
"""ticket 25 figures: one strip of five rungs per (arm, piece), r1|r2|r3|r4|r5 left to right.

Fixed colour-to-cluster-id map shared by every panel of every figure (per-panel colouring
would make a merge and a renumbering look the same). Grey is always "no cluster": rung 1's
reference cloud, points never claimed, rung-4 rejections and rung-5 points on neither surface.
Camera, axis scale and scale bar are identical across every panel of a figure. One shared
legend per figure lists each colour with that cluster's size at each rung.

usage: figures25.py <rundir>     writes <rundir>/out/figs/*.png and out/figures25.txt
"""
import sys, os, json

PALETTE = {-1: '#b3b3b3', 0: '#1f77b4', 1: '#d62728', 2: '#2ca02c', 3: '#9467bd',
           4: '#ff7f0e', 5: '#8c564b', 6: '#e377c2', 7: '#17becf'}
RUNGS = [('r1', 'r1_downsampled'), ('r2', 'r2_clusters_premerge'), ('r3', 'r3_after_merge'),
         ('r4', 'r4_after_reassign'), ('r5', 'r5_write')]
REJECT = (5, 6)

def read_dump(path):
    with open(path, 'rb') as f:
        raw = f.read()
    i = raw.find(b'end_header')
    if i < 0:
        raise ValueError('no end_header: ' + path)
    end = raw.find(b'\n', i)
    hdr = raw[:end].decode('ascii', 'replace').splitlines()
    n = 0
    for line in hdr:
        t = line.split()
        if len(t) >= 3 and t[0] == 'element' and t[1] == 'vertex':
            n = int(t[2])
    body = raw[end + 1:].decode('ascii', 'replace').splitlines()
    xs, ys, zs, cid, rsn = [], [], [], [], []
    for line in body:
        v = line.split()
        if len(v) < 8:
            continue
        xs.append(float(v[0])); ys.append(float(v[1])); zs.append(float(v[2]))
        cid.append(int(v[6])); rsn.append(int(v[7]))
        if len(xs) >= n:
            break
    return xs, ys, zs, cid, rsn

def sizes_per_rung(dumpdir):
    """{cluster_id: {rung: count}} for the legend, plus grey counts"""
    out = {}
    for rung, base in RUNGS:
        p = os.path.join(dumpdir, base + '.ply')
        if not os.path.isfile(p):
            continue
        xs, ys, zs, cid, rsn = read_dump(p)
        for c in cid:
            out.setdefault(c, {}).setdefault(rung, 0)
            out[c][rung] += 1
    return out

def pick_bar(span):
    for b in (1.0, 2.0, 5.0, 10.0, 20.0, 50.0):
        if b >= span / 6.0:
            return b
    return 100.0

def draw_figure(rows, title, outpath, dpi=120, panel_in=4.0):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    nrows = len(rows)
    fig = plt.figure(figsize=(panel_in * 5, panel_in * nrows + 1.6), dpi=dpi)
    gs = fig.add_gridspec(nrows, 6)
    # one set of limits per figure, from every panel: identical scale everywhere
    lims = None
    data = []
    for row in rows:
        panels = []
        for rung, base in RUNGS:
            p = os.path.join(row['dumpdir'], base + '.ply')
            panels.append(read_dump(p) if os.path.isfile(p) else None)
        data.append(panels)
        for panel in panels:
            if not panel:
                continue
            xs, ys, zs = panel[0], panel[1], panel[2]
            if not xs:
                continue
            if lims is None:
                lims = [[min(xs), max(xs)], [min(ys), max(ys)], [min(zs), max(zs)]]
            else:
                lims[0] = [min(lims[0][0], min(xs)), max(lims[0][1], max(xs))]
                lims[1] = [min(lims[1][0], min(ys)), max(lims[1][1], max(ys))]
                lims[2] = [min(lims[2][0], min(zs)), max(lims[2][1], max(zs))]
    if lims is None:
        raise SystemExit('no dump points for ' + title)
    centre = [(lo + hi) / 2.0 for lo, hi in lims]
    half = max((hi - lo) for lo, hi in lims) * 0.55
    lim3 = [(c - half, c + half) for c in centre]
    sb = pick_bar(2 * half)
    span_mm = 2 * half
    pixels = panel_in * dpi
    mm_per_px = span_mm / pixels

    legend_handles = {}
    for r, row in enumerate(rows):
        for c, (rung, base) in enumerate(RUNGS):
            ax = fig.add_subplot(gs[r, c], projection='3d')
            panel = data[r][c]
            if panel is None:
                ax.text2D(0.5, 0.5, 'rung not written', ha='center', va='center', transform=ax.transAxes)
            else:
                xs, ys, zs, cid, rsn = panel
                groups = {}
                for i in range(len(xs)):
                    key = (cid[i], (rsn[i] in REJECT) if rung == 'r4' else False)
                    groups.setdefault(key, ([], [], []))
                    groups[key][0].append(xs[i]); groups[key][1].append(ys[i]); groups[key][2].append(zs[i])
                for (k, rejected), (gx, gy, gz) in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
                    if rejected:
                        ax.scatter(gx, gy, gz, s=3, c=PALETTE[-1], depthshade=False,
                                   label=None, marker='o', linewidths=0)
                    else:
                        col = PALETTE.get(k, PALETTE[-1])
                        ax.scatter(gx, gy, gz, s=7, c=col, depthshade=False, linewidths=0)
                        if col not in legend_handles:
                            legend_handles[col] = k
            ax.set_xlim(*lim3[0]); ax.set_ylim(*lim3[1]); ax.set_zlim(*lim3[2])
            try:
                ax.set_box_aspect((1, 1, 1))
            except Exception:
                pass
            ax.view_init(elev=22, azim=-62)
            ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
            ax.set_title('%s  %s' % (rung, row['label']) if r == 0 else rung, fontsize=8)
            # scale bar: same value and same place in every panel of this figure
            x0 = lim3[0][0] + 0.06 * (lim3[0][1] - lim3[0][0])
            y0 = lim3[1][1] - 0.06 * (lim3[1][1] - lim3[1][0])
            z0 = lim3[2][0] + 0.04 * (lim3[2][1] - lim3[2][0])
            ax.plot([x0, x0 + sb], [y0, y0], [z0, z0], color='black', linewidth=3)
            ax.text(x0, y0, z0 - 0.10 * (lim3[2][1] - lim3[2][0]), '%g mm' % sb, fontsize=7)
            if c == 0 and r > 0:
                ax.set_ylabel(row['label'], fontsize=8)
    # one shared legend, each colour with that cluster's size at each rung
    handles = []
    labels = []
    for col, k in sorted(legend_handles.items(), key=lambda kv: (kv[1] if kv[1] is not None else 99)):
        handles.append(plt.Line2D([], [], marker='o', color='w', markerfacecolor=col, markersize=7, linewidth=0))
        parts = []
        for row in rows:
            sp = row['sizes']
            seq = ' '.join('%s %s' % (r, sp.get(k, {}).get(r, '-')) for r, _ in RUNGS[1:])
            parts.append(('%s: ' % row['label'] if len(rows) > 1 else '') + seq)
        labels.append('cluster id %s  (%s)' % (k, ' | '.join(parts)))
    grey_parts = []
    for row in rows:
        sp = row['sizes']
        grey_parts.append(('%s: ' % row['label'] if len(rows) > 1 else '') +
                          ' '.join('%s %s' % (r, sp.get(-1, {}).get(r, '-')) for r, _ in RUNGS))
    handles.append(plt.Line2D([], [], marker='o', color='w', markerfacecolor=PALETTE[-1], markersize=6, linewidth=0))
    labels.append('grey = no cluster: r1 reference cloud, never claimed, r4 rejected, r5 not written  (%s)'
                  % ' | '.join(grey_parts))
    fig.legend(handles, labels, loc='lower center', ncol=1, fontsize=7, frameon=False,
               bbox_to_anchor=(0.5, 0.005))
    fig.suptitle('%s   five rungs left to right, identical camera and scale in every panel, '
                 'scale bar %g mm, %.3f mm per pixel' % (title, sb, mm_per_px), fontsize=9)
    fig.tight_layout(rect=(0, 0.10 + 0.03 * max(1, len(labels)), 1, 0.97))
    fig.savefig(outpath, dpi=dpi)
    plt.close(fig)
    w = int(panel_in * 5 * dpi)
    h = int((panel_in * nrows + 1.6) * dpi)
    return dict(path=outpath, panels=5 * nrows, width_px=w, height_px=h, span_mm=span_mm,
                mm_per_px=mm_per_px, scale_bar_mm=sb, rows=nrows)

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    figdir = os.path.join(root, 'out', 'figs')
    os.makedirs(figdir, exist_ok=True)

    def row(arm, piece):
        d = os.path.join(root, 'out', 'dump', arm, piece)
        return dict(arm=arm, piece=piece, label='%s %s' % (piece.replace('Juglet_Piece_', 'J'), arm),
                    dumpdir=d, sizes=sizes_per_rung(d))

    specs = [
        ('F1_piece3_armB', [row('B', 'Juglet_Piece_3')], 'F1 Juglet_Piece_3 arm B (defaults): a merge fusing two patches of one wall'),
        ('F2_piece3_armE', [row('E', 'Juglet_Piece_3')], 'F2 Juglet_Piece_3 arm E (native density, chain off)'),
        ('F3_piece2_armB', [row('B', 'Juglet_Piece_2')], 'F3 Juglet_Piece_2 arm B (defaults): zero regions'),
        ('F4_piece5_armB_armD', [row('B', 'Juglet_Piece_5'), row('D', 'Juglet_Piece_5')],
         'F4 Juglet_Piece_5 rows B and D: one region vs the genuine wall pair'),
        ('F5_piece7_armE', [row('E', 'Juglet_Piece_7')], 'F5 Juglet_Piece_7 arm E: the known-good pair'),
        ('F6_piece7_armB', [row('B', 'Juglet_Piece_7')], 'F6 Juglet_Piece_7 arm B: two coplanar patches'),
    ]
    report = []
    for name, rows, title in specs:
        out = os.path.join(figdir, name + '.png')
        missing = [r['label'] for r in rows if not os.path.isdir(r['dumpdir'])]
        missing += [r['label'] + ':' + base for r in rows for rung, base in RUNGS
                    if not os.path.isfile(os.path.join(r['dumpdir'], base + '.ply'))]
        try:
            info = draw_figure(rows, title, out)
            info['name'] = name
            info['missing_rungs'] = missing
            report.append(info)
            print('[FIG25] %s %dx%d px mm_per_px=%.4f bar=%gmm rows=%d missing=%d'
                  % (out, info['width_px'], info['height_px'], info['mm_per_px'], info['scale_bar_mm'],
                     info['rows'], len(missing)))
        except Exception as e:
            report.append(dict(name=name, path=out, error='%s: %s' % (type(e).__name__, e), missing_rungs=missing))
            print('[FIG25] %s NOT DRAWN %s: %s' % (name, type(e).__name__, e))
    with open(os.path.join(root, 'out', 'figures25.txt'), 'w') as f:
        f.write(json.dumps(report, indent=1) + '\n')
    print('[FIG25] report rows=%d' % len(report))

if __name__ == '__main__':
    main()
