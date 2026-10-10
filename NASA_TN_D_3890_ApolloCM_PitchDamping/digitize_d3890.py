"""Digitize the four pitch-damping plots in NASA TN D-3890.

Coordinates are hand-selected from the 3x MuPDF renders of PDF pages 97-100.
Figure 14/15 rows are plotted symbol centers. Figure 16/17 rows sample the
published drawn curves (including between symbols); these are intentionally
marked as curve samples, not independent tunnel observations.
"""
from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
DEST = HERE
PDF = HERE / "19670010564.pdf"


def point_fig14(mach, x, y):
    zeros = {2.5: 280, 3.0: 405, 4.0: 530, 6.0: 655, 10.18: 780}
    return ((x - 625) / 6.27, (zeros[mach] - y) / 31.15)


def point_fig15(mach, x, y):
    zeros = {1.5: 550, 2.0: 720, 3.0: 890}
    return ((x - 595) / 85.8, (zeros[mach] - y) / 85.8)


# Marker centers. Dense clusters have fewer recoverable distinct centers than
# their printed symbols, and are never split into artificial observations.
FIG14 = {
    2.5: [(1442, 281), (1459, 281), (1484, 282), (1516, 287), (1535, 289), (1552, 292), (1566, 294)],
    3.0: [(1442, 405), (1472, 407), (1490, 409), (1514, 413), (1537, 416), (1566, 421)],
    4.0: [(1442, 530), (1470, 533), (1506, 539), (1524, 542), (1544, 545), (1564, 548)],
    6.0: [(1442, 655), (1456, 659), (1469, 660), (1484, 662), (1497, 664), (1509, 669), (1521, 675), (1537, 693), (1552, 705), (1567, 704), (1635, 641), (1635, 655), (1635, 670), (1635, 690), (1635, 712)],
    10.18: [(530, 781), (560, 796), (594, 812), (610, 1145), (625, 1257), (658, 1172), (689, 796), (690, 819), (782, 801), (817, 799), (848, 783), (879, 801), (939, 802), (1253, 773), (1284, 758), (1315, 760), (1377, 780), (1409, 786), (1440, 784), (1470, 783), (1503, 790), (1534, 796), (1565, 783)],
}

FIG15 = {
    1.5: [(725, 610), (747, 625), (751, 640), (785, 678), (794, 643), (844, 643), (920, 650), (1037, 683), (1042, 703), (1035, 721)],
    2.0: [(784, 756), (813, 744), (887, 757), (897, 744), (998, 756), (1035, 756), (1145, 756), (1266, 756), (1301, 757), (1470, 756), (1507, 756)],
    3.0: [(810, 914), (830, 917), (870, 917), (906, 918), (940, 919), (977, 918), (1000, 919), (1090, 917), (1140, 916), (1265, 914), (1327, 914), (1392, 913), (1500, 915), (1572, 916), (1688, 913), (1784, 914)],
}
FIG15_MEAN_ALPHA = {1.5: 143, 2.0: 138, 3.0: 148}

META = {
    14: {
        2.5: ("AEDC-A/C", -0.685, 0.058, 2.8, 0.0196),
        3.0: ("AEDC-A/C", -0.685, 0.058, 3.1, 0.0180),
        4.0: ("AEDC-A/C", -0.685, 0.058, 3.8, 0.0165),
        6.0: ("AEDC-A/C", -0.685, 0.058, 3.6, 0.0140),
        10.18: ("AEDC-A/C", -0.685, 0.058, 1.2, 0.0078),
    },
    15: {
        1.5: ("AEDC-A", -0.63, 0.056, 3.15, 0.0133),
        2.0: ("AEDC-A", -0.63, 0.056, 3.26, 0.0077),
        3.0: ("AEDC-A", -0.68, 0.059, 2.40, 0.0098),
    },
}


def write_markers(fig, observations, converter, independent):
    image = Image.open(DEST / f"Figure{fig}_source.png").convert("RGB")
    draw = ImageDraw.Draw(image)
    colors = [(220, 30, 40), (0, 110, 220), (0, 165, 100), (185, 50, 185), (235, 125, 10)]
    rows = []
    for i, (mach, points) in enumerate(observations.items()):
        for x, y in points:
            indep, value = converter(mach, x, y)
            facility, xd, zd, reynolds, k = META[fig][mach]
            rows.append([fig, mach, round(indep, 2), round(value, 3), FIG15_MEAN_ALPHA[mach] if fig == 15 else "", facility, xd, zd, reynolds, k, "symbol_center", x, y])
            c = colors[i]
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), outline=c, width=3)
    name = f"ApolloCM_pitch_damping_Figure{fig}.csv"
    with (DEST / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["figure", "mach", independent, "cm_q_plus_cm_alpha_dot", "mean_alpha_deg", "facility", "oscillation_center_x_over_d", "oscillation_center_z_over_d", "reynolds_million", "reduced_frequency_k", "trace_type", "pixel_x", "pixel_y"])
        w.writerows(rows)
    image.save(DEST / f"Figure{fig}_overlay.png")
    return name, len(rows)


