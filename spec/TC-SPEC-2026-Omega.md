# TC-SPEC-2026-Ω: Torsion-Comb Signatures in Kerr Black Hole Ringdown

**Document ID:** TC-SPEC-2026-Ω  
**Version:** 1.0  
**Date:** 2026-06-20  
**Prepared For:** Numerical Relativity Collaboration (NRHEP/LISA Consortium)

---

## 1. Objective

This specification defines the minimal simulation requirements to test for the presence of a **Quantum Torsion Comb** — a harmonic frequency signature in black hole ringdown waveforms predicted by the T_Ω^Kerr toy model when promoted to a quantum gravity framework via the Event-Spiral Torsion Invariant (Ω_EST = 8π/b). The simulation must isolate deviations from general relativity (GR) attributable *only* to the torsion-resonance mechanism, excluding known effects (echoes from exotic compact objects, axion clouds).

---

## 2. Core Prediction

The T_Ω^Kerr model predicts an additional harmonic comb in the ringdown strain:

```
h_torsion(t) = Σ_{m=1}^{m_max} A_m exp(-Γ_hf t) cos(m ω_0 t + φ_m)
```

where:
- Fundamental frequency: `ω_0 = (8π/b) Ω_H`
- Horizon angular velocity: `Ω_H = a / (2M r_+)`, `r_+ = M + √(M² - a²)`
- Spiral growth factor: `b` (free parameter, constrained by observability)
- Max harmonic: `m_max = ⌊ω_SR / ω_0⌋`, superradiance cutoff `ω_SR ≈ m Ω_H`
- Damping rate: `Γ_hf` (horizon-fluctuation leakage rate)
- Amplitude scaling: `A_m ∝ (1 - η_Kerr) G_{m,ω}` (see Section 3)

---

## 3. Required Input Parameters

| Parameter | Symbol | Required Range | Constraint |
|-----------|--------|----------------|------------|
| Black Hole Mass | M | [10², 10⁵] M☉ | Ensures η_Kerr ≳ 10⁻²⁰ |
| Dimensionless Spin | a/M | [0.9, 0.999] | Near-extremal needed |
| Spiral Growth Factor | b | [1, 10⁴] | b ≳ 250 puts ω_0 in LISA band |
| Horizon Fluctuation Rate | Γ_hf | [10⁻⁶/M, 10⁻²/M] | ≪ Γ_QNM |
| Superradiant Gain Threshold | G_min | > 1.0 | Modes below ignored |
| Initial Perturbation | h_0(t) | Gaussian wavepacket | l=m=2 dominant |

---

## 4. Simulation Requirements

### 4.1 Baseline GR Evolution

- Evolve vacuum Einstein equations via BSSNOK or Z4c formulation
- Initial data: Boosted Kerr-Schild BH + Gaussian perturbation
- Validation: Match GR QNM frequencies to within 10⁻⁴ for l=m=2,3,4 modes

### 4.2 Torsion-Comb Injection

Do **not** modify the Einstein equations. Implement as a phenomenological source term in the wave extraction phase:

1. During ringdown (t > t_peak), compute Ω_H(t) from the apparent horizon
2. Calculate ω_0(t) = (8π/b) Ω_H(t)
3. For each harmonic m = 1 to m_max(t):
   - `A_m(t) = A_0 (1 - η_Kerr) G_{m,ω} exp(-Γ_hf t)`
   - `η_Kerr = √(a/M) ℓ_P / r_s`
   - `G_{m,ω} = |1 - ω/(m Ω_H)|⁻¹`
   - `h_total ← h_GR + A_m cos(m ω_0 t + φ_m)`
4. Randomize phases φ_m ∈ [0, 2π)

### 4.3 Output Requirements

- Time-domain strain h(t) at ℐ⁺
- Frequency-domain h̃(f) via FFT (Tukey window α=0.1)
- PSD |h̃(f)|² showing peaks at f_m = m ω_0/(2π)

---

## 5. Validation Criteria

All of the following must hold for a detection claim:

1. **Comb structure:** peaks at f_m satisfy f_{m+1} - f_m = const within 1%
2. **Mass scaling:** Δf ∝ M⁻¹ (verify with M and 2M)
3. **Spin dependence:** Δf ∝ Ω_H ∝ a (fixed M)
4. **b-scaling:** Δf ∝ b⁻¹
5. **GR limit:** b → ∞ ⟹ h(t) → h_GR(t)
6. **Noise floor:** comb peaks exceed simulation noise by > 5σ

---

## 6. Known Systematics

- **Numerical artifacts:** test dx/M = [0.1, 0.05, 0.025]
- **Gauge effects:** compare Regge-Wheeler vs. Lorenz gauge
- **Echoes:** torsion comb is harmonic in frequency; echoes are periodic in time
- **Axion clouds:** monochromatic (not a comb)
- **Standard QNMs:** f_0 < f_QNM^{l=2}

---

## 7. Simulation Plan

| Step | Action | Tool | Success Metric |
|------|--------|------|----------------|
| 1 | Initial data | Einstein Toolkit (Lorene + Puncture) | Constraint violation < 10⁻⁶ |
| 2 | Evolve to ringdown | SpECTRE or Cactus/McLachlan | QNM match to 10⁻³ |
| 3 | Extract Ω_H(t) | ApparentHorizonFinder | Stable to 10⁻⁴ |
| 4 | Inject torsion comb | Python post-processor (h5py) | Peaks visible in PSD |
| 5 | Parameter sweep | HTCondor job array | Validate scaling laws |
| 6 | LISA noise injection | LISA Data Challenges tools | SNR > 8 |

---

## 8. Expected Outcome for LISA

For M = 10⁵ M☉, a = 0.99M, b = 500:

- **Corrected f_0:** ≈ 7.05 mHz (not 0.05 Hz as originally stated)
- Comb spacing: Δf = 7.05 mHz
- First harmonic: f₁ = 7.05 mHz (in LISA band)
- Tenth harmonic: f₁₀ = 70.5 mHz (in band)

See `../simulation/torsion_comb_mock.py` for full numerical implementation.

---

## 9. Non-Negotiable Constraints

- The torsion comb must be injected **only** via the Ω_EST-dependent prescription
- A null result for b < 10 is a **valid null result**
- ω_0 = (8π/b) Ω_H must derive directly from the spin-network eigenvalue
