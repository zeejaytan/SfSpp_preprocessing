% Debug the compute_cao_error cross product issue
fprintf('=== Debugging compute_cao_error Cross Product Issue ===\n');

try
    [C0, C1] = read_surfaces('A', 1, false);
    C = [C0, C1];
    decimated_C = C(:,1:10:size(C,2));
    
    % Reproduce the exact error condition
    rng(12345);  % Use the seed that caused the error
    
    % Normalize normals
    decimated_C(4:6,:) = decimated_C(4:6,:) ./ sqrt(sum(decimated_C(4:6,:).^2));
    
    % Get the problematic sample
    num_sample_set = 6;
    kidx = randsample(size(decimated_C, 2), num_sample_set);
    Cs = decimated_C(:, kidx);
    
    % Apply preprocessing
    mCs = mean(Cs(1:3,:), 2);
    Cs(1:3,:) = Cs(1:3,:) - mCs;
    scale = mean(abs(Cs(:)));
    Cs(1:3,:) = Cs(1:3,:) / scale;
    
    % Get vt from compute_pottmann_axis (this works)
    vt = compute_pottmann_axis(Cs);
    fprintf('vt from compute_pottmann_axis size: %dx%d\n', size(vt, 1), size(vt, 2));
    
    % Now call compute_biaxial_cao_error which calls compute_cao_error
    fprintf('\nCalling compute_biaxial_cao_error...\n');
    fprintf('vt size: %dx%d, decimated_C size: %dx%d\n', size(vt, 1), size(vt, 2), size(decimated_C, 1), size(decimated_C, 2));
    
    try
        combined_err = compute_biaxial_cao_error(vt, decimated_C);
        fprintf('✓ Success! combined_err size: %dx%d\n', size(combined_err, 1), size(combined_err, 2));
    catch ME
        fprintf('❌ Error in compute_biaxial_cao_error: %s\n', ME.message);
        
        % Step into compute_cao_error manually to debug the cross product
        fprintf('\nStepping into compute_cao_error manually...\n');
        
        X = decimated_C;
        fprintf('X size: %dx%d\n', size(X, 1), size(X, 2));
        fprintf('vt size: %dx%d\n', size(vt, 1), size(vt, 2));
        
        % Line 19: reshape vt
        vt_reshaped = reshape(vt, 6, 1, []);
        fprintf('vt_reshaped size: %dx%dx%d\n', size(vt_reshaped, 1), size(vt_reshaped, 2), size(vt_reshaped, 3));
        
        % Line 20: T1 calculation
        T1 = bsxfun(@minus, X(1:3,:), vt_reshaped(4:6,:,:));
        fprintf('T1 size: %dx%d\n', size(T1, 1), size(T1, 2));
        
        % Line 21: The problematic cross product
        fprintf('\nAttempting problematic cross product...\n');
        fprintf('T1 size: %dx%d\n', size(T1, 1), size(T1, 2));
        fprintf('vt(1:3,:,:) size after reshape: %dx%dx%d\n', ...
                size(vt_reshaped(1:3,:,:), 1), size(vt_reshaped(1:3,:,:), 2), size(vt_reshaped(1:3,:,:), 3));
        
        try
            T2 = cross(T1, vt_reshaped(1:3,:,:), 1);
            fprintf('✓ Cross product successful!\n');
        catch ME2
            fprintf('❌ Cross product failed: %s\n', ME2.message);
            
            % Analyze the dimension mismatch
            vt_part = vt_reshaped(1:3,:,:);
            fprintf('\nDimension analysis:\n');
            fprintf('T1 dimensions: [%s]\n', num2str(size(T1)));
            fprintf('vt_part dimensions: [%s]\n', num2str(size(vt_part)));
            
            % The issue might be that vt_part is 3D while T1 is 2D
            fprintf('Attempting fixes...\n');
            
            % Fix 1: Squeeze vt_part to remove singleton dimensions
            vt_part_squeezed = squeeze(vt_part);
            fprintf('vt_part_squeezed dimensions: [%s]\n', num2str(size(vt_part_squeezed)));
            
            % Fix 2: Replicate vt to match T1
            if size(vt_part_squeezed, 2) == 1
                vt_part_replicated = repmat(vt_part_squeezed, 1, size(T1, 2));
                fprintf('vt_part_replicated dimensions: [%s]\n', num2str(size(vt_part_replicated)));
                
                try
                    T2_fixed = cross(T1, vt_part_replicated);
                    fprintf('✓ Fixed cross product successful! T2_fixed size: %dx%d\n', size(T2_fixed, 1), size(T2_fixed, 2));
                    
                    fprintf('\n*** SOLUTION IDENTIFIED ***\n');
                    fprintf('The issue is that vt needs to be replicated to match the number of points in X\n');
                    fprintf('Original vt: %dx%d, needs to become: %dx%d\n', ...
                            size(vt_part_squeezed, 1), size(vt_part_squeezed, 2), size(T1, 1), size(T1, 2));
                    
                catch ME3
                    fprintf('❌ Fixed cross product still failed: %s\n', ME3.message);
                end
            end
        end
    end
    
catch ME
    fprintf('❌ Setup error: %s\n', ME.message);
end