results = [
    write_markers(14, FIG14, point_fig14, "alpha_deg"),
    write_markers(15, FIG15, point_fig15, "oscillation_amplitude_deg"),
]

# Curve samples chosen at marked alpha positions (roughly 10 degree spacing),
# with additional points at sharp transitions. Values are read from the plotted
# curve, not inferred from a fit or from a different report.
FIG16 = {
    0.5: [(-0.20), (-0.27), (-0.40), (-0.98), (-0.98), (-0.88), (-0.42), (0.10), (0.70), (0.18), (0.19), (0.22), (0.21), (0.22), (0.22), (0.47), (0.96), (1.35), (0.95), (0.48), (0.25), (0.17), (0.12), (0.13), (0.16), (0.19), (0.18), (0.18), (0.16), (0.13), (0.08), (0.06), (0.01), (-0.02), (-0.03), (-0.04), (-0.05)],
    0.8: [(-0.27), (-0.80), (-0.96), (-0.82), (-0.35), (-0.13), (0.40), (0.48), (0.50), (0.50), (0.53), (0.55), (0.54), (0.59), (0.55), (0.18), (-0.89), (-0.64), (0.47), (0.44), (0.36), (0.33), (0.30), (0.27), (0.26), (0.25), (0.27), (0.28), (0.27), (0.26), (0.28), (0.30), (0.31), (0.33), (0.32), (0.27), (-0.18)],
}

# Figure 17: y scale is 0.4 coefficient per 126 image pixels. Marked curves
# mostly lie within +/-0.1, with a narrow entry-attitude spike near 160 deg.
FIG17 = {
    0.3: [-0.10, -0.10, -0.06, 0.00, 0.06, 0.05, -0.02, -0.05, -0.08, -0.10, -0.11, -0.11, -0.12, -0.11, -0.02, 0.45, 0.80, 0.70, 0.02, 0.03, 0.06, 0.00, -0.03, -0.05, -0.06, -0.05, -0.06, -0.05, -0.03, 0.02, 0.05, 0.02, -0.02, -0.06, -0.10, -0.11, -0.11],
    0.5: [-0.06, -0.05, 0.00, 0.10, 0.18, 0.16, 0.08, 0.02, -0.02, -0.03, -0.04, -0.04, -0.03, 0.05, 0.22, 0.47, 0.80, 0.62, 0.00, 0.02, 0.08, 0.03, 0.00, -0.02, -0.04, -0.04, -0.04, -0.05, -0.05, 0.00, 0.10, 0.12, 0.07, 0.00, -0.05, -0.06, -0.06],
    0.7: [-0.12, -0.11, -0.09, -0.02, 0.08, 0.07, -0.02, -0.08, -0.05, -0.04, -0.03, -0.03, -0.05, -0.04, 0.20, -0.20, 0.80, 0.10, 0.00, 0.02, 0.05, -0.01, -0.09, -0.05, -0.02, -0.04, -0.05, -0.04, -0.03, 0.00, 0.03, 0.05, 0.03, 0.00, -0.05, -0.08, -0.08],
}


def write_curves(fig, curves):
    image = Image.open(DEST / f"Figure{fig}_source.png").convert("RGB")
    draw = ImageDraw.Draw(image)
    colors = {0.3: (175, 30, 190), 0.5: (220, 40, 30), 0.7: (0, 140, 100), 0.8: (0, 95, 220)}
    rows = []
    for mach, vals in curves.items():
        for alpha, value in enumerate(vals):
            alpha *= 10
            if fig == 16:
                x, y = round(360 + 4.32 * alpha), round({0.5: 795, 0.8: 1007}[mach] - 107 * value)
                xd, zd, facility = "", "", "NAA-TWT"
            else:
                x, y = round(592 + 3.125 * alpha), round({0.3: 690, 0.5: 943, 0.7: 1195}[mach] - 315 * value)
                xd, zd, facility = -0.637, 0.0584, "Ames 12-ft"
            rows.append([fig, mach, alpha, value, facility, xd, zd, "curve_sample", x, y])
            c = colors[mach]
            draw.ellipse((x - 4, y - 4, x + 4, y + 4), outline=c, width=3)
    name = f"ApolloCM_pitch_damping_Figure{fig}.csv"
    with (DEST / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["figure", "mach", "alpha_deg", "cm_q_plus_cm_alpha_dot", "facility", "oscillation_center_x_over_d", "oscillation_center_z_over_d", "trace_type", "pixel_x", "pixel_y"])
        w.writerows(rows)
    image.save(DEST / f"Figure{fig}_overlay.png")
    return name, len(rows)


results += [write_curves(16, FIG16), write_curves(17, FIG17)]
print(results)
