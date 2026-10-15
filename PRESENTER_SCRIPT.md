# PRESENTER SCRIPT: Step 1 mid-semester evaluation

Project: Grid-Forming Control of a PMSG Wind Turbine Using Rotor Kinetic-Energy Reserve for Inertia and Fast Frequency Support in Weak Grids (Indian context)

Files you open: `Step1_Slides.pdf` (12 slides), `Step1_Progress_Report.pdf` (13 pages), folder `sim/` for a live run.
Time plan: 8 to 10 minutes for the slides, then the report on request. A 90-second version is at the end.

Every number below comes from `results/A.json`, `B.json`, `C.json`. Nothing is rounded beyond what the report shows.

---

## PART A: slide-by-slide script

### Slide 1: Title (10 s)
SAY: "Sir, my design project is on grid-forming control of a PMSG wind turbine. The idea is to make the turbine itself supply inertia and frequency support to a weak grid, using its own rotor energy, without a battery. This is Step 1: the models, the first simulations, and the verification."

### Slide 2: Problem and India context (60 s)
ON SCREEN: bullets on inertia, PLL, India numbers.
SAY: "A modern wind turbine connects through a back-to-back converter. The converter is grid-following: a phase-locked loop measures the grid frequency and the converter injects maximum-power-point power. Two consequences. First, the rotor's kinetic energy is hidden behind the converter, so the turbine adds zero inertia. Second, in a weak grid the PLL is tracking a voltage that the converter itself is disturbing, so it can lose synchronism."
"This is now an Indian problem. About 54 GW of wind is installed. Ember reports 68 events between January 2022 and July 2025 where more than one gigawatt of renewable generation was lost in a single incident, traced to ride-through failures and PLL instability in weak-grid conditions, mostly in the Rajasthan renewable complexes. GRID-INDIA published a discussion paper on grid-forming inverters in February 2026. It recommends grid-forming capability, but it covers batteries and solar in detail and says very little about wind. That gap is what this project addresses. The CEA technical-standards amendment applies from April 2027, so the timing is right."

### Slide 3: Link to the course (45 s)
ON SCREEN: Figure A1, Cp versus tip-speed ratio for several pitch angles, Betz line.
SAY: "Everything here starts from what we did in class. Power in the wind is half rho A v cubed. The Betz limit is 16 by 27, about 0.593. This is the Cp versus lambda family for my 2 MW turbine, using the Heier model. The peak is Cp max 0.480 at lambda opt 8.10, which is 81 percent of Betz. Real blades sit below Betz because of drag, the C D by C L term from our aerodynamic-efficiency derivation. Maximum power point tracking means staying on this peak, the Cp-optimal line, which gives the P equals K omega cubed law. The control strategies from the notes, pitch control and controlling electrical power through the power-electronic interface, are exactly the two handles I use."

### Slide 4: Key idea, overspeed deloading (60 s)
ON SCREEN: Figure A2, power versus rotor speed, MPPT locus and 10 percent deloaded locus.
SAY: "Here is the one idea the whole project rests on. These grey curves are turbine power versus rotor speed for each wind speed. The black dashed line is the MPPT locus. I deliberately operate off it, on the overspeed side, shown by the green locus. At 9 metres per second, MPPT is 844 kilowatts at 19.7 rpm. Deloaded, the turbine runs at 23.3 rpm and produces 759 kilowatts. That holds back 84 kilowatts as reserve, and it stores extra kinetic energy because the rotor is faster."
"Now the important part. If the grid frequency falls and the converter pulls more power, the rotor slows. Because we are on the overspeed side, slowing moves the rotor toward the peak, so Cp rises and aerodynamic power increases exactly when the grid needs it. Kinetic energy and reserve come out together. On the MPPT side the opposite happens: slowing reduces aerodynamic power and you get a secondary dip. No pitch is used below rated wind. Above 12 metres per second the speed limit binds and pitch takes over, 1.2 degrees at 12 metres per second, 8.5 degrees at 14."

