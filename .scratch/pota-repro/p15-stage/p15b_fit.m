% POTA-15 attempt (a) confirmation: ONE run on P06 (sealed 05/07/08 untouched).
% Reports: refine-from-shipped stability + full-chain af_find_all errors vs shipped.
function p15b_fit()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p15-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);

frag = 6;
[C0, C1] = read_surfaces('A', frag);
SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
d = SHIP(1,4:6)'; d = d/norm(d); p = SHIP(1,1:3)';
vship = [d; p];
revS = af_orient(vship, C0, C1);
v1 = af_refine_raw(vship, C0(:,1:10:end), C1(:,1:10:end), revS, 1, 300, 1e-3);
vr = af_refine_raw(v1, C0, C1, revS, 1, 300, 1e-9);
[dds, rrs, pps] = score_vs_shipped(vr, SHIP);
fprintf('P15b P06 refine-from-shipped (%.2f,%.2f) %s\n', dds(1), rrs(1), passstr(all(pps)));
tic; [VOUT, NOUT] = af_find_all(C0, C1, 0); tA = toc;
[dd, rr, pp] = score_vs_shipped(VOUT, SHIP);
fprintf('P15b P06 chain nset=%d counts=[%s] time=%.0fs derr=[%s] rerr=[%s] %s\n', ...
  size(VOUT,2), num2str(NOUT','%d '), tA, ...
  num2str(dd','%.2f '), num2str(rr','%.2f '), passstr(all(pp)));
end

function s = passstr(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end
