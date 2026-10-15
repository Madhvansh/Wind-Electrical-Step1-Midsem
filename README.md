# Wind Electrical Systems - Step 1: Midsem Milestone

> **Topic:** Grid-Forming Converter Control with Aerodynamic Overspeed Deloading for Wind Turbines in Low-Inertia Weak Grids.

---

## 📌 Executive Summary

Modern wind turbines interface with the power grid through power electronic converters operated in **grid-following** mode. Grid-following converters synchronize via Phase-Locked Loops (PLLs) and inject Maximum Power Point Tracking (MPPT) power. Consequently:
1. They contribute **zero physical inertia** to the power system.
2. Under **weak grid conditions (low Short-Circuit Ratio, SCR)**, the PLL is susceptible to loss of synchronism and voltage instability.

This project implements a **grid-forming converter control** strategy paired with **aerodynamic overspeed deloading** (10% reserve) for wind turbines. Operating on the overspeed side of the $C_p - \lambda$ curve allows the turbine to release stored rotor kinetic energy and immediately increase aerodynamic lift during frequency events—providing true synthetic inertia and frequency support **without requiring secondary batteries or triggering secondary frequency dips**.

---

## 🚀 Key Results & Numbers

- **Turbine Specifications:** 2 MW PMSG, Rotor Radius $R = 35.4\text{ m}$, $\lambda_{\text{opt}} = 8.10$, $C_{p,\max} = 0.480$ (81% of Betz limit), rated at $12\text{ m/s}$ ($26.2\text{ rpm}$).
- **Deloaded Operating Point (9 m/s):**
  - MPPT Baseline: $844\text{ kW}$ at $19.7\text{ rpm}$.
  - Overspeed Deloaded (10%): $759\text{ kW}$ at $23.3\text{ rpm}$ ($\Delta P = 84\text{ kW}$ reserve, $+1.36\text{ MJ}$ additional kinetic energy).
- **Frequency Response (50 MW Step, 40% Wind, 9 m/s):**
  - Grid-Following (MPPT): Frequency nadir drops to **49.659 Hz**, RoCoF = **0.305 Hz/s**.
  - Conventional Synthetic Inertia (no reserve): Sags late to **49.815 Hz** at 11.2 s with secondary frequency dip.
  - **Proposed Grid-Forming with Deloading:** Frequency nadir preserved at **49.906 Hz** (well within IEGC 49.90–50.05 Hz operational band), initial RoCoF improved to **0.162 Hz/s**, effective system inertia raised to **8.51 s** (vs. 3.76 s).
- **Weak Grid Performance:**
  - Grid-following PLL loses small-signal stability around $\text{SCR} \approx 1.30 - 1.37$.
  - Grid-forming converter remains stable down to the static power transfer limit ($\text{SCR} \approx 1.0$).

---

## 📂 Repository Structure

```text
├── deck/                         # Automated presentation generator & PDF exporter
│   ├── build_deck.py             # Generates PowerPoint slides
│   └── export_pdf.py             # PPTX to PDF conversion utility
├── figures/                      # Plots and simulation diagrams (SVG/PNG)
├── papers/                       # Reference literature & IEEE papers
├── report/                       # LaTeX source files for progress report & slides
│   ├── main.tex                  # Comprehensive LaTeX progress report
│   ├── slides.tex                # Beamer presentation source
│   └── gen_*.tex                 # Dynamically generated report sections
├── results/                      # Output CSVs, benchmark data, and verification logs
├── sim/                          # Per-unit ODE simulation models in Python
│   ├── a_aero.py                 # Aerodynamic & $C_p(\lambda, \beta)$ deloading curves
│   ├── b_freq.py                 # System frequency response & inertia dynamics
│   ├── b_summary.py              # Statistical metrics & nadir / RoCoF summaries
│   ├── c_weakgrid.py             # Small-signal stability & SCR impedance analysis
│   └── turbine.py                # Turbine parameter definitions
├── status/                       # Milestone checklists and verification gates
├── PRESENTER_SCRIPT.md           # Script for midsem oral presentation
├── TALKING_POINTS.md             # Key talking points & Q&A preparation
├── Step1_Progress_Report.pdf     # Compiled Step 1 formal report
├── Step1_Slides_v2.pdf           # Compiled presentation slides (PDF)
└── Step1_Slides_v2.pptx          # Presentation deck (PowerPoint)
```

---

## ⚙️ Running the Simulations

The simulation suite runs on standard scientific Python (`scipy`, `numpy`, `matplotlib`).

1. **Aerodynamic & Deloading Curve Analysis:**
   ```bash
   python sim/a_aero.py
   ```
2. **Frequency Response Dynamics (Comparison across controls):**
   ```bash
   python sim/b_freq.py
   ```
3. **Weak-Grid SCR & Small-Signal Duality:**
   ```bash
   python sim/c_weakgrid.py
   ```

---

## 🔮 Future Roadmap (Step 2 & Step 3)

- **Step 2:** Detailed PMSG $dq$-axis machine model, back-to-back converter control with DC-link dynamics, fault ride-through (FRT), and IEEE 9-bus benchmark network integration.
- **Step 3:** Full grid-code compliance testing according to CEA / CERC Indian Electricity Grid Code (IEGC) regulations.
