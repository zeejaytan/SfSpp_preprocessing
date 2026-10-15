% POTA-12 V2c rerun: synthetic 2-axis from P01 only (fit data only).
function v2c_fit()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p12-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);
[C0, C1] = read_surfaces('A', 1);
SHIP1 = readmatrix([AXD '/Pot_A_Piece_01_Axis.xyz'], 'FileType','text');
rng(7);
[Q, ~] = qr(randn(3));
if det(Q) < 0, Q(:,1) = -Q(:,1); end
t = [500; -300; 200];
R = @(X) [Q*X(1:3,:) + t; Q*X(4:6,:)];
d1 = SHIP1(1,4:6)'; d1 = d1/norm(d1); p1 = SHIP1(1,1:3)';
d2 = Q*d1; p2 = Q*p1 + t; p2 = p2 - d2*(d2'*p2); p1 = p1 - d1*(d1'*p1);
S2 = [p1', d1'; p2', d2'];
P0 = C0(:,1:2:end); P1 = C1(:,1:2:end);
A0 = [P0, R(P0)]; A1 = [P1, R(P1)];
tic; [VOUT, ~] = af_find(A0, A1, 0); t = toc;
[dd, rr, pp] = score_vs_shipped(VOUT, S2);
fprintf('V2c synth2axis nset=%d time=%.0fs derr=[%s] rerr=[%s] %s\n', ...
  size(VOUT,2), t, num2str(dd','%.2f '), num2str(rr','%.2f '), passstr(all(pp)));
end

function s = passstr(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end
