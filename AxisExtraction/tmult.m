function C = tmult(A, B, transpose_flag)
%TMULT Tensor multiplication along the last two dimensions
%
% C = tmult(A, B) performs matrix multiplication along the last two dimensions
% for tensors A and B. For 3D tensors, this is equivalent to:
%   C(:,:,i) = A(:,:,i) * B(:,:,i) for each slice i
%
% C = tmult(A, B, true) transposes A before multiplication:
%   C(:,:,i) = A(:,:,i)' * B(:,:,i) for each slice i
%
% Input:
%   A: Tensor of size [m x n x k] or matrix [m x n]
%   B: Tensor of size [n x p x k] or matrix [n x p] 
%   transpose_flag: If true, transpose A before multiplication
%
% Output:
%   C: Result tensor of size [m x p x k] (or [n x p x k] if transpose_flag=true)

if nargin < 3
    transpose_flag = false;
end

% Handle 2D case (regular matrix multiplication)
if ndims(A) == 2 && ndims(B) == 2
    if transpose_flag
        C = A' * B;
    else
        C = A * B;
    end
    return;
end

% Handle 3D case (tensor multiplication)
if ndims(A) == 3 || ndims(B) == 3
    % Get sizes
    size_A = size(A);
    size_B = size(B);
    
    % Extend to 3D if needed
    if ndims(A) == 2
        A = repmat(A, [1, 1, size_B(3)]);
        size_A = size(A);
    end
    if ndims(B) == 2
        B = repmat(B, [1, 1, size_A(3)]);
        size_B = size(B);
    end
    
    % Ensure same number of slices
    num_slices = max(size_A(3), size_B(3));
    if size_A(3) == 1 && num_slices > 1
        A = repmat(A, [1, 1, num_slices]);
    end
    if size_B(3) == 1 && num_slices > 1
        B = repmat(B, [1, 1, num_slices]);
    end
    
    % Determine output size
    if transpose_flag
        output_rows = size_A(2);
        output_cols = size_B(2);
    else
        output_rows = size_A(1);
        output_cols = size_B(2);
    end
    
    % Initialize output tensor
    C = zeros(output_rows, output_cols, num_slices);
    
    % Perform slice-wise multiplication
    for k = 1:num_slices
        if transpose_flag
            C(:,:,k) = A(:,:,k)' * B(:,:,k);
        else
            C(:,:,k) = A(:,:,k) * B(:,:,k);
        end
    end
    
    return;
end

% Fallback: handle higher-dimensional tensors
error('tmult: Tensors with more than 3 dimensions are not supported');

end