### Slide 5: What the reserve buys (45 s)
ON SCREEN: Figure A4, reserve power and releasable kinetic energy versus wind speed.
SAY: "Top panel: the reserve grows with wind speed, 25 kilowatts at 6 metres per second, 84 at 9, 154 at 11, and 200 kilowatts at rated. Bottom panel: the kinetic energy that can be released. At 9 metres per second one turbine can release 1.36 megajoules while slowing back to the MPPT speed, and 3.23 megajoules down to the 0.5 per-unit speed limit. In inertia terms that is an equivalent H of 0.68 seconds and 1.62 seconds on the 2 MW rating."
"The cost is energy. For an illustrative Indian onshore site with a Weibull k of 2 and scale 7.5, a permanent 10 percent deload cuts annual energy from 4,725 to 4,253 megawatt-hours, capacity factor 27 to 24.3 percent, about 16.5 lakh rupees a year at 3.5 rupees per unit. That is an upper bound. The reserve only has to be held in low-inertia hours, and it replaces a battery."

### Slide 6: Test system and the five cases (45 s)
ON SCREEN: table of cases C0 to C4.
SAY: "The test system is a Kundur-style equivalent: one synchronous fleet with H of 5 seconds and a reheat steam governor, a DC power-flow network, 1000 megawatts of load, and a 50 megawatt load step at one second. Wind supplies 40 percent of the load at 9 metres per second, which is 474 turbines, 948 megawatts installed."
"Five cases. C0, all synchronous, the reference. C1, grid-following MPPT wind, today's practice. C2, grid-following with synthetic inertia and droop but no reserve, which is what vendors offer now. C3, the same grid-following controller but with my 10 percent reserve. C4, the proposal: a grid-forming virtual synchronous machine with the 10 percent reserve. C2, C3 and C4 use identical gains, H v of 5 seconds and 5 percent droop, so the comparison is fair."

### Slide 7: Headline result, frequency after the step (75 s)
ON SCREEN: Figure B1, load-bus frequency, five curves, IEGC band shaded.
SAY: "This is the main result. Grey band is the IEGC operating band, 49.90 to 50.05 hertz."
"Black dashed, all synchronous: nadir 49.771 hertz. Red, grid-following MPPT: replacing 40 percent of generation with wind cuts the system inertia from 5.88 to 3.76 seconds, the nadir drops to 49.659 and the RoCoF at the step goes from 0.21 to 0.33 hertz per second."
"Orange, synthetic inertia without reserve. It looks good for the first two seconds, then keeps sagging. It borrows rotor energy, the rotor falls from 0.75 to 0.70 per unit, leaves the Cp optimum, capture drops, and the frequency reaches its minimum only at 11 seconds, 49.815 hertz, and settles worse than no support at all. That is the known secondary-dip problem, reference Ullah 2008."
"Green, the proposal. Nadir 49.906 hertz, inside the IEGC band. RoCoF at the instant of the step 0.162 hertz per second, half of grid-following. System inertia 8.51 seconds. Rotor only slows from 0.888 to 0.831 per unit, still above the MPPT speed, so there is no secondary dip."
"I want to be honest about one thing. Blue, grid-following with the same reserve, reaches the same nadir. The reserve sets the nadir. Where grid-forming wins is the instantaneous RoCoF, because it responds as a voltage source without measuring frequency, the real inertia it adds, and weak-grid stability, which is the next slide but one."

### Slide 8: Why, the wind-plant response (45 s)
ON SCREEN: Figure B2, plant electrical power, aerodynamic power, rotor speed for C2, C3, C4.
SAY: "This explains the previous slide. Top: electrical power. Orange, no reserve, spikes to 433 megawatts and then decays, because it is only borrowing. Green, with reserve, steps from 360 to about 397 megawatts and holds about 387. Middle: aerodynamic power. Orange falls as the rotor leaves the optimum. Green rises from 360 to 386 megawatts as the rotor slows toward the peak, exactly the overspeed effect from slide 4. Bottom: rotor speed. Orange drops below the MPPT speed. Green stays above it throughout."

### Slide 9: Metrics and penetration sweep (45 s)
ON SCREEN: Figures B3 and B4.
SAY: "B3 summarises nadir, RoCoF and secondary dip per case. B4 is the result I find most interesting. As wind share rises from 10 to 60 percent, the grid-following nadir gets worse, 49.751 down to 49.547 hertz. The grid-forming nadir gets better, 49.811 up to 49.928 hertz. Every grid-forming turbine you add brings its own inertia and its own reserve, so more wind means a stronger grid, not a weaker one."

