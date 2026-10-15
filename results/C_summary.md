# Task C: weak-grid synchronisation stability, GFL vs GFM

Model: quasi-static phasor, algebraic network, w_b = 2*pi*50, converter base. One converter exports P0 = 1.0 pu to an infinite bus (Vg = 1) through Xg = 1/SCR. SCR swept 10 to 1.0 (0.2 steps above 3, 0.01 steps below 3). Equilibria by fsolve with continuation, Jacobian by central differences, eigenvalues by numpy. Script: sim/c_weakgrid.py.

GFL: SRF-PLL (zeta 0.707, bandwidth 10/20/40 Hz; Kp = 2*0.707*(2*pi*f)/w_b, Ki = (2*pi*f)^2/w_b), id* = P0/vd_filtered, AC-voltage PI with Kpv = 0, Kiv = 20 per s holding |v_pcc| = 1, current loop first-order lag 2 ms, voltage filter 5 ms. GFM: VSM/droop, Xv = 0.15 pu, D = 1/R = 20, H = 2 and 5 s, E set so |v_pcc| = 1 (constant in the small-signal model).

## Gates
- GC1 PASS: AC-voltage loop off and iq = 0, the last SCR with a GFL equilibrium is 2.000 (continuation, 0.002 steps) and the independent existence scan gives 2.000; theory 2*P0 = 2.000; error 0.00 %.
- GC2 PASS (H = 2 s, SCR 5): wn numeric 14.713 vs closed form 14.713 rad/s; zeta numeric 0.1699 vs closed form 0.1699 (errors below 1e-9).
- GC2 PASS (H = 5 s, SCR 5): wn numeric 9.305 vs closed form 9.305 rad/s; zeta numeric 0.1075 vs closed form 0.1075 (errors below 1e-9).
- GC3 PASS: at SCR 10 the GFL max real part is 10 Hz -2.05 1/s, 20 Hz -2.05 1/s, 40 Hz -2.05 1/s (all stable).
- GC4 PASS: GFL minimum damping ratio of oscillatory modes at SCR 10 / 3 / 1.5: 10 Hz 0.702 / 0.646 / 0.195; 20 Hz 0.706 / 0.690 / 0.380; 40 Hz 0.712 / 0.780 / 0.622, and every GFL variant crosses into the RHP inside the sweep. GFM swing damping at SCR 2 vs 10: H = 2.0 s 0.250 vs 0.142; H = 5.0 s 0.158 vs 0.090; monotone in SCR for H = 5 s.

## Critical SCR

| Variant | Critical SCR | Mechanism | Last equilibrium SCR |
|---|---|---|---|
| GFL_10Hz | 1.367 | eigenvalue crosses into RHP (oscillatory, Hopf) | 1.00 |
| GFL_20Hz | 1.332 | eigenvalue crosses into RHP (oscillatory, Hopf) | 1.00 |
| GFL_40Hz | 1.298 | eigenvalue crosses into RHP (oscillatory, Hopf) | 1.00 |
| GFM_H2 | 1.010 | stable down to the last equilibrium (static limit) | 1.01 |
| GFM_H5 | 1.010 | stable down to the last equilibrium (static limit) | 1.01 |

Static (no-equilibrium) limits: GFL at unity PF with iq = 0: SCR = 2*P0 = 2.0 (numeric 2.000). GFL with AC-voltage control holding |v| = 1: SCR = P0 = 1.0 (sin th = P0*Xg). GFM with |v_pcc| = 1: same PCC-angle law, last converged SCR 1.01 for both H (EMF angle reaches 90 deg at SCR 1.0).

## Values at selected SCR

GFL: max Re of all eigenvalues (1/s) and minimum damping ratio of oscillatory modes.

| SCR | 10 Hz maxRe | 10 Hz zeta | 20 Hz maxRe | 20 Hz zeta | 40 Hz maxRe | 40 Hz zeta |
|---|---|---|---|---|---|---|
| 1.5 | -6.69 | 0.195 | -18.41 | 0.380 | -30.60 | 0.622 |
| 2.0 | -15.81 | 0.530 | -16.52 | 0.653 | -16.70 | 0.939 |
| 3.0 | -8.04 | 0.646 | -8.06 | 0.690 | -8.07 | 0.780 |
| 5.0 | -4.30 | 0.687 | -4.30 | 0.703 | -4.30 | 0.730 |
| 10.0 | -2.05 | 0.702 | -2.05 | 0.706 | -2.05 | 0.712 |

GFM: swing mode (closed form equals numeric).

