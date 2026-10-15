"""Task B: frequency-support dynamics, SG fleet + 2 MW PMSG wind plant (GFL cases C1-C3, GFM-VSM case C4).
Per unit on SB = 1000 MVA, f0 = 50 Hz. Run: python sim/b_freq.py"""
import os, sys, json, time
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve
from scipy.signal import find_peaks
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import turbine as T
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

BASE = os.path.dirname(HERE)
FIG, RES, STAT = (os.path.join(BASE, d) for d in ("figures", "results", "status"))
plt.rcParams.update({"font.size": 9})

SB, F0 = 1000e6, 50.0
WB = 2 * np.pi * F0
PL0, DL, DP, T_EV, T_END = 1.0, 1.0, 0.05, 1.0, 40.0
HSG, DSG, RG, TG, TCH, FHP, TRH = 5.0, 1.0, 0.05, 0.2, 0.3, 0.3, 7.0
X13, X23_0, XV_W = 0.25, 0.20, 0.15
HV, RW, TAU_M, TAU_F = 5.0, 0.05, 0.05, 1.0
V = 9.0
CASES = ["C0", "C1", "C2", "C3", "C4"]
LABEL = {"C0": "C0 all-synchronous", "C1": "C1 GFL-MPPT", "C2": "C2 GFL+SI+droop, no reserve",
         "C3": "C3 GFL+SI+droop, 10% reserve", "C4": "C4 GFM-VSM, 10% reserve (proposed)"}
STYLE = {"C0": dict(color="k", ls="--", lw=1.2), "C1": dict(color="#d62728", lw=1.2),
         "C2": dict(color="#ff7f0e", lw=1.2), "C3": dict(color="#1f77b4", lw=1.2),
         "C4": dict(color="#2ca02c", lw=2.0)}
BARC = {"C0": "0.3", "C1": "#d62728", "C2": "#ff7f0e", "C3": "#1f77b4", "C4": "#2ca02c"}

DEL = T.deload_point(V, 0.10)
PAV_PU = T.p_avail(V) / T.P_RATED
PDEL_PU = DEL["P_del"] / T.P_RATED
RES_PU = DEL["reserve"] / T.P_RATED
WDEL = DEL["w_del"] / T.W_RATED
WOPT = T.w_opt(V) / T.W_RATED
BETA = DEL["beta"]
KOPT_PU = T.K_OPT * T.W_RATED**3 / T.P_RATED
KDEL_PU = PDEL_PU / WDEL**3

def paero_pu(wr, beta=BETA):
    return float(T.p_aero(wr * T.W_RATED, V, beta)) / T.P_RATED

# state: 0 d1, 1 w1, 2 Pv, 3 Pch, 4 Prh, 5 wr, 6 wm, 7 dv, 8 wv, 9 wf, 10 Ea, 11 Ee
NX = 12

def make(case, p=0.40, X23=X23_0, Dd=40.0, damp_ref="pcc"):
    P = {"case": case, "p": p, "X23": X23, "Dd": Dd, "damp_ref": damp_ref}
    if case == "C0":
        P["Ssg"] = PL0 / 0.85; P["N"] = 0.0; P["kw"] = 0.0
    else:
        P["Ssg"] = (1 - 0.9 * p) * PL0 / 0.85
        P["N"] = p * PL0 * SB / T.p_avail(V)
        P["kw"] = P["N"] * T.P_RATED / SB
    P["Sw_MW"] = P["kw"] * SB / 1e6
    P["X2"] = X23 + (XV_W / P["kw"] if P["kw"] > 0 else 0.0)
    P["gfm"] = case == "C4"
    P["reserve"] = case in ("C3", "C4")
    P["beta"] = BETA if P["reserve"] else 0.0
    return P

KG = 5.0  # stall-guard slope, pu power per pu speed
def guard(wr):
    """Stall guard: if the rotor passes the Cp peak (w_opt), back the set-point off so it never runs onto the unstable low-speed side."""
    return KG * max(0.0, WOPT - wr)

