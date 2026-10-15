# Task A summary
- lambda_opt = 8.10, Cp_max = 0.480 (Betz 16/27 = 0.593; 81.0% of Betz).
- Rated wind speed 12.00 m/s; rated rotor speed 26.22 rpm (2.746 rad/s); K_opt = 96616 W/(rad/s)^3; J = 1.592e+06 kg m^2.
- Speed limits 13.11 to 31.46 rpm (0.5 to 1.2 pu).
- At 6 m/s: reserve 25 kW, overspeed, w_del 15.5 vs w_opt 13.1 rpm, E to W_MIN 0.60 MJ (H_eq 0.30 s).
- At 10 m/s: reserve 116 kW, overspeed, beta 0.00 deg, E to W_MIN 4.34 MJ (H_eq 2.17 s).
- At 12 m/s: reserve 200 kW, pitch, beta 1.18 deg, E to W_MIN 4.50 MJ (H_eq 2.25 s).
- Modes by v (6..14): 6:overspeed, 7:overspeed, 8:overspeed, 9:overspeed, 10:overspeed, 11:overspeed, 12:pitch, 13:pitch, 14:pitch.
- Worked example 9 m/s: w = 19.67 rpm, TSR = 8.10, Cp = 0.480, P = 0.844 MW.
- AEP (Weibull k=2, c=7.5, illustrative Indian onshore site): MPPT 4,725 MWh/yr (CF 27.0%), deloaded 4,253 MWh/yr (CF 24.3%); loss 10.00%.
- Cost of a continuous 10% reserve: 473 MWh/yr = INR 16.5 lakh/yr at 3.5 INR/kWh (revenue 165.4 to 148.9 lakh).
- The reserve need only be held in low-inertia hours, so the real cost is a fraction of this upper bound.
- Gates: GA1 PASS, GA2 PASS, GA3 PASS, GA4 PASS, GA5 PASS, GA6 PASS.

Captions
- A1: Cp(lambda) for beta 0 to 20 deg; peak at lambda_opt, well under the Betz limit.
- A2: Turbine power vs rotor speed per wind speed with MPPT and 10% deloaded loci; overspeed moves the point right of the peak.
- A3: Steady power curve, MPPT vs 10% deloaded, shaded reserve band, cut-in/rated/cut-out.
- A4: Reserve power by mode (top) and releasable kinetic energy with equivalent H_eq (bottom).
- A5: Weibull wind distribution and annual energy, MPPT vs deloaded.
