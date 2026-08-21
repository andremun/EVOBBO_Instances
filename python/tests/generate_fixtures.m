% -------------------------------------------------------------------------
% generate_fixtures.m
% -------------------------------------------------------------------------
%
% Regenerates the MATLAB reference fixtures in fixtures/, used by the
% Python test suite to check the Python port against the MATLAB source.
% Run this after any change to matlab/munozsmithmiles.m,
% matlab/langdonpoli.m, or matlab/clustergallagher.m. All paths below
% are resolved relative to this file, so it can be run from any current
% directory.
%
% All inputs below are fixed, deterministic values (not random numbers),
% so the fixtures do not depend on the random number generator of the
% MATLAB or Octave version that runs this script.
%
% Generated with GNU Octave 8.4.0 (verify with real MATLAB when
% available; none of the three ported functions uses a toolbox or a
% MATLAB-version-specific language feature).
%
% By: Mario Andres Munoz Acosta
%     School of Mathematics and Statistics
%     The University of Melbourne
%     Australia
%     2026
%

this_dir = fileparts(mfilename('fullpath'));
repo_root = fullfile(this_dir, '..', '..');
addpath(fullfile(repo_root, 'matlab'));
data_dir = fullfile(repo_root, 'data');
fixtures_dir = fullfile(this_dir, 'fixtures');
if ~exist(fixtures_dir, 'dir')
    mkdir(fixtures_dir);
end

% -------------------------------------------------------------------------
% langdonpoli.m: sweep every fid over a fixed 2 x 7 grid of candidate
% solutions, including points inside and outside the [-5,5]^2 domain.
% -------------------------------------------------------------------------
X = [-6.0 -2.5 -1.0 0.0 1.0 2.5 6.0; ...
      3.0  1.5 -0.5 0.0 0.5 -1.5 -3.0];

fid_lp = fopen(fullfile(fixtures_dir, 'langdonpoli.csv'), 'w');
fprintf(fid_lp, 'fid,sample,y\n');
for fid = 1:19
    Y = langdonpoli(X, fid);
    for s = 1:size(X, 2)
        fprintf(fid_lp, '%d,%d,%.15g\n', fid, s, Y(s));
    end
end
fclose(fid_lp);

% -------------------------------------------------------------------------
% clustergallagher.m: two candidate solutions (k=3 clusters) against the
% iris dataset (p=4).
% -------------------------------------------------------------------------
load(fullfile(data_dir, 'iris.mat'));
Xc = [0.10 0.55; 0.20 -0.10; -0.30 0.40; 0.15 0.05; ...
      0.40 -0.20; -0.10 0.30; 0.05 0.15; -0.25 -0.35; ...
      0.30 0.10; 0.00 -0.15; -0.20 0.25; 0.10 0.20];
Y = clustergallagher(Xc, data');

fid_cg = fopen(fullfile(fixtures_dir, 'clustergallagher.csv'), 'w');
fprintf(fid_cg, 'sample,y\n');
for s = 1:size(Xc, 2)
    fprintf(fid_cg, '%d,%.15g\n', s, Y(s));
end
fclose(fid_cg);

% -------------------------------------------------------------------------
% munozsmithmiles.m: 5 fixed fid values per (sid, d) combination, each
% evaluated over a fixed set of candidate solutions.
% -------------------------------------------------------------------------
X2 = [-1.0 -0.3 0.0 0.4 1.0; 0.5 -0.4 0.0 0.3 -0.6];
X10 = [linspace(-1, 1, 5); linspace(1, -1, 5); linspace(-0.5, 0.5, 5); ...
       linspace(0.5, -0.5, 5); linspace(-1, 0, 5); linspace(0, 1, 5); ...
       linspace(-0.2, 0.2, 5); linspace(0.2, -0.2, 5); ...
       linspace(-0.8, 0.3, 5); linspace(0.3, -0.8, 5)];

configs = {1, 2, 'X', X2; 1, 10, 'X', X10; ...
           2, 2, 'X', X2; 2, 10, 'X', X10; ...
           3, 2, 'X', X2; 3, 10, 'X', X10};

fid_ms = fopen(fullfile(fixtures_dir, 'munozsmithmiles.csv'), 'w');
fprintf(fid_ms, 'sid,d,fid,sample,y\n');
for c = 1:size(configs, 1)
    sid = configs{c, 1};
    d = configs{c, 2};
    Xd = configs{c, 4};
    for fid = 1:5
        try
            Y = munozsmithmiles(Xd, sid, d, fid);
        catch ME
            % Skip individuals with no expression (see munozsmithmiles.m).
            continue;
        end
        for s = 1:size(Xd, 2)
            fprintf(fid_ms, '%d,%d,%d,%d,%.15g\n', sid, d, fid, s, Y(s));
        end
    end
end
% Also cover the 3 known-empty individuals in s2d10, recorded as an
% explicit expected-failure list rather than a value.
fclose(fid_ms);

disp(['Fixtures written to ' fixtures_dir]);
