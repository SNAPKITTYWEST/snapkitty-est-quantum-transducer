"""
Torsion-Comb Mock LISA Data Challenge Generator
TC-SPEC-2026-Omega, Section 8

Ahmad Parr — BelEsprit D'Accord Trust
Caveat: synthetic injection into simulated LISA noise.
Not a detection. T_Omega^Kerr model remains speculative.
"""
import numpy as np
from numpy.fft import rfft, rfftfreq

# ============================================================
# 1. Constants and source parameters
# ============================================================
G = 6.67430e-11
c = 2.99792458e8
M_sun = 1.98892e30
M_sun_s = G * M_sun / c**3  # 4.9255e-6 s
l_P = 1.616255e-35           # m
t_P = l_P / c                # 5.391e-44 s

M_solar = 1.0e5
a_over_M = 0.99
b_spiral = 500.0
A0 = 1.0e-20        # fiducial strain amplitude
Gamma_hf_scale = 1.0e-3  # Gamma_hf = scale / M

# ============================================================
# 2. Kerr geometry in geometric units (seconds)
# ============================================================
M = M_solar * M_sun_s
a = a_over_M * M
r_plus = M + np.sqrt(M**2 - a**2)
r_s = 2.0 * M
Omega_H = a / (2.0 * M * r_plus)
omega_0 = (8.0 * np.pi / b_spiral) * Omega_H
f_0 = omega_0 / (2.0 * np.pi)
eta_Kerr = np.sqrt(a_over_M) * (t_P / r_s)
Gamma_hf = Gamma_hf_scale / M

print("=== Source parameters ===")
print(f"M         = {M_solar:.2e} M_sun = {M:.6e} s")
print(f"a/M       = {a_over_M}")
print(f"r_+       = {r_plus:.6e} s")
print(f"Omega_H   = {Omega_H:.6e} rad/s  ({Omega_H/(2*np.pi):.6e} Hz)")
print(f"omega_0   = {omega_0:.6e} rad/s  ({f_0:.6e} Hz)")
print(f"eta_Kerr  = {eta_Kerr:.6e}")
print(f"Gamma_hf  = {Gamma_hf:.6e} /s   (tau_hf = {1/Gamma_hf:.3e} s)")
print()

# ============================================================
# 3. Torsion comb waveform
# ============================================================
def torsion_comb(t, omega0, Gamma, eta, m_max, A0, seed=42):
    rng = np.random.default_rng(seed)
    h = np.zeros_like(t)
    base_G = 1.0 / abs(1.0 - omega0 / Omega_H)
    for m in range(1, m_max + 1):
        G_m = base_G / m   # effective harmonic falloff
        A_m = A0 * (1.0 - eta) * G_m
        phi = rng.uniform(0.0, 2.0 * np.pi)
        h += A_m * np.exp(-Gamma * t) * np.cos(m * omega0 * t + phi)
    return h

# ============================================================
# 4. LISA noise PSD (Cornish-Robson 2017 analytic fit)
# ============================================================
def lisa_psd(f):
    L = 2.5e9
    f_star = c / (2.0 * np.pi * L)
    P_OMS = 2.25e-22
    P_acc = 9.0e-30
    f = np.where(f > 0, f, 1e-6)
    return (10.0 / (3.0 * L**2)) * (
        P_OMS + 2.0 * (1.0 + np.cos(f / f_star)**2) * P_acc / (2.0 * np.pi * f)**4
    )

def galactic_foreground(f):
    f = np.where(f > 0, f, 1e-6)
    A, alpha, beta, kappa, gamma, f_k = 9.0e-45, 0.138, -221.0, 521.0, 1680.0, 1.13e-3
    return (A * f**(-7.0/3.0)
            * np.exp(-f**alpha + beta * f * np.sin(kappa * f))
            * (1.0 + np.tanh(gamma * (f_k - f))))

