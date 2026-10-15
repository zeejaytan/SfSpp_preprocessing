% POTA-16 phase 2 (b): multi-start refine of top-6 diverse vote modes,
% round winner by full-residual GM cost. Before/after on 05/07/08 + P06 guard.
function p16c_fit()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p16-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);

for frag = [5,6,7,8]
  [C0, C1] = read_surfaces('A', frag);
  SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
  tic; [VOUT, NOUT] = af_find_all(C0, C1, 0); tA = toc;
  [dd, rr, pp] = score_vs_shipped(VOUT, SHIP);
  fprintf('P16c P%02d chain(B) nset=%d nans=%d counts=[%s] time=%.0fs derr=[%s] rerr=[%s] %s\n', ...
    frag, size(VOUT,2), size(SHIP,1), num2str(NOUT','%d '), tA, ...
    num2str(dd','%.2f '), num2str(rr','%.2f '), passstr(all(pp)));
end
end

function s = passstr(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end