### Slide 10: Weak-grid stability, the duality (60 s)
ON SCREEN: Figure C1, GFL eigenvalue real part versus SCR for three PLL bandwidths; GFM damping versus SCR.
SAY: "Short-circuit ratio is the fault level at the connection point divided by the plant rating. Below 3 is weak by IEEE Standard 1204. Rajasthan hubs are weak in this sense."
"Left: a grid-following converter exporting 1 per unit with a PLL and an AC-voltage loop. As SCR falls its damping collapses, from about 0.70 at SCR 10 down to between 0.19 and 0.62 at SCR 1.5, and a 5 to 7 hertz PLL-voltage-loop oscillation crosses into the right half plane at SCR 1.30 to 1.37 depending on PLL bandwidth. Right: the grid-forming virtual synchronous machine stays stable all the way down to the static limit at SCR 1.0, and its swing-mode damping improves as the grid gets weaker. This is the duality from Li, Gu and Green, 2022: grid-following likes a stiff grid, grid-forming likes a weak one. Weak Indian hubs are exactly where grid-forming belongs."
"I also checked the frequency case with a weaker connection, SCR from 3 down to 1. The nadir stays at 49.906 and the damping ratio of the machine-converter mode rises from 0.25 to 0.60."

### Slide 11: Verification (30 s)
ON SCREEN: table of 16 checks.
SAY: "I did not want simulations that merely look plausible, so every model is checked against a hand-derivable result. Sixteen checks, all pass. Examples: Cp max below Betz. MPPT reproduces rated power at 12 metres per second to 1 percent. The initial rate of change of frequency matches the analytic delta P times f0 over 2 H to within 1 percent in all cases. The grid-following steady-state frequency matches the droop formula to 10 to the minus 10. Rotor energy balance closes to 10 to the minus 11. The grid-forming swing mode matches the closed-form natural frequency and damping to 2 percent."

### Slide 12: Steps 2 and 3 (30 s)
SAY: "Step 1 is an aggregated model, averaged converters and a DC power-flow network. Step 2 adds the detailed PMSG dq model with machine-side and grid-side converters and the DC link, dual-port grid-forming control from Lyu and Gross, current limiting and fault ride-through, and realistic frequency-measurement windows for the grid-following comparison. Step 3 moves to the IEEE 9-bus system, turbulent wind, and a check against the Indian grid-code requirements, then the final report. Thank you, sir."

---

## PART B: walking him through the LaTeX report

Open `Step1_Progress_Report.pdf`. Say "the report has the equations and all the numbers behind the slides", then follow this order.

1. **Page 1, abstract and the key-numbers box.** Point at the box. "These eight numbers are the summary. Nadir 49.659 versus 49.906. RoCoF 0.332 versus 0.162. System inertia 3.76 versus 8.51 seconds. Critical SCR 1.30 to 1.37 for grid-following, 1.0 for grid-forming."
2. **Section 1, Motivation.** The three India facts with citations [11] GRID-INDIA, [12] Ember, [13] CEA. One line each.
3. **Section 2, Link to course theory.** Point at the Key idea paragraph: operate off the Cp-optimal line on the overspeed side.
4. **Section 4.1, equation (1).** "The Heier Cp model, same form as the course's Cp versus lambda, with the six coefficients from Heier [8]. Table 1 is the turbine."
5. **Section 4.2, equation (2) onward.** "Deloading is Cp at lambda del equals 0.9 Cp max. The rotor swing equation 2 H omega d omega by dt equals P aero minus P e is the same swing equation we use for a synchronous machine."
6. **Section 4 GFL and GFM laws.** Point at the synthetic-inertia law, minus 2 H v d omega m by dt minus droop, and say it needs a measured frequency. Then the grid-forming law, 2 H v d omega v by dt equals P del minus the stall guard plus droop minus P e minus damping. "No frequency measurement appears on the right-hand side. That is the whole difference." If he asks what the stall guard is: it backs the set-point off only if the rotor ever passes the Cp peak, so the turbine can never run onto the unstable low-speed side.
7. **Section 4, test system.** Kundur reheat governor parameters [7], network reactances, 474 turbines.
8. **Section 5.1, figures A1 to A5.** Only if he wants the aerodynamic detail. A5 is the energy-cost figure.
9. **Section 5.2, figure B1 and the metrics table.** Read the C1 and C4 rows. Say the honest C3 point yourself before he does.
10. **Section 5.3, figure C1.** The duality. Mention the model is quasi-static, so the fast-PLL penalty is a Step 2 item.
11. **Section 6, verification table.** "Sixteen gates, every one against an analytic value."
12. **Section 7, plan table.** Weeks for Steps 2 and 3.
13. **References.** See Part C if he asks which paper is the base.

