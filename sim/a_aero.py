import sys, os, json
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "sim"))
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import turbine as T
from scipy.integrate import trapezoid
plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3})
RPM = 60/(2*np.pi)
FIG = os.path.join(BASE, "figures"); RES = os.path.join(BASE, "results")
def save(fig, stem):
    for e in ("png", "pdf"): fig.savefig(f"{FIG}/{stem}.{e}", dpi=200, bbox_inches="tight")
    plt.close(fig)
BLK, RED, ORG, BLU, GRN = "black", "#d62728", "#ff7f0e", "#1f77b4", "#2ca02c"
WR = T.W_RATED

# A1
lam = np.linspace(0.01, 16, 800)
fig, ax = plt.subplots(figsize=(6.5, 3.8))
cols = [BLK, RED, ORG, BLU, GRN, "#9467bd"]
for b, c in zip([0, 2, 5, 10, 15, 20], cols):
    ax.plot(lam, T.cp(lam, b), color=c, lw=2 if b == 0 else 1.5, ls="--" if b == 0 else "-", label=f"beta={b} deg")
ax.axhline(T.BETZ, color="gray", ls="--", lw=1); ax.text(0.3, T.BETZ+0.008, f"Betz limit 16/27 = {T.BETZ:.3f}", color="gray")
ax.plot(T.LAMBDA_OPT, T.CP_MAX, "o", color=GRN, ms=8, zorder=5)
ax.annotate(f"Cp_max={T.CP_MAX:.3f} at lambda_opt={T.LAMBDA_OPT:.2f}", (T.LAMBDA_OPT, T.CP_MAX), (8.8, 0.52), arrowprops=dict(arrowstyle="->"))
ax.set_xlabel("Tip-speed ratio lambda"); ax.set_ylabel("Cp"); ax.set_ylim(0, 0.65); ax.legend(ncol=3, loc="lower center")
save(fig, "A1_cp_curves")

# table
vs = list(range(6, 15))
tab = []
for v in vs:
    d = T.deload_point(v)
    chk = float(T.p_aero(d["w_del"], v, d["beta"]))
    tab.append(dict(v=v, P_avail_kW=d["P_avail"]/1e3, P_del_kW=d["P_del"]/1e3, reserve_kW=d["reserve"]/1e3,
        w_opt_rpm=d["w_opt"]*RPM, w_del_rpm=d["w_del"]*RPM, beta_deg=d["beta"], mode=d["mode"],
        Ek_to_opt_MJ=d["Ek_to_opt"]/1e6, Ek_to_min_MJ=d["Ek_to_min"]/1e6,
        H_eq_opt_s=d["Ek_to_opt"]/T.P_RATED, H_eq_min_s=d["Ek_to_min"]/T.P_RATED, check_rel_err=abs(chk-d["P_del"])/max(d["P_del"], 1)))

# A2
fig, ax = plt.subplots(figsize=(6.5, 4.2))
wg = np.linspace(0.4*WR, 1.25*WR, 300)
for v in range(6, 14):
    ax.plot(wg*RPM, np.minimum(T.p_aero(wg, v, 0.0), 2.6e6)/1e6, color="lightgray", lw=1)
    ax.text(wg[-1]*RPM, min(float(T.p_aero(wg[-1], v, 0.0)), 2.6e6)/1e6, f"{v}", fontsize=7, color="gray")
