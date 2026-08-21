function Y = clustergallagher(X,dataset)
% -------------------------------------------------------------------------
% clustergallagher.m
% -------------------------------------------------------------------------
%
% Vectorized function fitnessclustsse by Marcus Gallagher
%
% By: Mario Andres Munoz Acosta
%     School of Mathematics and Statistics
%     The University of Melbourne
%     Australia
%     2019
%
% Input: 
%   X       - a (kp x N) matrix of candidate solutions, where each column
%             vector represents the positions of k cluster centers.  That
%             is, the dimensionality of the optimization problem is kp.
%   dataset - an (p x n) dataset to be clustered (n data points of
%             dimensionality p). There are several examples of data given
%             in this package (all files but 'munozsmithmiles.mat')
% Output:
%   Y       - a (N x 1) vector of fitness values
%
% Version History:
%     v1: 30/07/2015
%     v2: 01/09/2015 | Removed redundant operations and improved speed and
%                      memory access by changing the arrayfun for a simple
%                      for-loop.
%     v3: 08/07/2019 | Version published in MATILDA re "Generating New
%                      Space-Filling Test Instances for Continuous
%                      Black-Box Optimization" Accepted in Evol. Comput.
%

% Formatting the data
[p,n] = size(dataset);
[kp,N] = size(X);
k = kp./p;
X = reshape(X,p,k,N);
% Pairwise distances of all data points
D = zeros(k,n,N);
for i=1:N
    D(:,:,i) =  L2_distance(X(:,:,i),dataset);
end
% Find which cluster center is closest to each datapoint
Y = squeeze(sum(min(D,[],1).^2,2));

end

% -------------------------------------------------------------------------
function d = L2_distance(a, b)
% L2_DISTANCE - computes Euclidean distance matrix
%
% E = L2_distance(A,B)
%
%    A - (DxM) matrix 
%    B - (DxN) matrix
% 
% Returns:
%    E - (MxN) Euclidean distances between vectors in A and B
%
%
% Description : 
%    This fully vectorized (VERY FAST!) m-file computes the 
%    Euclidean distance between two vectors by:
%
%                 ||A-B|| = sqrt ( ||A||^2 + ||B||^2 - 2*A.B )
%
% Example : 
%    A = rand(400,100); B = rand(400,200);
%    d = distance(A,B);

% Author   : Roland Bunschoten
%            University of Amsterdam
%            Intelligent Autonomous Systems (IAS) group
%            Kruislaan 403  1098 SJ Amsterdam
%            tel.(+31)20-5257524
%            bunschot@wins.uva.nl
% Last Rev : Wed Oct 20 08:58:08 MET DST 1999
% Tested   : PC Matlab v5.2 and Solaris Matlab v5.3

% Copyright notice: You are free to modify, extend and distribute 
%    this code granted that the author of the original code is 
%    mentioned as the original author of the code.

% Fixed by JBT (3/18/00) to work for 1-dimensional vectors
% and to warn for imaginary numbers.  Also ensures that 
% output is all real, and allows the option of forcing diagonals to
% be zero.  
%
%

% This file is part of the Matlab Toolbox for Dimensionality Reduction.
% The toolbox can be obtained from http://homepage.tudelft.nl/19j49
% You are free to use, change, or redistribute this code in any way you
% want for non-commercial purposes. However, it is appreciated if you 
% maintain the name of the original author.
%
% (C) Laurens van der Maaten, Delft University of Technology


    if nargin < 2
       error('Not enough input arguments');
    end
    if size(a, 1) ~= size(b, 1)
        error('A and B should be of same dimensionality');
    end
    if ~isreal(a) || ~isreal(b)
        warning('Computing distance table using imaginary inputs. Results may be off.'); 
    end

    % Padd zeros if necessray
    if size(a, 1) == 1
        a = [a; zeros(1, size(a, 2))]; 
        b = [b; zeros(1, size(b, 2))]; 
    end

    % Compute distance table
    d = sqrt(bsxfun(@plus, sum(a .* a)', bsxfun(@minus, sum(b .* b), 2 * a' * b)));

    % Make sure result is real
    d = real(d);
end