---

## PART C: which research paper was used for what

If he asks "which paper is your base paper", answer: **Lyu and Gross, IEEE Transactions on Sustainable Energy 2024 [1]**, with **Yao et al., Frontiers in Energy Research 2026 [3]** for the deloading strategy. Then:

| Ref | Paper | What I took from it |
|---|---|---|
| [1] | Y. Lyu, D. Gross, "Grid forming fast frequency response for PMSG-based wind turbines," IEEE Trans. Sustainable Energy, 15(1), 23-38, 2024 | The base paper. Grid-forming PMSG turbine whose reserve and kinetic energy are set by rotor-speed and pitch; covers MPPT to inertia to fast frequency response with no mode switching. My C4 is a simplified version. Step 2 implements their dual-port control. |
| [2] | Lyu, Subotic, Gross, "Unified grid-forming control of PMSG wind turbines for fast frequency response and MPPT," IREP 2022, arXiv 2207.09536 | Conference version of [1]; the small-signal stability conditions linking control gains and curtailment. |
| [3] | Yao et al., "Grid-forming wind turbine control based on novel deloading strategy and adaptive configurable natural droop controller," Frontiers in Energy Research, 2026 | The deloading recipe: target Cp equals k del times Cp max, overspeed first, pitch only when the speed limit binds, a speed floor at the optimum. Their 2 MW PMSG with H 3 s is my turbine size. |
| [4] | D'Arco, Suul, "Equivalence of virtual synchronous machines and frequency-droops for converter-based microgrids," IEEE Trans. Smart Grid, 5(1), 2014 | The VSM swing law used for C4 and the damping term referenced to the measured PCC frequency. |
| [5] | Li, Gu, Green, "Revisiting grid-forming and grid-following inverters: a duality theory," IEEE Trans. Power Systems, 37(6), 2022 | Task C: grid-following loses stability as SCR falls, grid-forming gains damping; the duality framing on slide 10. |
| [6] | Ullah, Thiringer, Karlsson, "Temporary primary frequency control support by variable speed wind turbines," IEEE Trans. Power Systems, 23(2), 2008 | The secondary-dip and recovery problem of non-deloaded turbines, which my case C2 reproduces. |
| [7] | Kundur, Power System Stability and Control, 1994 | Reheat steam governor-turbine model and parameters, swing equation, centre-of-inertia frequency. |
| [8] | Heier, Grid Integration of Wind Energy Conversion Systems, 1998 | The Cp(lambda, beta) coefficient model, equation (1). |
| [9] | Bhadra, Kastha, Banerjee, Wind Electrical Systems, OUP | The course textbook: Betz, Cp-TSR, MPPT on the Cp-optimal line, control strategies. |
| [10] | "An overview of grid-forming control for wind turbine converters," IEEE IECON 2021 | Survey used for the literature review and the classification of GFM methods. |
| [11] | GRID-INDIA, discussion paper on grid-forming inverters, Feb 2026 | India motivation: GFM recommended, wind under-addressed. |
| [12] | Ember, India renewables integration analysis, 2026 | The 68 events of more than 1 GW lost, PLL instability in Rajasthan. |
| [13] | CEA, Technical Standards (Amendment) Regulations, 2026 | Applies from 1 April 2027. |
| [14] | CERC, Indian Electricity Grid Code 2023 | The 49.90 to 50.05 Hz operating band shaded in figure B1. |
| [15] | IEEE Std 1204-1997 | SCR below 3 defines a weak grid. |

Gap statement, one sentence: "[1] and [3] are validated on strong-grid test systems and do not treat the Indian weak-grid context or the trade-off against grid-following with the same reserve; my Step 1 adds both, and Step 2 adds the detailed converter model."

---

## PART D: if he asks to run the code

Open a terminal (PowerShell) and paste these, one at a time. Everything is Python, no MATLAB.

```
cd "C:\Users\Administrator\Downloads\Wind electrical\STEP1_MIDSEM\sim"
python turbine.py
```
Instant. Prints lambda opt 8.10, Cp max 0.480, rated 12 m/s, 26.2 rpm, and the deloaded operating point per wind speed with a check column showing the error is 1e-14. Say: "This is the shared physics module every simulation imports."

