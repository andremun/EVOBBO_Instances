classdef TestClusterGallagher < matlab.unittest.TestCase
% -------------------------------------------------------------------------
% TestClusterGallagher.m
% -------------------------------------------------------------------------
%
% Checks clustergallagher.m against the fixed reference values in
% tests/fixtures/clustergallagher.csv. tests/generate_fixtures.m
% produced those values. It used the same candidate solutions this
% class reads from tests/fixtureInputs.m, and evaluated them against
% the iris dataset.
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
        testCase.Dataset = irisData.data;  % (n x p) = (150 x 4), native orientation
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
        % multiple of the dataset's p=4, so clustergallagher.m's
        % mod(kp,p) guard errors explicitly.
        badX = testCase.X(1:end-1, :);
        try
            clustergallagher(badX, testCase.Dataset);
            testCase.verifyFail('Expected an error for X rows not a multiple of p.');
        catch
            % Expected.
        end
    end

    function testTransposedDatasetWarns(testCase)
        % A dataset in the old (p x n) convention, or any dataset with
        % more columns than rows, should warn. This shape is unusual
        % for these benchmark datasets, and it is exactly what an
        % accidental transpose looks like. This test builds the dataset
        % synthetically (2 points, 12 features, k=1), so the mod(kp,p)
        % guard does not also fire and hide the warning under test.
        syntheticDataset = ones(2, 12);
        syntheticX = ones(12, 1);
        testCase.verifyWarning(@() clustergallagher(syntheticX, syntheticDataset), ...
            'clustergallagher:datasetShape');
    end
end

end
