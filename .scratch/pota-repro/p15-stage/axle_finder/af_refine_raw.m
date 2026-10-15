function vt_out = af_refine_raw(vt_init, C0, C1, rev, W, max_iters, func_tol)
% AF_REFINE_RAW LM refinement on fixed-orientation GM raw Cao cost (P15a:
% Huber -> GM so refine optimises the same robustifier the vote selects
% with; residual only — LM skeleton, frozen rev, signature unchanged).
% rev(q): use reversed normals for surface q (frozen at the vote winner, no
% per-point softmin gaming during the walk). W: GM width in residual units
% (callers pass 1.0 = robustifier_gm default = selection cost width).
% Residual vector t with 0.5*sum(t.^2) = sum of per-point GM rho.
if nargin < 5 || isempty(W), W = 10; end
if nargin < 6 || isempty(max_iters), max_iters = 300; end
if nargin < 7 || isempty(func_tol), func_tol = 1e-9; end
x = vt_init(:);
[r, cost] = resid(x);
m = numel(r);
d = x(1:3)/norm(x(1:3)); P = eye(3) - d*d';
lambda = 1e-1; lam_grow = 2.0; h_base = 1e-7;
for iter = 1:max_iters
  J = zeros(m, 6);
  for k = 1:6
    h = h_base*(1 + abs(x(k)));
    xp = x; xp(k) = xp(k) + h;
    [rp, ~] = resid(xp);
    J(:,k) = (rp - r)/h;
  end
  J(:,1:3) = J(:,1:3)*P;
  JTJ = J'*J; grad = J'*r;
  if norm(grad) < 1e-12, break; end
  improved = false;
  for trial = 1:10
    dx = -(JTJ + lambda*eye(6)) \ grad;
    x_cand = cao_update_func(x, dx);
    [r_cand, cost_cand] = resid(x_cand);
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
  if dcost < 0.5*func_tol*max(cost,1e-300), break; end
  if cost < func_tol, break; end
end
vt_out = x;

  function [t, c] = resid(xx)
    Cs = {C0, C1}; tt = cell(1,2); cc = 0;
    for q = 1:2
      Rq = compute_cao_error(xx, Cs{q}, rev(q)); % pristine, read-only (r2fix on path)
      sq = sum(Rq.^2, 1);
      tau2 = W*W;
      rho = 2*sq*tau2 ./ (sq + tau2); % GM rho, same robustifier as the vote
      tt{q} = sqrt(max(rho,0))';
      cc = cc + sum(rho);
    end
    t = [tt{1}; tt{2}];
    c = 0.5*sum(t.^2);
  end
end
