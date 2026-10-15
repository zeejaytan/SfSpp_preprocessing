function [r, c] = af_resid(vt, C0, C1, w)
% AF_RESID residual vector for LM: 0.5*sum(r.^2) tracks AF_WCOST/2, so the
% argmin is identical to af_wcost's. Per surface: r_s = sqrt(conf*rho/sumconf/2).
if nargin < 4 || isempty(w), w = 0.1; end
tau2 = w*w; s = 100;
Cs = {C0, C1}; rs = cell(1,2);
for q = 1:2
  X = Cs{q};
  [Rfw, Rrv, nT2, nT3] = af_parts(vt, X);
  den = max(nT2, 5);
  qf = sum((Rfw ./ den).^2, 1);
  qr = sum((Rrv ./ den).^2, 1);
  cm = min(qf, qr);
  qq = -1/s*log(exp(s*-(qf-cm)) + exp(s*-(qr-cm))) + cm;
  rho = 2*qq*tau2 ./ (qq + tau2);
  conf = min(nT3, 1);
  sc = max(sum(conf), 1e-12);
  rs{q} = sqrt(conf .* rho / sc / 2)';
end
r = [rs{1}; rs{2}];
c = 0.5*sum(r.^2);
end
