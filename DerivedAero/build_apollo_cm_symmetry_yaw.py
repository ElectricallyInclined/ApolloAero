"""Derive pure-sideslip apex yaw moment from reviewed configuration-C apex Cm.

This is an axisymmetry-based model, not a measured yaw dataset. It applies at
alpha=0 only. The body-axis sign mapping is Cn_apex(beta)=-Cm_apex(beta) for
positive beta, extended oddly to negative beta. Beta=0 is set to zero by
symmetry despite scan/digitization offsets in source Cm(0).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
parser.add_argument('--output-dir',type=Path)
args=parser.parse_args()
root=args.root.resolve()
out=(args.output_dir or root/'derived').resolve()
source_id='NASA_TN_D_4688_Apollo_Command_Module_Aerodynamic_Characteristics'
names=[f'ApolloCM_CmApex_Figure{figure}a.csv' for figure in (4,5,6)]
output_name='ApolloCM_yaw_apex_symmetry_Figures4a5a6a.csv'

def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fmt(value:Decimal)->str:
    return format(value.normalize(),'f')

registry=json.loads((root/'DATASETS.json').read_text(encoding='utf-8'))
by_name={Path(d['path']).name:d for d in registry['datasets'] if d['source_id']==source_id}
rows=[]
domains=[]
inputs=[]
five=Decimal(5)
for name in names:
    entry=by_name[name]
    path=root/entry['path']
    digest=sha(path)
    review=entry['mark_review']
    if digest!=entry['sha256'] or review['status']!='checked_by_mark' or digest!=review['reviewed_sha256']:
        raise ValueError(f'Source modified or not currently checked by Mark: {name}')
    series=defaultdict(list)
    with path.open(newline='',encoding='utf-8') as f:
        for item in csv.DictReader(f):
            series[Decimal(item['mach'])].append(item)
    figure=int(name.split('Figure')[1][0])
    for mach,source_rows in sorted(series.items()):
        alpha_map={}
        reynolds={item['reynolds_number_millions'] for item in source_rows}
        facilities={item['facility'] for item in source_rows}
        if len(reynolds)!=1 or len(facilities)!=1:
            raise ValueError(f'Inconsistent legend metadata: {name}, M={mach}')
        for item in source_rows:
            alpha=Decimal(item['angle_of_attack_deg'])
            if alpha in alpha_map:
                raise ValueError(f'Duplicate source angle: {name}, M={mach}, alpha={alpha}')
            alpha_map[alpha]=Decimal(item['pitching_moment_coefficient_apex'])
        required={five*i for i in range(19)}
        if not required.issubset(alpha_map):
            raise ValueError(f'Missing source points for beta=0..90: {name}, M={mach}: {sorted(required-set(alpha_map))}')
        for beta_int in range(-90,91,5):
            beta=Decimal(beta_int)
            alpha=abs(beta)
            source_cm=alpha_map[alpha]
            yaw=Decimal(0) if beta==0 else (-source_cm if beta>0 else source_cm)
            rows.append({
                'mach':fmt(mach),
                'reynolds_number_millions':next(iter(reynolds)),
                'beta_deg':fmt(beta),
                'yawing_moment_coefficient_apex':fmt(yaw),
                'source_alpha_deg':fmt(alpha),
                'source_pitching_moment_coefficient_apex':fmt(source_cm),
                'derivation':'zero_by_symmetry' if beta==0 else 'axisymmetric_sign_map',
                'figure_group':f'Figure {figure}(a)',
                'facility':next(iter(facilities)),
            })
        domains.append({'figure':figure,'mach':fmt(mach),'beta_min_deg':-90,'beta_max_deg':90,'rows':37})
    inputs.append({'dataset_id':entry['id'],'path':entry['path'],'sha256':digest,
                   'mark_review_status':review['status'],'mark_review_date':review['date']})

out.mkdir(parents=True,exist_ok=True)
output=out/output_name
fieldnames=['mach','reynolds_number_millions','beta_deg','yawing_moment_coefficient_apex',
            'source_alpha_deg','source_pitching_moment_coefficient_apex','derivation',
            'figure_group','facility']
with output.open('w',newline='',encoding='utf-8') as f:
    writer=csv.DictWriter(f,fieldnames=fieldnames,lineterminator='\n')
    writer.writeheader(); writer.writerows(rows)
provenance={
    'name':'Apollo CM configuration-C apex yaw-moment symmetry model',
    'csv':output_name,
    'csv_sha256':sha(output),
    'row_count':len(rows),
    'mach_station_count':len(domains),
    'source_report':'NASA TN D-4688',
    'source_pdf':f'sources/{source_id}/19680021973.pdf',
    'configuration':'C',
    'reference':'theoretical apex',
    'flight_condition':'pure sideslip, alpha=0 degrees',
    'beta_domain_deg':[-90,90],
    'beta_spacing_deg':5,
    'method':'Assume rotational symmetry of basic configuration C about its X axis. For beta>0, Cn_apex(M,beta)=-Cm_apex(M,alpha=beta); for beta<0 use odd symmetry. Force Cn_apex(M,0)=0 to remove scan/digitization offset. Use only exact source alpha points; no angular or Mach interpolation. Moment sign uses the body axes in Figure 1 of NASA TN D-4688.',
    'limitations':'Inferred yaw coefficient, not wind-tunnel yaw data. Valid only for unstraked basic configuration C at alpha=0 under the report body-axis convention. Not a c.g.-referenced yaw moment; c.g. shift requires force and moment-arm terms. Do not apply the one-dimensional beta mapping at nonzero alpha or to asymmetric hardware.',
    'review_status':'not_checked',
    'review_note':'All three apex Cm input CSVs are checked by Mark. This transformed yaw table has not been separately reviewed by Mark.',
    'domains':domains,
    'inputs':inputs,
}
(out/'ApolloCM_yaw_apex_symmetry_Figures4a5a6a_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
print(f'{len(rows)} rows, {len(domains)} Mach stations, beta=-90..90 degrees; {output}')
