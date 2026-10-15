% POTA-12 V5 FROZEN VALIDATION on sealed pieces 05-08. RUN ONCE. No finder
% changes after this point regardless of outcome. Finder = af_find_all as
% verified in V4 (job 33086913): vote 6pt/6000 raw-GM -> orient freeze ->
% fixed-orient Huber W=1 refine -> sequential peel by inlier count
% (minfrac 10%, maxK 4) per spatial component (eps 10mm) -> hard-IRLS x8
% polish -> position-aware dedup (10deg/2mm). Seed 0 throughout.
function v5_validate()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p12-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);
for frag = 5:8
  [C0, C1] = read_surfaces('A', frag);
  SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
  fprintf('V5 P%02d nAns=%d npts=(%d,%d)\n', frag, size(SHIP,1), size(C0,2), size(C1,2));
  tic; [VOUT, NOUT] = af_find_all(C0, C1, 0); t = toc;
  [dd, rr, pp] = score_vs_shipped(VOUT, SHIP);
  fprintf('V5 P%02d nset=%d counts=[%s] time=%.0fs derr=[%s] rerr=[%s] %s\n', ...
    frag, size(VOUT,2), num2str(NOUT','%d '), t, ...
    num2str(dd','%.2f '), num2str(rr','%.2f '), passstr(all(pp)));
end
end

function s = passstr(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end
