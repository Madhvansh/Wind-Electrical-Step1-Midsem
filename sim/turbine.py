"""Shared turbine physics for Step 1: 2 MW PMSG wind turbine, Heier/Slootweg Cp(lambda, beta) model.
Units: SI (W, rad/s, m/s, J) unless a name ends in _pu. Import this; never redefine constants elsewhere."""
import numpy as np
from scipy.optimize import brentq, minimize_scalar

RHO = 1.225                      # air density, kg/m^3
R = 35.4                         # rotor radius, m
A = np.pi * R**2                 # swept area, m^2
P_RATED = 2.0e6                  # W
V_CUTIN, V_CUTOUT = 3.5, 25.0    # m/s
H_WT = 3.0                       # s, rotor+generator inertia constant on P_RATED at W_RATED
W_MIN_PU, W_MAX_PU = 0.5, 1.2    # rotor speed limits, pu of W_RATED (full-converter PMSG)
C1, C2, C3, C4, C5, C6 = 0.5176, 116.0, 0.4, 5.0, 21.0, 0.0068   # Heier / Slootweg coefficients
BETZ = 16.0 / 27.0

def cp(lam, beta=0.0):
    """Power coefficient Cp(lambda, beta[deg]), clipped at 0."""
    lam = np.asarray(lam, dtype=float); beta = np.asarray(beta, dtype=float)
    inv_li = 1.0 / (lam + 0.08 * beta) - 0.035 / (beta**3 + 1.0)
    val = C1 * (C2 * inv_li - C3 * beta - C4) * np.exp(-C5 * inv_li) + C6 * lam
    return np.maximum(val, 0.0)

_r = minimize_scalar(lambda l: -float(cp(l, 0.0)), bounds=(4.0, 14.0), method="bounded", options={"xatol": 1e-10})
LAMBDA_OPT = float(_r.x)
CP_MAX = float(cp(LAMBDA_OPT, 0.0))
V_RATED = (P_RATED / (0.5 * RHO * A * CP_MAX)) ** (1.0 / 3.0)   # m/s, MPPT reaches rated power here
W_RATED = LAMBDA_OPT * V_RATED / R                             # rad/s (rotor side, direct drive)
J = 2.0 * H_WT * P_RATED / W_RATED**2                          # kg m^2
K_OPT = 0.5 * RHO * A * R**3 * CP_MAX / LAMBDA_OPT**3          # W/(rad/s)^3, MPPT law P = K_OPT w^3

def p_aero(w, v, beta=0.0):
    """Aerodynamic power, W, at rotor speed w [rad/s], wind v [m/s], pitch beta [deg]."""
    v = np.maximum(np.asarray(v, dtype=float), 1e-6)
    return 0.5 * RHO * A * v**3 * cp(np.asarray(w, dtype=float) * R / v, beta)

def p_avail(v):
    """Available (MPPT) power, W, capped at rated; zero outside cut-in/cut-out."""
    v = float(v)
    if v < V_CUTIN or v > V_CUTOUT:
        return 0.0
    return min(0.5 * RHO * A * v**3 * CP_MAX, P_RATED)

def w_opt(v):
    """Optimal (MPPT) rotor speed, rad/s; held at W_RATED above rated wind."""
    return min(LAMBDA_OPT * float(v) / R, W_RATED)

def kinetic_energy(w):
    return 0.5 * J * np.asarray(w, dtype=float)**2

def deload_point(v, d=0.10):
    """Steady operating point holding a reserve d*P_avail. Overspeed first, pitch only if the speed limit binds."""
    v = float(v); P_av = p_avail(v); P_t = (1.0 - d) * P_av
    wmax = W_MAX_PU * W_RATED; wo = w_opt(v)
    if v < V_RATED:
        lam_d = brentq(lambda l: float(cp(l, 0.0)) - (1.0 - d) * CP_MAX, LAMBDA_OPT, 25.0)
        w_d, beta, mode = lam_d * v / R, 0.0, "overspeed"
        if w_d > wmax:
            w_d = wmax
            beta = brentq(lambda b: float(p_aero(w_d, v, b)) - P_t, 0.0, 30.0)
            mode = "overspeed+pitch"
    else:
        w_d = W_RATED
        beta = brentq(lambda b: float(p_aero(w_d, v, b)) - P_t, 0.0, 45.0)
        mode = "pitch"
    E = kinetic_energy
    return {"v": v, "P_avail": P_av, "P_del": P_t, "reserve": P_av - P_t, "w_opt": wo, "w_del": w_d,
            "beta": beta, "mode": mode,
            "Ek_to_opt": float(max(E(w_d) - E(wo), 0.0)),
            "Ek_to_min": float(E(w_d) - E(W_MIN_PU * W_RATED))}

if __name__ == "__main__":
    rpm = 60.0 / (2 * np.pi)
    print(f"lambda_opt={LAMBDA_OPT:.4f} Cp_max={CP_MAX:.4f} (Betz {BETZ:.4f}) V_rated={V_RATED:.3f} m/s")
    print(f"W_rated={W_RATED:.4f} rad/s = {W_RATED*rpm:.2f} rpm  J={J:.4e} kg m2  K_opt={K_OPT:.2f} W/(rad/s)^3")
    for v in [6, 8, 9, 10, 11, 12, 14]:
        d = deload_point(v)
        chk = float(p_aero(d['w_del'], v, d['beta']))
        print(f"v={v:>4} Pav={d['P_avail']/1e6:.3f}MW Pdel={d['P_del']/1e6:.3f} res={d['reserve']/1e3:6.1f}kW "
              f"wopt={d['w_opt']/W_RATED:.3f}pu wdel={d['w_del']/W_RATED:.3f}pu beta={d['beta']:.2f} {d['mode']:<16}"
              f" Ek_opt={d['Ek_to_opt']/1e6:.2f}MJ Ek_min={d['Ek_to_min']/1e6:.2f}MJ check={abs(chk-d['P_del'])/max(d['P_del'],1):.1e}")
