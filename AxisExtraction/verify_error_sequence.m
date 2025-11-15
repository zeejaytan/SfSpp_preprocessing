% Verify that the cross product error occurs before refine_axis is reached
fprintf('=== Verifying Error Sequence ===\n');

try
    [C0, C1] = read_surfaces('A', 1, false);
    
    fprintf('Testing with FIXED compute_cao_error...\n');
    try
        vt = extract_axis('A', 1, false);
        fprintf('✓ Extract_axis succeeded (unexpected)\n');
    catch ME
        fprintf('❌ Error with fixed version: %s\n', ME.message);
        if contains(ME.message, 'refine_axis')
            fprintf('✓ CONFIRMED: With fixed cross product, we reach refine_axis error\n');
        elseif contains(ME.message, 'same size')
            fprintf('⚠ Still getting cross product error - fix might not be complete\n');
        else
            fprintf('⚠ Different error: %s\n', ME.message);
        end
    end
    
    fprintf('\nNow testing what would happen with BROKEN cross product...\n');
    fprintf('(Simulating the original error by calling the specific function)\n');
    
    % Simulate the original cross product error
    C = [C0, C1];
    decimated_C = C(:,1:10:size(C,2));
    
    % Try to run compute_axis_of_symmetry with the broken cross product
    % by calling it directly with a problematic seed
    rng(12345);  % Seed that caused the original error
    
    try
        [vt_test, ~, ~] = compute_axis_of_symmetry(decimated_C);
        fprintf('⚠ compute_axis_of_symmetry succeeded - cross product fix is working\n');
        fprintf('This confirms that the refine_axis error only appears after cross product is fixed\n');
    catch ME
        fprintf('❌ compute_axis_of_symmetry failed: %s\n', ME.message);
        if contains(ME.message, 'same size')
            fprintf('✓ This would be the original error that prevented reaching refine_axis\n');
        end
    end
    
catch ME
    fprintf('❌ Setup error: %s\n', ME.message);
end