def fade(wr):
    x = np.clip((wr - T.W_MIN_PU) / 0.05, 0.0, 1.0)
    return x * x * (3 - 2 * x)

def algebra(t, x, P, step=None):
    """Return dict of algebraic quantities."""
    d1, w1, Pv, Pch, Prh, wr, wm, dv, wv, wf = x[:10]
    if step is None:
        step = 1.0 if t >= T_EV else 0.0
    kw, Ssg = P["kw"], P["Ssg"]
    case = P["case"]
    if P["gfm"]:
        wcoi = (HSG * Ssg * w1 + HV * kw * wv) / (HSG * Ssg + HV * kw)
    else:
        wcoi = w1
    PL = (PL0 + DP * step) * (1 + DL * (wcoi - 1))
    out = {"PL": PL, "wcoi": wcoi}
    Pa = paero_pu(wr, P["beta"]) if kw > 0 else 0.0
    out["Pa"] = Pa
    if P["gfm"]:
        X2 = P["X2"]
        th3 = (d1 / X13 + dv / X2 - PL) / (1 / X13 + 1 / X2)
        Pe1 = (d1 - th3) / X13
        Pe2 = (dv - th3) / X2
        out.update(Pe1=Pe1, Pew=Pe2 / kw, w3=(w1 / X13 + wv / X2) / (1 / X13 + 1 / X2))
    else:
        if case == "C0":
            Pw = 0.0
        else:
            dwm = (w1 - wm) / TAU_M
            if case == "C1":
                Pw = KOPT_PU * wr**3
            else:
                si = np.clip(-2 * HV * dwm, -0.1, 0.1)
                if case == "C2":
                    dr = np.clip(-(wm - 1) / RW, -0.1, 0.1)
                    Pw = KOPT_PU * wr**3 + fade(wr) * (si + dr)
                else:
                    dr = np.clip(-(wm - 1) / RW, -RES_PU, RES_PU)
                    Pw = PDEL_PU - guard(wr) + fade(wr) * (si + dr)   # constant deloaded set-point: self-stabilising on the overspeed side, releases the full reserve
            Pw = min(Pw, 1.1)
        out.update(Pe1=PL - Pw * kw, Pew=Pw, w3=w1)
    return out

def rhs(t, x, P, step=None):
    d1, w1, Pv, Pch, Prh, wr, wm, dv, wv, wf = x[:10]
    A = algebra(t, x, P, step)
    Ssg, kw = P["Ssg"], P["kw"]
    dx = np.zeros(NX)
    Pm = np.clip(Ssg * (FHP * Pch + (1 - FHP) * Prh), 0.0, Ssg)
    dx[0] = WB * (w1 - 1)
    dx[1] = (Pm - A["Pe1"] - DSG * Ssg * (w1 - 1)) / (2 * HSG * Ssg)
    dx[2] = (P["Pref"] - (w1 - 1) / RG - Pv) / TG
    dx[3] = (Pv - Pch) / TCH
    dx[4] = (Pch - Prh) / TRH
    if kw > 0:
        dx[5] = (A["Pa"] - A["Pew"]) / (2 * T.H_WT * wr)
        dx[10] = A["Pa"]; dx[11] = A["Pew"]
    if P["case"] in ("C2", "C3"):
        dx[6] = (w1 - wm) / TAU_M
    if P["gfm"]:
        Pset = PDEL_PU - guard(wr)   # constant deloaded set-point: self-stabilising on the overspeed side, releases the full reserve
        dPdr = np.clip(-(wv - 1) / RW, -RES_PU, RES_PU)
        dx[7] = WB * (wv - 1)
        wref = A["w3"] if P.get("damp_ref", "pcc") == "pcc" else wf
        dx[8] = (Pset + dPdr - A["Pew"] - P["Dd"] * (wv - wref)) / (2 * HV)
        dx[9] = (wv - wf) / TAU_F
    return dx

