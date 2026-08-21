function y = negexp(x)
% -------------------------------------------------------------------------
% negexp.m
% -------------------------------------------------------------------------
%
% Elementwise negative exponential, y = exp(-x). This building-block
% function is called by some of the expressions stored in
% munozsmithmiles.mat.
%
% By: Mario Andres Munoz Acosta
%     School of Mathematics and Statistics
%     The University of Melbourne
%     Australia
%     2026
%
% Input:
%   x       - an array of any size.
% Output:
%   y       - exp(-x), the same size as x.
%

y = exp(-x);

end