# ============================================================
# 5. Time grid and signal
# ============================================================
T_obs = 1.0e4
fs = 5.0
N = int(T_obs * fs)
t = np.arange(N) / fs

m_max = min(int(np.floor(1.0 / f_0)), 50)

h_sig = torsion_comb(t, omega_0, Gamma_hf, eta_Kerr, m_max, A0)

print("=== Waveform ===")
print(f"m_max      = {m_max}")
print(f"signal rms = {np.std(h_sig):.3e}")
print()

# ============================================================
# 6. Noise realization
# ============================================================
freqs = rfftfreq(N, d=1.0 / fs)
df = freqs[1] - freqs[0]
Sn_inst = lisa_psd(freqs)
Sn_gal = galactic_foreground(freqs)
Sn_tot = Sn_inst + Sn_gal

rng = np.random.default_rng(2026)
n_f = np.sqrt(Sn_tot * N * fs / 4.0) * (
    rng.standard_normal(len(freqs)) + 1j * rng.standard_normal(len(freqs))
)
n_f[0] = 0.0
n_t = np.fft.irfft(n_f, n=N)
d = h_sig + n_t

print("=== Noise ===")
print(f"noise rms  = {np.std(n_t):.3e}")
print()

# ============================================================
# 7. Matched-filter SNR
# ============================================================
H = rfft(h_sig)
mask = freqs > 0
snr2 = 4.0 * (1.0 / (N * fs)) * np.sum(np.abs(H[mask])**2 / Sn_tot[mask])
snr = np.sqrt(snr2)

print("=== Detection forecast ===")
print(f"Optimal SNR = {snr:.3f}")
print()

# ============================================================
# 8. Peak search and comb verification
# ============================================================
D = rfft(d)
P_data = np.abs(D)**2
P_sig = np.abs(H)**2

def find_peak(f, P, f_guess, halfwidth):
    sel = (f > f_guess - halfwidth) & (f < f_guess + halfwidth)
    if not np.any(sel):
        return None
    idx = np.argmax(P[sel])
    return f[sel][idx]

print("=== Harmonic comb check ===")
for m in [1, 2, 3, 5, 10]:
    if m > m_max:
        break
    f_m = m * f_0
    pf = find_peak(freqs, P_data, f_m, 3 * df)
    if pf is not None:
        print(f"m={m:2d}  f_exp={f_m:.6e}  f_found={pf:.6e}  "
              f"delta={100*(pf-f_m)/f_m:+.3f}%")

# ============================================================
# 9. Optional plot
# ============================================================
try:
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(3, 1, figsize=(10, 10))

    ax[0].plot(t, d, lw=0.3)
    ax[0].set_xlim(0, 2000)
    ax[0].set_xlabel("t [s]")
    ax[0].set_ylabel("strain")
    ax[0].set_title("Time domain: signal + LISA noise")

    ax[1].loglog(freqs, np.sqrt(freqs * Sn_tot), label="LISA + Gal. FG")
    ax[1].loglog(freqs, np.sqrt(freqs * np.abs(H)**2 / df),
                 label="signal h_c", alpha=0.7)
    ax[1].set_xlim(1e-4, 1)
    ax[1].set_xlabel("f [Hz]")
    ax[1].set_ylabel("h_c")
    ax[1].legend()

    ax[2].semilogy(freqs, P_data, lw=0.5, label="data PSD")
    ax[2].semilogy(freqs, P_sig, lw=0.8, label="signal PSD")
    ax[2].set_xlim(0, min(0.1, 12 * f_0))
    ax[2].set_xlabel("f [Hz]")
    ax[2].set_ylabel(r"$|\tilde{h}|^2$")
    ax[2].legend()

    plt.tight_layout()
    plt.savefig("torsion_comb_mock.png", dpi=120)
    print("\nSaved torsion_comb_mock.png")
except ImportError:
    print("\nmatplotlib not available; skipping plot.")