def init(P):
    """Exact pre-event steady state: analytic guess refined with fsolve, d1 pinned to 0."""
    kw, Ssg = P["kw"], P["Ssg"]
    x0 = np.zeros(NX); x0[1] = 1; x0[6] = 1; x0[8] = 1; x0[9] = 1
    if P["case"] == "C0":
        wr, Pw = 1.0, 0.0
    elif P["reserve"]:
        wr, Pw = WDEL, PDEL_PU
    else:
        wr, Pw = WOPT, KOPT_PU * WOPT**3
    x0[5] = wr
    Pe1 = PL0 - Pw * kw
    if P["gfm"]:
        th3 = -Pe1 * X13
        x0[7] = th3 + Pw * kw * P["X2"]
    pm = Pe1 / Ssg
    x0[2:5] = pm; P["Pref"] = pm
    idx = [1, 2, 3, 4] + ([5] if kw > 0 else []) + ([7, 8, 9] if P["gfm"] else [])
    def F(z):
        x = x0.copy(); x[idx] = z
        P["Pref"] = x[2]
        r = rhs(0.0, x, P, step=0.0)
        r[0] = x[1] - 1  # replace angle eq: w1 = 1 (equivalent)
        return r[[0, 2, 3, 4] + ([5] if kw > 0 else []) + ([7, 8, 9] if P["gfm"] else [])]
    z = fsolve(F, x0[idx], xtol=1e-14)
    x0[idx] = z; P["Pref"] = x0[2]
    d = rhs(0.0, x0, P, step=0.0)
    P["init_resid"] = float(np.max(np.abs(d[:10])))
    return x0

def simulate(P, dt=0.001):
    x0 = init(P)
    kw = dict(method="LSODA", max_step=0.005, rtol=1e-6, atol=1e-9)
    t1 = np.clip(np.arange(0, T_EV + 1e-12, dt), 0, T_EV)
    s1 = solve_ivp(lambda t, x: rhs(t, x, P, 0.0), (0, T_EV), x0, t_eval=t1, **kw)
    t2 = np.clip(np.arange(T_EV, T_END + 1e-12, dt), T_EV, T_END)
    s2 = solve_ivp(lambda t, x: rhs(t, x, P, 1.0), (T_EV, T_END), s1.y[:, -1], t_eval=t2, **kw)
    assert s1.success and s2.success
    t = np.concatenate([s1.t[:-1], s2.t]); X = np.concatenate([s1.y[:, :-1], s2.y], axis=1)
    n = len(t)
    f = np.empty(n); fcoi = np.empty(n); dfdt = np.empty(n); dcoi = np.empty(n); Pew = np.empty(n); Pa = np.empty(n)
    for i in range(n):
        st = 1.0 if t[i] >= T_EV else 0.0
        A = algebra(t[i], X[:, i], P, st); d = rhs(t[i], X[:, i], P, st)
        f[i] = F0 * A["w3"]; fcoi[i] = F0 * A["wcoi"]; Pew[i] = A["Pew"]; Pa[i] = A["Pa"]
        if P["gfm"]:
            g = (1 / X13) / (1 / X13 + 1 / P["X2"])
            dfdt[i] = F0 * (g * d[1] + (1 - g) * d[8])
            Hs = HSG * P["Ssg"] + HV * P["kw"]
            dcoi[i] = F0 * (HSG * P["Ssg"] * d[1] + HV * P["kw"] * d[8]) / Hs
        else:
            dfdt[i] = F0 * d[1]; dcoi[i] = dfdt[i]
    return {"t": t, "X": X, "f": f, "fcoi": fcoi, "dfdt": dfdt, "dcoi": dcoi, "Pew": Pew, "Pa": Pa, "x0": x0, "P": P}

