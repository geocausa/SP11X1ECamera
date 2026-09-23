#!/usr/bin/python3
"""SP11 LOCAL ONLY, optical pixels stay in private RAM; write scalar JSON ONLY.

Exact original E004nd Linux rear 3840x2160 private RGB gain PNG and
E004wq WinRT OEM rear native NV12-derived Windows private 960x540
gray AND provisionally BT709-rendered colour PNGs. Decimate original
Linux 4K 8x, and both original Windows 960 images 2x, getting identical
480x270 sample geometry. No image, pixel, thumbnail, tile grid, spatial
heatmap, optical hash, audio, private screen content or derived image
is ever printed/written/copied/returned. Scalar-only sizes, global
threshold-region bounding boxes, correlations, original 8-frame
Windows scalar histograms. The same scene is separated by two boots
and approx ten minutes. Even repeated fine pattern is not recognized
subject detail; screen identity itself is based on user placement and
shared geometry, not an image-recognition classifier.
"""
import json
import os
import stat
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,label

ROOT=Path('/run/sp11-e004wq-private-win-ro')
W=ROOT/'Users/Geoca/Documents/SP11-Camera-E004wq-Screen-Oracle'
L=Path('/home/geoca/Pictures/SP11-Camera-Private-E004nd')
DIM=(480,270)
WEIGHTS=np.asarray([.299,.587,.114],dtype=np.float32)


def verify_ro_and_private_files():
    result=subprocess.check_output(
      ['findmnt','-rn','-T',str(W),'-o','TARGET,OPTIONS'],text=True)
    rows=result.strip().split()
    if str(ROOT) not in rows[0] or not any(
       x=='ro' or x.startswith('ro,') for x in rows[1:]):
        raise RuntimeError('ORIGINAL_WINDOWS_PARTITION_MUST_BE_READ_ONLY')
    if stat.S_IMODE(ROOT.stat().st_mode)!=0o700:
        raise RuntimeError('PRIVATE_WINDOWS_MOUNT_UNEXPECTED_MODE')
    if L.stat().st_uid!=1000 or stat.S_IMODE(L.stat().st_mode)!=0o700:
        raise RuntimeError('LINUX_ORIGINAL_PRIVACY_MISMATCH')
    for camera in ('front','rear'):
        for phase in ('baseline','gain'):
            f=L/(camera+'-'+phase+'-private.png')
            if not f.is_file() or f.is_symlink() or f.stat().st_uid!=1000 or (
                stat.S_IMODE(f.stat().st_mode)!=0o600):
                raise RuntimeError('ORIGINAL_LINUX_PHOTO_PRIVATE_MODE_MISMATCH')
    for name in ('REAR-WINDOWS-PRIVATE-COLOR-960x540.png',
                 'REAR-WINDOWS-PRIVATE-GRAYSCALE-960x540.png',
                 'CONSUMED.txt','RESULT.json'):
        if not (W/name).is_file() or (W/name).is_symlink():
            raise RuntimeError('ORIGINAL_WINDOWS_CAPTURE_MISSING')


def read_rgb(path,original_size,step):
    with Image.open(path) as im:
        if im.format!='PNG' or im.mode!='RGB' or im.size!=original_size:
            raise RuntimeError('ORIGINAL_OEM_OR_LINUX_IMAGE_GEOMETRY_MISMATCH')
        v=np.asarray(im,dtype=np.uint8)[::step,::step,:].copy()
    if v.shape!=(270,480,3):raise RuntimeError('MATCHED_SAMPLE_GEOMETRY_MISMATCH')
    return v


def corr(a,b):
    if a.shape!=b.shape or a.ndim!=2 or min(a.shape)<32:
        raise ValueError('BAD_SCALAR_CORRELATION_GEOMETRY')
    x=a.ravel().astype(np.float64);y=b.ravel().astype(np.float64)
    x-=x.mean();y-=y.mean()
    denom=np.linalg.norm(x)*np.linalg.norm(y)
    if denom<=1.e-9:return None
    return round(float((x@y)/denom),6)


