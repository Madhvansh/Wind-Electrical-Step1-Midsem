"""Task C: weak-grid small-signal stability, GFL (SRF-PLL) vs GFM (VSM/droop).
Quasi-static phasor model, algebraic network, converter base, w_b = 2*pi*50.
Converter exports P0 = 1 pu to an infinite bus Vg = 1 through Xg = 1/SCR."""
import os, sys, json
import numpy as np
from scipy.optimize import fsolve
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import turbine  # noqa: F401  shared physics module (network study uses none of its constants)

BASE = os.path.dirname(HERE)
FIG, RES, STAT = (os.path.join(BASE, d) for d in ("figures", "results", "status"))
for d in (FIG, RES, STAT):
    os.makedirs(d, exist_ok=True)
plt.rcParams.update({"font.size": 9})

WB = 2 * np.pi * 50.0
P0, VG = 1.0, 1.0
TAU_I, TAU_V = 2e-3, 5e-3
KPV, KIV = 0.0, 20.0
XV, D_GFM = 0.15, 20.0
COL = {"C0": dict(color="k", ls="--", lw=1.4), "C1": dict(color="#d62728", lw=1.4),
       "C2": dict(color="#ff7f0e", lw=1.4), "C3": dict(color="#1f77b4", lw=1.4),
       "C4": dict(color="#2ca02c", lw=2.0)}
GFL_CASES = [(10, "C0"), (20, "C2"), (40, "C1")]   # PLL bandwidth Hz -> colour
GFM_CASES = [(2.0, "C3"), (5.0, "C4")]             # H s -> colour (C4 = proposed)
SCR_GRID = np.unique(np.round(np.concatenate([np.linspace(10, 3, 36), np.linspace(3, 1.0, 201)]), 6))[::-1]


# ---------------- GFL ----------------
def pll_gains(f):
    w = 2 * np.pi * f
    return 2 * 0.707 * w / WB, w**2 / WB  # Kp, Ki


def gfl_rhs(x, Xg, Kp, Ki, vc=True):
    th, xpll, i_d, i_q, vdf, vmf, xv = x
    vd = VG * np.cos(th) - Xg * i_q
    vq = -VG * np.sin(th) + Xg * i_d
    vm = np.hypot(vd, vq)
    idr = P0 / vdf
    iqr = -(KPV * (1 - vmf) + xv) if vc else 0.0
    return np.array([WB * (Kp * vq + xpll), Ki * vq, (idr - i_d) / TAU_I, (iqr - i_q) / TAU_I,
                     (vd - vdf) / TAU_V, (vm - vmf) / TAU_V, KIV * (1 - vmf) if vc else 0.0])


def gfl_scaled(x, *a):
    f = gfl_rhs(x, *a)
    return f * np.array([1 / WB, 1, TAU_I, TAU_I, TAU_V, TAU_V, 1 / KIV])


def num_jac(f, x, h=1e-6):
    n = len(x)
    J = np.zeros((n, n))
    for k in range(n):
        e = np.zeros(n)
        e[k] = h * max(1.0, abs(x[k]))
        J[:, k] = (f(x + e) - f(x - e)) / (2 * e[k])
    return J


def modal(ev):
    osc = ev[np.abs(ev.imag) > 1e-3]
    zmin = float(np.min(-osc.real / np.abs(osc))) if len(osc) else None
    return float(np.max(ev.real)), zmin


def solve_eq(fun, x0, args):
    x, info, ier, msg = fsolve(fun, x0, args=args, full_output=True, xtol=1e-12)
    res = float(np.max(np.abs(fun(x, *args))))
    return x, (ier == 1 and res < 1e-8)


