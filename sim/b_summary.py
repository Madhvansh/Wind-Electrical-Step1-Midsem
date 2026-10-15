"""Builds results/B_summary.md from results/B.json (Task B)."""
import json, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = json.load(open(os.path.join(BASE, "results", "B.json")))
M = B["metrics"]; P = B["parameters"]; G = B["gates"]; S = B["sweep_penetration"]; W = B["sweep_weak_connection"]
L = []; a = L.append
a("# Task B: frequency-support dynamics (headline result)\n")
a("Source: sim/b_freq.py (imports sim/turbine.py). All numbers below are copied from results/B.json.\n")
a("## Metrics per case (p = 0.40, v = 9 m/s, 50 MW load step at t = 1 s, X23 = 0.20 pu)\n")
a("| Case | f_nadir (Hz) | nadir dev (mHz) | t_nadir (s) | RoCoF_inst (Hz/s) | RoCoF_500ms (Hz/s) | df_ss at 40 s (Hz) | secondary dip (mHz) | min w_r (pu) | extra wind energy 10 s (MJ) | peak extra wind (MW) |")
a("|---|---|---|---|---|---|---|---|---|---|---|")
f = lambda v, n: "-" if v is None else f"{v:.{n}f}"
for c in ["C0", "C1", "C2", "C3", "C4"]:
    m = M[c]
    a(f"| {B['labels'][c]} | {m['f_nadir_Hz']:.4f} | {m['nadir_dev_mHz']:.1f} | {m['t_nadir_s']:.2f} | {m['RoCoF_inst_Hzps']:.4f} | {m['RoCoF_500ms_Hzps']:.4f} | {m['df_ss_Hz']:.4f} | {m['secondary_dip_mHz']:.1f} | {f(m['min_wr_pu'],4)} | {m['extra_wind_energy_10s_MJ']:.1f} | {f(m.get('peak_extra_wind_MW'),1)} |")
a("\nFrequency is reported at the load bus (bus 3): GFL cases w3 = w1; GFM case w3 = (w1/X13 + wv/X2)/(1/X13 + 1/X2). RoCoF_inst = max |df/dt| in the first 100 ms (exact, from the state derivatives). Secondary dip = recovery peak minus the next local minimum (prominence > 0.2 mHz), 0 if none. Extra wind energy = integral of (plant Pe minus pre-event Pe) over 1 to 11 s, plant level.\n")
a("## Parameters\n")
keys = ["SB_MVA", "f0_Hz", "PL0_pu", "DL", "dP_MW", "Hsg_s", "Dsg", "R_gov", "TG", "TCH", "FHP", "TRH", "X13", "X23",
        "Xv_windbase", "Xv_sys", "X2_C4", "Hv_s", "Rw", "tau_m_s", "tau_f_s", "Dd_chosen", "v_wind", "p_baseline",
        "N_turbines", "Sw_MW", "Ssg_pu_C0", "Ssg_pu_wind_cases", "P_avail_9_MW", "P_avail_pu", "P_del_pu", "reserve_pu",
        "reserve_plant_MW", "w_opt_pu", "w_del_pu", "beta_del_deg", "K_OPT_pu", "k_del_pu", "Ek_to_opt_MJ_per_turbine",
        "SCR_wind_bus_baseline", "solver"]
a("| Parameter | Value |\n|---|---|")
for k in keys:
    v = P[k]; a(f"| {k} | {v:.4g} |" if isinstance(v, float) else f"| {k} | {v} |")
mb = P["SG_VSM_mode_baseline"]
a(f"\nSG-VSM electromechanical mode at Dd = {P['Dd_chosen']}: damping ratio {mb['zeta']:.3f}, frequency {mb['f_Hz']:.2f} Hz (numerical Jacobian at the pre-event equilibrium). Dd ladder: "
  + ", ".join(f"Dd={q['Dd']}: zeta {q['zeta']:.3f}" for q in P["Dd_tuning"]) + ".\n")
a(f"MODEL CHANGE (stated): with the VSM damping referenced to the washout state wf (tau_f = 1 s) as first specified, the SG-VSM mode damping ratio peaks at only {P['washout_damping_max_zeta']:.3f} (scan: "
  + ", ".join(f"Dd={q['Dd']}: {q['zeta']:.3f}" for q in P["washout_damping_scan"])
  + "), because a large Dd stiffens the VSM against its own slow reference and the SG then swings almost undamped against it. The damping term was therefore referenced to the PLL-measured PCC (load-bus) frequency, Dd*(wv - w3), the VSM damping form of D'Arco and Suul 2014; it is zero in steady state and does not change the COI inertia. Dd = 100 then gives zeta >= 0.3.\n")
