#!/usr/bin/env python3
import importlib.util,json,re,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
EF=HERE.parent/'ef-clean-awb-gain-adjust-replay'/'gain_adjust.py'
s=importlib.util.spec_from_file_location('ga',EF); ga=importlib.util.module_from_spec(s); sys.modules['ga']=ga; s.loader.exec_module(ga)
def need(x,m):
    if not x: raise AssertionError(m)
def frombits(h): return struct.unpack('<f',struct.pack('<I',int(h,16)))[0]
def kv(line): return dict(re.findall(r'(\w+)=([0-9A-Fa-f]+)',line))
# Unique float32 calibration reciprocal scales solved from R4's authoritative Windows
# mesh weights, then independently verified unchanged over R5..R11.
CAL_RG_BITS=0x3f80a277; CAL_BG_BITS=0x3f83427b
CAL_RG=frombits(f'{CAL_RG_BITS:08x}'); CAL_BG=frombits(f'{CAL_BG_BITS:08x}')
lines=[x.strip() for x in (HERE/'ORACLE-PAIRS.txt').read_text().splitlines() if x.strip()]
ga_rows=[kv(x) for x in lines if x.startswith('EG_GA ')]
pub_rows=[kv(x) for x in lines if x.startswith('EG_PUB ')]
need(len(ga_rows)==len(pub_rows)==8,'8 paired samples')
t=ga.GainAdjustTuning(); rows=[]
for i,(w,p) in enumerate(zip(ga_rows,pub_rows)):
    need(int(w['n'])==i and int(p['n'])==i,'sequence')
    need(int(p['req'])==i+4,'request label')
    rg,bg,lux,cct=[frombits(w[k]) for k in ('rg','bg','lux','cct')]
    z=ga.adjust(t,rg,bg,lux,cct,CAL_RG,CAL_BG,triangle_hint=int(w['tri']))
    exp_tri=int(w['tri']); exp_vs=[int(w[k]) for k in ('v0','v1','v2')]
    exp_w=[int(w[k],16) for k in ('w0','w1','w2')]
    exp_c=[int(w[k],16) for k in ('cctr','cctg','cctb')]
    exp_a=[int(w[k],16) for k in ('ar','ag','ab')]
    got_w=[ga.bits(x) for x in z['weights']]; got_c=[ga.bits(x) for x in z['cct_rgb']]; got_a=[ga.bits(x) for x in z['final_rgb']]
    need(z['triangle']==exp_tri,f'R{i+4} triangle')
    need(z['vertices']==exp_vs,f'R{i+4} vertices')
    need(got_w==exp_w,f'R{i+4} weights got={got_w} exp={exp_w}')
    need(got_c==exp_c,f'R{i+4} CCT multiplier')
    need(got_a==exp_a,f'R{i+4} GA RGB got={got_a} exp={exp_a}')
    need(int(cct)==int(p['CCT']),f'R{i+4} published CCT')
    ar,ag,ab=z['final_rgb']; need(ga.bits(ag)==0x3f800000,'observed G adjust unity')
    # Windows divides raw decision ratios by GA R/B multipliers, then normalizes gain triplet.
    arg=ga.div(rg,ar); abg=ga.div(bg,ab); M=ga.f32(max(ga.f32(1.0),arg,abg))
    pred=[ga.bits(ga.div(M,arg)),ga.bits(M),ga.bits(ga.div(M,abg))]
    exp_pub=[int(p[k],16) for k in ('R','G','B')]
    need(pred==exp_pub,f'R{i+4} publisher gains got={pred} exp={exp_pub}')
    rows.append({'request':i+4,'triangle':z['triangle'],'mesh_point_bits':z['mesh_point_bits'],
                 'weights_bits':[f'0x{x:08x}' for x in got_w],
                 'ga_bits':[f'0x{x:08x}' for x in got_a],
                 'published_gain_bits':[f'0x{x:08x}' for x in pred],
                 'cct_bits':f'0x{ga.bits(cct):08x}','published_cct':int(p['CCT'])})
out={'schema':'sp11-e003i-eg-windows-awb-gain-adjust-oracle-v1','status':'PASS_8_OF_8_BIT_EXACT',
     'requests':[4,5,6,7,8,9,10,11],
     'runtime_calibration_scale_bits':{'rg':f'0x{CAL_RG_BITS:08x}','bg':f'0x{CAL_BG_BITS:08x}'},
     'ga_core_bit_exact':'8/8','triangle_identity':'8/8','barycentric_weights_bit_exact':'8/8',
     'nested_multiplier_bit_exact':'8/8','ga_final_rgb_bit_exact':'8/8','publisher_rgb_bit_exact':'8/8',
     'publisher_cct_truncation':'8/8',
     'device_mft_sha256':'c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35',
     'tuning_sha256':ga.TUNING_SHA256,
     'windows_full_log_sha256':'2601f5da6d7f87439253ea9315111f43af1fcac386a206771d5e57395cf6ffe9',
     'windows_pairs_sha256_reported':'2f36240441984d38ebfac776128bd1cc620cf6be8b2c1a600e16866b5db48c5a',
     'windows_differential_same_request':True,'contained_triangle_path_proven':True,
     'runtime_calibration_source_linux_bound':False,'out_of_mesh_fallback_proven':False,'continuous_aec':False,
     'rows':rows}
(HERE/'RESULT.json').write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
