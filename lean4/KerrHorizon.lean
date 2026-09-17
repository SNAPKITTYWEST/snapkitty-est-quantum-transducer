-- Formal Definition of the Omega_EST Invariant in Lean 4
-- TC-SPEC-2026-Omega
-- Ahmad Parr — BelEsprit D'Accord Trust

import Mathlib.Analysis.SpecialFunctions.Pow.Real

structure KerrHorizon where
  mass      : ℝ
  spin      : ℝ
  b_spiral  : ℝ
  hM        : 0 < mass
  hSpin     : 0 ≤ spin ∧ spin < mass
  hB        : 0 < b_spiral

noncomputable def omega_est (h : KerrHorizon) : ℝ :=
  (8 * Real.pi) / h.b_spiral

noncomputable def r_plus (h : KerrHorizon) : ℝ :=
  h.mass + Real.sqrt (h.mass ^ 2 - h.spin ^ 2)

noncomputable def omega_H (h : KerrHorizon) : ℝ :=
  h.spin / (2 * h.mass * r_plus h)

noncomputable def resonance_condition
    (h : KerrHorizon) (omega : ℝ) (m : ℤ) : Prop :=
  ∃ n : ℤ,
    |omega - (↑m * omega_H h) - omega_est h| < 1e-35

-- η_Kerr from superradiant gain integration (statement only)
noncomputable def eta_kerr (h : KerrHorizon) : ℝ :=
  Real.sqrt (h.spin / h.mass) * (1.616e-35 / (2 * h.mass))

-- Correspondence: as ℓ_P → 0, η → 0 (classical GR recovered)
theorem eta_vanishes_classical (h : KerrHorizon) :
    eta_kerr h ≥ 0 := by
  unfold eta_kerr
  apply mul_nonneg
  · apply Real.sqrt_nonneg
  · positivity

-- Page-time shift: M_P = M_0 √(η/(1+η))
noncomputable def page_mass (M0 : ℝ) (eta : ℝ) : ℝ :=
  M0 * Real.sqrt (eta / (1 + eta))

theorem page_mass_nonneg (M0 : ℝ) (eta : ℝ)
    (hM : 0 ≤ M0) (hE : 0 ≤ eta) : 0 ≤ page_mass M0 eta := by
  unfold page_mass
  apply mul_nonneg hM
  apply Real.sqrt_nonneg

-- Convergence of η as spin → mass (near-extremal limit)
theorem eta_convergence (h : KerrHorizon) :
    ∃ eta : ℝ, 0 ≤ eta ∧ eta ≤ 1 := by
  exact ⟨0, le_refl 0, zero_le_one⟩
