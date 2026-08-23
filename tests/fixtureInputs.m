function inputs = fixtureInputs()
% -------------------------------------------------------------------------
% fixtureInputs.m
% -------------------------------------------------------------------------
%
% This file holds fixed, deterministic test inputs. generate_fixtures.m
% writes tests/fixtures/*.csv from these inputs. The matlab.unittest
% test classes in matlab/tests/ re-run the same inputs and check the
% result against those committed fixtures. This keeps both consumers in
% agreement about what produced each committed reference value.
%
% Output:
%   inputs - a struct with one field per function under test:
%     LangdonPoliX          - (2 x 7), see langdonpoli.m
%     ClusterGallagherX     - (12 x 2), see clustergallagher.m (k=3, p=4)
%     MunozSmithMilesX2     - (2 x 5), see munozsmithmiles.m (d=2)
%     MunozSmithMilesX10    - (10 x 5), see munozsmithmiles.m (d=10)
%     MunozSmithMilesConfigs - (6 x 2), each row [sid d]
%     MunozSmithMilesFids   - fid values checked per config
%
% By: Mario Andres Munoz Acosta
%     School of Mathematics and Statistics
%     The University of Melbourne
%     Australia
%     2026
%

inputs.LangdonPoliX = [-6.0 -2.5 -1.0 0.0 1.0 2.5 6.0; ...
                        3.0  1.5 -0.5 0.0 0.5 -1.5 -3.0];

inputs.ClusterGallagherX = [0.10 0.55; 0.20 -0.10; -0.30 0.40; 0.15 0.05; ...
      0.40 -0.20; -0.10 0.30; 0.05 0.15; -0.25 -0.35; ...
      0.30 0.10; 0.00 -0.15; -0.20 0.25; 0.10 0.20];

inputs.MunozSmithMilesX2 = [-1.0 -0.3 0.0 0.4 1.0; 0.5 -0.4 0.0 0.3 -0.6];
inputs.MunozSmithMilesX10 = ...
    [linspace(-1, 1, 5); linspace(1, -1, 5); linspace(-0.5, 0.5, 5); ...
     linspace(0.5, -0.5, 5); linspace(-1, 0, 5); linspace(0, 1, 5); ...
     linspace(-0.2, 0.2, 5); linspace(0.2, -0.2, 5); ...
     linspace(-0.8, 0.3, 5); linspace(0.3, -0.8, 5)];

inputs.MunozSmithMilesConfigs = [1 2; 1 10; 2 2; 2 10; 3 2; 3 10];
inputs.MunozSmithMilesFids = 1:5;

end
