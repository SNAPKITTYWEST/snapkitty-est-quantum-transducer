function torsion_antenna_demo()
% TORSION_ANTENNA_DEMO
% Theoretical Omega_EST-based antenna for horizon mode reception.
% Toy model; not a physical device.
%
% Ahmad Parr — BelEsprit D'Accord Trust

% ---------- parameters ----------
b = 0.15;              % spiral growth factor
Omega_EST = 8*pi/b;   % torsion invariant
N = 256;               % number of detector elements
theta0 = 0;
dtheta = 2*pi/64;      % angular spacing
a_spiral = 1.0;        % spiral scale (geometric units)
sigma = 0.05;          % horizon proximity envelope width

% ---------- geometry ----------
n = (0:N-1)';
theta = theta0 + n*dtheta;
r = a_spiral * exp(b*theta);

% ---------- transfer function ----------
omega = linspace(-4*Omega_EST, 4*Omega_EST, 4000);
H = zeros(size(omega));

for k = 1:numel(omega)
    Phi = -r + (omega(k)/Omega_EST)*theta;   % torsion phase
    env = exp(-(r - mean(r)).^2/(2*sigma^2));
    H(k) = sum(exp(1i*Phi).*env)/N;
end

% ---------- resonance condition ----------
[~, idx0] = max(abs(H));
omega_res = omega(idx0);
Phi_res = -r + (omega_res/Omega_EST)*theta;
residual = abs(mod(Phi_res, 2*pi));
residual = min(residual, 2*pi - residual);

% ---------- test signal ----------
fs = 20*Omega_EST;
t = (0:1/fs:200/Omega_EST)';
s_in  = exp(-((t-5/Omega_EST)*Omega_EST).^2) .* cos(omega_res*t);
s_out = filter(H(idx0)*ones(64,1)/64, 1, s_in);

% ---------- plots ----------
figure('Position',[100 100 900 700]);

subplot(2,2,1);
polarplot(theta, r, 'LineWidth', 1.2);
title('Spiral antenna geometry r = a e^{b\theta}');

subplot(2,2,2);
plot(omega/Omega_EST, abs(H), 'LineWidth', 1.2);
xlabel('\omega / \Omega_{EST}');
ylabel('|H(\omega)|');
title('Antenna transfer function');
grid on;

subplot(2,2,3);
scatter(mod(Phi_res,2*pi), residual, 12, 'filled');
xlabel('mod(\Phi_{res}, 2\pi)');
ylabel('residual to nearest 2\pi k');
title('Torsion resonance residual');
grid on;

subplot(2,2,4);
plot(t*Omega_EST, s_in,  'b',   ...
     t*Omega_EST, s_out, 'r--', 'LineWidth', 1.1);
xlabel('\Omega_{EST} t');
ylabel('amplitude');
legend('input','received');
title('Antenna response to torsion mode');
grid on;

% ---------- report ----------
fprintf('Omega_EST       = %.6f\n', Omega_EST);
fprintf('Peak |H|        = %.4f\n', abs(H(idx0)));
fprintf('Resonant omega  = %.6f  (omega/Omega_EST = %.4f)\n', ...
        omega_res, omega_res/Omega_EST);
fprintf('Peak residual   = %.3e rad\n', max(residual));
fprintf('Elements in phase = %d / %d\n', sum(residual < 0.1), N);
end
