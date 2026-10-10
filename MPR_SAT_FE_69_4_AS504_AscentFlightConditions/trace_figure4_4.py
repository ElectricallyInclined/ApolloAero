"""Rebuild the reviewed AS-504 Figure 4-4 Mach and dynamic-pressure trace.

Coordinates refer to the included 2x source-page render. The published solid
curves are followed; dashed nominal/predicted curves are excluded. Dependencies:
numpy, opencv-python, Pillow. Changing the CSV requires fresh Mark review.
"""
from __future__ import annotations
import csv
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SOURCE_IMAGE = HERE / "Figure4_4_source.png"
COLORS = [(220, 38, 38), (20, 130, 210)]
FIGURES = {"Figure4_4_mach_dynamic_pressure": {'lines': [{'name': 'mach',
            'origin': 0.0,
            'points': [(375, 663),
                       (408, 663),
                       (441, 662),
                       (474, 659),
                       (507, 655),
                       (540, 646),
                       (573, 634),
                       (606, 620),
                       (639, 603),
                       (672, 582),
                       (705, 570),
                       (738, 548),
                       (771, 527),
                       (804, 505),
                       (837, 487),
                       (870, 465),
                       (888, 450)],
            'quality': 'pixel_guided_manual_trace',
            'unit': '1',
            'xcal': (375, 900, 0, 160),
            'ycal': (663, 146, 0, 16)},
           {'name': 'dynamic_pressure',
            'origin': 0.0,
            'points': [(375, 663),
                       (408, 654),
                       (441, 636),
                       (474, 602),
                       (507, 553),
                       (540, 485),
                       (573, 395),
                       (606, 322),
                       (639, 278),
                       (672, 290),
                       (688, 325),
                       (705, 377),
                       (738, 475),
                       (771, 538),
                       (804, 604),
                       (837, 636),
                       (870, 650),
                       (888, 658)],
            'quality': 'pixel_guided_manual_trace',
            'unit': 'N/cm^2',
            'xcal': (375, 900, 0, 160),
            'ycal': (663, 146, 0, 4)}],
 'page': 78}}

def track(gray, anchors, step=6, radius=14, ink_weight=4, prior_weight=1):
    """Follow local curve ink near manual anchors, suppressing long grid lines.

    Dynamic programming rewards dark curved pixels while penalizing distance
    from the anchors and abrupt changes in that distance. Anchor x positions
    are included even when they fall between regular sample positions.
    """
    anchors = np.array(anchors, dtype=float)
    xs = np.unique(np.r_[np.arange(int(anchors[0, 0]), int(anchors[-1, 0]) + 1, step),
                         anchors[:, 0].astype(int)])
    prediction = np.interp(xs, anchors[:, 0], anchors[:, 1])
    offsets = np.arange(-radius, radius + 1)

    dark = (gray < 180).astype(np.uint8)
    horizontal = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((1, 45), np.uint8))
    vertical = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((45, 1), np.uint8))
    curve_ink = dark - np.minimum(dark, np.maximum(horizontal, vertical))
    ink_score = cv2.GaussianBlur(curve_ink.astype(np.float32), (3, 3), 0.7)

    scores = np.empty((len(xs), len(offsets)), dtype=np.float32)
    anchor_xs = set(anchors[:, 0].astype(int))
    for i, x in enumerate(xs):
        ys = np.clip(np.rint(prediction[i] + offsets).astype(int), 0, gray.shape[0] - 1)
        scores[i] = ink_score[ys, x] * ink_weight - prior_weight * (offsets / radius) ** 2
        if x in anchor_xs:
            scores[i] -= 0.06 * offsets ** 2

    delta = np.subtract.outer(offsets, offsets)
    transition = -0.07 * delta ** 2
    back = np.zeros(scores.shape, dtype=np.int16)
    cumulative = scores[0].copy()
    for i in range(1, len(xs)):
        choices = cumulative[None, :] + transition
        back[i] = np.argmax(choices, axis=1)
        cumulative = scores[i] + np.max(choices, axis=1)

    state = int(np.argmax(cumulative))
    traced = []
    for i in range(len(xs) - 1, -1, -1):
        traced.append((int(xs[i]), int(round(prediction[i] + offsets[state]))))
        state = int(back[i, state])
    return traced[::-1]


def convert(cal, pixel):
    px0, px1, v0, v1 = cal
    return v0 + (pixel - px0) * (v1 - v0) / (px1 - px0)


def main():
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
    for stem, figure in FIGURES.items():
        page = Image.open(SOURCE_IMAGE).convert("RGB")
        gray = np.asarray(page).mean(2)
        overlay = page.copy()
        draw = ImageDraw.Draw(overlay)
        rows = []
        for series_index, series in enumerate(figure["lines"]):
            color = COLORS[series_index]
            radius = (30 if stem.startswith("Figure4_1") else
                      8 if stem.startswith("Figure4_3") else
                      18 if stem.startswith("Figure4_") else 8)
            points = track(gray, series["points"], radius=radius)
            if stem == "Figure4_1_ascent_position" and series_index == 0:
                points = [(x, max(645, min(651, y)) if x >= 780 else y) for x, y in points]
            if stem == "Figure4_1_ascent_position" and series_index == 2:
                points = [(x, max(1023, y) if x < 520 else y) for x, y in points]
            draw.line(points, fill=color, width=2)
            for i, (x, y) in enumerate(points):
                if i % 4 == 0:
                    draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=color)
                relative_time = convert(series["xcal"], x)
                value = convert(series["ycal"], y)
                rows.append(dict(figure=stem, pdf_page=figure["page"], series=series["name"],
                                 sample_index=i, time_from_axis_s=round(relative_time, 3),
                                 range_time_s=round(relative_time + series["origin"], 3),
                                 value=round(value, 6), unit=series["unit"],
                                 pixel_x=x, pixel_y=y, quality=series["quality"]))
        with (HERE / f"{stem}.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        band = Image.new("RGB", (page.width, 36 + 31 * len(figure["lines"])), "white")
        legend = ImageDraw.Draw(band)
        legend.text((15, 8), f"AS-504 {stem}: dense traces of solid curves", fill="black", font=font)
        for j, series in enumerate(figure["lines"]):
            y = 36 + 31 * j
            legend.rectangle((17, y + 4, 32, y + 19), fill=COLORS[j])
            legend.text((43, y), f"{series['name']} ({series['unit']})", fill="black", font=font)
        composite = Image.new("RGB", (page.width, page.height + band.height), "white")
        composite.paste(overlay)
        composite.paste(band, (0, page.height))
        composite.save(HERE / f"{stem}_overlay.png")
        print(stem, len(rows))


if __name__ == "__main__":
    main()
