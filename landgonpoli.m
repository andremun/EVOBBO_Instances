function Y = landgonpoli(X,fid)
% -------------------------------------------------------------------------
% munozsmithmiles.m
% -------------------------------------------------------------------------
%
% Functions from Landgon and Poli 2007 (IEEE Tran. Evol. Comput.) generated
% for the paper "Generating New Space-Filling Test Instances for Continuous
% Black-Box Optimization" Accepted in Evol. Comput. 2019
%
% By: Mario Andres Munoz Acosta
%     School of Mathematics and Statistics
%     The University of Melbourne
%     Australia
%     2019
%
% Input: 
%   X       - a matrix of (d x N) candidate solutions.
%   fid     - function identifier. Determines the number of functions
%             available. Cannot be larger than 19.
%             
% Output:
%   Y       - a (N) vector of fitness values
%
 
evalstr = {@(x) 0.11 + 0.77.*x(:,1).*(1 - x(:,1)) - 0.075.*x(:,2);          % Fig 2
           @(x) 0.127 + 0.063.*x(:,1);                                      % Fig 3
           @(x) x(:,2).*(1.32 + 1.78.*x(:,1) - x(:,1).^2 - x(:,2)) + 0.37;  % Fig 4
           @(x) 0.54.*x(:,1) - x(:,1).^2 + 0.24.*x(:,2) - 1.26;             % Fig 5
           @(x) 0.063.*x(:,1) - 0.052;                                      % Fig 6
           @(x) -(0.171 + 0.0188.*x(:,2)).*x(:,2);                          % Fig 7
           @(x) 0.00124.*(x(:,1).^2).*x(:,2);                               % Fig 12
           @(x) x(:,1).*(0.643 + x(:,2) - x(:,1).*(0.299.*x(:,1) + 2.81 + x(:,2) + x(:,2).^2));
           @(x) (1.27 - 1.1.*x(:,1) - 0.53.*x(:,1).^2).*x(:,1);             % Fig 20
           @(x) (0.33 - 0.32.*x(:,1) - 2.32.*x(:,2)).*x(:,2);               % Fig 21
           @(x) x(:,2).*(0.093 + 0.39.*x(:,2) + 0.15.*x(:,2).^2 - 0.17.*x(:,2).^3 - (0.19.*x(:,2).^2 + 0.20.*x(:,2).^3).*x(:,1).^2);
           @(x) x(:,1) - (x(:,1) - 1)./x(:,1);                              % Fig 23
           @(x) 0.063.*x(:,1);                                              % Fig 24
           @(x) -(0.13 + 0.24.*x(:,2)).*x(:,2);                             % Fig 25
           @(x) 0.0043 + 0.024.*x(:,2);                                     % Fig 28
           @(x) 0.102 + 0.00189.*x(:,2) + 0.00635.*x(:,2).^2;               % Fig 29
           @(x) x(:,1) - x(:,2);                                            % Fig 32
           @(x) (1.03 + 2.81.*x(:,1)).*x(:,2);                              % Fig 33
           @(x) (x(:,1).^2).*(x(:,2).^4)};                                  % Fig 34

if fid>length(evalstr)
    error(['The function index ' num2str(fid) ' is incorrect, there are ' ...
                num2str(length(evalstr)) ' functions available']);
end

Y = feval(evalstr{fid},X');

end