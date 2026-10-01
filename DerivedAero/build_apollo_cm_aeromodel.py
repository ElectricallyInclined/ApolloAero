"""Combine reviewed NASA TN D-4688 Figure 4-6 curves into one lookup CSV.

At each measured Mach station, use the union of the three source angle grids
within their common supported interval. Source points remain exact; missing
coefficients are linearly interpolated in angle only. No Mach interpolation or
extrapolation is performed.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path


PARSER = argparse.ArgumentParser(description=__doc__)
PARSER.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
PARSER.add_argument('--output-dir', type=Path)
ARGS = PARSER.parse_args()
ROOT = ARGS.root.resolve()
OUT = (ARGS.output_dir or ROOT/'derived').resolve()
SOURCE_ID = 'NASA_TN_D_4688_Apollo_Command_Module_Aerodynamic_Characteristics'
OUTPUT_NAME = 'ApolloCM_aeromodel_Figures4to6.csv'
SOURCE_NAMES = {
    4: {'cm': 'ApolloCM_CmCG_Figure4b.csv', 'cn': 'ApolloCM_CN_Figure4c.csv', 'ca': 'ApolloCM_CA_Figure4d.csv'},
    5: {'cm': 'ApolloCM_CmCG_Figure5b.csv', 'cn': 'ApolloCM_CN_Figure5c.csv', 'ca': 'ApolloCM_CA_Figure5d.csv'},
    6: {'cm': 'ApolloCM_CmCG_Figure6b.csv', 'cn': 'ApolloCM_CN_Figure6c.csv', 'ca': 'ApolloCM_CA_Figure6d.csv'},
}
COLUMNS = {
    'cm': 'pitching_moment_coefficient_cg',
    'cn': 'normal_force_coefficient',
    'ca': 'axial_force_coefficient',
}
QUANT = Decimal('0.000001')


def fmt(value: Decimal) -> str:
    return format(value.normalize(), 'f')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_facility(value: str) -> str:
    return ' '.join(value.replace('JPL-20SWT', 'JPL-20 SWT').strip().split())


registry = json.loads((ROOT/'DATASETS.json').read_text(encoding='utf-8'))
source_datasets = {Path(d['path']).name: d for d in registry['datasets'] if d['source_id'] == SOURCE_ID}
source_dir = ROOT/'sources'/SOURCE_ID
series: dict[tuple[int, str, Decimal], dict] = {}
inputs = []

for figure, quantity_files in SOURCE_NAMES.items():
    for quantity, name in quantity_files.items():
        d = source_datasets[name]
        path = source_dir/name
        actual_hash = digest(path)
        if actual_hash != d['sha256'] or d['mark_review']['status'] != 'checked_by_mark' or actual_hash != d['mark_review']['reviewed_sha256']:
            raise ValueError(f'Source missing, modified, or not currently checked by Mark: {name}')
        grouped: dict[Decimal, list] = defaultdict(list)
        with path.open(newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                grouped[Decimal(row['mach'])].append(row)
        for mach, rows in grouped.items():
            ordered = sorted(rows, key=lambda x: Decimal(x['angle_of_attack_deg']))
            angles = [Decimal(x['angle_of_attack_deg']) for x in ordered]
            if len(set(angles)) != len(angles):
                raise ValueError(f'Duplicate angle in {name}, M={mach}')
            reynolds = {Decimal(x['reynolds_number_millions']) for x in ordered}
            facilities = {normalized_facility(x.get('facility', '')) for x in ordered}
            if len(reynolds) != 1 or len(facilities) != 1:
                raise ValueError(f'Inconsistent legend metadata in {name}, M={mach}')
            series[(figure, quantity, mach)] = {
                'angles': angles,
                'values': {Decimal(x['angle_of_attack_deg']): Decimal(x[COLUMNS[quantity]]) for x in ordered},
                'reynolds': next(iter(reynolds)),
                'facility': next(iter(facilities)),
            }
        inputs.append({
            'dataset_id': d['id'], 'path': d['path'], 'sha256': actual_hash,
            'mark_review_status': d['mark_review']['status'],
            'mark_review_date': d['mark_review']['date'],
        })


def at_angle(s: dict, angle: Decimal) -> tuple[Decimal, str]:
    if angle in s['values']:
        return s['values'][angle], 'source_point'
    ix = bisect.bisect_left(s['angles'], angle)
    if ix == 0 or ix == len(s['angles']):
        raise ValueError('Extrapolation attempted')
    a0, a1 = s['angles'][ix-1:ix+1]
    v0, v1 = s['values'][a0], s['values'][a1]
    result = v0 + (v1-v0)*(angle-a0)/(a1-a0)
    return result.quantize(QUANT, rounding=ROUND_HALF_EVEN), 'linear_angle_interpolation'


output_rows = []
domain = []
basis_counts = Counter()
for figure in SOURCE_NAMES:
    mach_sets = [{mach for f,q,mach in series if f == figure and q == quantity} for quantity in COLUMNS]
    if not mach_sets[0] or any(m != mach_sets[0] for m in mach_sets[1:]):
        raise ValueError(f'Mach stations do not align across Figure {figure} panels')
    for mach in sorted(mach_sets[0]):
        cur = {quantity: series[(figure, quantity, mach)] for quantity in COLUMNS}
        if len({s['reynolds'] for s in cur.values()}) != 1:
            raise ValueError(f'Reynolds number differs across Figure {figure}, M={mach}')
        facilities = {s['facility'] for s in cur.values() if s['facility']}
        if len(facilities) > 1:
            raise ValueError(f'Facility differs across Figure {figure}, M={mach}')
        lo = max(s['angles'][0] for s in cur.values())
        hi = min(s['angles'][-1] for s in cur.values())
        if lo > hi:
            raise ValueError(f'No common angle support for Figure {figure}, M={mach}')
        angles = sorted({a for s in cur.values() for a in s['angles'] if lo <= a <= hi})
        domain.append({'figure': figure, 'mach': fmt(mach), 'alpha_min_deg': fmt(lo), 'alpha_max_deg': fmt(hi), 'rows': len(angles)})
        for angle in angles:
            values = {quantity: at_angle(s, angle) for quantity,s in cur.items()}
            for _, basis in values.values():
                basis_counts[basis] += 1
            output_rows.append({
                'figure_group': f'Figure {figure}',
                'mach': fmt(mach),
                'reynolds_number_millions': fmt(cur['cm']['reynolds']),
                'facility': next(iter(facilities), ''),
                'angle_of_attack_deg': fmt(angle),
                'pitching_moment_coefficient_cg': fmt(values['cm'][0]),
                'normal_force_coefficient': fmt(values['cn'][0]),
                'axial_force_coefficient': fmt(values['ca'][0]),
                'pitching_moment_basis': values['cm'][1],
                'normal_force_basis': values['cn'][1],
                'axial_force_basis': values['ca'][1],
            })

OUT.mkdir(parents=True, exist_ok=True)
out_csv = OUT/OUTPUT_NAME
with out_csv.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'mach', 'reynolds_number_millions', 'angle_of_attack_deg',
        'pitching_moment_coefficient_cg', 'normal_force_coefficient',
        'axial_force_coefficient', 'pitching_moment_basis',
        'normal_force_basis', 'axial_force_basis', 'figure_group', 'facility',
    ], lineterminator='\n')
    writer.writeheader()
    writer.writerows(output_rows)

manifest = {
    'name': 'Apollo command module aerodynamic coefficient lookup, NASA TN D-4688 Figures 4-6',
    'csv': OUTPUT_NAME,
    'csv_sha256': digest(out_csv),
    'row_count': len(output_rows),
    'mach_station_count': len(domain),
    'source_report': 'NASA TN D-4688',
    'configuration': 'C',
    'reference': 'pitching moment about c.g.; each source Mach curve calibrated to its printed local zero line',
    'angle_unit': 'degrees',
    'coefficients': ['pitching_moment_coefficient_cg', 'normal_force_coefficient', 'axial_force_coefficient'],
    'method': 'At each measured Mach station, union the three source angle grids within their shared support. Preserve original coefficient values at their source angles; linearly interpolate only in angle within the same Mach curve for missing values. Never interpolate across Mach or extrapolate beyond any source curve.',
    'discontinuity': 'Figure 4(b) M=0.4 contains separate 70.0 and 70.1 degree points around a sharp plotted drop. Both are retained; interpolation between them is a plotting convention, not a measured transition width.',
    'review_status': 'not_checked',
    'review_note': 'All nine input CSVs are checked by Mark. This combined, interpolated output is a new derived dataset and has not been separately reviewed by Mark.',
    'source_value_counts': dict(basis_counts),
    'domains': domain,
    'inputs': inputs,
}
(OUT/'ApolloCM_aeromodel_Figures4to6_provenance.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
print(f'{len(output_rows)} rows, {len(domain)} Mach stations, M={domain[0]["mach"]}-{domain[-1]["mach"]}')
print(f'Basis counts: {dict(basis_counts)}')
print(out_csv)
