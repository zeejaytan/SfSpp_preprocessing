% POTA-12 V4: verify the FROZEN assembly (af_find_all + af_polish) on fit data.
% Expected: P01 FAIL(~2.4) P02 PASS P03 PASS P04 FAIL(~3.0); synth nset=2.
% No changes after this except the sealed 05-08 run.
function v4_verify_fit()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p12-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);
for frag = 1:4
  [C0, C1] = read_surfaces('A', frag);
  SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
  tic; [VOUT, NOUT] = af_find_all(C0, C1, 0); t = toc;
  [dd, rr, pp] = score_vs_shipped(VOUT, SHIP);
  fprintf('V4 P%02d nset=%d counts=[%s] time=%.0fs derr=[%s] rerr=[%s] %s\n', ...
    frag, size(VOUT,2), num2str(NOUT','%d '), t, ...
    num2str(dd','%.2f '), num2str(rr','%.2f '), passstr(all(pp)));
end
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
tic; [V2, N2] = af_find_all([P0, R(P0)], [P1, R(P1)], 0); t = toc;
[dd, rr, pp] = score_vs_shipped(V2, S2);
fprintf('V4 synth nset=%d counts=[%s] time=%.0fs derr=[%s] rerr=[%s] %s\n', ...
  size(V2,2), num2str(N2','%d '), t, num2str(dd','%.2f '), num2str(rr','%.2f '), passstr(all(pp)));
end

function s = passstr(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end