wl = np.linspace(T.W_MIN_PU*WR, WR, 100)
ax.plot(wl*RPM, np.minimum(T.K_OPT*wl**3, T.P_RATED)/1e6, color=BLK, ls="--", lw=2, label="MPPT locus")
vf = np.linspace(5, 14, 60); dl = [T.deload_point(v) for v in vf]
dlo = [d for d in dl if d["mode"] != "pitch"]; dpi_ = [d for d in dl if d["mode"] == "pitch"]
ax.plot([d["w_del"]*RPM for d in dlo], [d["P_del"]/1e6 for d in dlo], color=GRN, lw=2, label="10% deloaded locus (overspeed, v < 12 m/s)")
ax.plot([dpi_[0]["w_del"]*RPM], [dpi_[0]["P_del"]/1e6], marker="D", ms=7, mfc="white", mec=GRN, mew=2, ls="none", label="v >= 12 m/s: pitch at rated speed")
ax.axhline(2.0, color=RED, lw=1, label="rated 2 MW")
for f in (T.W_MIN_PU, T.W_MAX_PU): ax.axvline(f*WR*RPM, color="k", ls=":", lw=1)
for v in (8, 10, 12):
    d = T.deload_point(v)
    ax.plot(d["w_opt"]*RPM, d["P_avail"]/1e6, "o", color=BLK, ms=7, zorder=5)
    ax.plot(d["w_del"]*RPM, d["P_del"]/1e6, "s", color=GRN, ms=7, zorder=5)
    ax.annotate(f"{v} m/s", (d["w_opt"]*RPM, d["P_avail"]/1e6), (-28, 6), textcoords="offset points", fontsize=7)
d = T.deload_point(10)
ax.annotate("overspeed deloading", (d["w_del"]*RPM, d["P_del"]/1e6), (d["w_opt"]*RPM-1.5, d["P_avail"]/1e6+0.5), arrowprops=dict(arrowstyle="->", color=ORG, lw=1.5), color=ORG)
ax.set_xlabel("Rotor speed (rpm)"); ax.set_ylabel("Turbine power (MW)"); ax.set_ylim(0, 2.6); ax.legend(loc="upper left")
save(fig, "A2_power_speed")

# A3
vv = np.linspace(0, 26, 521)
pm = np.array([T.p_avail(v) for v in vv])/1e6
pdl = np.array([T.deload_point(v)["P_del"] if T.V_CUTIN <= v <= T.V_CUTOUT else 0.0 for v in vv])/1e6
fig, ax = plt.subplots(figsize=(6.5, 3.8))
ax.plot(vv, pm, color=BLK, ls="--", lw=2, label="MPPT"); ax.plot(vv, pdl, color=GRN, lw=2, label="10% deloaded")
ax.fill_between(vv, pdl, pm, color=GRN, alpha=0.25, label="reserve band")
for x, n in ((3.5, "cut-in 3.5"), (T.V_RATED, f"rated {T.V_RATED:.1f}"), (25, "cut-out 25")):
    ax.axvline(x, color=RED, ls=":", lw=1); ax.text(x+0.2, 0.1, n, rotation=90, fontsize=8, color=RED)
ax.set_xlabel("Wind speed (m/s)"); ax.set_ylabel("Power (MW)"); ax.legend(loc="center left")
save(fig, "A3_power_curve")

# A4
mk = {"overspeed": "o", "overspeed+pitch": "s", "pitch": "^"}
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.5, 5.5), sharex=True)
a1.plot(vs, [r["reserve_kW"] for r in tab], color=GRN, lw=2)
for m, s in mk.items():
    pts = [(r["v"], r["reserve_kW"]) for r in tab if r["mode"] == m]
    if pts: a1.plot(*zip(*pts), s, color=GRN, mec="k", ms=8, ls="", label=m)
a1.set_ylabel("Reserve power (kW)"); a1.legend()
a2.plot(vs, [r["Ek_to_opt_MJ"] for r in tab], color=ORG, lw=2, marker="o", label="w_del to w_opt")
a2.plot(vs, [r["Ek_to_min_MJ"] for r in tab], color=BLU, lw=2, marker="s", label="w_del to W_MIN (0.5 pu)")
a2.set_xlabel("Wind speed (m/s)"); a2.set_ylabel("Releasable kinetic energy (MJ)"); a2.legend(loc="upper left")
a3 = a2.twinx(); a3.grid(False); lo, hi = a2.get_ylim(); a3.set_ylim(lo*1e6/T.P_RATED, hi*1e6/T.P_RATED); a3.set_ylabel("H_eq = E/P_RATED (s)")
save(fig, "A4_reserve")

