% POTA-12 V2c-diag: where does the 2nd synthetic axis die?
function v2c_diag()
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
[VT, CR] = af_vote(A0, A1, 3000, 0.1, 0, 'raw', 12);
fprintf('vote costs: best=%.4f p10=%.4f p50=%.4f worst=%.4f\n', CR(1), CR(10), CR(50), CR(end));
for k = [1:10, 20, 50, 100, 200, 500, 1000]
  [dd, rr, ~] = score_vs_shipped(VT(:,k), S2);
  fprintf('rank %4d cost=%.4f ax1 (%.2f,%.2f) ax2 (%.2f,%.2f)\n', k, CR(k), dd(1), rr(1), dd(2), rr(2));
end
[VC, CC] = af_cluster(VT, CR, 10, 2, 1.1, 6);
fprintf('clusters: %d\n', size(VC,2));
for k = 1:size(VC,2)
  [dd, rr, ~] = score_vs_shipped(VC(:,k), S2);
  fprintf('cl %d cost=%.4f ax1 (%.2f,%.2f) ax2 (%.2f,%.2f)\n', k, CC(k), dd(1), rr(1), dd(2), rr(2));
end
end
