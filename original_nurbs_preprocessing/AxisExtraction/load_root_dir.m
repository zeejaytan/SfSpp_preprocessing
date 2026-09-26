function root_dir = load_root_dir(default_path, extended)
% Simple implementation of load_root_dir function
% This replaces the missing function in the AxisExtraction code

if nargin < 2
    extended = false;
end

% For our testing, always return the current preprocessing directory
root_dir = '/data/gpfs/projects/punim2657/sfs_preprocessing';

end