function [r, c] = af_residf(vt, C0, C1, w, F0, F1)
% AF_RESIDF residual vector with FROZEN weights (fixed at vote winner):
% 0.5*sum(r.^2) == frozen cost. No renormalization gaming while LM walks.
if nargin < 4 || isempty(w), w = 0.1; end
tau2 = w*w; s = 100;
Cs = {C0, C1}; Fs = {F0, F1}; rs = cell(1,2); cc = 0;
for q = 1:2
  X = Cs{q}; F = Fs{q};
  [Rfw, Rrv, nT2, ~] = af_parts(vt, X);
  den = max(nT2, 5);
  qf = sum((Rfw ./ den).^2, 1);
  qr = sum((Rrv ./ den).^2, 1);
  cm = min(qf, qr);
  qq = -1/s*log(exp(s*-(qf-cm)) + exp(s*-(qr-cm))) + cm;
  rho = 2*qq*tau2 ./ (qq + tau2);
  rs{q} = sqrt(F .* rho)';
  cc = cc + sum(F .* rho);
end
r = [rs{1}; rs{2}];
c = 0.5*sum(r.^2);
end
