"""Build Step1_Slides_v2.pptx (16:9, 13 slides) from the verified figures and numbers. Run: python build_deck.py"""
import os, sys
from pathlib import Path
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "figures"
OUT = BASE / "Step1_Slides_v2.pptx"

NAVY = RGBColor(0x1F, 0x3A, 0x5F); GREEN = RGBColor(0x2C, 0xA0, 0x2C); GREY = RGBColor(0x5F, 0x6B, 0x7A)
LIGHT = RGBColor(0xF2, 0xF4, 0xF7); WHITE = RGBColor(0xFF, 0xFF, 0xFF); BLACK = RGBColor(0x22, 0x22, 0x22)
RED = RGBColor(0xD6, 0x27, 0x28)
W, H = Inches(13.333), Inches(7.5)
FOOT = "Step 1 progress report, Wind Electrical Systems, BITS Goa"

prs = Presentation(); prs.slide_width, prs.slide_height = W, H
BLANK = prs.slide_layouts[6]
slides = []

def rect(slide, x, y, w, h, fill, shape=MSO_SHAPE.RECTANGLE, line=None):
    s = slide.shapes.add_shape(shape, x, y, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None: s.line.fill.background()
    else: s.line.color.rgb = line; s.line.width = Pt(1)
    s.shadow.inherit = False
    return s

def text(slide, x, y, w, h, lines, size=18, color=BLACK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, box=None, spacing=1.15):
    """lines: str or list of (text, opts) / str. opts: size, bold, color."""
    shp = box if box is not None else slide.shapes.add_textbox(x, y, w, h)
    tf = shp.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.08); tf.margin_top = tf.margin_bottom = Inches(0.04)
    if isinstance(lines, str): lines = [lines]
    first = True
    for item in lines:
        t, o = (item, {}) if isinstance(item, str) else item
        p = tf.paragraphs[0] if first else tf.add_paragraph(); first = False
        p.alignment = align; p.line_spacing = spacing
        r = p.add_run(); r.text = t
        r.font.size = Pt(o.get("size", size)); r.font.bold = o.get("bold", bold); r.font.color.rgb = o.get("color", color); r.font.name = "Calibri"
    return shp