```
python a_aero.py
```
About 5 seconds. Prints gates GA1 to GA6 PASS and rewrites figures A1 to A5 in the figures folder. Say: "Aerodynamics and the operating-point design."

```
python b_freq.py
```
About 45 seconds to a minute. Prints the metrics dictionary for C0 to C4, then GB1 to GB6 PASS, then the penetration and weak-connection sweeps. Rewrites figures B1 to B5. Say: "This is the frequency study. The gate lines are the analytic checks. The sweeps take most of the time." Open `figures\B1_frequency.png` after it finishes.

```
python c_weakgrid.py
```
About a minute. Prints GC1 to GC4 PASS and the critical SCR for each variant. Rewrites C1 and C2.

Where things are: `sim/` the four scripts, `figures/` PNG and PDF of every plot, `results/` the JSON with every number plus a summary markdown per task, `report/` the LaTeX source. If he asks what the model is written in: SciPy `solve_ivp` with LSODA, per-unit equations, numerical Jacobians for the eigenvalue study.

---

## PART E: the eight questions to be ready for

1. **Why overspeed and not pitch?** Overspeed stores energy and the converter releases it in milliseconds; pitch is slow and wears the actuator. Pitch is used only above rated wind when the 1.2 pu speed limit binds.
2. **Synthetic inertia already exists, what is new?** It needs a measured frequency, so it is delayed and noisy, and without a reserve it causes a secondary dip. Grid-forming responds as a voltage source and the reserve removes the dip.
3. **GFL with reserve gets the same nadir, so why GFM?** Instantaneous RoCoF halves, real inertia is added, and it stays stable in weak grids where the PLL fails. Say this before he asks.
4. **Isn't 10 percent deloading wasteful?** 473 MWh per year per turbine if held all year, an upper bound. Hold it only in low-inertia hours, and it replaces a battery.
5. **What is SCR?** Fault level divided by plant rating. Below 3 is weak.
6. **Why Python and not Simulink?** Custom per-unit model on SciPy's ODE solvers, every block checked against an analytic result. Step 2 can go to Simulink if required.
7. **Why such a simple network?** Step 1 is about seconds-timescale frequency dynamics. Switching, current loops and the network's electromagnetic dynamics are Step 2.
8. **Cp max is 0.48 but Betz is 0.593?** Drag, tip loss and wake rotation; the tan epsilon term in our efficiency derivation.

---

## 90-second version (if he is short of time)
"Wind turbines today give zero inertia and their PLL fails in weak grids, which is exactly what is happening in Rajasthan. I make the turbine grid-forming and run it 10 percent off the Cp-optimal line on the overspeed side, so when frequency drops the rotor releases kinetic energy and, because slowing raises Cp, the aerodynamic power rises too. On a 1000 MW test system with 40 percent wind and a 50 MW load step, grid-following gives a nadir of 49.659 hertz; my grid-forming turbine gives 49.906, inside the IEGC band, with half the initial RoCoF and no secondary dip. Grid-following loses stability at an SCR of about 1.3; grid-forming is stable to 1.0. Sixteen analytic checks pass. Step 2 is the detailed converter model."

---

## PART F: every figure, explained (what is on the axes, what each curve is, what to say)

All figures are in `figures/` as PNG and PDF. Report figure numbers in brackets.

### A1 Cp versus tip-speed ratio [Fig. 1]
Axes: x = tip-speed ratio lambda = omega R / v, 0 to 16; y = power coefficient Cp. Six curves for pitch angle beta = 0, 2, 5, 10, 15, 20 degrees. A dot marks Cp max 0.480 at lambda opt 8.10 on the beta = 0 curve. A dashed horizontal line is the Betz limit 16/27 = 0.593.
SAY: "Same shape as the Cp-lambda curve from class. Zero pitch gives the highest peak. Increasing pitch pulls the whole curve down, which is how pitch control sheds power above rated wind. The peak sits at 81 percent of Betz because of drag and tip losses. Left of the peak is the stall side, where Cp falls steeply as lambda falls; that side is unstable for a constant-power controller, which is why my stall guard exists."

