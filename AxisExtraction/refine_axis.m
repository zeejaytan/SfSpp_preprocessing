function vt_refined = refine_axis(vt_initial, X, method, unused1, unused2, max_iters, tolerance)
%REFINE_AXIS Refine axis of symmetry using iterative optimization
%
% Input:
%   vt_initial (6x1): Initial axis estimate [direction; position]
%   X (6xN): Point cloud data [points; normals]
%   method: Optimization method (2 = biaxial Cao error)
%   unused1, unused2: Unused parameters for compatibility
%   max_iters: Maximum iterations for optimization
%   tolerance: Convergence tolerance
%
% Output:
%   vt_refined (6x1): Refined axis estimate

if nargin < 7
    tolerance = 1e-9;
end
if nargin < 6
    max_iters = 300;
end
if nargin < 3
    method = 2; % Default to biaxial Cao error
end

% Set up optimization functions based on method
switch method
    case 1
        % Single-sided Cao error
        res_func = @(vt) compute_cao_error(vt, X);
        
    case 2
        % Biaxial Cao error (default and most robust)
        res_func = @(vt) compute_biaxial_cao_error(vt, X);
        
    otherwise
        error('Unknown refinement method: %d', method);
end

% Update function for axis parameters
update_func = @cao_update_func;

% Choose robustifier (Huber is robust for axis estimation)
robustifier = @robustifier_huber;

% Perform optimization using Levenberg-Marquardt
try
    [vt_refined, final_error, optimization_log] = optimize_using_lm(...
        vt_initial, res_func, update_func, robustifier, max_iters, tolerance);
    
    % Ensure the refined axis satisfies constraints
    vt_refined(1:3) = vt_refined(1:3) / norm(vt_refined(1:3)); % Unit direction
    vt_refined(4:6) = vt_refined(4:6) - vt_refined(1:3) * (vt_refined(1:3)' * vt_refined(4:6)); % Orthogonal position
    
catch ME
    fprintf('Warning: Axis refinement failed: %s\n', ME.message);
    fprintf('Returning initial axis estimate\n');
    vt_refined = vt_initial;
end

end