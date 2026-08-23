function Y = munozsmithmiles(X,sid,d,fid)
% -------------------------------------------------------------------------
% munozsmithmiles.m
% -------------------------------------------------------------------------
%
% Functions generated for the paper "Generating New Space-Filling Test
% Instances for Continuous Black-Box Optimization" Accepted in Evol.
% Comput. 2019
%
% By: Mario Andres Munoz Acosta
%     School of Mathematics and Statistics
%     The University of Melbourne
%     Australia
%     2019
%
% Input: 
%   X       - a matrix of (d x N) candidate solutions.
%   sid     - a strategy identifier. It can be a number between 1 and 3.
%   d       - function dimension. It can be either 2 or 10
%   fid     - function identifier. Determines the number of functions
%             available. It is given by the following table:
%             
%             s1d2  <= 600
%             s1d10 <= 120
%             s2d2  <= 100
%             s2d10 <= 500
%             s3d2  <= 100
%             s3d10 <= 100
% 
% Output:
%   Y       - a (N) vector of fitness values
%
% Must have the file '../data/munozsmithmiles.mat', relative to this
% file, to work. Must have square.m and negexp.m on the MATLAB path:
% these are extra building-block functions used by some of the
% generated expressions.
%
% Version History:
%     v1: 2019 | Original release.
%     v2: 2026 | Fixed two bugs that made every call fail: the cache
%                check tested the string literal 'evalstr' instead of
%                the variable evalstr, so the .mat file was never
%                loaded, and the expression was evaluated with feval on
%                a string (which needs a function name, not an
%                expression) instead of eval. Also fixed the cache key
%                to include sid and d, so switching strategy or
%                dimension between calls now reloads correctly, and
%                added an explicit error for the 3 individuals (all in
%                experiment s2d10) that carry no expression.
%     v3: 2026 | Moved to matlab/; the data file now loads from
%                ../data/munozsmithmiles.mat relative to this file
%                instead of the MATLAB current directory.
%     v4: 2026 | Added a guard for X not having exactly d rows. Before
%                this, passing X with more than d rows silently used
%                only the first d and ignored the rest; passing fewer
%                rows than d threw a confusing "index exceeds matrix
%                dimensions" error instead of naming the actual problem.
%


if size(X,1) ~= d
    error(['X has ' num2str(size(X,1)) ' rows, expected exactly d = ' ...
            num2str(d) ' rows (one per dimension, one column per candidate solution).']);
end

persistent evalstr cached_key

key = ['s' num2str(sid) 'd' num2str(d)];

if isempty(evalstr) || ~strcmp(cached_key, key)
    this_dir = fileparts(mfilename('fullpath'));
    mat_path = fullfile(this_dir, '..', 'data', 'munozsmithmiles.mat');
    try
        load(mat_path, key);
    catch ME
        disp('Either the strategy number or the dimension are incorrect.');
        disp('Choose an strategy number between 1 and 3 and a dimension equal to 2 or 10.');
        rethrow(ME);
    end

    evalstr = eval(key);
    cached_key = key;
end

nfunc = length(evalstr);
if fid>nfunc
    error(['The function index ' num2str(fid) ' is incorrect, there are ' ...
            num2str(nfunc) ' functions in experiment ' key]);
end

expr = evalstr{fid};
if ~ischar(expr) || isempty(strtrim(expr)) || strcmp(strtrim(expr), '[]')
    error(['Function ' num2str(fid) ' in experiment ' key ' has no expression (empty individual).']);
end

Y = eval(expr);

end

% ExpID = [1 3 2 9 8 4];
% ExpLabels = {'S1/2D','S1/10D','S2/2D','S2/10D','S3/2D','S3/10D'}; %
% load('gpExp1_results.mat','GPstr');
% s1d2 = GPstr;
% load('gpExp3_results.mat','GPstr');
% s1d10 = GPstr;
% load('gpExp2_results.mat','GPstr');
% s2d2 = GPstr;
% load('gpExp9_results.mat','GPstr');
% s2d10 = GPstr;
% load('gpExp8_results.mat','GPstr');
% s3d2 = GPstr;
% load('gpExp4_results.mat','GPstr');
% s3d10 = GPstr;
% save('munozsmithmiles.mat','s1d2','s1d10','s2d2','s2d10','s3d2','s3d10');
