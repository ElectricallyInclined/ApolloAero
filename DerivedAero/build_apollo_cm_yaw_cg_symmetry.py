"""Build pure-sideslip yaw moment about the c.g. for Apollo CM configuration C.

Uses reviewed NASA TN D-4688 apex Cm and normal-force traces. This is an
axisymmetry-derived engineering model, not measured yaw data. Report axes:
Cn_cg = Cn_apex + 0.685*CY, with x_cg/d=-0.685 and y_cg/d=0.
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

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
parser.add_argument('--output-dir',type=Path)
args=parser.parse_args()
root=args.root.resolve()
out=(args.output_dir or root/'derived').resolve()
source_id='NASA_TN_D_4688_Apollo_Command_Module_Aerodynamic_Characteristics'
output_name='ApolloCM_yaw_cg_symmetry_Figures4to6.csv'
quant=Decimal('0.000001')
arm=Decimal('0.685')

def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fmt(value:Decimal)->str:
    return format(value.normalize(),'f')

def rounded(value:Decimal)->str:
    return fmt(value.quantize(quant,rounding=ROUND_HALF_EVEN))

def norm_facility(value:str)->str:
    return ' '.join(value.replace('JPL-20SWT','JPL-20 SWT').strip().split())

registry=json.loads((root/'DATASETS.json').read_text(encoding='utf-8'))
by_name={Path(item['path']).name:item for item in registry['datasets'] if item['source_id']==source_id}
inputs=[]
rows=[]
domains=[]
basis_counts=Counter()

def load(figure:int,kind:str)->dict[Decimal,dict]:
    name=f'ApolloCM_{"CmApex" if kind=="cm" else "CN"}_Figure{figure}{"a" if kind=="cm" else "c"}.csv'
    entry=by_name[name]
    path=root/entry['path']
    actual=digest(path)
    review=entry['mark_review']
    if actual!=entry['sha256'] or review['status']!='checked_by_mark' or actual!=review['reviewed_sha256']:
        raise ValueError(f'Source modified or not currently reviewed by Mark: {name}')
    inputs.append({'dataset_id':entry['id'],'path':entry['path'],'sha256':actual,
                   'mark_review_status':review['status'],'mark_review_date':review['date']})
    grouped=defaultdict(list)
    with path.open(newline='',encoding='utf-8') as f:
        for item in csv.DictReader(f):
            grouped[Decimal(item['mach'])].append(item)
    result={}
    for mach,items in grouped.items():
        re={Decimal(item['reynolds_number_millions']) for item in items}
        fac={norm_facility(item['facility']) for item in items}
        if len(re)!=1 or len(fac)!=1:
            raise ValueError(f'Inconsistent legend metadata: {name}, M={mach}')
        column='pitching_moment_coefficient_apex' if kind=='cm' else 'normal_force_coefficient'
        values={Decimal(item['angle_of_attack_deg']):Decimal(item[column]) for item in items}
        if len(values)!=len(items) or Decimal(0) not in values:
            raise ValueError(f'Duplicate angles or missing zero angle: {name}, M={mach}')
        result[mach]={'angles':sorted(values),'values':values,'reynolds':next(iter(re)),
                      'facility':next(iter(fac))}
    return result

def value_at(series:dict,alpha:Decimal)->tuple[Decimal,str]:
    values=series['values']
    if alpha in values:
        return values[alpha],'source_point'
    angles=series['angles']
    pos=bisect.bisect_left(angles,alpha)
    if pos==0 or pos==len(angles):
        raise ValueError(f'Extrapolation required at alpha={alpha}')
    left,right=angles[pos-1],angles[pos]
    value=values[left]+(values[right]-values[left])*(alpha-left)/(right-left)
    return value,'linear_angle_interpolation'

for figure in (4,5,6):
    cm_series=load(figure,'cm')
    cn_series=load(figure,'cn')
    if set(cm_series)!=set(cn_series):
        raise ValueError(f'Mach mismatch between Figure {figure}(a) and (c)')
    for mach in sorted(cm_series):
        cm=cm_series[mach]; cn=cn_series[mach]
        if cm['reynolds']!=cn['reynolds']:
            raise ValueError(f'Reynolds mismatch: Figure {figure}, M={mach}')
        facilities={value for value in (cm['facility'],cn['facility']) if value}
        if len(facilities)>1:
            raise ValueError(f'Facility mismatch: Figure {figure}, M={mach}: {facilities}')
        if not (cm['angles'][0]<=0<=90<=cm['angles'][-1] and cn['angles'][0]<=0<=90<=cn['angles'][-1]):
            raise ValueError(f'Source does not cover alpha=0..90: Figure {figure}, M={mach}')
        cm0=cm['values'][Decimal(0)]; cn0=cn['values'][Decimal(0)]
        for beta_int in range(-90,91,5):
            beta=Decimal(beta_int); alpha=abs(beta)
            cm_value,cm_basis=value_at(cm,alpha)
            cn_value,cn_basis=value_at(cn,alpha)
            if cm_basis!='source_point':
                raise ValueError(f'Apex Cm unexpectedly requires interpolation: Figure {figure}, M={mach}, alpha={alpha}')
            basis_counts[cn_basis]+=1
            sign=1 if beta>0 else -1 if beta<0 else 0
            apex_yaw=Decimal(-sign)*(cm_value-cm0)
            cy=Decimal(-sign)*(cn_value-cn0)
            cg_yaw=apex_yaw+arm*cy
            rows.append({
                'mach':fmt(mach),
                'reynolds_number_millions':fmt(cm['reynolds']),
                'beta_deg':fmt(beta),
                'yawing_moment_coefficient_cg':rounded(cg_yaw),
                'yawing_moment_coefficient_apex_recentered':rounded(apex_yaw),
                'side_force_coefficient_symmetry':rounded(cy),
                'source_alpha_deg':fmt(alpha),
                'source_pitching_moment_coefficient_apex':fmt(cm_value),
                'source_normal_force_coefficient':fmt(cn_value),
                'source_cm_apex_zero':fmt(cm0),
                'source_cn_zero':fmt(cn0),
                'normal_force_basis':cn_basis,
                'figure_group':f'Figure {figure}',
                'facility':next(iter(facilities),'')
            })
        domains.append({'figure':figure,'mach':fmt(mach),'beta_min_deg':-90,'beta_max_deg':90,'rows':37})

out.mkdir(parents=True,exist_ok=True)
csv_path=out/output_name
with csv_path.open('w',newline='',encoding='utf-8') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
    writer.writeheader(); writer.writerows(rows)
manifest={
    'name':'Apollo CM configuration-C pure-sideslip yaw-moment coefficient about c.g., symmetry-derived',
    'csv':output_name,
    'csv_sha256':digest(csv_path),
    'row_count':len(rows),
    'mach_station_count':len(domains),
    'source_report':'NASA TN D-4688',
    'source_pdf':f'sources/{source_id}/19680021973.pdf',
    'configuration':'C',
    'reference':'nominal c.g., x/d=-0.685, y/d=0, z/d=0.059 from theoretical apex',
    'flight_condition':'pure sideslip, alpha=0 degrees',
    'beta_domain_deg':[-90,90],
    'beta_spacing_deg':5,
    'method':'For each measured Mach and beta, set a=abs(beta), s=sign(beta). Recenter scanned source curves Cm*=Cm_apex(a)-Cm_apex(0) and CN*=CN(a)-CN(0). Rotational symmetry gives Cn_apex=-s*Cm* and CY=-s*CN*. Shift moment to c.g. using Cn_cg=Cn_apex+0.685*CY. Therefore Cn_cg=-s*(Cm*+0.685*CN*). At beta=0 all inferred lateral quantities are exactly zero. No Mach interpolation or extrapolation. CN is linearly interpolated in alpha within adjacent source points only where its grid does not contain a 5-degree output angle.',
    'normal_force_basis_counts':dict(basis_counts),
    'limitations':'Derived engineering approximation, not measured yaw data. Rotational symmetry assumed for unstraked basic configuration C; valid for pure sideslip at alpha=0 only. Body-axis yaw sign follows Figure 1 of NASA TN D-4688. Source curve zero offsets are removed as a modeling choice. Not valid for nonzero-alpha trim, asymmetric hardware, or without checking simulator axis signs. The c.g. has no specified lateral y offset; a nonzero y offset would add an axial-force moment term.',
    'review_status':'not_checked',
    'review_note':'All six source CSVs are checked by Mark; this new derived c.g. yaw table has not been separately reviewed by Mark.',
    'domains':domains,
    'inputs':inputs,
}
(out/'ApolloCM_yaw_cg_symmetry_Figures4to6_provenance.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(f'{len(rows)} rows, {len(domains)} Mach stations; CN basis {dict(basis_counts)}; {csv_path}')
