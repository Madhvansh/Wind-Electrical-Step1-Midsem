# Task B summary (frequency support), regenerated 17:10 after the set-point fix

MODEL NOTE: the reserve cases (C3, C4) now hold a CONSTANT deloaded set-point P_del (plus a stall guard that backs the set-point off only if the rotor passes the Cp peak). The first version used k_del*w^3, which withdrew part of the reserve as the rotor slowed and produced a slow sag to 49.838 Hz at 11 s. A constant set-point is self-stabilising on the overspeed side (dP_aero/dw < 0 there) and releases the full reserve. VSM damping term is referenced to the PCC (load-bus) frequency, Dd*(wv - w3), as in D'Arco and Suul; Dd = 100. All gates GB1-GB6 re-checked: PASS.

| Case | nadir (Hz) | nadir dev (mHz) | t_nadir after event (s) | RoCoF_inst (Hz/s) | RoCoF_500ms (Hz/s) | df_ss at 40 s (Hz) | min w_r (pu) | extra wind energy 10 s (MJ) | peak extra wind (MW) |
|---|---|---|---|---|---|---|---|---|---|
| C0 all-synchronous | 49.771 | -229 | 2.14 | 0.213 | 0.198 | -0.097 | n/a | 0 | n/a |
| C1 GFL-MPPT | 49.659 | -341 | 2.09 | 0.332 | 0.305 | -0.148 | 0.750 | 0 | 0.0 |
| C2 GFL+SI+droop, no reserve | 49.815 | -185 | 11.20 | 0.332 | 0.122 | -0.160 | 0.701 | 167 | 33.4 |
| C3 GFL+SI+droop, 10% reserve | 49.906 | -94 | 2.07 | 0.332 | 0.115 | -0.070 | 0.831 | 317 | 36.9 |
| C4 GFM-VSM, 10% reserve (proposed) | 49.906 | -94 | 2.03 | 0.162 | 0.116 | -0.070 | 0.831 | 317 | 37.2 |

COI RoCoF just after the step (Hz/s): C0 0.212, C1 0.331, C2 0.268, C3 0.268, C4 0.148
System inertia constant H_sys (s): C0 5.88, C1 3.76, C4 8.51 (virtual inertia of the GFM plant counted).

Penetration sweep p = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
- C1 nadir (Hz): [49.751, 49.726, 49.696, 49.659, 49.611, 49.547] ; RoCoF_500ms (Hz/s): [0.217, 0.24, 0.268, 0.305, 0.353, 0.419]
- C2 nadir (Hz): [49.807, 49.825, 49.827, 49.815, 49.785, 49.685] ; RoCoF_500ms (Hz/s): [0.172, 0.152, 0.135, 0.122, 0.111, 0.101]
- C4 nadir (Hz): [49.811, 49.851, 49.888, 49.906, 49.918, 49.928] ; RoCoF_500ms (Hz/s): [0.166, 0.145, 0.129, 0.116, 0.104, 0.093]
- C0 reference: nadir 49.771 Hz, RoCoF_500ms 0.198 Hz/s

Weak-connection sweep for C4 (Dd fixed):
| X23 (pu) | SCR at wind bus | nadir (Hz) | RoCoF_500ms (Hz/s) | SG-VSM damping ratio | mode (Hz) |
|---|---|---|---|---|---|
| 0.10 | 3.01 | 49.906 | 0.112 | 0.250 | 1.83 |
| 0.20 | 2.34 | 49.906 | 0.116 | 0.312 | 1.62 |
| 0.40 | 1.62 | 49.906 | 0.125 | 0.419 | 1.32 |
| 0.60 | 1.24 | 49.906 | 0.136 | 0.512 | 1.09 |
| 0.80 | 1.00 | 49.906 | 0.148 | 0.600 | 0.89 |

Gates: GB1 PASS, GB2 PASS, GB3 PASS, GB4 PASS, GB5 PASS, GB6 PASS
GB2 analytic vs simulated COI RoCoF (Hz/s): C0 0.2125 vs 0.2121 (err 0.19%); C1 0.3320 vs 0.3312 (err 0.24%); C4 0.1470 vs 0.1483 (err 0.93%)
GB3 C1 steady-state df analytic -0.14826 Hz vs sim -0.14826 Hz.

FINDINGS (plain words):
- Replacing 40% of generation with grid-following MPPT wind (C1) cuts system inertia from 5.88 s to 3.76 s; the nadir falls from 49.771 Hz (all-synchronous) to 49.659 Hz and RoCoF_500ms rises from 0.198 to 0.305 Hz/s.
- Synthetic inertia without a reserve (C2) only borrows rotor kinetic energy: the rotor slows from 0.750 to 0.701 pu, leaves its Cp-optimum, and the frequency keeps sagging to a late minimum of 49.815 Hz at 11.2 s after the step, settling at -0.160 Hz deviation, worse than no support at all (C1 -0.148 Hz). This is the secondary-dip / recovery problem of non-deloaded turbines (Ullah et al. 2008), here appearing as a prolonged sag.
- With the 10% overspeed reserve (C3, C4) the rotor slows only from 0.888 to 0.831 pu, staying above the MPPT speed, so slowing RAISES aerodynamic power; the plant delivers about 37 MW extra and the nadir is 49.906 Hz, inside the IEGC 49.90-50.05 Hz band, with no secondary dip.
- Grid-forming (C4) vs grid-following with the same reserve (C3): nadir and settling are practically identical, because the reserve sets them. GFM halves the instantaneous RoCoF at the step (0.162 vs 0.332 Hz/s, COI 0.148 vs 0.268 Hz/s) because it responds as a voltage source with no frequency measurement, and it adds real inertia (H_sys 8.51 s vs 3.76 s). Over a 500 ms window both are about 0.116 Hz/s because our GFL measurement lag is an optimistic 50 ms; realistic RoCoF-measurement windows (100-500 ms) and weak-grid PLL limits (Task C) are where GFM is decisive. Step 2 will quantify this.
- Penetration sweep: as wind share rises from 10% to 60%, the GFL-MPPT nadir worsens from 49.751 to 49.547 Hz, while the proposed GFM nadir IMPROVES from 49.811 to 49.928 Hz, because every added GFM turbine adds both virtual inertia and reserve.

Captions:
- B1_frequency: Load-bus frequency after a 50 MW (5%) load step at 40% wind, 9 m/s, for the five cases; inset zooms on the first 300 ms; shaded IEGC 2023 band.
- B2_wind_response: Wind-plant electrical power, aerodynamic power and rotor speed for C2, C3 and C4.
- B3_metrics: Nadir deviation, 500 ms RoCoF and secondary-dip depth per case.
- B4_penetration: Nadir and 500 ms RoCoF versus wind penetration for C1, C2 and C4, with the all-synchronous reference.
- B5_weak_connection: Proposed GFM plant versus short-circuit ratio at the wind bus: nadir, RoCoF and SG-VSM mode damping ratio.