def metrics(S):
    t, f, P = S["t"], S["f"], S["P"]
    post = t >= T_EV
    i_ev = np.argmax(post)
    ip = np.argmin(f[post]) + i_ev
    m = {"f_nadir_Hz": float(f[ip]), "nadir_dev_mHz": float((f[ip] - F0) * 1e3), "t_nadir_s": float(t[ip] - T_EV)}
    w100 = (t >= T_EV) & (t <= T_EV + 0.1)
    m["RoCoF_inst_Hzps"] = float(np.max(np.abs(S["dfdt"][w100])))
    f05 = np.interp(T_EV + 0.5, t, f)
    m["RoCoF_500ms_Hzps"] = float(abs(f05 - f[i_ev]) / 0.5)
    w20 = (t >= T_EV) & (t <= T_EV + 0.02)
    m["RoCoF_COI_20ms_Hzps"] = float(abs(np.mean(S["dcoi"][w20])))
    m["df_ss_Hz"] = float(f[-1] - F0)
    m["pre_event_df_Hz"] = float(np.max(np.abs(f[~post] - F0)))
    # secondary dip: local minima after the event with prominence > 0.2 mHz
    fp = f[post]
    mins, _ = find_peaks(-fp, prominence=2e-4)
    sec = 0.0; t_sec = None
    if len(mins) >= 2:
        a, b = mins[0], mins[1]
        rec = np.max(fp[a:b + 1])
        sec = float((rec - fp[b]) * 1e3); t_sec = float(t[post][b] - T_EV)
    elif len(mins) == 1:
        a = mins[0]
        pk, _ = find_peaks(fp[a:], prominence=2e-4)
        if len(pk):
            b = a + pk[0] + np.argmin(fp[a + pk[0]:])
            if fp[b] < fp[a + pk[0]] - 2e-4:
                sec = float((fp[a + pk[0]] - fp[b]) * 1e3); t_sec = float(t[post][b] - T_EV)
    m["secondary_dip_mHz"] = sec; m["t_secondary_min_s"] = t_sec
    if P["kw"] > 0:
        wr = S["X"][5]
        m["min_wr_pu"] = float(np.min(wr)); m["wr0_pu"] = float(wr[0])
        w10 = (t >= T_EV) & (t <= T_EV + 10)
        Pmw = S["Pew"] * P["Sw_MW"]
        m["extra_wind_energy_10s_MJ"] = float(np.trapezoid(Pmw[w10] - Pmw[i_ev - 1], t[w10]))
        m["peak_extra_wind_MW"] = float(np.max(Pmw[post] - Pmw[i_ev - 1]))
        m["max_Pe_pu_plant"] = float(np.max(S["Pew"]))
    else:
        m["min_wr_pu"] = None; m["extra_wind_energy_10s_MJ"] = 0.0
    return m

def energy_check(S):
    """Per turbine: integral(Paero-Pe) vs change in kinetic energy, window event -> time of min w_r."""
    t, X = S["t"], S["X"]
    i0 = np.argmax(t >= T_EV)
    i1 = i0 + int(np.argmin(X[5, i0:]))
    if i1 - i0 < 10:
        i1 = np.argmax(t >= T_EV + 10)
    Eint = (X[10, i1] - X[11, i1] - X[10, i0] + X[11, i0]) * T.P_RATED
    dEk = float(T.kinetic_energy(X[5, i1] * T.W_RATED) - T.kinetic_energy(X[5, i0] * T.W_RATED))
    return {"window_s": [float(t[i0]), float(t[i1])], "int_Pa_minus_Pe_MJ": Eint / 1e6, "dEk_MJ": dEk / 1e6,
            "rel_err": float(abs(Eint - dEk) / max(abs(dEk), 1e-9))}