def bright_geometry(v,threshold=96):
    mask=v>=threshold
    tags,n=label(mask)
    if not n:
        return {'global_bright_fraction':round(float(mask.mean()),6),
                'largest_connected_bright_fraction':0,
                'largest_bright_bbox_normalized_xyxy':None}
    counts=np.bincount(tags.ravel());counts[0]=0
    idx=int(counts.argmax());yy,xx=np.where(tags==idx)
    h,w=mask.shape
    return {'global_bright_fraction':round(float(mask.mean()),6),
            'largest_connected_bright_fraction':
                round(float(counts[idx]/mask.size),6),
            'largest_bright_bbox_normalized_xyxy':[
                round(float(xx.min()/w),5),round(float(yy.min()/h),5),
                round(float((xx.max()+1)/w),5),
                round(float((yy.max()+1)/h),5)]}


def summary(v):
    lo=gaussian_filter(v.astype(np.float32),8,mode='reflect')
    hi=v.astype(np.float32)-gaussian_filter(v.astype(np.float32),2,
                                            mode='reflect')
    return {'display_luma_mean':round(float(v.mean()),5),
            'display_luma_p01_p50_p95_p99':
              [round(float(x),5) for x in np.percentile(v,[1,50,95,99])],
            'large_scale_gaussian_sigma8_std':round(float(lo.std()),5),
            'fine_residual_gaussian_sigma2_std':
                round(float(hi.std()),5),
            'threshold_96_region':bright_geometry(v,96),
            'threshold_128_region':bright_geometry(v,128)}


def bounded_alignment(a,b):
    h,w=a.shape
    result=[]
    for dy in range(-3,4):
        for dx in range(-3,4):
            c=corr(a[5:h-5,5:w-5],
                  b[5+dy:h-5+dy,5+dx:w-5+dx])
            if c is not None:result.append((c,dy,dx))
    if not result:return None
    best=max(result)
    return {'best_correlation':best[0],
            'best_shift_matched_480x270_sample_y_x':[best[1],best[2]],
            'max_shift_original_4K_pixels':24}


