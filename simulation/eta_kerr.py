"""
Kerr-Enhanced T_Omega Transducer — Resonance Efficiency Calculator
TC-SPEC-2026-Omega

Ahmad Parr — BelEsprit D'Accord Trust
"""
import numpy as np


def eta_kerr(M, a, b_spiral, l_max=10, N_omega=1000):
    """
    Compute resonance efficiency η for Kerr-enhanced T_Ω transducer.

    Parameters
    ----------
    M        : black hole mass (Planck units)
    a        : spin parameter (0 <= a < M)
    b_spiral : logarithmic spiral growth factor
    l_max    : max azimuthal quantum number
    N_omega  : frequency resolution

    Returns
    -------
    eta : float in [0, 1]
    """
    r_plus = M + np.sqrt(M**2 - a**2)
    Omega_H = a / (2 * M * r_plus)
    Omega_EST = 8 * np.pi / b_spiral

    omega_max = l_max * Omega_H
    omega_vals = np.linspace(0, omega_max, N_omega)

    total_weight = 0.0
    transduced_weight = 0.0

    for m in range(1, l_max + 1):
        for omega in omega_vals:
            # Superradiance condition
            if omega >= m * Omega_H:
                continue

            # Superradiant gain factor
            G = 1.0 / abs(1.0 - omega / (m * Omega_H)) if omega > 0 else 1e6

            # Torsion resonance phase
            Phi_tors = (-1.0 + Omega_EST * (m * Omega_H)) * r_plus
            n_opt = round(Phi_tors / (2 * np.pi))
            residual = abs(Phi_tors - n_opt * 2 * np.pi)

            # Resonance width broadened by superradiance
            epsilon_0 = 1.616e-35 / (2 * np.pi * 2 * M)
            epsilon_Kerr = epsilon_0 * np.sqrt(G)

            if residual < epsilon_Kerr:
                transduced_weight += G
            total_weight += G

    return transduced_weight / total_weight if total_weight > 0 else 0.0


if __name__ == "__main__":
    # Solar-mass BH in Planck units (~10^38), near-extremal spin
    M_sun_kg = 1.989e30
    m_P_kg = 2.176e-8
    M_planck = M_sun_kg / m_P_kg   # ~10^38
    a = 0.99 * M_planck
    b_spiral = 0.15

    eta = eta_kerr(M_planck, a, b_spiral, l_max=5)
    print(f"Kerr-enhanced η for near-extremal solar-mass BH: {eta:.2e}")

    print("\nSpin dependence:")
    for spin in [0.5, 0.7, 0.9, 0.99]:
        e = eta_kerr(M_planck, spin * M_planck, b_spiral, l_max=3)
        print(f"  a/M = {spin:.2f}  η = {e:.2e}")