### A2 Turbine power versus rotor speed [Fig. 2]
Axes: x = rotor speed in rpm, 10 to 33; y = turbine power in MW. Grey curves: one per wind speed 6 to 13 m/s, labelled on the right. Black dashed: MPPT locus P = K opt omega cubed, through the peaks, capped at 2 MW. Green: the 10 percent deloaded locus for 6 to 12 m/s, to the right of the peaks. Black circles: MPPT points at 8, 10, 12 m/s. Green squares: deloaded points. Green diamond at 26.2 rpm, 1.8 MW: above rated wind the speed is held at rated and pitch does the deloading. Dotted verticals: speed limits 13.1 and 31.5 rpm (0.5 and 1.2 pu). Red line: rated 2 MW.
SAY: "Pick 10 m/s. MPPT sits on the peak at 21.8 rpm, 1.16 MW. The deloaded point is to the right at 25.8 rpm, 1.04 MW. From there, if the converter draws more power than the aerodynamics supply, the rotor decelerates, moves left toward the peak, and aerodynamic power rises. That is the whole trick. At 12 m/s the deloaded speed would exceed the 1.2 pu limit, so the controller holds 26.2 rpm and pitches 1.18 degrees instead."

### A3 Steady power curve [Fig. 3]
Axes: x = wind speed 0 to 26 m/s; y = power in MW. Black dashed: MPPT curve, cubic from cut-in 3.5 m/s to rated 12 m/s, flat at 2 MW to cut-out 25 m/s, zero after. Green: 10 percent deloaded curve, 1.8 MW flat part. Shaded band between them: the reserve. Vertical markers at cut-in, rated, cut-out.
SAY: "This is the textbook power curve with cut-in, rated and furling speeds from the notes. The shaded band is what I give back to the grid as reserve: it grows as v cubed up to rated, then is a constant 200 kW."

### A4 Reserve and releasable kinetic energy [Fig. 4]
Top panel: x = wind speed 6 to 14 m/s; y = reserve power in kW; marker style shows the mode: overspeed only (6 to 11 m/s), pitch (12 to 14 m/s). Bottom panel: y = kinetic energy in MJ that one turbine can release, two curves: from the deloaded speed down to the MPPT speed, and down to the 0.5 pu minimum; right axis converts to an equivalent inertia constant H eq = E / 2 MW in seconds.
SAY: "Reserve rises from 25 kW at 6 m/s to 200 kW at rated. The energy curve to the MPPT speed is zero above 12 m/s because the deloaded speed equals the rated speed there; the energy to the speed floor is about 4.5 MJ, H eq 2.25 s. At 9 m/s, 1.36 MJ and 3.23 MJ."

### A5 Site energy and annual production [Fig. 5]
Left: Weibull wind-speed probability density, k = 2, c = 7.5 m/s, a typical Indian onshore shape with mean about 6.6 m/s. Right: bars of annual energy per turbine, MPPT 4,725 MWh versus deloaded 4,253 MWh.
SAY: "The energy price of a permanent reserve is 10 percent exactly, 473 MWh a year, about 16.5 lakh rupees. It is an upper bound because the reserve is only needed in low-inertia hours."

### B1 System frequency after the load step [Fig. 6]
Axes: x = time 0 to 40 s; y = load-bus frequency in Hz. Grey band: IEGC 49.90 to 50.05 Hz. Five curves: black dashed C0, red C1, orange C2, blue dashed C3, green C4 (C3 and C4 overlap after the first second, which is why C3 is dashed). Inset: the first 300 ms after the step.
SAY: what is written under slide 7. Point at the inset: "In the first 300 ms the green and blue curves have the same slope because my grid-following measurement lag is only 50 ms, an optimistic assumption; the difference shows at the very first instant, 0.162 against 0.332 Hz per second, and in the inertia count."

### B2 Wind-plant response [Fig. 7]
Three panels against time. Top: plant electrical power in MW (sum of 474 turbines). Middle: plant aerodynamic power in MW. Bottom: rotor speed in pu of rated, with a dotted line at the MPPT speed 0.75 pu for 9 m/s. Orange C2, blue dashed C3, green C4.
SAY: "Orange starts at 400 MW on MPPT, spikes to 433 MW using the inertia loop, then decays because the rotor slows below the optimum and aerodynamic power falls to 394 MW. Green starts at 360 MW deloaded, steps to about 397 MW, and holds about 387 MW, because the rotor moves from 0.888 to 0.831 pu, still above the optimum, and aerodynamic power rises from 360 to 386 MW. The extra 37 MW is the reserve plus kinetic energy."