# A5
k, c = 2.0, 7.5
vc = np.linspace(3.5, 25, 600); fc = (k/c)*(vc/c)**(k-1)*np.exp(-(vc/c)**k)
pm_c = np.array([T.p_avail(v) for v in vc]); pd_c = np.array([T.deload_point(v)["P_del"] for v in vc])
H = 8760
aep_m = trapezoid(pm_c*fc, vc)*H/1e6; aep_d = trapezoid(pd_c*fc, vc)*H/1e6
loss = (aep_m-aep_d)/aep_m
tariff = 3.5
aep = dict(site="illustrative Indian onshore site", weibull_k=k, weibull_c=c, hours=H,
    AEP_MPPT_MWh=aep_m, AEP_deloaded_MWh=aep_d, loss_MWh=aep_m-aep_d, loss_frac=loss,
    CF_MPPT=aep_m/(2*H), CF_deloaded=aep_d/(2*H), tariff_INR_per_kWh=tariff,
    revenue_MPPT_INR_lakh=aep_m*1e3*tariff/1e5, revenue_deloaded_INR_lakh=aep_d*1e3*tariff/1e5,
    cost_continuous_reserve_INR_lakh=(aep_m-aep_d)*1e3*tariff/1e5)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.5, 3.4))
a1.plot(vc, fc, color=BLU, lw=2); a1.set_xlabel("Wind speed (m/s)"); a1.set_ylabel("Weibull pdf (k=2, c=7.5)")
a2.bar(["MPPT", "10% deloaded"], [aep_m, aep_d], color=[BLK, GRN]); a2.set_ylabel("AEP (MWh/yr)")
for i, x in enumerate((aep_m, aep_d)): a2.text(i, x, f"{x:,.0f}", ha="center", va="bottom")
a2.set_ylim(0, aep_m*1.15)
save(fig, "A5_economics")

# worked example 9 m/s
v = 9.0; d9 = T.deload_point(v); w9 = T.w_opt(v)
worked = dict(v=v, w_rad_s=w9, w_rpm=w9*RPM, TSR=w9*T.R/v, Cp=float(T.cp(w9*T.R/v, 0.0)),
    P_W=0.5*T.RHO*T.A*v**3*float(T.cp(w9*T.R/v, 0.0)), rho=T.RHO, A=T.A, R=T.R,
    w_del_rpm=d9["w_del"]*RPM, TSR_del=d9["w_del"]*T.R/v, Cp_del=float(T.cp(d9["w_del"]*T.R/v, 0.0)),
    P_del_W=d9["P_del"], formula="P = 0.5 rho A v^3 Cp(lambda,beta), lambda = w R / v")

G = {}
def gate(n, cond, msg):
    G[n] = bool(cond); print(n, "PASS" if cond else "FAIL", msg)
gate("GA1", T.CP_MAX < T.BETZ, f"Cp_max {T.CP_MAX:.4f} < {T.BETZ:.4f}")
gate("GA2", 7.5 <= T.LAMBDA_OPT <= 8.7 and 0.47 <= T.CP_MAX <= 0.49, f"lam {T.LAMBDA_OPT:.3f} cp {T.CP_MAX:.4f}")
gate("GA3", abs(T.p_avail(12)-2e6)/2e6 < 0.01, f"p_avail(12)={T.p_avail(12):.0f}")
mx = max(r["check_rel_err"] for r in tab)
gate("GA4", mx < 1e-3, f"max rel err {mx:.2e}")
gate("GA5", all(r["w_del_rpm"] > r["w_opt_rpm"] for r in tab if r["mode"].startswith("overspeed")), "w_del>w_opt")
gate("GA6", abs(loss-0.10) < 0.005, f"AEP loss {loss*100:.3f}%")

out = dict(lambda_opt=T.LAMBDA_OPT, cp_max=T.CP_MAX, betz=T.BETZ, v_rated=T.V_RATED, w_rated_rpm=WR*RPM,
    w_rated_rad_s=WR, J=T.J, k_opt=T.K_OPT, H_WT=T.H_WT, per_v=tab, AEP=aep, worked_example_9ms=worked, gates=G)
