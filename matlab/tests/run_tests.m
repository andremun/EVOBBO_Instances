% -------------------------------------------------------------------------
% run_tests.m
% -------------------------------------------------------------------------
%
% Thin runner for the matlab.unittest suite in this folder. Invoked by
% .github/workflows/matlab-tests.yml through matlab-actions/run-command.
% Resolves every path from this file's own location rather than the
% MATLAB current directory: matlab.unittest does not guarantee the
% current directory stays put during a run.
%
% By: Mario Andres Munoz Acosta
%     School of Mathematics and Statistics
%     The University of Melbourne
%     Australia
%     2026
%

import matlab.unittest.TestSuite
import matlab.unittest.TestRunner
import matlab.unittest.plugins.CodeCoveragePlugin
import matlab.unittest.plugins.codecoverage.CoberturaFormat

testsDir = fileparts(mfilename('fullpath'));   % matlab/tests
repoRoot = fileparts(fileparts(testsDir));      % repository root

suite = TestSuite.fromFolder(testsDir, 'IncludingSubfolders', false);
runner = TestRunner.withTextOutput();

% Coverage of matlab/ only, not matlab/bbob.v13.09/: that vendored
% snapshot is not exercised by this suite, see PYTHON_PORT.md.
coverageReportFile = fullfile(repoRoot, 'coverage.xml');
sourceFolders = {fullfile(repoRoot, 'matlab')};
runner.addPlugin(CodeCoveragePlugin.forFolder(sourceFolders, ...
    'IncludingSubfolders', false, 'Producing', CoberturaFormat(coverageReportFile)));

results = runner.run(suite);

fprintf('\n[TEST] ================= Summary =================\n');
for i = 1:numel(results)
    if results(i).Failed
        status = 'FAIL';
    elseif results(i).Incomplete
        status = 'SKIP';
    else
        status = 'PASS';
    end
    fprintf('[TEST] [%s] %s\n', status, results(i).Name);
end
nFailed = sum([results.Failed]);
nCases = numel(results);
fprintf('[TEST] %d failed of %d cases.\n', nFailed, nCases);

if nFailed == 0
    fprintf('EOF:SUCCESS\n');
else
    fprintf('EOF:ERROR\n');
    error('EVOBBOInstances:testRunner:caseFailures', ...
        '%d of %d test case(s) failed.', nFailed, nCases);
end