def damping(P):
    """SG-VSM electromechanical mode from a numerical Jacobian at the pre-event equilibrium."""
    x0 = init(P)
    idx = [0, 1, 2, 3, 4, 5, 7, 8, 9]
    J = np.zeros((len(idx), len(idx)))
    for j, k in enumerate(idx):
        h = 1e-6
        xp = x0.copy(); xm = x0.copy(); xp[k] += h; xm[k] -= h
        J[:, j] = (rhs(0, xp, P, 0.0)[idx] - rhs(0, xm, P, 0.0)[idx]) / (2 * h)
    ev, vec = np.linalg.eig(J)
    osc = [(i, e) for i, e in enumerate(ev) if e.imag > 1e-3]
    if not osc:
        return {"zeta": 1.0, "f_Hz": 0.0, "eig": None}
    # electromechanical SG-VSM swing mode = the highest-frequency oscillatory mode (1-2 Hz here)
    i, e = max(osc, key=lambda q: q[1].imag)
    return {"zeta": float(-e.real / abs(e)), "f_Hz": float(e.imag / (2 * np.pi)), "eig": [float(e.real), float(e.imag)]}

def savefig(fig, stem):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"{stem}.{ext}"), dpi=200, bbox_inches="tight")
    plt.close(fig)

def main():
    t0 = time.time()
    # ---- tune Dd: smallest from the ladder with SG-VSM damping ratio >= 0.3
    ladder = [40, 60, 80, 100, 120, 150, 200, 250, 300, 400]
    washout_scan = [{"Dd": Dd, **damping(make("C4", Dd=Dd, damp_ref="washout"))} for Dd in [10, 40, 80, 100, 150, 300, 1000]]
    print("washout-referenced damping scan:", [(q["Dd"], round(q["zeta"], 3)) for q in washout_scan])
    tune = []
    for Dd in ladder:
        dm = damping(make("C4", Dd=Dd)); tune.append({"Dd": Dd, **dm})
        if dm["zeta"] >= 0.3:
            break
    DD = tune[-1]["Dd"]
    print("Dd tuning:", [(q["Dd"], round(q["zeta"], 3), round(q["f_Hz"], 3)) for q in tune])
    sims, M = {}, {}
    for c in CASES:
        S = simulate(make(c, Dd=DD)); sims[c] = S; M[c] = metrics(S)
        print(c, {k: (round(v, 5) if isinstance(v, float) else v) for k, v in M[c].items()}, f"{time.time()-t0:.0f}s")
    # ---- gates
    G = {}
    G["GB1"] = {"vals": {c: M[c]["pre_event_df_Hz"] for c in CASES},
                "init_resid": {c: sims[c]["P"]["init_resid"] for c in CASES}}
    G["GB1"]["pass"] = bool(all(v < 1e-4 for v in G["GB1"]["vals"].values()))
    gb2 = {}
    for c in ("C0", "C1", "C4"):
        P = sims[c]["P"]
        Hsys = HSG * P["Ssg"] + (HV * P["kw"] if P["gfm"] else 0.0)
        an = DP * F0 / (2 * Hsys)
        sim = M[c]["RoCoF_COI_20ms_Hzps"]
        gb2[c] = {"Hsys_s": Hsys, "analytic_Hzps": an, "sim_COI_Hzps": sim, "rel_err": abs(sim - an) / an}
    G["GB2"] = {"vals": gb2, "pass": bool(all(v["rel_err"] < 0.15 for v in gb2.values()))}
    P1 = sims["C1"]["P"]
    an3 = -DP * F0 / (P1["Ssg"] / RG + DL * (PL0 + DP) + DSG * P1["Ssg"])
    G["GB3"] = {"analytic_Hz": an3, "sim_Hz": M["C1"]["df_ss_Hz"], "rel_err": abs(M["C1"]["df_ss_Hz"] - an3) / abs(an3)}
    G["GB3"]["pass"] = bool(G["GB3"]["rel_err"] < 0.05)
    G["GB4"] = {c: energy_check(sims[c]) for c in ("C2", "C3", "C4")}
    G["GB4"]["pass"] = bool(all(G["GB4"][c]["rel_err"] < 0.01 for c in ("C2", "C3", "C4")))
    lim5 = WOPT - 0.01
    G["GB5"] = {"min_wr_C4": M["C4"]["min_wr_pu"], "limit": lim5, "pass": bool(M["C4"]["min_wr_pu"] >= lim5)}
    G["GB6"] = {"RoCoF500_C4": M["C4"]["RoCoF_500ms_Hzps"], "RoCoF500_C1": M["C1"]["RoCoF_500ms_Hzps"],
                "nadir_C4": M["C4"]["f_nadir_Hz"], "nadir_C1": M["C1"]["f_nadir_Hz"], "nadir_C2": M["C2"]["f_nadir_Hz"]}
    G["GB6"]["pass"] = bool(M["C4"]["RoCoF_500ms_Hzps"] < M["C1"]["RoCoF_500ms_Hzps"] and
                            M["C4"]["RoCoF_inst_Hzps"] < M["C1"]["RoCoF_inst_Hzps"] and
                            M["C4"]["f_nadir_Hz"] > M["C1"]["f_nadir_Hz"] and M["C4"]["f_nadir_Hz"] > M["C2"]["f_nadir_Hz"])
    for g in ("GB1", "GB2", "GB3", "GB4", "GB5", "GB6"):
        print(g, "PASS" if G[g]["pass"] else "FAIL")
    # ---- figures B1-B3
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    ax.axhspan(49.90, 50.05, color="0.9", zorder=0, label="IEGC 2023 band 49.90-50.05 Hz")
    ST1 = {c: dict(STYLE[c]) for c in CASES}; ST1["C3"].update(ls=(0, (4, 2)), lw=1.6, zorder=5)   # C3 dashed on top so it is visible over C4
    for c in CASES:
        ax.plot(sims[c]["t"], sims[c]["f"], label=LABEL[c], **ST1[c])
    ax.set_xlim(0, 40); ax.set_xlabel("time (s)"); ax.set_ylabel("load-bus frequency (Hz)")
    lo = min(M[c]["f_nadir_Hz"] for c in CASES); ax.set_ylim(lo - 0.02, 50.06)
    ax.grid(alpha=0.3); ax.legend(loc="lower right", fontsize=7)
    ins = inset_axes(ax, width="38%", height="42%", loc="upper right", borderpad=1.2)
    for c in CASES:
        ins.plot(sims[c]["t"], sims[c]["f"], **ST1[c])
    ins.axhspan(49.90, 50.05, color="0.9", zorder=0)
    ins.set_xlim(0.98, 1.3); ins.set_ylim(49.89, 50.003); ins.grid(alpha=0.3); ins.tick_params(labelsize=7)
    ins.set_title("zoom: first 300 ms after the step", fontsize=6.5)
    ax.set_title(f"50 MW load step at t = 1 s, wind penetration {int(40)}%, 9 m/s")
    savefig(fig, "B1_frequency")

    fig, axs = plt.subplots(3, 1, figsize=(6.5, 6.0), sharex=True)
    for c in ("C2", "C3", "C4"):
        S = sims[c]; Sw = S["P"]["Sw_MW"]
        axs[0].plot(S["t"], S["Pew"] * Sw, label=LABEL[c], **ST1[c])
        axs[1].plot(S["t"], S["Pa"] * Sw, **ST1[c])
        axs[2].plot(S["t"], S["X"][5], **ST1[c])
    axs[2].axhline(WOPT, color="0.4", lw=0.8, ls=":"); axs[2].text(30, WOPT + 0.003, "w_opt(9 m/s)", fontsize=7)
    axs[0].set_ylabel("plant electrical P (MW)"); axs[1].set_ylabel("plant aero P (MW)"); axs[2].set_ylabel("rotor speed (pu)")
    axs[2].set_xlabel("time (s)"); axs[0].legend(fontsize=7)
    for a in axs: a.grid(alpha=0.3)
    axs[2].set_xlim(0, 40)
    savefig(fig, "B2_wind_response")

    fig, axs = plt.subplots(1, 3, figsize=(6.5, 2.8))
    keys = [("nadir_dev_mHz", "nadir deviation (mHz)", -1), ("RoCoF_500ms_Hzps", "RoCoF 500 ms (Hz/s)", 1),
            ("secondary_dip_mHz", "secondary dip (mHz)", 1)]
    for a, (k, lab, sgn) in zip(axs, keys):
        vals = [sgn * M[c][k] for c in CASES]
        a.bar(range(5), vals, color=[BARC[c] for c in CASES])
        a.set_xticks(range(5)); a.set_xticklabels(CASES); a.set_title(lab, fontsize=9); a.grid(alpha=0.3, axis="y")
        for i, v in enumerate(vals):
            a.text(i, v, f"{v:.0f}" if k != "RoCoF_500ms_Hzps" else f"{v:.3f}", ha="center", va="bottom", fontsize=6)
    fig.tight_layout()
    savefig(fig, "B3_metrics")
    print(f"B1-B3 done {time.time()-t0:.0f}s")

    # ---- B4 penetration sweep
    ps = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    sweep = {"p": ps, "C0": {"nadir_Hz": M["C0"]["f_nadir_Hz"], "RoCoF_500ms": M["C0"]["RoCoF_500ms_Hzps"]}}
    for c in ("C1", "C2", "C4"):
        sweep[c] = {"nadir_Hz": [], "RoCoF_500ms": [], "Sw_MW": [], "Ssg_pu": []}
        for p in ps:
            S = simulate(make(c, p=p, Dd=DD), dt=0.002); mm = metrics(S)
            sweep[c]["nadir_Hz"].append(mm["f_nadir_Hz"]); sweep[c]["RoCoF_500ms"].append(mm["RoCoF_500ms_Hzps"])
            sweep[c]["Sw_MW"].append(S["P"]["Sw_MW"]); sweep[c]["Ssg_pu"].append(S["P"]["Ssg"])
        print(c, "sweep", [round(v, 4) for v in sweep[c]["nadir_Hz"]], f"{time.time()-t0:.0f}s")
    fig, axs = plt.subplots(1, 2, figsize=(6.5, 2.8))
    for c in ("C1", "C2", "C4"):
        st = {k: v for k, v in STYLE[c].items()}
        axs[0].plot(ps, sweep[c]["nadir_Hz"], marker="o", ms=3, label=c, **st)
        axs[1].plot(ps, sweep[c]["RoCoF_500ms"], marker="o", ms=3, label=c, **st)
    axs[0].axhline(sweep["C0"]["nadir_Hz"], label="C0", **STYLE["C0"])
    axs[1].axhline(sweep["C0"]["RoCoF_500ms"], label="C0", **STYLE["C0"])
    axs[0].set_ylabel("frequency nadir (Hz)"); axs[1].set_ylabel("RoCoF 500 ms (Hz/s)")
    for a in axs: a.set_xlabel("wind penetration p"); a.grid(alpha=0.3)
    axs[1].legend(fontsize=7); fig.tight_layout()
    savefig(fig, "B4_penetration")

    # ---- B5 weak connection (optional)
    b5 = {"X23": [0.1, 0.2, 0.4, 0.6, 0.8], "SCR": [], "nadir_Hz": [], "RoCoF_500ms": [], "zeta": [], "mode_Hz": []}
    try:
        for X in b5["X23"]:
            P = make("C4", X23=X, Dd=DD)
            b5["SCR"].append(SB / (P["kw"] * SB * (X13 + X)))
            dm = damping(make("C4", X23=X, Dd=DD))
            S = simulate(P, dt=0.002); mm = metrics(S)
            b5["nadir_Hz"].append(mm["f_nadir_Hz"]); b5["RoCoF_500ms"].append(mm["RoCoF_500ms_Hzps"])
            b5["zeta"].append(dm["zeta"]); b5["mode_Hz"].append(dm["f_Hz"])
        fig, axs = plt.subplots(1, 3, figsize=(6.5, 2.6))
        for a, k, lab in zip(axs, ("nadir_Hz", "RoCoF_500ms", "zeta"), ("nadir (Hz)", "RoCoF 500 ms (Hz/s)", "SG-VSM damping ratio")):
            a.plot(b5["SCR"], b5[k], marker="o", ms=3, **STYLE["C4"]); a.set_title(lab, fontsize=9)
            if k == "nadir_Hz": a.ticklabel_format(useOffset=False, axis="y"); a.set_ylim(49.900, 49.912); a.axhspan(49.90, 50.05, color="0.9", zorder=0)
            a.set_xlabel("SCR at wind bus"); a.grid(alpha=0.3)
        axs[2].axhline(0.3, color="0.4", ls=":", lw=0.8)
        fig.tight_layout(); savefig(fig, "B5_weak_connection")
        print("B5", b5, f"{time.time()-t0:.0f}s")
    except Exception as e:
        b5["error"] = repr(e)

    params = {"SB_MVA": SB / 1e6, "f0_Hz": F0, "PL0_pu": PL0, "DL": DL, "dP_pu": DP, "dP_MW": DP * SB / 1e6,
              "t_event_s": T_EV, "t_end_s": T_END, "Hsg_s": HSG, "Dsg": DSG, "R_gov": RG, "TG": TG, "TCH": TCH,
              "FHP": FHP, "TRH": TRH, "X13": X13, "X23": X23_0, "Xv_windbase": XV_W, "Hv_s": HV, "Rw": RW,
              "tau_m_s": TAU_M, "tau_f_s": TAU_F, "Dd_chosen": DD, "Dd_tuning": tune, "damping_reference": "PLL-measured PCC (load-bus) frequency w3, D'Arco-Suul style; washout wf state kept but not used in damping",
              "washout_damping_scan": washout_scan, "washout_damping_max_zeta": max(q["zeta"] for q in washout_scan), "v_wind": V,
              "p_baseline": 0.4, "N_turbines": sims["C4"]["P"]["N"], "Sw_MW": sims["C4"]["P"]["Sw_MW"],
              "Ssg_pu_C0": sims["C0"]["P"]["Ssg"], "Ssg_pu_wind_cases": sims["C1"]["P"]["Ssg"],
              "X2_C4": sims["C4"]["P"]["X2"], "Xv_sys": sims["C4"]["P"]["X2"] - X23_0,
              "P_avail_9_MW": T.p_avail(V) / 1e6, "P_avail_pu": PAV_PU, "P_del_pu": PDEL_PU, "reserve_pu": RES_PU,
              "reserve_plant_MW": RES_PU * sims["C4"]["P"]["Sw_MW"], "w_opt_pu": WOPT, "w_del_pu": WDEL, "beta_del_deg": BETA,
              "K_OPT_pu": KOPT_PU, "k_del_pu": KDEL_PU, "Ek_to_opt_MJ_per_turbine": DEL["Ek_to_opt"] / 1e6,
              "SCR_wind_bus_baseline": SB / (sims["C4"]["P"]["kw"] * SB * (X13 + X23_0)),
              "SG_VSM_mode_baseline": tune[-1], "solver": "LSODA max_step 0.005 rtol 1e-6 atol 1e-9"}
    out = {"parameters": params, "metrics": M, "gates": G, "sweep_penetration": sweep, "sweep_weak_connection": b5,
           "labels": LABEL}
    with open(os.path.join(RES, "B.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    print(f"total {time.time()-t0:.0f}s")
    return out

if __name__ == "__main__":
    main()
