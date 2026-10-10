# NASA TN D-3890: Apollo command-module pitch damping

[19670010564.pdf](19670010564.pdf) is NASA TN D-3890, *Stability Characteristics of the Apollo Command Module* (March 1967). [NASA source](https://ntrs.nasa.gov/api/citations/19670010564/downloads/19670010564.pdf). Figures 14–17 appear on printed pp. 89–92 / PDF pp. 97–100. Each CSV has a corresponding `FigureNN_source.png` and `FigureNN_overlay.png`; [digitize_d3890.py](digitize_d3890.py) contains the calibrated extraction and overlay construction.

| Figure | CSV | Mach | Configuration | Horizontal axis | Trace type |
|---|---|---|---|---|---|
| 14 | [CSV](ApolloCM_pitch_damping_Figure14.csv) · [overlay](Figure14_overlay.png) | 2.5, 3, 4, 6, 10.18 | Without protuberances | Mean angle of attack | Plotted symbol centers |
| 15 | [CSV](ApolloCM_pitch_damping_Figure15.csv) · [overlay](Figure15_overlay.png) | 1.5, 2, 3 | Without protuberances | Oscillation amplitude | Plotted symbol centers |
| 16 | [CSV](ApolloCM_pitch_damping_Figure16.csv) · [overlay](Figure16_overlay.png) | 0.5, 0.8 | With protuberances | Angle of attack | Drawn-curve samples at 10° intervals |
| 17 | [CSV](ApolloCM_pitch_damping_Figure17.csv) · [overlay](Figure17_overlay.png) | 0.3, 0.5, 0.7 | With umbilical fairing, vent, and surviving antenna | Angle of attack | Drawn-curve samples at 10° intervals |

All four CSVs were **checked by Mark on 2026-10-10** against their overlays. The [public registry](../DATASETS.json) records the reviewed SHA-256 for each exact CSV. Rebuilding or editing a CSV requires a fresh review.

The ordinate is `C_mq + C_m_alpha_dot`, a **combined** pitch-damping derivative. The plot labels negative values as positive damping. Figure 15 is an average over a full oscillation; its amplitude axis is not angle of attack. Figures 14–15 use different oscillation centers. The report says damping depends appreciably on oscillation center and that transfer to a desired flight c.g. was inconclusive (pp. 9–10). These data have not been merged into the TN D-4688 static model.

Symbol centers in Figures 14–15 are approximate where markers overlap. Figure 14's Mach 6 cluster near 160° contains scatter associated with oscillation amplitude, so nearby points remain distinct. Figures 16–17 sample the published curves, not separate tunnel observations; narrow peaks near 150–170° are under-resolved at 10° spacing. Visual extraction precision is roughly 0.1–0.2 coefficient units for Figures 14–15 and 0.05 for Figures 16–17 away from narrow peaks; this is an extraction estimate, not a NASA uncertainty statement. Check geometry and reference conditions before using values across figures or combining with TN D-4688.
