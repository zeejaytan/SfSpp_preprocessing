function vt_out = af_refine(vt_init, C0, C1, w, max_iters, func_tol)
% AF_REFINE Levenberg-Marquardt on the angular-cost residual with weights
% FROZEN at vt_init (af_residf): the objective cannot game its own weights
% while walking. Manifold retraction via pristine cao_update_func (read-only
% reuse). Iteration skeleton adapted from the 09 R3 scaffold.
if nargin < 4 || isempty(w), w = 0.1; end
if nargin < 5 || isempty(max_iters), max_iters = 300; end
if nargin < 6 || isempty(func_tol), func_tol = 1e-9; end
x = vt_init(:);
[F0, F1] = af_freeze_weights(x, C0, C1);
[r, cost] = af_residf(x, C0, C1, w, F0, F1);
c0 = cost;
m = numel(r);
d = x(1:3)/norm(x(1:3)); P = eye(3) - d*d';
lambda = 1e-1; lam_grow = 2.0; h_base = 1e-7;
niter = 0;
for iter = 1:max_iters
  J = zeros(m, 6);
  for k = 1:6
    h = h_base*(1 + abs(x(k)));
    xp = x; xp(k) = xp(k) + h;
    [rp, ~] = af_residf(xp, C0, C1, w, F0, F1);
    J(:,k) = (rp - r)/h;
  end
  J(:,1:3) = J(:,1:3)*P;
  JTJ = J'*J; grad = J'*r;
  if norm(grad) < 1e-12, break; end
  improved = false;
  for trial = 1:10
    dx = -(JTJ + lambda*eye(6)) \ grad;
    x_cand = cao_update_func(x, dx);
    [r_cand, cost_cand] = af_residf(x_cand, C0, C1, w, F0, F1);
    pred = 0.5*(sum(r.^2) - sum((r + J*dx).^2));
    if pred > 0, rho_q = (0.5*(cost - cost_cand))/pred; else, rho_q = -1; end
    if rho_q > 0 && isfinite(cost_cand)
      dcost = 0.5*(cost - cost_cand);
      x = x_cand; r = r_cand; cost = cost_cand;
      d = x(1:3)/norm(x(1:3)); P = eye(3) - d*d';
      lambda = max(1e-14, lambda/3); lam_grow = 2.0;
      improved = true;
      break;
    end
    lambda = min(1e14, lambda*lam_grow); lam_grow = lam_grow*2;
  end
  if ~improved, break; end
  niter = iter;
  if dcost < 0.5*func_tol*max(cost,1e-300), break; end
  if cost < func_tol, break; end
end
if strcmp(getenv('P12_VERBOSE'),'1')
  fprintf('af_refine: iters=%d cost %.6e -> %.6e\n', niter, c0, cost);
end
vt_out = x;
end
