% POTA-12 V1: weighting-only fit on pieces 01-04 (sealed 05-08 never loaded).
% Protocol mirrors run_potsac staging: vote on 10% -> refine sub -> refine full,
% but every ranking/refinement uses the angular cost. Reports vote-top1 and
% refined errors to separate vote gain from refine gain.
function v1_fit()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p12-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);
w = 0.1;
for frag = 1:4
  [C0, C1] = read_surfaces('A', frag);
  SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
  tic;
  [VT, COST] = af_vote(C0, C1, 1000, w, 0);
  t1 = toc;
  [dv, rv, pv] = score_vs_shipped(VT(:,1), SHIP);
  v1 = af_refine(VT(:,1), C0(:,1:10:end), C1(:,1:10:end), w, 300, 1e-3);
  [d1, r1, p1] = score_vs_shipped(v1, SHIP);
  v2 = af_refine(v1, C0, C1, w, 300, 1e-9);
  tic; [d2, r2, p2] = score_vs_shipped(v2, SHIP); t2 = toc;
  fprintf('V1 P%02d votetime=%.0fs nrank-cost-ratio=%.4f | vote (%.2f,%.2f) %s | sub (%.2f,%.2f) %s | full (%.2f,%.2f) %s\n', ...
    frag, t1, COST(1)/COST(100), dv(1), rv(1), passstr(all(pv)), ...
    d1(1), r1(1), passstr(all(p1)), d2(1), r2(1), passstr(all(p2)));
end
end

function s = passstr(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end
