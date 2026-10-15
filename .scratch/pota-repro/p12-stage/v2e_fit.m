% POTA-12 V2e: freeze the finder assembly on fit data only (05-08 sealed).
% (a) af_split eps {5,10,20} on 01-04 (must stay 1 component) + synthetic
%     (must split 2). (b) af_find_all on 01-04 + synthetic.
function v2e_fit()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p12-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);
for frag = 1:4
  [C0, C1] = read_surfaces('A', frag);
  C = [C0, C1];
  for eps = [5 10 20]
    [comp, ~] = af_split(C, eps, 300);
    fprintf('V2e-a P%02d eps=%2d ncomp=%d sizes=[%s]\n', frag, eps, max(comp), ...
      num2str(accumarray(comp(comp>0),1)','%d '));
  end
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
A0 = [P0, R(P0)]; A1 = [P1, R(P1)];
[comp, ~] = af_split([A0, A1], 10, 300);
fprintf('V2e-a synth eps=10 ncomp=%d sizes=[%s]\n', max(comp), ...
  num2str(accumarray(comp(comp>0),1)','%d '));
for frag = 1:4
  [Q0, Q1] = read_surfaces('A', frag);
  SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
  tic; [VOUT, NOUT] = af_find_all(Q0, Q1, 0); t = toc;
  [dd, rr, pp] = score_vs_shipped(VOUT, SHIP);
  fprintf('V2e-b P%02d nset=%d counts=[%s] time=%.0fs derr=[%s] rerr=[%s] %s\n', ...
    frag, size(VOUT,2), num2str(NOUT','%d '), t, ...
    num2str(dd','%.2f '), num2str(rr','%.2f '), passstr(all(pp)));
end
tic; [V2, N2] = af_find_all(A0, A1, 0); t = toc;
[dd, rr, pp] = score_vs_shipped(V2, S2);
fprintf('V2e-b synth nset=%d counts=[%s] time=%.0fs derr=[%s] rerr=[%s] %s\n', ...
  size(V2,2), num2str(N2','%d '), t, num2str(dd','%.2f '), num2str(rr','%.2f '), passstr(all(pp)));
end

function s = passstr(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end