def sweep_gfl(fpll):
    Kp, Ki = pll_gains(fpll)
    Xg0 = 1 / SCR_GRID[0]
    th0 = np.arcsin(P0 * Xg0)
    x = np.array([th0, 0, P0, (np.cos(th0) - 1) / Xg0, 1, 1, -(np.cos(th0) - 1) / Xg0])
    out = []
    for scr in SCR_GRID:
        Xg = 1 / scr
        x, ok = solve_eq(gfl_scaled, x, (Xg, Kp, Ki, True))
        if not ok or abs(x[0]) >= np.pi / 2:
            out.append(dict(scr=float(scr), eq=False))
            break
        ev, V = np.linalg.eig(num_jac(lambda z: gfl_rhs(z, Xg, Kp, Ki, True), x))
        mr, zm = modal(ev)
        # participation factors; synchronisation (PLL) modes = participation of (th, xpll) > 0.3
        Pf = np.abs(V * np.linalg.inv(V).T)
        Pf = Pf / Pf.sum(axis=0, keepdims=True)
        sync = ev[(Pf[0] + Pf[1]) > 0.3]
        sre = float(np.max(sync.real))
        so = sync[np.abs(sync.imag) > 1e-3]
        szeta = float(np.min(-so.real / np.abs(so))) if len(so) else None
        tha = np.arcsin(P0 * Xg)
        out.append(dict(scr=float(scr), eq=True, maxre=mr, zmin=zm, sync_re=sre, sync_zeta=szeta, th_deg=float(np.degrees(x[0])),
                        iq=float(x[3]), eq_err=float(abs(x[0] - tha)), ev=ev))
    return out


def gc1_static():
    """AC-voltage loop off, iq = 0: last SCR with an equilibrium (continuation, fine steps)."""
    Kp, Ki = pll_gains(20)
    grid = np.round(np.arange(4.0, 1.0, -0.002), 6)
    th0 = 0.5 * np.arcsin(2 * P0 / 4.0)
    x = np.array([th0, 0, P0 / np.cos(th0), 0, np.cos(th0), np.cos(th0), 0])
    last = None
    for scr in grid:
        xn, ok = solve_eq(gfl_scaled, x, (1 / scr, Kp, Ki, False))
        if not ok:
            break
        x, last = xn, float(scr)
    th = np.linspace(0, np.pi / 2, 200001)
    smax = np.max(np.sin(th) * np.cos(th))
    exist = [s for s in grid if smax >= P0 / s]
    return last, float(min(exist)), 2 * P0


# ---------------- GFM ----------------
def gfm_eq_res(z, Xg):
    E, d = z
    Xt = XV + Xg
    vp = VG + Xg / Xt * (E * np.exp(1j * d) - VG)
    return [abs(vp) - 1.0, E * VG * np.sin(d) / Xt - P0]


def gfm_rhs(x, Xg, E, H):
    d, w = x
    P = E * VG * np.sin(d) / (XV + Xg)
    return np.array([WB * (w - 1), (P0 - P - D_GFM * (w - 1)) / (2 * H)])


def sweep_gfm(H):
    z = np.array([1.0, np.arcsin(P0 * (XV + 1 / SCR_GRID[0]))])
    out = []
    for scr in SCR_GRID:
        Xg = 1 / scr
        zn, info, ier, _ = fsolve(gfm_eq_res, z, args=(Xg,), full_output=True, xtol=1e-12)
        if ier != 1 or max(abs(np.array(gfm_eq_res(zn, Xg)))) > 1e-8 or zn[1] >= np.pi / 2:
            out.append(dict(scr=float(scr), eq=False))
            break
        z = zn
        E, d = z
        ev = np.linalg.eigvals(num_jac(lambda q: gfm_rhs(q, Xg, E, H), np.array([d, 1.0])))
        mr, _ = modal(ev)
        # swing-mode damping ratio from the 2x2 pair (valid also when overdamped, then zeta > 1)
        zm = float(-np.sum(ev).real / (2 * np.sqrt(np.prod(ev).real)))
        Ks = E * VG * np.cos(d) / (XV + Xg)
        wn = np.sqrt(Ks * WB / (2 * H))
        zcf = D_GFM / (4 * H * wn)
        out.append(dict(scr=float(scr), eq=True, maxre=mr, zmin=zm, E=float(E), d_deg=float(np.degrees(d)),
                        Ks=float(Ks), wn_cf=float(wn), z_cf=float(zcf), ev=ev))
    return out


