# Apollo aerodynamic data

Digitized Apollo command-module aerodynamic coefficients, derived lookup tables, and one Apollo 9 ascent flight-condition trace. The 17 reviewed source CSVs from TN D-4688, TN D-3890, and Apollo 9 are indexed by exact SHA-256 in [DATASETS.json](DATASETS.json). Editing one makes its review stale until Mark checks it again. The legacy Apollo 4 folder documents its status separately. Derived tables are **not** separately reviewed by Mark.

| Folder | Report and contents | Status |
|---|---|---|
| [ReconstructedAeroData](ReconstructedAeroData/README.md) | NASA TN D-4688, configuration-C static moment and force plots, Figures 4–6; source PDF, CSVs, overlays, extraction notes | 12 input CSVs checked by Mark |
| [NASA_TN_D_3890_ApolloCM_PitchDamping](NASA_TN_D_3890_ApolloCM_PitchDamping/README.md) | NASA TN D-3890, Figures 14–17; combined pitch-damping derivative, source PDF, CSVs, overlays, source-page images, extraction script | 4 CSVs checked by Mark on 2026-10-10 |
| [MPR_SAT_FE_69_4_AS504_AscentFlightConditions](MPR_SAT_FE_69_4_AS504_AscentFlightConditions/README.md) | MPR-SAT-FE-69-4 / AS-504 Apollo 9, Figure 4-4; Mach and dynamic pressure versus range time, CSV, overlay, source-page render, trace script | CSV checked by Mark on 2026-10-10 |
| [DerivedAero](DerivedAero/README.md) | Stitched c.g. pitch/normal/axial model and symmetry-derived yaw tables | Built from reviewed TN D-4688 inputs; outputs not separately checked |
| [ReconstructedReentryData](ReconstructedReentryData/README.md) | Apollo 4 reentry traces retained from the earlier public collection | See folder README for per-file status |

The [TN D-4688 report](https://ntrs.nasa.gov/api/citations/19680021973/downloads/19680021973.pdf) provides static wind-tunnel coefficients. [TN D-3890](https://ntrs.nasa.gov/api/citations/19670010564/downloads/19670010564.pdf) provides a *combined* pitch-damping derivative under several configurations and oscillation conditions. Its values cannot simply be appended to the static model or treated as separate `C_mq` and `C_m_alpha_dot` terms. The Apollo 9 Figure 4-4 trace is an **ascent flight-condition reference**, not a command-module aerodynamic coefficient. Keep its units and vehicle context separate from the tunnel datasets.

The original reports and plots should be consulted before simulation use. Decimal precision in digitized CSVs reflects the extraction, not physical measurement accuracy. Each source folder documents the axes, limits, and tracing method. The three scripts in `DerivedAero` rebuild the derived CSVs from the local reviewed inputs and reject source files whose hashes no longer match the registry.