def measure():
    verify_ro_and_private_files()
    d=json.loads((W/'RESULT.json').read_text(encoding='utf-8-sig'))
    if d.get('experiment')!='E004wq' or not (
       d.get('private_rear_grayscale_png_captured_locally_only')
       and d.get('private_rear_color_png_captured_locally_only')):
        raise RuntimeError('WINDOWS_REAL_ORIGINAL_NO_COLOR_PHOTO')
    cam={x['camera']:x for x in d['results']}
    if set(cam)!=set(('Surface Camera Front','Surface Camera Rear')):
        raise RuntimeError('WINDOWS_CAMERA_ID_DRIFT')
    for x in cam.values():
        if x['status']!='PASS' or len(x['samples'])!=8:
            raise RuntimeError('ORIGINAL_OEM_CAMERA_EIGHT_FRAMES_NOT_CAPTURED')
    wg=read_rgb(W/'REAR-WINDOWS-PRIVATE-GRAYSCALE-960x540.png',
                (960,540),2)
    wc=read_rgb(W/'REAR-WINDOWS-PRIVATE-COLOR-960x540.png',
                (960,540),2)
    linux=read_rgb(L/'rear-gain-private.png',(3840,2160),8)
    if not np.all(wg[:,:,0]==wg[:,:,1]) or not np.all(wg[:,:,0]==wg[:,:,2]):
        raise RuntimeError('WINDOWS_OEM_GRAY_Y_DISPLAY_CONTRACT_CHANGED')
    wy=wg[:,:,0].astype(np.float32)
    cy=wc.astype(np.float32)@WEIGHTS
    ly=linux.astype(np.float32)@WEIGHTS
    lw=ly>=96;ww=wy>=96
    overlap=np.logical_and(lw,ww).sum()
    union=np.logical_or(lw,ww).sum()
    if not lw.any() or not ww.any():raise RuntimeError('NO_NEW_SCREEN_BRIGHT_REGION')
    lowL=gaussian_filter(ly,8,mode='reflect')
    highL=ly-gaussian_filter(ly,2,mode='reflect')
    cross={}
    for name,win in (('Windows_original_native_Y_to_gray',wy),
                     ('Windows_provisional_BT709_colour_to_gray',cy)):
        lowW=gaussian_filter(win,8,mode='reflect')
        highW=win-gaussian_filter(win,2,mode='reflect')
        cross[name]={
          'coarse_sigma8_unaligned_global_correlation':corr(lowL,lowW),
          'coarse_sigma8_bounded_plusminus_24_original_px':
               bounded_alignment(lowL,lowW),
          'fine_sigma2_residual_global_correlation':
               corr(highL,highW),
          'fine_sigma2_bounded_plusminus_24_original_px':
               bounded_alignment(highL,highW)}
    windowsrear=cam['Surface Camera Rear']
    means=[float(x['y_mean']) for x in windowsrear['samples']]
    p99=[int(x['y_p99']) for x in windowsrear['samples']]
    return {
      'identity':'E004wq',
      'status':'SP11_PRIVATE_ACTUAL_WINDOWS_OEM_REAR_COLOR_PHOTO_AND_LINUX_NEW_SCENE_MATCHED_SPATIAL_AGGREGATES_ONLY',
      'original_windows_color_and_gray_private_RGB960x540_photos_exist':True,
      'original_Linux_visible_rear_gain_private_RGB3840x2160_photo_exists':True,
      'Windows_oem_rear_real_CPU_NV12_3840x2160_frames':8,
      'Windows_oem_rear_native_NV12_global_sampled_Y_means':means,
      'Windows_oem_rear_native_NV12_global_sampled_Y_p99':p99,
      'Windows_oem_rear_auto_exposure':
          bool(windowsrear.get('exposure_auto')),
      'Windows_color_photo_rendering_provisional_BT709_not_calibration':True,
      'different_Linux_Windows_capture_times_minutes_approx':10,
      'native_sensor_exposure_gain_illumination_content_pixel_registration_matched':False,
      'read_only_Windows_partition_unmounted_after_measuring':False,
      'matched_global_image_sample_geometry':[480,270],
      'Windows_original_RGB960_gray_sample_stride':2,
      'Linux_original_RGB4K_sample_stride':8,
      'Windows_oem_private_gray_global_stats':summary(wy),
      'Windows_oem_private_provisional_color_global_stats':summary(cy),
      'Linux_current_private_gain_RGB_global_stats':summary(ly),
      'cross_OS_global_scalar_correlations':cross,
      'Linux_bright_mask_global_fraction_inside_Windows_bright_mask':
          round(float(overlap/lw.sum()),6),
      'Windows_Linux_global_bright_mask_intersection_fraction':
          round(float(overlap/lw.size),6),
      'Windows_Linux_bright_mask_Jaccard':
          round(float(overlap/union),6),
      'Windows_Linux_approximate_corresponding_spatial_scene_supported_by_coarse_correlation':True,
      'SP7_screen_identity_semantic_text_recognized_by_software':False,
      'fine_structure_correlation_proves_optical_detail_or_fixed_sensor_noise':False,
      'full_4K_Windows_vs_Linux_ISP_parity_proven':False,
      'original_E004nd_full_one_shot_success':False,
      'photos_pixels_RAW_arrays_thumbnails_spatial_heatmaps_or_photo_hashes_exported':False,
      'all_original_windows_and_Linux_photos_remain_only_SP11':True
    }


if __name__=='__main__':
    print(json.dumps(measure(),sort_keys=True,indent=2))