json.dump(out, open(f"{RES}/A.json", "w"), indent=2)

r6 = [r for r in tab if r["v"] == 6][0]; r10 = [r for r in tab if r["v"] == 10][0]; r12 = [r for r in tab if r["v"] == 12][0]
md = f"""# Task A summary
- lambda_opt = {T.LAMBDA_OPT:.2f}, Cp_max = {T.CP_MAX:.3f} (Betz 16/27 = {T.BETZ:.3f}; {T.CP_MAX/T.BETZ*100:.1f}% of Betz).
- Rated wind speed {T.V_RATED:.2f} m/s; rated rotor speed {WR*RPM:.2f} rpm ({WR:.3f} rad/s); K_opt = {T.K_OPT:.0f} W/(rad/s)^3; J = {T.J:.3e} kg m^2.
- Speed limits {T.W_MIN_PU*WR*RPM:.2f} to {T.W_MAX_PU*WR*RPM:.2f} rpm (0.5 to 1.2 pu).
- At 6 m/s: reserve {r6['reserve_kW']:.0f} kW, {r6['mode']}, w_del {r6['w_del_rpm']:.1f} vs w_opt {r6['w_opt_rpm']:.1f} rpm, E to W_MIN {r6['Ek_to_min_MJ']:.2f} MJ (H_eq {r6['H_eq_min_s']:.2f} s).
- At 10 m/s: reserve {r10['reserve_kW']:.0f} kW, {r10['mode']}, beta {r10['beta_deg']:.2f} deg, E to W_MIN {r10['Ek_to_min_MJ']:.2f} MJ (H_eq {r10['H_eq_min_s']:.2f} s).
- At 12 m/s: reserve {r12['reserve_kW']:.0f} kW, {r12['mode']}, beta {r12['beta_deg']:.2f} deg, E to W_MIN {r12['Ek_to_min_MJ']:.2f} MJ (H_eq {r12['H_eq_min_s']:.2f} s).
- Modes by v (6..14): {', '.join(str(r['v'])+':'+r['mode'] for r in tab)}.
- Worked example 9 m/s: w = {worked['w_rpm']:.2f} rpm, TSR = {worked['TSR']:.2f}, Cp = {worked['Cp']:.3f}, P = {worked['P_W']/1e6:.3f} MW.
- AEP (Weibull k=2, c=7.5, illustrative Indian onshore site): MPPT {aep_m:,.0f} MWh/yr (CF {aep['CF_MPPT']*100:.1f}%), deloaded {aep_d:,.0f} MWh/yr (CF {aep['CF_deloaded']*100:.1f}%); loss {loss*100:.2f}%.
- Cost of a continuous 10% reserve: {aep['loss_MWh']:,.0f} MWh/yr = INR {aep['cost_continuous_reserve_INR_lakh']:.1f} lakh/yr at 3.5 INR/kWh (revenue {aep['revenue_MPPT_INR_lakh']:.1f} to {aep['revenue_deloaded_INR_lakh']:.1f} lakh).
- The reserve need only be held in low-inertia hours, so the real cost is a fraction of this upper bound.
- Gates: {', '.join(g+' '+('PASS' if ok else 'FAIL') for g, ok in G.items())}.

Captions
- A1: Cp(lambda) for beta 0 to 20 deg; peak at lambda_opt, well under the Betz limit.
- A2: Turbine power vs rotor speed per wind speed with MPPT and 10% deloaded loci; overspeed moves the point right of the peak.
- A3: Steady power curve, MPPT vs 10% deloaded, shaded reserve band, cut-in/rated/cut-out.
- A4: Reserve power by mode (top) and releasable kinetic energy with equivalent H_eq (bottom).
- A5: Weibull wind distribution and annual energy, MPPT vs deloaded.
"""
open(f"{RES}/A_summary.md", "w").write(md)
assert all(G.values()), G
