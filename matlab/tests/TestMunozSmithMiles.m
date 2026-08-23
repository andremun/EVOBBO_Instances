classdef TestMunozSmithMiles < matlab.unittest.TestCase
% -------------------------------------------------------------------------
% TestMunozSmithMiles.m
% -------------------------------------------------------------------------
%
% Checks munozsmithmiles.m against the fixed reference values in
% tests/fixtures/munozsmithmiles.csv, produced by
% tests/generate_fixtures.m from the same candidate solutions this class
% reads from tests/fixtureInputs.m. Also checks the error paths
% munozsmithmiles.m documents in its own header: an out-of-range fid, an
% invalid strategy/dimension combination, and the 3 individuals (all in
% s2d10) that carry no expression. See munozsmithmiles.m's version
% history for why those errors exist at all.
%
% Also checks that X must have exactly d rows (see testWrongRowCountErrors
% below): before that guard was added, passing X with more rows than d
% silently used only the first d and ignored the rest, matching the
% Python port's stricter behavior only by accident of the Python port
% validating this from the start.
%
% By: Mario Andres Munoz Acosta
%     School of Mathematics and Statistics
%     The University of Melbourne
%     Australia
%     2026
%

properties (TestParameter)
    % Each field is one (sid, d) combination actually defined in
    % munozsmithmiles.mat; the field name becomes the readable test name.
    Config = struct('s1d2', [1 2], 's1d10', [1 10], 's2d2', [2 2], ...
                     's2d10', [2 10], 's3d2', [3 2], 's3d10', [3 10]);
    Fid = num2cell(1:5);
end

properties
    XByD
    Fixture
end

methods (TestClassSetup)
    function setupPaths(testCase)
        repoRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
        addpath(fullfile(repoRoot, 'matlab'));
        addpath(fullfile(repoRoot, 'tests'));
        inputs = fixtureInputs();
        testCase.XByD = containers.Map({2, 10}, {inputs.MunozSmithMilesX2, inputs.MunozSmithMilesX10});
        testCase.Fixture = readtable(fullfile(repoRoot, 'tests', 'fixtures', 'munozsmithmiles.csv'));
    end
end

methods (Test)
    function testMatchesFixture(testCase, Config, Fid)
        sid = Config(1);
        d = Config(2);
        rows = testCase.Fixture(testCase.Fixture.sid == sid ...
            & testCase.Fixture.d == d & testCase.Fixture.fid == Fid, :);
        % s2d10 fid=2 (and 41, 54, not covered by this TestParameter
        % range) has no stored expression; skip rather than fail, since
        % this combination is not meant to be evaluated. See
        % testEmptyIndividualErrors below for that case specifically.
        testCase.assumeFalse(isempty(rows), ...
            'No fixture rows for this (sid,d,fid): a known-empty individual.');

        X = testCase.XByD(d);
        Y = munozsmithmiles(X, sid, d, Fid);
        [~, order] = sort(rows.sample);
        expected = rows.y(order);
        testCase.verifyEqual(Y(:), expected(:), 'AbsTol', 1e-9, 'RelTol', 1e-9);
    end

    function testEmptyIndividualErrors(testCase)
        % s2d10 fid 2, 41, and 54 have no expression (see
        % munozsmithmiles.m's version history and PYTHON_PORT.md).
        X = testCase.XByD(10);
        try
            munozsmithmiles(X, 2, 10, 2);
            testCase.verifyFail('Expected an error for an empty individual (s2d10 fid=2).');
        catch
            % Expected.
        end
    end

    function testOutOfBoundsFidErrors(testCase)
        X = testCase.XByD(2);
        try
            munozsmithmiles(X, 1, 2, 10000);
            testCase.verifyFail('Expected an error for an out-of-range fid.');
        catch
            % Expected.
        end
    end

    function testInvalidStrategyErrors(testCase)
        X = testCase.XByD(2);
        try
            munozsmithmiles(X, 4, 2, 1);
            testCase.verifyFail('Expected an error for an invalid strategy id.');
        catch
            % Expected: no variable s4d2 exists in munozsmithmiles.mat.
        end
    end

    function testWrongRowCountErrors(testCase)
        % X10 has 10 rows; requesting d=2 expects exactly 2.
        X10 = testCase.XByD(10);
        try
            munozsmithmiles(X10, 1, 2, 1);
            testCase.verifyFail('Expected an error for X not having exactly d rows.');
        catch
            % Expected.
        end
    end
end

end