| SCR | E (pu) | delta (deg) | Ks (pu) | H=2: wn (rad/s) | H=2: zeta | H=5: wn (rad/s) | H=5: zeta |
|---|---|---|---|---|---|---|---|
| 1.5 | 1.0679 | 49.89 | 0.843 | 8.13 | 0.307 | 5.14 | 0.194 |
| 2.0 | 1.0510 | 38.21 | 1.271 | 9.99 | 0.250 | 6.32 | 0.158 |
| 3.0 | 1.0366 | 27.79 | 1.897 | 12.21 | 0.205 | 7.72 | 0.130 |
| 5.0 | 1.0262 | 19.94 | 2.756 | 14.71 | 0.170 | 9.31 | 0.107 |
| 10.0 | 1.0186 | 14.21 | 3.950 | 17.61 | 0.142 | 11.14 | 0.090 |

## Captions

- figures/C1_weakgrid_stability (.png/.pdf): Weak-grid small-signal stability of a converter exporting 1 pu versus short-circuit ratio. (a) Grid-following converter (SRF-PLL, 2 ms current loop, AC-voltage PI): real part of the dominant eigenvalue for PLL bandwidths 10, 20 and 40 Hz; shaded band = unstable; dashed line SCR = 3 (IEEE Std 1204 weak-grid threshold). Above SCR 2 the dominant pole is the slow real AC-voltage-integrator pole; below SCR 2 a coupled PLL/voltage-loop oscillatory pair (5 to 7 Hz) takes over and crosses into the RHP. (b) Grid-forming VSM (Xv = 0.15 pu, D = 20 pu): swing-mode damping ratio for H = 2 s and 5 s.
- figures/C2_eig_loci (.png/.pdf): Eigenvalue loci as SCR falls from 10 to the static limit (colour = SCR); modes faster than -200 1/s omitted. Left: GFL with 20 Hz PLL. Right: GFM with H = 5 s.

Colour key: GFL 10 Hz = C0 black dashed, GFL 20 Hz = C2 orange, GFL 40 Hz = C1 red, GFM H 2 s = C3 blue, GFM H 5 s = C4 green (proposed).

## Findings
1. The grid-following converter loses small-signal stability before it loses its equilibrium: critical SCR 1.37 (10 Hz PLL), 1.33 (20 Hz), 1.30 (40 Hz), against a static limit of 1.0 with voltage support and 2.0 at unity power factor. Without reactive support the GFL cannot even export 1 pu below SCR 2.
2. The GFL margin collapses inside the IEEE Std 1204 weak-grid band (SCR < 3): its least-damped oscillatory mode falls from about 0.70 damping at SCR 10 to 0.19 to 0.62 at SCR 1.5, and a coupled PLL/AC-voltage oscillation of roughly 5 to 7 Hz crosses into the right half plane. In this quasi-static model the PLL bandwidth shifts the critical SCR only slightly (1.30 to 1.37, faster PLL marginally better); the well-known penalty of a fast PLL needs network and current-loop dynamics (EMT detail) that this model omits, so it is not claimed here.
3. The grid-forming VSM stays stable at every SCR down to its static limit (last equilibrium SCR 1.01) for both H = 2 s and H = 5 s; its swing-mode damping actually rises as the grid weakens (H = 5 s: 0.090 at SCR 10, 0.194 at SCR 1.5).
4. This is the duality of Li, Gu and Green (IEEE Trans. Power Systems 2022): GFL is robust in strong grids and fragile in weak ones; GFM is the opposite, its weak spot is a lightly damped swing mode in strong grids (H = 5 s: zeta about 0.09 at SCR 10), which a larger D or a virtual-impedance damper addresses.
5. Indian context: large renewable complexes such as those in western Rajasthan feed long EHV corridors far from synchronous generation, which is exactly the low-SCR regime where this study shows GFL margins vanish and GFM remains stable. No substation-specific SCR values are asserted here; site SCRs must come from CEA/CTUIL system studies.

## Caveats
- Quasi-static (phasor) network: no line dynamics, no current-loop PI detail, no converter current limit; GFM E held constant in small-signal (no voltage-loop dynamics).
- GFL critical SCR uses the max real part of all eigenvalues, linearly interpolated on the 0.01 SCR grid.
- At SCR 10 to 2 the GFL dominant eigenvalue is the slow real AC-voltage-integrator pole (about -Kiv*Xg-scaled), so max Re alone is not monotone; the GC4 trend uses the minimum damping ratio of the oscillatory modes.
