classdef TestLangdonPoli < matlab.unittest.TestCase
% -------------------------------------------------------------------------
% TestLangdonPoli.m
% -------------------------------------------------------------------------
%
% Checks langdonpoli.m against the fixed reference values in
% tests/fixtures/langdonpoli.csv. Those values were produced by
% tests/generate_fixtures.m from the same input grid this class reads
% from tests/fixtureInputs.m, so a mismatch here means langdonpoli.m
% itself changed behavior, not that the two definitions of the input
% drifted apart.
%
% By: Mario Andres Munoz Acosta
%     School of Mathematics and Statistics
%     The University of Melbourne
%     Australia
%     2026
%

properties (TestParameter)
    Fid = num2cell(1:19)
end

properties
    X
    Fixture
end

methods (TestClassSetup)
    function setupPaths(testCase)
        repoRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
        addpath(fullfile(repoRoot, 'matlab'));
        addpath(fullfile(repoRoot, 'tests'));
        testCase.X = fixtureInputs().LangdonPoliX;
        testCase.Fixture = readtable(fullfile(repoRoot, 'tests', 'fixtures', 'langdonpoli.csv'));
    end
end

methods (Test)
    function testMatchesFixture(testCase, Fid)
        Y = langdonpoli(testCase.X, Fid);
        rows = testCase.Fixture(testCase.Fixture.fid == Fid, :);
        [~, order] = sort(rows.sample);
        expected = rows.y(order);
        testCase.verifyEqual(Y(:), expected(:), 'AbsTol', 1e-9, 'RelTol', 1e-9);
    end

    function testOutOfBoundsFidErrors(testCase)
        % fid=20 exceeds the 19 functions langdonpoli.m defines.
        try
            langdonpoli(testCase.X, 20);
            testCase.verifyFail('Expected an error for an out-of-range fid.');
        catch
            % Expected: langdonpoli.m errors when fid > length(evalstr).
        end
    end

    function testOutOfDomainIsZeroed(testCase)
        % Column 1 of X scales to 2*(-6.0) = -12.0, outside [-10, 10], so
        % langdonpoli.m forces that sample's output to 0.
        Y = langdonpoli(testCase.X, 1);
        testCase.verifyEqual(Y(1), 0);
    end

    function testWrongRowCountErrors(testCase)
        % langdonpoli.m needs exactly 2 rows; this repo's functions are
        % defined in 2 dimensions only.
        badX = testCase.X(1, :);
        try
            langdonpoli(badX, 1);
            testCase.verifyFail('Expected an error for X not having exactly 2 rows.');
        catch
            % Expected.
        end
    end
end

end
