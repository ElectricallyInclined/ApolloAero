# NASA TN D-4688: Aerodynamic stability characteristics of the Apollo command module

Source ID: `NASA_TN_D_4688_Apollo_Command_Module_Aerodynamic_Characteristics`

Report number: **NASA TN D-4688**

PDF: [19680021973.pdf](19680021973.pdf) — 184 PDF pages.

Original repository path: `User-added directly to this source folder; earlier path not recorded`

NASA TN D-4688 cover verified; August 1968. Figure 4(b) c.g. moment plot at printed p.43 / PDF p.56.

## Extracted datasets

| File | Mark review | Source locator |
|---|---|---|
| [ApolloCM_CmCG_Figure4b.csv](ApolloCM_CmCG_Figure4b.csv) | **Checked by Mark — 2026-09-28** | Figure 4(b), printed p.43 / PDF p.56; configuration C, C_m about c.g., M=0.4-1.35 |
| [ApolloCM_CmCG_Figure5b.csv](ApolloCM_CmCG_Figure5b.csv) | **Checked by Mark — 2026-09-28** | Figure 5(b), printed p.49 / PDF p.62; configuration C, C_m about c.g., M=1.575-3.27 |
| [ApolloCM_CN_Figure4c.csv](ApolloCM_CN_Figure4c.csv) | **Checked by Mark — 2026-09-28** | Figure 4(c), printed p.44 / PDF p.57; configuration C, normal-force coefficient, M=0.4-1.35 |
| [ApolloCM_CA_Figure4d.csv](ApolloCM_CA_Figure4d.csv) | **Checked by Mark — 2026-09-28** | Figure 4(d), printed p.45 / PDF p.58; configuration C, axial-force coefficient, M=0.4-1.35 |
| [ApolloCM_CN_Figure5c.csv](ApolloCM_CN_Figure5c.csv) | **Checked by Mark — 2026-09-28** | Figure 5(c), printed p.50 / PDF p.63; configuration C, normal-force coefficient, M=1.575-3.27 |
| [ApolloCM_CA_Figure5d.csv](ApolloCM_CA_Figure5d.csv) | **Checked by Mark — 2026-09-28** | Figure 5(d), printed p.51 / PDF p.64; configuration C, axial-force coefficient, M=1.575-3.27 |
| [ApolloCM_CmCG_Figure6b.csv](ApolloCM_CmCG_Figure6b.csv) | **Checked by Mark — 2026-09-28** | Figure 6(b), printed p.55 / PDF p.68; configuration C, pitching-moment coefficient about c.g., M=3.99-9.0 |
| [ApolloCM_CN_Figure6c.csv](ApolloCM_CN_Figure6c.csv) | **Checked by Mark — 2026-09-28** | Figure 6(c), printed p.56 / PDF p.69; configuration C, normal-force coefficient, M=3.99-9.0 |
| [ApolloCM_CA_Figure6d.csv](ApolloCM_CA_Figure6d.csv) | **Checked by Mark — 2026-09-28** | Figure 6(d), printed p.57 / PDF p.70; configuration C, axial-force coefficient, M=3.99-9.0 |
| [ApolloCM_CmApex_Figure4a.csv](ApolloCM_CmApex_Figure4a.csv) | **Checked by Mark — 2026-09-29** | Figure 4(a), printed p.42 / PDF p.55; configuration C, pitching-moment coefficient about apex, M=0.4-1.35 |
| [ApolloCM_CmApex_Figure5a.csv](ApolloCM_CmApex_Figure5a.csv) | **Checked by Mark — 2026-09-29** | Figure 5(a), printed p.48 / PDF p.61; configuration C, pitching-moment coefficient about apex, M=1.575-3.27 |
| [ApolloCM_CmApex_Figure6a.csv](ApolloCM_CmApex_Figure6a.csv) | **Checked by Mark — 2026-09-29** | Figure 6(a), printed p.54 / PDF p.67; configuration C, pitching-moment coefficient about apex, M=3.99-9.0 |

The Figure 4-6 panel matrix includes c.g. pitching moment, normal force and axial force across M=0.4-9.0. [Reproducible seven-panel trace script](trace_ApolloCM_Figures4to6.py). Each CSV has a matching `_notes.txt` and `_overlay.png` in this folder. The nine b/c/d CSVs were checked by Mark on 2026-09-28. Three apex-moment a-panel CSVs were added and checked by Mark on 2026-09-29; they remain excluded from the stitched c.g. aeromodel.

[Figure 4(b) extraction notes](ApolloCM_CmCG_Figure4b_notes.txt), [source overlay](ApolloCM_CmCG_Figure4b_overlay.png), and [reproducible trace script](trace_ApolloCM_CmCG_Figure4b.py). The six Mach curves are normalized to separate local zero lines. [Figure 5(b) extraction notes](ApolloCM_CmCG_Figure5b_notes.txt), [higher-Mach overlay](ApolloCM_CmCG_Figure5b_overlay.png), and [higher-Mach trace script](trace_ApolloCM_CmCG_Figure5b.py) document the five additional curves and their separate zero lines.

[Apex-moment trace script](trace_ApolloCM_CmApex_Figures4to6.py) covers Figures 4(a), 5(a), and 6(a). Each has a CSV, overlay, and notes. The apex and c.g. moment references must stay distinct.

Supporting figure images, where present, are in `figures/`. Their inherited filenames and page mappings require verification; they are evidence candidates, not reviewed data.

Review authority: [top-level index](../../DATA_INDEX.md) and [registry](../../DATASETS.json). Existing embedded confidence/quality statements are historical and do not override those records.