def base(title, notes=""):
    s = prs.slides.add_slide(BLANK); slides.append(s)
    bar = rect(s, 0, 0, W, Inches(0.95), NAVY)
    text(s, Inches(0.4), Inches(0.08), Inches(12.5), Inches(0.8), title, size=26, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    rect(s, 0, Inches(0.95), W, Inches(0.06), GREEN)
    text(s, Inches(0.4), Inches(7.05), Inches(10), Inches(0.35), FOOT, size=10, color=GREY)
    text(s, Inches(12.2), Inches(7.05), Inches(0.8), Inches(0.35), str(len(slides)), size=10, color=GREY, align=PP_ALIGN.RIGHT)
    if notes: s.notes_slide.notes_text_frame.text = notes
    return s

def bullets(slide, x, y, w, h, items, size=18, color=BLACK):
    return text(slide, x, y, w, h, [("•  " + t if isinstance(t, str) else ("•  " + t[0], t[1])) for t in items], size=size, color=color, spacing=1.25)

def pic(slide, name, x, y, w, h):
    p = FIG / f"{name}.png"; iw, ih = Image.open(p).size
    sc = min(w / iw, h / ih); pw, ph = int(iw * sc), int(ih * sc)
    return slide.shapes.add_picture(str(p), int(x + (w - pw) / 2), int(y + (h - ph) / 2), width=pw, height=ph)

def tile(slide, x, y, w, h, big, small, color=NAVY):
    b = rect(slide, x, y, w, h, LIGHT, MSO_SHAPE.ROUNDED_RECTANGLE)
    b.adjustments[0] = 0.08
    text(slide, x, y + Inches(0.1), w, h * 0.55, big, size=26, color=color, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(slide, x, y + h * 0.55, w, h * 0.42, small, size=13, color=GREY, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.TOP)

def callout(slide, x, y, w, h, lines, size=15):
    b = rect(slide, x, y, w, h, LIGHT, MSO_SHAPE.ROUNDED_RECTANGLE, line=GREEN); b.adjustments[0] = 0.06
    text(slide, x, y, w, h, lines, size=size, anchor=MSO_ANCHOR.MIDDLE, box=b)

def table(slide, x, y, w, h, rows, widths=None, size=12, header=True, highlight_row=None):
    nr, nc = len(rows), len(rows[0])
    t = slide.shapes.add_table(nr, nc, x, y, w, h).table
    if widths:
        tot = sum(widths)
        for j, cw in enumerate(widths): t.columns[j].width = int(w * cw / tot)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j); c.text = ""; c.margin_left = c.margin_right = Inches(0.06); c.margin_top = c.margin_bottom = Inches(0.03)
            p = c.text_frame.paragraphs[0]; r = p.add_run(); r.text = str(val); r.font.size = Pt(size); r.font.name = "Calibri"
            if i == 0 and header:
                c.fill.solid(); c.fill.fore_color.rgb = NAVY; r.font.color.rgb = WHITE; r.font.bold = True
            else:
                c.fill.solid(); c.fill.fore_color.rgb = LIGHT if i % 2 else WHITE; r.font.color.rgb = BLACK
                if highlight_row is not None and i == highlight_row: r.font.bold = True; r.font.color.rgb = GREEN
    return t

# ---------------------------------------------------------------- 1 title
s = prs.slides.add_slide(BLANK); slides.append(s)
rect(s, 0, 0, W, H, NAVY); rect(s, 0, Inches(4.9), W, Inches(0.08), GREEN)
text(s, Inches(0.8), Inches(1.3), Inches(11.7), Inches(2.4), "Grid-Forming Control of a PMSG Wind Turbine Using Rotor Kinetic-Energy Reserve for Inertia and Fast Frequency Support in Weak Grids", size=34, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
text(s, Inches(0.8), Inches(3.8), Inches(11.7), Inches(1.0), [("Step 1 Progress Report, Mid-Semester Evaluation", {"size": 22, "color": RGBColor(0xC9, 0xE7, 0xC9)}), ("Wind Electrical Systems Design Project", {"size": 20, "color": WHITE})], color=WHITE)
text(s, Inches(0.8), Inches(5.3), Inches(11.7), Inches(1.4), [("Madhvansh (2023A8PS0561G)", {"size": 20, "bold": True}), ("BITS Pilani, K K Birla Goa Campus", {"size": 16}), ("13 October 2026", {"size": 16})], color=WHITE)
s.notes_slide.notes_text_frame.text = "Sir, my design project is on grid-forming control of a PMSG wind turbine. The idea is to make the turbine itself supply inertia and frequency support to a weak grid, using its own rotor energy, without a battery. This is Step 1: the models, the first simulations, and the verification."

# ---------------------------------------------------------------- 2 problem
s = base("The problem: converter-interfaced wind gives no inertia, and grid-following control fails in weak grids",
         "A modern turbine connects through a back-to-back converter that is grid-following: a PLL measures grid frequency and the converter injects MPPT power. So the rotor kinetic energy is hidden, zero inertia, and in a weak grid the PLL tracks a voltage the converter itself disturbs and can lose synchronism. India: 54 GW wind; Ember counts 68 events with more than 1 GW lost each, Jan 2022 to Jul 2025, traced to ride-through failures and PLL instability in Rajasthan. GRID-INDIA Feb 2026 discussion paper recommends grid-forming but covers BESS and solar, little on wind: that is the gap. CEA amendment applies from April 2027.")
bullets(s, Inches(0.4), Inches(1.3), Inches(7.3), Inches(5.5), [
    "Today's turbine is grid-following: a PLL measures the grid frequency and the converter injects MPPT power. The rotor's kinetic energy is hidden, so the turbine adds zero inertia.",
    "In a weak grid the PLL tracks a voltage that the converter itself disturbs, and it can lose synchronism.",
    "GRID-INDIA's discussion paper on grid-forming inverters (Feb 2026) recommends GFM capability but treats BESS and solar in detail and says little about wind.",
    ("This project: make the wind turbine itself grid-forming, with its reserve and inertia coming from the rotor, not from a battery.", {"bold": True, "color": NAVY}),
], size=17)
tile(s, Inches(8.1), Inches(1.4), Inches(4.8), Inches(1.6), "54 GW", "wind installed in India by late 2025")
tile(s, Inches(8.1), Inches(3.2), Inches(4.8), Inches(1.6), "68 events", "more than 1 GW of renewables lost in a single incident, Jan 2022 to Jul 2025 (Ember); PLL instability under weak-grid conditions, Rajasthan hubs", RED)
tile(s, Inches(8.1), Inches(5.0), Inches(4.8), Inches(1.6), "1 Apr 2027", "CEA technical-standards amendment 2026 takes effect")

# ---------------------------------------------------------------- 3 course link
s = base("Link to the course: Betz, the Cp-lambda curve and the Cp-optimal line",
         "Everything starts from class. Power in the wind is half rho A v cubed; Betz limit 16/27 = 0.593. This is the Cp-lambda family for my 2 MW turbine with the Heier model: Cp max 0.480 at lambda opt 8.10, 81 percent of Betz; real blades sit below Betz because of drag, the CD/CL term from our aerodynamic-efficiency derivation. MPPT means staying on the peak, the Cp-optimal line, which gives P = K omega cubed. The two control handles from the notes, pitch and electrical power control through the converter, are the ones I use.")
bullets(s, Inches(0.4), Inches(1.3), Inches(5.6), Inches(5.6), [
    "Power in the wind: P = ½ ρ A v³. Betz limit 16/27 = 0.593.",
    "Heier model Cp(λ, β) for the 2 MW turbine: Cp,max = 0.480 at λ_opt = 8.10, 81 percent of Betz (drag, tip loss, wake rotation).",
    "MPPT = staying on the peak, the Cp-optimal line: P = K_opt ω³ with K_opt = 96.6 kW/(rad/s)³.",
    "Course control strategies used here: pitch control (mechanical power) and controlling the electrical power through the power-electronic interface.",
    ("Turbine: R = 35.4 m, 2 MW at 12 m/s and 26.2 rpm, H = 3 s, speed limits 0.5 to 1.2 pu.", {"color": GREY, "size": 15}),
], size=17)
pic(s, "A1_cp_curves", Inches(6.2), Inches(1.2), Inches(6.9), Inches(5.7))

# ---------------------------------------------------------------- 4 key idea
s = base("Key idea: operate off the Cp-optimal line, on the overspeed side",
         "Grey curves: power versus rotor speed per wind speed. Black dashed: MPPT locus. I deliberately run on the overspeed side, the green locus. At 9 m/s MPPT is 844 kW at 19.7 rpm; deloaded the turbine runs 23.3 rpm, 759 kW, holding 84 kW reserve and storing extra kinetic energy. When frequency falls and the converter pulls more power the rotor slows, moves toward the peak, Cp rises, aerodynamic power increases exactly when the grid needs it: kinetic energy and reserve come out together, no secondary dip. Below rated no pitch; above 12 m/s the speed limit binds and pitch takes over, 1.2 deg at 12 m/s, 8.5 deg at 14.")
pic(s, "A2_power_speed", Inches(0.3), Inches(1.15), Inches(8.4), Inches(5.8))
callout(s, Inches(8.9), Inches(1.4), Inches(4.1), Inches(5.3), [
    ("At 9 m/s", {"bold": True, "size": 17, "color": NAVY}),
    "MPPT: 844 kW at 19.7 rpm",
    "Deloaded 10 percent: 759 kW at 23.3 rpm, pitch 0 deg",
    "Reserve: 84 kW per turbine",
    ("Why the overspeed side", {"bold": True, "size": 17, "color": NAVY}),
    "When the converter draws more power the rotor slows toward the peak, so Cp RISES and aerodynamic power increases while the grid needs it.",
    "Kinetic energy and reserve are released together: no secondary dip.",
    ("Above 12 m/s the 1.2 pu speed limit binds and pitch does the deloading (1.18 deg at 12 m/s, 8.5 deg at 14 m/s).", {"size": 13, "color": GREY}),
], size=15)

# ---------------------------------------------------------------- 5 reserve
s = base("What the reserve buys: power headroom plus stored kinetic energy",
         "Top: reserve grows with wind speed, 25 kW at 6 m/s, 84 at 9, 154 at 11, 200 kW at rated. Bottom: releasable kinetic energy. At 9 m/s one turbine releases 1.36 MJ slowing back to MPPT speed and 3.23 MJ down to the 0.5 pu floor; equivalent H 0.68 s and 1.62 s on 2 MW. Cost: for an illustrative Indian site, Weibull k 2, c 7.5, a permanent 10 percent deload cuts annual energy from 4725 to 4253 MWh, CF 27.0 to 24.3 percent, about 16.5 lakh rupees a year at 3.5 per unit. An upper bound: the reserve is needed only in low-inertia hours and it replaces a battery.")
pic(s, "A4_reserve", Inches(0.3), Inches(1.15), Inches(7.9), Inches(5.8))
tile(s, Inches(8.5), Inches(1.3), Inches(4.5), Inches(1.25), "25 → 200 kW", "reserve per turbine, 6 m/s to rated (84 kW at 9 m/s)")
tile(s, Inches(8.5), Inches(2.7), Inches(4.5), Inches(1.25), "1.36 MJ / 3.23 MJ", "kinetic energy releasable at 9 m/s: to MPPT speed / to 0.5 pu (H_eq 0.68 s / 1.62 s)", GREEN)
tile(s, Inches(8.5), Inches(4.1), Inches(4.5), Inches(1.25), "4,725 → 4,253 MWh/yr", "annual energy, MPPT vs 10 percent deloaded (CF 27.0 → 24.3 percent), Weibull k = 2, c = 7.5 m/s")
tile(s, Inches(8.5), Inches(5.5), Inches(4.5), Inches(1.25), "INR 16.5 lakh/yr", "upper-bound cost at 3.5 INR/kWh; reserve is needed only in low-inertia hours, and it replaces a battery", RED)

# ---------------------------------------------------------------- 6 test system
s = base("Test system and the five cases",
         "Kundur-style equivalent: one synchronous fleet, H 5 s, reheat steam governor; DC power-flow network; 1000 MW load; 50 MW step at 1 s. Wind supplies 40 percent at 9 m/s: 474 turbines, 948 MW. Five cases: C0 all synchronous; C1 grid-following MPPT, today's practice; C2 grid-following plus synthetic inertia and droop, no reserve, what vendors offer; C3 the same controller with my 10 percent reserve; C4 the proposal, a grid-forming VSM with the reserve. C2 to C4 use identical gains, Hv 5 s and 5 percent droop, so the comparison is fair.")
y0 = Inches(1.45); bh = Inches(1.2)
b1 = rect(s, Inches(0.5), y0, Inches(3.3), bh, LIGHT, MSO_SHAPE.ROUNDED_RECTANGLE, line=NAVY); text(s, 0, 0, 0, 0, [("Synchronous fleet", {"bold": True, "color": NAVY}), ("H = 5 s, reheat steam governor, droop 5 percent", {"size": 13})], size=15, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, box=b1)
b2 = rect(s, Inches(5.0), y0, Inches(3.3), bh, LIGHT, MSO_SHAPE.ROUNDED_RECTANGLE, line=NAVY); text(s, 0, 0, 0, 0, [("Load bus 3", {"bold": True, "color": NAVY}), ("1000 MW, +50 MW step at t = 1 s", {"size": 13})], size=15, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, box=b2)
b3 = rect(s, Inches(9.5), y0, Inches(3.3), bh, LIGHT, MSO_SHAPE.ROUNDED_RECTANGLE, line=GREEN); text(s, 0, 0, 0, 0, [("Wind plant", {"bold": True, "color": GREEN}), ("474 x 2 MW PMSG = 948 MW, 9 m/s, 40 percent of load", {"size": 13})], size=15, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, box=b3)
for xa, xb, lab in ((Inches(3.8), Inches(5.0), "X13 = 0.25 pu"), (Inches(8.3), Inches(9.5), "X23 = 0.20 pu")):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, xa, y0 + bh // 2, xb, y0 + bh // 2); c.line.color.rgb = NAVY; c.line.width = Pt(2.5)
    text(s, xa, y0 + bh // 2 - Inches(0.45), xb - xa, Inches(0.4), lab, size=12, color=GREY, align=PP_ALIGN.CENTER)
text(s, Inches(0.5), Inches(2.75), Inches(12.3), Inches(0.4), "Base 1000 MVA, 50 Hz. Load self-regulation D = 1. Controller gains identical in C2, C3, C4: virtual inertia H_v = 5 s, droop 5 percent on the wind base.", size=13, color=GREY)
table(s, Inches(0.5), Inches(3.3), Inches(12.3), Inches(3.4), [
    ["Case", "Wind-plant control", "Reserve", "What it represents"],
    ["C0", "no wind, all synchronous", "-", "reference grid"],
    ["C1", "grid-following, MPPT", "none", "today's standard practice"],
    ["C2", "grid-following + synthetic inertia + droop", "none", "what vendors offer now; support is borrowed from the rotor"],
    ["C3", "grid-following + synthetic inertia + droop", "10 percent overspeed", "same controller as C2, with the reserve"],
    ["C4", "grid-forming virtual synchronous machine (proposed)", "10 percent overspeed", "voltage source: inertia and droop with no frequency measurement"],
], widths=[0.7, 4.2, 1.9, 5.5], size=13, highlight_row=5)

# ---------------------------------------------------------------- 7 headline
s = base("Headline: grid-forming with the reserve keeps the nadir inside the IEGC band",
         "Grey band: IEGC 49.90 to 50.05 Hz. C0 nadir 49.771. C1 grid-following MPPT: 40 percent wind cuts system inertia from 5.88 to 3.76 s, nadir 49.659, RoCoF at the step 0.33 Hz/s. C2 synthetic inertia without reserve looks good for two seconds then keeps sagging: the rotor falls from 0.75 to 0.70 pu, leaves the optimum, capture drops, minimum 49.815 Hz at 11 s and it settles worse than no support. This is the secondary-dip problem, Ullah 2008. C4 proposed: nadir 49.906, inside the band, RoCoF at the step 0.162 Hz/s, half of grid-following, system inertia 8.51 s, rotor 0.888 to 0.831 pu, no secondary dip. Honest point: C3, grid-following with the same reserve, reaches the same nadir, the reserve sets the nadir. Grid-forming wins on instantaneous RoCoF, real inertia, and weak-grid stability.")
pic(s, "B1_frequency", Inches(0.3), Inches(1.15), Inches(8.6), Inches(5.8))
table(s, Inches(9.1), Inches(1.3), Inches(3.95), Inches(3.0), [
    ["Case", "Nadir (Hz)", "RoCoF at step"],
    ["C0 all-sync", "49.771", "0.213 Hz/s"],
    ["C1 GFL MPPT", "49.659", "0.332 Hz/s"],
    ["C2 GFL + SI", "49.815 (11 s)", "0.332 Hz/s"],
    ["C3 GFL + reserve", "49.906", "0.332 Hz/s"],
    ["C4 GFM + reserve", "49.906", "0.162 Hz/s"],
], widths=[1.6, 1.2, 1.3], size=12, highlight_row=5)
callout(s, Inches(9.1), Inches(4.5), Inches(3.95), Inches(2.35), [
    ("System inertia H_sys: 3.76 s (C1) → 8.51 s (C4)", {"bold": True, "color": NAVY}),
    "The reserve sets the nadir: C3 and C4 tie at 49.906 Hz.",
    "Grid-forming halves the instantaneous RoCoF because it responds as a voltage source with no frequency measurement.",
], size=13)

# ---------------------------------------------------------------- 8 why
s = base("Why it works: the wind plant during the event",
         "Top, electrical power. Orange no-reserve spikes to 433 MW then decays because it is borrowing. Green with reserve steps from 360 to about 397 MW and holds about 387. Middle, aerodynamic power: orange falls as the rotor leaves the optimum; green rises from 360 to 386 MW as the rotor slows toward the peak, the overspeed effect. Bottom: orange rotor drops below the MPPT speed 0.75 pu to 0.70; green stays above it, 0.888 to 0.831 pu.")
pic(s, "B2_wind_response", Inches(0.3), Inches(1.15), Inches(7.6), Inches(5.8))
callout(s, Inches(8.2), Inches(1.4), Inches(4.8), Inches(1.6), [("Electrical power (top)", {"bold": True, "color": NAVY}), "C2 spikes to 433 MW and decays: it only borrows. C4 steps from 360 to 397 MW and holds about 387 MW."], size=14)
callout(s, Inches(8.2), Inches(3.2), Inches(4.8), Inches(1.6), [("Aerodynamic power (middle)", {"bold": True, "color": NAVY}), "C2 falls to 394 MW as the rotor leaves the optimum. C4 rises from 360 to 386 MW as the rotor slows toward the peak."], size=14)
callout(s, Inches(8.2), Inches(5.0), Inches(4.8), Inches(1.75), [("Rotor speed (bottom)", {"bold": True, "color": NAVY}), "C2 drops below the MPPT speed, 0.750 to 0.701 pu. C4 stays above it, 0.888 to 0.831 pu: the extra 37 MW is reserve plus kinetic energy."], size=14)

# ---------------------------------------------------------------- 9 metrics + penetration
s = base("Metrics by case, and what happens as wind share grows",
         "B3 summarises nadir, RoCoF and secondary dip. The 500 ms RoCoF bars of C2, C3, C4 are similar, which is honest: over half a second a fast synthetic-inertia loop matches grid-forming with my optimistic 50 ms measurement lag. B4: from 10 to 60 percent wind the grid-following nadir worsens 49.751 to 49.547 Hz; the grid-forming nadir improves 49.811 to 49.928 Hz, because every GFM turbine adds inertia and reserve. More wind means a stronger grid.")
pic(s, "B4_penetration", Inches(0.3), Inches(1.2), Inches(7.6), Inches(4.3))
pic(s, "B3_metrics", Inches(8.0), Inches(1.2), Inches(5.1), Inches(4.3))
text(s, Inches(0.5), Inches(5.0), Inches(12.3), Inches(0.5), "Left (B4): nadir and 500 ms RoCoF versus wind share. Right (B3): nadir deviation, 500 ms RoCoF and secondary dip per case at 40 percent wind.", size=13, color=GREY)
callout(s, Inches(0.5), Inches(5.6), Inches(12.3), Inches(1.25), [
    ("10 to 60 percent wind: grid-following nadir worsens 49.751 → 49.547 Hz; grid-forming nadir improves 49.811 → 49.928 Hz. Every grid-forming turbine adds inertia and reserve, so more wind strengthens the grid.", {"bold": True, "color": NAVY}),
], size=15)

# ---------------------------------------------------------------- 10 weak grid
s = base("Weak-grid stability: grid-following fails where grid-forming gets better",
         "SCR = fault level over plant rating; below 3 is weak by IEEE 1204, and the Rajasthan hubs are weak in this sense. Left: a grid-following converter exporting 1 pu with PLL and AC-voltage loop. As SCR falls its damping collapses and a 5 to 7 Hz PLL-voltage-loop oscillation crosses into the right half plane at SCR 1.30 to 1.37. Right: the grid-forming VSM stays stable to the static limit at SCR 1.0 and its swing-mode damping improves as the grid weakens. The duality of Li, Gu and Green 2022. Also, in the frequency case, weakening the connection from SCR 3 to 1 leaves the nadir at 49.906 and raises the machine-converter damping from 0.25 to 0.60.")
pic(s, "C1_weakgrid_stability", Inches(0.3), Inches(1.15), Inches(8.6), Inches(4.3))
tile(s, Inches(9.1), Inches(1.3), Inches(3.95), Inches(1.3), "SCR 1.30 to 1.37", "grid-following loses stability (40 / 20 / 10 Hz PLL); IEEE 1204 weak-grid threshold is SCR 3", RED)
tile(s, Inches(9.1), Inches(2.8), Inches(3.95), Inches(1.3), "stable to SCR 1.0", "grid-forming VSM stays stable to the static limit; damping rises as the grid weakens", GREEN)
tile(s, Inches(9.1), Inches(4.3), Inches(3.95), Inches(1.3), "ζ 0.25 → 0.60", "damping of the proposed plant as its connection weakens from SCR 3 to 1 (nadir unchanged)")
callout(s, Inches(0.5), Inches(5.75), Inches(12.55), Inches(1.15), [
    ("Duality (Li, Gu and Green, 2022): grid-following likes a stiff grid, grid-forming likes a weak one. Weak Indian RE hubs are exactly where grid-forming wind belongs.", {"bold": True, "color": NAVY}),
    ("Quasi-static model: PLL bandwidth shifts the critical SCR only slightly here; the fast-PLL penalty needs the electromagnetic network dynamics planned for Step 2.", {"size": 13, "color": GREY}),
], size=15)

# ---------------------------------------------------------------- 11 verification
s = base("Verification: 16 checks against hand-derivable results, all pass",
         "I did not want simulations that merely look plausible, so every model is checked against an analytic result. Sixteen checks, all pass. Cp max below Betz; MPPT gives rated power at 12 m/s; the initial RoCoF matches delta P f0 over 2 H to within 1 percent; the grid-following steady-state frequency matches the droop formula to 1e-10; rotor energy balance closes to 1e-11; the grid-forming swing mode matches the closed-form natural frequency and damping to 2 percent.")
table(s, Inches(0.4), Inches(1.2), Inches(12.5), Inches(5.7), [
    ["Gate", "What it checks", "Value", "Result"],
    ["GA1", "Cp,max below the Betz limit", "0.480 < 0.593", "PASS"],
    ["GA2", "λ_opt and Cp,max in the expected range for the Heier model", "8.10, 0.480", "PASS"],
    ["GA3", "MPPT power at 12 m/s equals the 2 MW rating", "2.000 MW", "PASS"],
    ["GA4", "Deloaded operating point reproduces 0.9 P_avail at every wind speed", "max error 6e-14", "PASS"],
    ["GA5", "Deloaded speed above MPPT speed in every overspeed case", "yes, 6 to 11 m/s", "PASS"],
    ["GA6", "Annual-energy loss of the deloaded case equals 10 percent", "10.000 percent", "PASS"],
    ["GB1", "Exact pre-event steady state (no drift before the step)", "|Δf| = 0", "PASS"],
    ["GB2", "Initial COI RoCoF equals ΔP f0 / (2 H_sys), cases C0, C1, C4", "errors 0.19, 0.24, 0.93 percent", "PASS"],
    ["GB3", "C1 steady-state Δf equals the droop and load-damping formula", "error 1e-10", "PASS"],
    ["GB4", "Rotor energy balance: ∫(P_aero − P_e) dt equals ΔE_kinetic", "error 1e-11", "PASS"],
    ["GB5", "Proposed case keeps the rotor above the MPPT speed", "min 0.831 pu (limit 0.740)", "PASS"],
    ["GB6", "Ordering: C4 RoCoF below C1, C4 nadir above C1 and C2", "0.116 < 0.305 Hz/s", "PASS"],
    ["GC1", "GFL static limit without voltage support at SCR = 2 P0", "within 2 percent", "PASS"],
    ["GC2", "GFM swing mode matches closed-form ω_n and ζ at SCR 5", "within 2 percent", "PASS"],
    ["GC3", "Every GFL variant stable at SCR 10", "yes", "PASS"],
    ["GC4", "GFL margin falls as SCR falls; GFM damping falls as SCR rises", "yes", "PASS"],
], widths=[0.7, 6.3, 2.8, 0.9], size=11)

# ---------------------------------------------------------------- 12 plan
s = base("Steps 2 and 3",
         "Step 1 is an aggregated model with averaged converters and a DC power-flow network. Step 2 adds the detailed PMSG dq model with machine-side and grid-side converters and the DC link, dual-port grid-forming control from Lyu and Gross, current limiting and fault ride-through, and realistic frequency-measurement windows for the grid-following comparison. Step 3 moves to the IEEE 9-bus system, turbulent wind, a check against the Indian grid-code requirements, and the final report. Thank you, sir.")
callout(s, Inches(0.5), Inches(1.4), Inches(6.0), Inches(4.3), [
    ("Step 2: detailed converter model", {"bold": True, "size": 19, "color": NAVY}),
    "•  PMSG dq model with machine-side and grid-side converters and the DC link",
    "•  Dual-port grid-forming control (Lyu and Gross, 2024)",
    "•  Current limiting and fault ride-through",
    "•  Realistic frequency-measurement windows for the grid-following comparison",
    "•  Weak-grid study with electromagnetic network dynamics (fast-PLL penalty)",
], size=15)
callout(s, Inches(6.8), Inches(1.4), Inches(6.0), Inches(4.3), [
    ("Step 3: system test and final report", {"bold": True, "size": 19, "color": NAVY}),
    "•  IEEE 9-bus test system with the detailed plant",
    "•  Turbulent wind input and wind-speed sensitivity",
    "•  Check against Indian grid-code requirements (IEGC 2023, CEA 2026)",
    "•  Design recommendation for wind plants in weak Indian grids",
    "•  Final report",
], size=15)
text(s, Inches(0.5), Inches(5.9), Inches(12.3), Inches(1.0), [("Step 1 delivered: aerodynamic design, frequency-support simulation, weak-grid stability study, 16 verified checks. Grid-forming wind with a rotor reserve keeps the nadir inside the IEGC band and stays stable where grid-following fails.", {"bold": True, "color": GREEN})], size=16)

# ---------------------------------------------------------------- 13 references
s = base("References", "Base paper is [1] Lyu and Gross 2024 with [3] Yao 2026 for the deloading strategy; [5] for the weak-grid duality; [6] for the secondary-dip problem; [7] to [9] for the models and the course theory; [11] to [15] for the Indian context and standards.")
refs = [
    "[1] Y. Lyu, D. Gross, Grid forming fast frequency response for PMSG-based wind turbines, IEEE Trans. Sustainable Energy, 15(1), 23-38, 2024.",
    "[2] Y. Lyu, I. Subotic, D. Gross, Unified grid-forming control of PMSG wind turbines for fast frequency response and MPPT, IREP 2022, arXiv 2207.09536.",
    "[3] Yao et al., Grid-forming wind turbine control based on novel deloading strategy and adaptive configurable natural droop controller, Frontiers in Energy Research, 2026.",
    "[4] S. D'Arco, J. A. Suul, Equivalence of virtual synchronous machines and frequency-droops for converter-based microgrids, IEEE Trans. Smart Grid, 5(1), 2014.",
    "[5] Y. Li, Y. Gu, T. C. Green, Revisiting grid-forming and grid-following inverters: a duality theory, IEEE Trans. Power Systems, 37(6), 2022.",
    "[6] J. Ullah, T. Thiringer, D. Karlsson, Temporary primary frequency control support by variable speed wind turbines, IEEE Trans. Power Systems, 23(2), 2008.",
    "[7] P. Kundur, Power System Stability and Control, McGraw-Hill, 1994.",
    "[8] S. Heier, Grid Integration of Wind Energy Conversion Systems, Wiley, 1998.",
    "[9] S. N. Bhadra, D. Kastha, S. Banerjee, Wind Electrical Systems, Oxford University Press, 2005.",
    "[10] Yu et al., An overview of grid-forming control for wind turbine converters, IEEE IECON 2021.",
    "[11] GRID-INDIA, Discussion paper on grid-forming inverters, 2026 (Power Line, Feb 2026).",
    "[12] Ember, Transmission gaps are beginning to constrain India's rapid renewables integration, 2026.",
    "[13] CEA, Technical Standards for Construction of Electrical Plants and Electric Lines (Amendment) Regulations, 2026.",
    "[14] CERC, Indian Electricity Grid Code Regulations, 2023.",
    "[15] IEEE Std 1204-1997, Guide for planning DC links terminating at AC locations having low short-circuit capacities.",
]
text(s, Inches(0.4), Inches(1.2), Inches(6.2), Inches(5.7), refs[:8], size=12, spacing=1.2)
text(s, Inches(6.8), Inches(1.2), Inches(6.2), Inches(5.7), refs[8:], size=12, spacing=1.2)

prs.save(OUT)
print("saved", OUT, "slides", len(prs.slides))
