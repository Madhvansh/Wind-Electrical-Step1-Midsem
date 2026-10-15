# Step 1: what to say to the professor (read this once, 10 minutes)

## The 3-minute pitch
1. **Problem.** Wind turbines connect through power electronics. Today they are *grid-following*: a PLL measures grid frequency and the converter injects MPPT power. So they add **zero inertia**, and in **weak grids (low SCR)** the PLL itself can lose synchronism. India logged 68 events (Jan 2022 to Jul 2025) where more than 1 GW of renewables tripped in one incident, mostly in the Rajasthan RE hubs (Ember). GRID-INDIA's Feb 2026 discussion paper asks for *grid-forming* capability but focuses on batteries and solar, not wind. That gap is my project.
2. **Idea.** Make the turbine *grid-forming*: its converter behaves like a virtual synchronous machine with its own internal voltage and frequency. Run the rotor slightly **off the Cp-optimal line on the overspeed side** (10% deloading). When frequency falls, the converter instantly delivers more power and the rotor slows. Because we sat on the overspeed side, slowing moves lambda back toward lambda_opt, so **Cp rises and aerodynamic power increases exactly when the grid needs it**. Kinetic energy and reserve come out together, with **no secondary frequency dip** and no battery.
3. **Step 1 results.** See the numbers block below.
4. **Next.** Step 2: detailed PMSG dq model with both converters and DC link, current limiting and fault ride-through, IEEE 9-bus. Step 3: compliance with Indian grid-code requirements and final report.

## Numbers to quote (filled from the verified results)
- **Turbine:** 2 MW, R = 35.4 m, lambda_opt = 8.10, Cp_max = 0.480 (81% of Betz), rated 12 m/s at 26.2 rpm.
- **At 9 m/s:** MPPT gives 844 kW at 19.7 rpm. Overspeed deloading gives 759 kW at 23.3 rpm, with no pitch. That holds a 84 kW reserve per turbine, plus 1.36 MJ of kinetic energy released while slowing back to the MPPT speed.
- **Frequency test (50 MW step, 40% wind, 9 m/s):** all-synchronous nadir 49.771 Hz. Grid-following MPPT 49.659 Hz with 500 ms RoCoF 0.305 Hz/s. Synthetic inertia without reserve sags late to 49.815 Hz at 11.2 s and settles worse than no support. **Proposed grid-forming: 49.906 Hz, inside the IEGC 49.90 to 50.05 Hz band.**
- **RoCoF at the instant of the step:** 0.162 Hz/s for grid-forming vs 0.332 Hz/s for grid-following. System inertia 8.51 s vs 3.76 s.
- **Honest point:** grid-following with the same reserve reaches the same nadir (49.906 Hz) because the reserve sets the nadir. Grid-forming wins on instantaneous RoCoF, real inertia and weak-grid stability.
- **Penetration 10% to 60%:** the grid-following nadir worsens from 49.751 to 49.547 Hz. The grid-forming nadir improves from 49.811 to 49.928 Hz.
- **Weak grid:** grid-following with a PLL loses stability at an SCR of about 1.30 to 1.37, depending on PLL bandwidth. Grid-forming stays stable down to the static limit near SCR 1.0.
- **Cost of the reserve:** held continuously, it costs 10% of energy, 473 MWh/yr per turbine, about INR 16.5 lakh/yr at an illustrative INR 3.5/kWh. That is an upper bound, because the reserve is only needed in low-inertia hours.

## Likely questions and short answers
- **Why overspeed and not pitch for the reserve?** Overspeed stores extra kinetic energy (E = 0.5 J w^2) and the converter releases it in milliseconds. Pitch actuators are slow and wear. Pitch is used only when the 1.2 pu speed limit binds, above about 12 m/s.
- **Where does the inertia energy come from?** Rotor kinetic energy. H = 3 s means the rotor stores 3 seconds of rated power at rated speed.
- **Synthetic inertia already exists. What is new?** Grid-following synthetic inertia must first *measure* frequency (PLL + df/dt filter), so it is delayed and noise-sensitive. Without a reserve the rotor slows below its optimum, output falls, and you get a *secondary dip*. Grid-forming responds instantly as a voltage source, like a real generator, and the reserve removes the dip.
- **Isn't 10% deloading wasteful?** Held all year it costs 10% of energy. It only needs to be held in low-inertia hours, and it replaces a battery. Grid codes are moving toward paying for this service.
- **What is SCR?** Short-circuit ratio = fault level at the connection point / plant rating. Below 3 is weak (IEEE Std 1204).
- **Why Python, not Simulink?** Custom per-unit model on SciPy's ODE solvers. Every model is checked against an analytic result (the verification table), so the numbers are defensible.
- **Why such a simple network?** Step 1 studies frequency dynamics on a timescale of seconds. Electromagnetic detail (converter switching, current loops) is Step 2.
- **Cp_max is 0.48, but Betz says 0.593?** Real blades have drag (C_D/C_L, the tan epsilon term in our aerodynamic-efficiency derivation), tip losses and wake rotation, so they sit below Betz.
- **What is the duality result?** A grid-following converter gets *less* stable as the grid gets weaker. A grid-forming converter gets *better damped* as the grid gets weaker and needs damping in stiff grids. So weak Indian RE hubs are exactly where grid-forming fits.
