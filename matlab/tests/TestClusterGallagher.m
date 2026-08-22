classdef TestClusterGallagher < matlab.unittest.TestCase
% -------------------------------------------------------------------------
% TestClusterGallagher.m
% -------------------------------------------------------------------------
%
% Checks clustergallagher.m against the fixed reference values in
% tests/fixtures/clustergallagher.csv, produced by
% tests/generate_fixtures.m from the same candidate solutions this class
% reads from tests/fixtureInputs.m, evaluated against the iris dataset.
%
% By: Mario Andres Munoz Acosta
%     School of Mathematics and Statistics
%     The University of Melbourne
%     Australia
%     2026
%

properties
    X
    Dataset
    Fixture
end

methods (TestClassSetup)
    function setupPaths(testCase)
        repoRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
        addpath(fullfile(repoRoot, 'matlab'));
        addpath(fullfile(repoRoot, 'tests'));
        testCase.X = fixtureInputs().ClusterGallagherX;
        irisData = load(fullfile(repoRoot, 'data', 'iris.mat'));
        testCase.Dataset = irisData.data';  % (p x n) = (4 x 150)
        testCase.Fixture = readtable(fullfile(repoRoot, 'tests', 'fixtures', 'clustergallagher.csv'));
    end
end

methods (Test)
    function testMatchesFixture(testCase)
        Y = clustergallagher(testCase.X, testCase.Dataset);
        [~, order] = sort(testCase.Fixture.sample);
        expected = testCase.Fixture.y(order);
        testCase.verifyEqual(Y(:), expected(:), 'AbsTol', 1e-9, 'RelTol', 1e-9);
    end

    function testMismatchedDimensionalityErrors(testCase)
        % X has 12 rows (k=3, p=4). Dropping one row leaves 11, not a
        % multiple of the dataset's p=4, so reshape(X, p, k, N) inside
        % clustergallagher.m errors on the non-integer k = 11/4.
        badX = testCase.X(1:end-1, :);
        try
            clustergallagher(badX, testCase.Dataset);
            testCase.verifyFail('Expected an error for X rows not a multiple of p.');
        catch
            % Expected.
        end
    end
end

end