a("## Gates\n")
g = G
a(f"- GB1 PASS={g['GB1']['pass']}: pre-event max |df| = {max(g['GB1']['vals'].values()):.2e} Hz in all cases; max initial derivative residual {max(g['GB1']['init_resid'].values()):.2e}.")
for c, v in g["GB2"]["vals"].items():
    a(f"- GB2 {c}: Hsys = {v['Hsys_s']:.3f} s, analytic COI RoCoF {v['analytic_Hzps']:.4f} Hz/s, simulated (mean of first 20 ms) {v['sim_COI_Hzps']:.4f} Hz/s, error {100*v['rel_err']:.1f}%")
a(f"- GB2 PASS={g['GB2']['pass']} (limit 15%).")
a(f"- GB3 PASS={g['GB3']['pass']}: C1 df_ss analytic {g['GB3']['analytic_Hz']:.5f} Hz vs simulated {g['GB3']['sim_Hz']:.5f} Hz, error {100*g['GB3']['rel_err']:.2f}% (limit 5%).")
for c in ["C2", "C3", "C4"]:
    e = g["GB4"][c]
    a(f"- GB4 {c}: window {e['window_s'][0]:.2f} to {e['window_s'][1]:.2f} s, integral(Paero - Pe) {e['int_Pa_minus_Pe_MJ']:.4f} MJ vs dEk {e['dEk_MJ']:.4f} MJ per turbine, error {100*e['rel_err']:.4f}%")
a(f"- GB4 PASS={g['GB4']['pass']} (limit 1%).")
a(f"- GB5 PASS={g['GB5']['pass']}: C4 min w_r {g['GB5']['min_wr_C4']:.4f} pu >= limit {g['GB5']['limit']:.4f} pu.")
a(f"- GB6 PASS={g['GB6']['pass']}: RoCoF_500ms C4 {g['GB6']['RoCoF500_C4']:.4f} < C1 {g['GB6']['RoCoF500_C1']:.4f} Hz/s (also RoCoF_inst); nadir C4 {g['GB6']['nadir_C4']:.4f} > C1 {g['GB6']['nadir_C1']:.4f} and C2 {g['GB6']['nadir_C2']:.4f} Hz.\n")
a("## Penetration sweep (B4)\n")
a("| p | C1 nadir (Hz) | C2 nadir (Hz) | C4 nadir (Hz) | C1 RoCoF500 | C2 RoCoF500 | C4 RoCoF500 |\n|---|---|---|---|---|---|---|")
for i, p in enumerate(S["p"]):
    a(f"| {p:.1f} | {S['C1']['nadir_Hz'][i]:.4f} | {S['C2']['nadir_Hz'][i]:.4f} | {S['C4']['nadir_Hz'][i]:.4f} | {S['C1']['RoCoF_500ms'][i]:.4f} | {S['C2']['RoCoF_500ms'][i]:.4f} | {S['C4']['RoCoF_500ms'][i]:.4f} |")
a(f"\nC0 reference: nadir {S['C0']['nadir_Hz']:.4f} Hz, RoCoF500 {S['C0']['RoCoF_500ms']:.4f} Hz/s. Dd fixed at {P['Dd_chosen']} across the sweep.\n")
if W.get("zeta"):
    a("## Weak-connection sweep (B5, C4 only)\n")
    a("| X23 (pu) | SCR at wind bus | nadir (Hz) | RoCoF500 (Hz/s) | SG-VSM zeta | mode (Hz) |\n|---|---|---|---|---|---|")
    for i, x in enumerate(W["X23"]):
        a(f"| {x} | {W['SCR'][i]:.2f} | {W['nadir_Hz'][i]:.4f} | {W['RoCoF_500ms'][i]:.4f} | {W['zeta'][i]:.3f} | {W['mode_Hz'][i]:.2f} |")
    a("")
c0, c1, c2, c3, c4 = (M[k] for k in ["C0", "C1", "C2", "C3", "C4"])
a("## Figure captions\n")
a("- B1_frequency: Load-bus frequency after a 50 MW (0.05 pu) load step at t = 1 s, 40% wind at 9 m/s, cases C0 to C4; inset zooms 0.9 to 4 s; grey band is the IEGC 2023 normal band 49.90 to 50.05 Hz. C3 (blue) lies almost under C4 (green) after about 2 s.")
a("- B2_wind_response: Wind-plant electrical power, aerodynamic power (both MW, plant level) and rotor speed (pu) for C2, C3 and C4; dotted line marks the MPPT speed at 9 m/s.")
a("- B3_metrics: Nadir deviation (mHz, shown positive), RoCoF over the first 500 ms (Hz/s) and secondary-dip depth (mHz) per case.")
a("- B4_penetration: Frequency nadir and 500 ms RoCoF versus wind penetration p = 0.1 to 0.6 for C1, C2 and C4, with the all-synchronous C0 as a horizontal reference.")
if W.get("zeta"):
    a("- B5_weak_connection: C4 nadir, 500 ms RoCoF and SG-VSM mode damping ratio versus the short-circuit ratio at the wind bus (X23 = 0.1 to 0.8 pu); dotted line at zeta = 0.3.")