### B3 Metrics by case [Fig. 8]
Three bar groups, one bar per case C0 to C4: nadir deviation in mHz (229, 341, 185, 94, 94), RoCoF over the first 500 ms in Hz/s (0.198, 0.305, 0.122, 0.115, 0.116), secondary dip in mHz (about 1, about 1, 0, 0, 0).
SAY: "Nadir deviation drops from 341 mHz with grid-following to 94 with the reserve. The 500 ms RoCoF bars for C2, C3, C4 are similar, which is honest: over half a second a fast synthetic-inertia loop can match grid-forming. The instantaneous value and the weak-grid behaviour are where they differ."

### B4 Sensitivity to wind penetration [Fig. 9]
Two panels against wind share p = 0.1 to 0.6. Left: frequency nadir in Hz; right: 500 ms RoCoF in Hz/s. Red C1, orange C2, green C4, black dashed horizontal C0 reference.
SAY: "Red falls monotonically: more grid-following wind, less inertia. Orange is not monotonic, it peaks at 30 percent then collapses at 60 percent, because without a reserve it has nothing to draw on. Green rises: every grid-forming turbine adds inertia and reserve, so at 60 percent the nadir is 49.928 Hz, better than the all-synchronous grid."

### B5 Effect of a weak connection on the proposed plant [Fig. 10]
Three small panels against SCR at the wind bus, 1 to 3, obtained by raising X23 from 0.1 to 0.8 pu. Nadir in Hz (flat at 49.906 within 0.0002 Hz; the axis label shows an offset), 500 ms RoCoF (0.112 to 0.148 Hz/s), damping ratio of the synchronous-machine-versus-VSM mode (0.25 at SCR 3 to 0.60 at SCR 1; dotted line at 0.3).
SAY: "Weakening the connection does not hurt the support. The nadir is unchanged, RoCoF rises slightly because the plant is electrically farther away, and the damping of the electromechanical mode improves as the grid gets weaker, which is the same duality as Task C."

### C1 Weak-grid small-signal stability [Fig. 11]
(a) Grid-following converter. x = SCR from 10 down to 1 (note the reversed axis: weaker grid to the right); y = real part of the dominant eigenvalue in 1/s on a symmetric log scale; shaded pink = unstable. Three curves: PLL bandwidth 10 Hz black dashed, 20 Hz orange, 40 Hz red, almost on top of each other. Dashed vertical at SCR 3, the IEEE 1204 weak-grid threshold.
SAY: "From SCR 10 down to about 2 the slowest pole is the AC-voltage integrator, sitting a few per second into the left half plane. Below SCR 2 a coupled PLL and voltage-loop oscillation of a few hertz takes over and shoots into the right half plane at SCR 1.37, 1.33, 1.30 for the three bandwidths. PLL bandwidth barely matters in this quasi-static model; the well-known penalty of a fast PLL needs the electromagnetic dynamics of the network, which are a Step 2 item."
(b) Grid-forming VSM. y = damping ratio of the swing mode. Blue H = 2 s, green H = 5 s.
SAY: "Damping is low in a stiff grid, 0.09 to 0.14 at SCR 10, and rises as the grid weakens, approaching 1 at SCR 1. The closed form is zeta = D divided by 4 H omega n with omega n = root of K s omega b over 2 H; a weaker grid lowers K s, lowers omega n and raises zeta. Higher H lowers zeta for the same D, which is why the green curve is below the blue. Check GC2 confirms this formula to 2 percent."

### C2 Eigenvalue loci [Fig. 12]
Two s-planes, x = real part in 1/s, y = imaginary part in rad/s, colour = SCR from 10 (yellow) to 1 (purple). Left: grid-following, 20 Hz PLL. Right: grid-forming, H = 5 s.
SAY: "Left: as SCR falls, the complex pair that starts near minus 85 plus or minus 88 rad/s walks to the right, bends, and crosses the imaginary axis at about plus or minus 20 to 40 rad/s, 3 to 7 hertz: that is the PLL-voltage-loop oscillation going unstable. Right: the grid-forming swing pair stays at a real part of exactly minus 1 per second, which is D over 4 H = 20 over 20, independent of SCR; only its frequency shrinks from 11 rad/s to about 1 rad/s as the grid weakens. The real part never moves toward the axis. That is why grid-forming is the natural choice for a weak grid."