def critical(rows):
    """First SCR (scanning down) where max Re crosses 0, interpolated; else the static limit."""
    eqr = [r for r in rows if r["eq"]]
    for a, b in zip(eqr[:-1], eqr[1:]):
        if a["maxre"] < 0 <= b["maxre"]:
            s = a["scr"] + (b["scr"] - a["scr"]) * (0 - a["maxre"]) / (b["maxre"] - a["maxre"])
            osc = abs(b["ev"][np.argmax(b["ev"].real)].imag) > 1e-3
            return float(s), "eigenvalue crosses into RHP (" + ("oscillatory, Hopf" if osc else "real") + ")"
    if eqr and eqr[-1]["maxre"] >= 0:
        return eqr[0]["scr"], "unstable over whole sweep"
    return float(eqr[-1]["scr"]), "stable down to the last equilibrium (static limit)"


def at(rows, s):
    cand = [r for r in rows if r["eq"]]
    r = min(cand, key=lambda r: abs(r["scr"] - s))
    return r if abs(r["scr"] - s) < 1e-6 else None


def main():
    gfl = {f: sweep_gfl(f) for f, _ in GFL_CASES}
    gfm = {H: sweep_gfm(H) for H, _ in GFM_CASES}

    gates = {}
    last, exist_min, theory = gc1_static()
    err1 = abs(last - theory) / theory
    gates["GC1"] = dict(pass_=bool(err1 <= 0.02 and abs(exist_min - theory) / theory <= 0.02),
                        last_converged_scr=last, scan_min_scr=exist_min, theory_scr=theory, rel_err=err1)
    g2 = []
    for H in (2.0, 5.0):
        r = at(gfm[H], 5.0)
        ev = r["ev"][np.argmax(r["ev"].imag)]
        wn_n, z_n = abs(ev), -ev.real / abs(ev)
        g2.append(dict(H=H, wn_num=float(wn_n), wn_cf=r["wn_cf"], z_num=float(z_n), z_cf=r["z_cf"],
                       wn_err=float(abs(wn_n - r["wn_cf"]) / r["wn_cf"]),
                       z_err=float(abs(z_n - r["z_cf"]) / r["z_cf"])))
    gates["GC2"] = dict(pass_=all(g["wn_err"] <= 0.02 and g["z_err"] <= 0.02 for g in g2), detail=g2)
    gates["GC3"] = dict(pass_=all(at(gfl[f], 10.0)["maxre"] < 0 for f, _ in GFL_CASES),
                        maxre_scr10={str(f): at(gfl[f], 10.0)["maxre"] for f, _ in GFL_CASES})
    # GFL margin = min damping ratio of the oscillatory modes; must be lower at SCR 1.5 than at SCR 3 and 10,
    # and the dominant eigenvalue must cross into the RHP inside the sweep
    t_gfl = {str(f): {str(s_): at(gfl[f], s_)["zmin"] for s_ in (10.0, 3.0, 1.5)} for f, _ in GFL_CASES}
    gfl_ok = all(v["1.5"] < v["3.0"] and v["1.5"] < v["10.0"] for v in t_gfl.values()) and         all(critical(gfl[f])[1].startswith("eigenvalue") for f, _ in GFL_CASES)
    t_gfm = {str(H): (at(gfm[H], 2.0)["zmin"], at(gfm[H], 10.0)["zmin"]) for H, _ in GFM_CASES}
    gfm_ok = all(b < a for a, b in t_gfm.values())
    zs = [r["zmin"] for r in gfm[5.0] if r["eq"]]
    mono = bool(np.all(np.diff(zs) >= -1e-9))
    gates["GC4"] = dict(pass_=bool(gfl_ok and gfm_ok and mono), gfl_min_zeta_at_scr=t_gfl,
                        gfm_zeta_scr2_vs_scr10=t_gfm, gfm_H5_zeta_monotone_in_scr=mono)
    for k, g in gates.items():
        print(k, "PASS" if g["pass_"] else "FAIL", {kk: v for kk, v in g.items() if kk != "pass_"})

    S = [1.5, 2.0, 3.0, 5.0, 10.0]
    res = dict(task="C weak-grid sync stability GFL vs GFM", model=dict(
        wb=WB, P0=P0, Vg=VG, tau_i=TAU_I, tau_v=TAU_V, Kpv=KPV, Kiv=KIV, Xv=XV, D=D_GFM,
        pll_gains={str(f): dict(zip(("Kp", "Ki"), pll_gains(f))) for f, _ in GFL_CASES},
        scr_grid="10 to 3 in steps of 0.2, 3 to 1.0 in steps of 0.01",
        notes="GFL: id*=P0/vdf, AC-voltage PI (Kpv 0, Kiv 20/s) holds |v_pcc|=1; "
              "GFM: E set for |v_pcc|=1, constant in small-signal."),
        static_limits=dict(
            gfl_unity_pf_iq0=dict(theory=2 * P0, numeric_last_converged=last),
            gfl_with_ac_voltage_control=dict(theory=P0, note="|v|=1 requires sin(th)=P0*Xg <= 1"),
            gfm_vpcc1=dict(theory=P0, note="PCC angle obeys sin(th_pcc)=P0*Xg; last converged SCR in sweep",
                           numeric={str(H): [r for r in gfm[H] if r["eq"]][-1]["scr"] for H, _ in GFM_CASES})),
        variants={},
        gates={k: {**{kk: v for kk, v in g.items() if kk != "pass_"}, "pass": g["pass_"]} for k, g in gates.items()},
        colours=dict(GFL_10Hz="C0 black dashed", GFL_20Hz="C2 #ff7f0e", GFL_40Hz="C1 #d62728",
                     GFM_H2="C3 #1f77b4", GFM_H5="C4 #2ca02c (proposed)"))

    def table(rows, extra=()):
        t = {}
        for s in S:
            r = at(rows, s)
            t[str(s)] = None if r is None else dict(max_real=r["maxre"], min_damping=r["zmin"],
                                                      **{e: r[e] for e in extra})
        return t

    for f, _ in GFL_CASES:
        cs, why = critical(gfl[f])
        res["variants"][f"GFL_{f}Hz"] = dict(critical_scr=cs, mechanism=why,
                                             last_equilibrium_scr=[r for r in gfl[f] if r["eq"]][-1]["scr"],
                                             at_scr=table(gfl[f], ("sync_re", "sync_zeta", "th_deg", "iq")),
                                             critical_scr_sync_mode=critical([dict(r, maxre=r["sync_re"]) if r["eq"] else r for r in gfl[f]])[0])
    for H, _ in GFM_CASES:
        cs, why = critical(gfm[H])
        res["variants"][f"GFM_H{int(H)}"] = dict(critical_scr=cs, mechanism=why,
                                                 last_equilibrium_scr=[r for r in gfm[H] if r["eq"]][-1]["scr"],
                                                 at_scr=table(gfm[H], ("E", "d_deg", "Ks", "wn_cf", "z_cf")))

    # figure C1
    fig, ax = plt.subplots(1, 2, figsize=(6.5, 2.8))
    for f, c in GFL_CASES:
        rr = [r for r in gfl[f] if r["eq"]]
        ax[0].plot([r["scr"] for r in rr], [r["maxre"] for r in rr], label=f"GFL, PLL {f} Hz", **COL[c])
    ax[0].set_yscale("symlog", linthresh=1.0)
    yl = ax[0].get_ylim()
    top = max(yl[1], 10)
    ax[0].axhspan(0, top, color="#d62728", alpha=0.10, lw=0, label="unstable (Re > 0)")
    ax[0].set_ylim(yl[0], top)
    ax[0].axhline(0, color="k", lw=0.6)
    ax[0].axvline(3, color="gray", ls="--", lw=1)
    ax[0].text(3.15, -60, "SCR = 3\nIEEE Std 1204\nweak-grid\nthreshold", fontsize=6.5, color="gray", ha="right")
    ax[0].set_xlabel("SCR")
    ax[0].set_ylabel(r"max Re($\lambda$) (1/s)")
    ax[0].set_title("(a) GFL: dominant eigenvalue", fontsize=9)
    ax[0].legend(fontsize=6.5, loc="upper left")
    for H, c in GFM_CASES:
        rr = [r for r in gfm[H] if r["eq"]]
        ax[1].plot([r["scr"] for r in rr], [r["zmin"] for r in rr], label=f"GFM, H = {H:g} s", **COL[c])
    ax[1].axvline(3, color="gray", ls="--", lw=1)
    ax[1].set_xlabel("SCR")
    ax[1].set_ylabel(r"swing-mode damping ratio $\zeta$")
    ax[1].set_title("(b) GFM: swing-mode damping", fontsize=9)
    ax[1].set_ylim(0, 1.0)
    ax[1].legend(fontsize=7)
    for a in ax:
        a.grid(alpha=0.3)
        a.set_xlim(1, 10)
    ax[0].set_xlim(10, 1)
    ax[1].set_xlim(10, 1)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"C1_weakgrid_stability.{ext}"), dpi=200, bbox_inches="tight")
    plt.close(fig)

    # figure C2 (optional)
    fig, ax = plt.subplots(1, 2, figsize=(6.5, 2.8))
    for a, rows, title in ((ax[0], gfl[20], "GFL, PLL 20 Hz"), (ax[1], gfm[5.0], "GFM, H = 5 s")):
        rr = [r for r in rows if r["eq"]]
        evs = np.concatenate([r["ev"] for r in rr])
        sc = np.concatenate([[r["scr"]] * len(r["ev"]) for r in rr])
        m = evs.real > -200
        h = a.scatter(evs.real[m], evs.imag[m], c=sc[m], cmap="viridis", s=4)
        a.axvline(0, color="k", lw=0.6)
        a.grid(alpha=0.3)
        a.set_xlabel("Re (1/s)")
        a.set_ylabel("Im (rad/s)")
        a.set_title(title, fontsize=9)
    fig.colorbar(h, ax=ax, label="SCR")
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"C2_eig_loci.{ext}"), dpi=200, bbox_inches="tight")
    plt.close(fig)

    res["captions"] = dict(
        C1="Weak-grid small-signal stability of a converter exporting 1 pu versus short-circuit ratio. "
           "(a) Grid-following converter (SRF-PLL, 2 ms current loop, AC-voltage PI): real part of the dominant "
           "eigenvalue for PLL bandwidths 10, 20 and 40 Hz; shaded band = unstable; dashed line SCR = 3 "
           "(IEEE Std 1204 weak-grid threshold). Above SCR 2 the dominant pole is the slow real AC-voltage-integrator pole; "
           "below SCR 2 a coupled PLL/voltage-loop oscillatory pair (5 to 7 Hz) takes over and crosses into the RHP. (b) Grid-forming VSM (Xv = 0.15 pu, D = 20 pu): swing-mode "
           "damping ratio for H = 2 s and 5 s.",
        C2="Eigenvalue loci as SCR falls from 10 to the static limit (colour = SCR); modes faster than -200 1/s "
           "omitted. Left: GFL with 20 Hz PLL. Right: GFM with H = 5 s.")
    with open(os.path.join(RES, "C.json"), "w") as fh:
        json.dump(res, fh, indent=2, default=float)
    for k in gates:
        assert gates[k]["pass_"], k
    return res


if __name__ == "__main__":
    res = main()
    for k, v in res["variants"].items():
        print(k, round(v["critical_scr"], 3), v["mechanism"], "last eq", v["last_equilibrium_scr"])
        for s, t in v["at_scr"].items():
            print("   ", s, t)