a("\n## Findings\n")
a(f"- Plain grid-following MPPT wind (C1) makes frequency worse than the all-synchronous system: nadir {c1['f_nadir_Hz']:.3f} Hz vs {c0['f_nadir_Hz']:.3f} Hz and 500 ms RoCoF {c1['RoCoF_500ms_Hzps']:.3f} vs {c0['RoCoF_500ms_Hzps']:.3f} Hz/s, because 36% less synchronous inertia is online and the wind gives none.")
a(f"- The proposed grid-forming VSM (C4) is the only case that cuts the instantaneous RoCoF: {c4['RoCoF_inst_Hzps']:.3f} Hz/s vs {c1['RoCoF_inst_Hzps']:.3f} Hz/s for every grid-following case (C1 to C3), because a GFL controller only reacts after its PLL/filter sees the change; the simulated COI RoCoF matches the analytic SG + VSM inertia value within {100*G['GB2']['vals']['C4']['rel_err']:.0f}%.")
a(f"- Over 500 ms, C4 holds RoCoF to {c4['RoCoF_500ms_Hzps']:.3f} Hz/s, {100*(1-c4['RoCoF_500ms_Hzps']/c1['RoCoF_500ms_Hzps']):.0f}% below C1 and {100*(1-c4['RoCoF_500ms_Hzps']/c0['RoCoF_500ms_Hzps']):.0f}% below the all-synchronous C0; the nadir rises to {c4['f_nadir_Hz']:.3f} Hz ({c4['nadir_dev_mHz']:.0f} mHz vs {c1['nadir_dev_mHz']:.0f} mHz for C1). C3 reaches the same nadir ({c3['f_nadir_Hz']:.3f} Hz) because both are bounded by the same 10% reserve; the GFM gain over a well-tuned GFL is in the first second (RoCoF_inst), not in the nadir.")
a(f"- Without reserve (C2) the support is borrowed from rotor kinetic energy: the rotor falls from {c2['wr0_pu']:.3f} to {c2['min_wr_pu']:.3f} pu, MPPT capture drops, the frequency keeps sagging to its nadir {c2['f_nadir_Hz']:.3f} Hz only at {c2['t_nadir_s']:.1f} s and settles worst of all ({c2['df_ss_Hz']*1e3:.0f} mHz at 40 s vs {c4['df_ss_Hz']*1e3:.0f} mHz for C4). With the overspeed reserve (C3, C4) the rotor only dips to {c4['min_wr_pu']:.3f} pu, above the MPPT speed {P['w_opt_pu']:.3f} pu, and the plant holds about {P['reserve_plant_MW']:.0f} MW extra in steady state.")
a(f"- The advantage of C4 grows with penetration: at p = 0.6 the C4 nadir is {S['C4']['nadir_Hz'][-1]:.3f} Hz vs {S['C1']['nadir_Hz'][-1]:.3f} Hz (C1) and {S['C2']['nadir_Hz'][-1]:.3f} Hz (C2), better than the all-synchronous {S['C0']['nadir_Hz']:.3f} Hz.")
if W.get("zeta"):
    a(f"- In weak connections C4 stays stable and is better damped: SG-VSM damping ratio rises from {W['zeta'][0]:.2f} (SCR {W['SCR'][0]:.1f}) to {W['zeta'][-1]:.2f} (SCR {W['SCR'][-1]:.1f}), while RoCoF500 grows only from {W['RoCoF_500ms'][0]:.3f} to {W['RoCoF_500ms'][-1]:.3f} Hz/s. zeta is {W['zeta'][0]:.2f} (below 0.3) at the strongest link X23 = 0.1 with Dd = 100.")
a("\n## Caveats\n")
a(f"- DC power flow, lossless, |V| = 1 pu; no voltage or current-limit dynamics of the GFM converter (peak plant power {c4['max_Pe_pu_plant']:.3f} pu, far below the 1.1 pu limit).")
a("- VSM damping is referenced to the PCC frequency instead of the washout state (see MODEL CHANGE). The washout state is still integrated but unused.")
a(f"- Secondary dips are small in all cases (largest {max(M[k]['secondary_dip_mHz'] for k in M):.1f} mHz, C3/C4 near 23 s after the event, from the slow rotor re-acceleration toward the deload speed interacting with the reheat governor).")
a("- Single aggregated plant at one wind speed (9 m/s), no wind variability, one equivalent SG fleet.")
open(os.path.join(BASE, "results", "B_summary.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("ok")
