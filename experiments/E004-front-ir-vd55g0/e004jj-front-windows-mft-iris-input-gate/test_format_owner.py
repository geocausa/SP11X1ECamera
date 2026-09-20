#!/usr/bin/env python3
"""E004jj offline/readonly format-owner audit of actual SP11 Windows archive.

These checks establish only documented/source interface bounds. They do not
execute Windows MFT, convert QC10C, open camera/video devices, or authorize
physical front ISP writes.
"""
from pathlib import Path
import hashlib,json,subprocess,unittest

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
KERNEL=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src")
ARCHIVE=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
MFT=ARCHIVE/"surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"
HOLDER=REPO/"experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-vfe1-cgc-cold-path/HOLDER-SUCCESS.txt"
VDEC=KERNEL/"drivers/media/platform/qcom/iris/iris_vdec.c"
GEN2=KERNEL/"drivers/media/platform/qcom/iris/iris_platform_gen2.c"
CONTRACT=REPO/"src/front-imx681/desktop-output-contract.json"
MFT_SHA="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
HOLDER_SHA="c3482698b31668771a8ad531455cd03b31e26793063415a9df0444cae8707d02"

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class FormatOwnership(unittest.TestCase):
    def test_pinned_same_machine_windows_mft_binary_and_custom_winrt_holder(self):
        self.assertEqual(sha(MFT),MFT_SHA)
        self.assertEqual(sha(HOLDER),HOLDER_SHA)
        h=HOLDER.read_text()
        self.assertIn("E003H_SOURCE device=Surface Camera Front kind=Color stream=VideoRecord fmt=NV12 dims=1920x1080",h)
        self.assertIn("E003H_READER_CREATED",h)
        self.assertIn("E003H_START_STATUS=Success",h)
        # Holder contains neither frame hash nor proof of conversion origin.
        self.assertNotIn("E003H_PIXEL_BYTE_MATCH",h)

    def test_actual_windows_device_mft_contains_both_format_classes(self):
        r=subprocess.run(["strings","-a","-el","-n","6",str(MFT)],
                         capture_output=True,text=True,timeout=26,check=True)
        raw=r.stdout
        self.assertIn("IMAGE_FORMAT_LINEAR_NV12",raw)
        self.assertIn("IMAGE_FORMAT_UBWC_TP_10",raw)
        self.assertIn("UBWCTP10",raw)
        # Co-resident strings cannot prove which component converts pixels.
        self.assertNotIn("WINRT_QC10C_TO_NV12_OWNER_PROVEN",raw)
        lines=raw.splitlines()
        linear=next(i for i,line in enumerate(lines) if "regOut->format == IMAGE_FORMAT_INVALID || regOut->format == IMAGE_FORMAT_LINEAR_NV12" in line)
        tp10=next(i for i,line in enumerate(lines) if "(format != IMAGE_FORMAT_UBWC_NV12_4R) && (format != IMAGE_FORMAT_UBWC_TP_10)" in line)
        self.assertIn("bpsStripingLib.c",lines[linear+1])
        self.assertIn("ipestripingmanagerwrapper.c",lines[tp10+1])

    def test_installed_iris_vdec_input_is_encoded_bitstream_not_qc10c(self):
        gen=GEN2.read_text()
        block=gen.split("static struct iris_fmt platform_fmts_sm8550_dec[] =",1)[1].split("};",1)[0]
        for fmt in ("H264","HEVC","VP9","AV1"):
            self.assertIn("V4L2_PIX_FMT_"+fmt,block)
        self.assertEqual(block.count("V4L2_BUF_TYPE_VIDEO_OUTPUT_MPLANE"),4)
        self.assertNotIn("V4L2_PIX_FMT_QC10C",block)
        vdec=VDEC.read_text()
        cap=vdec.split("static const struct iris_fmt iris_vdec_formats_cap[] =",1)[1].split("};",1)[0]
        self.assertIn("V4L2_PIX_FMT_NV12",cap)
        self.assertIn("V4L2_PIX_FMT_QC08C",cap)
        self.assertNotIn("V4L2_PIX_FMT_QC10C",cap)
        self.assertIn("case V4L2_BUF_TYPE_VIDEO_OUTPUT_MPLANE:",vdec)
        self.assertIn("fmt = inst->core->iris_platform_data->inst_iris_fmts;",vdec)

    def test_front_ubwc_four_region_contract_is_not_encoded_video_or_linear(self):
        p=json.loads(CONTRACT.read_text())
        self.assertEqual(p["v4l2_fourcc"],"Q10C")
        self.assertTrue(p["pixel_semantics"].startswith("ISP-processed 10-bit YUV420"))
        self.assertEqual(p["allocation_bytes"],7778304)
        self.assertEqual([x["name"] for x in p["regions"]],
                         ["Y_META","Y_TP10","C_META","C_TP10"])
        self.assertFalse(p["raw_bayer"])
        self.assertFalse(p["linear_nv12"])
        self.assertFalse(p["desktop_conversion_proven"])
        self.assertFalse(p["drm_import_mapping_proven"])

    def test_only_explicit_converted_image_or_validated_linear_isp_can_clear_gate(self):
        gate=json.loads((HERE/"format-route-gate.json").read_text())
        self.assertEqual(gate["status"],"NO_VALIDATED_FRONT_QC10C_TO_APP_NV12")
        self.assertFalse(gate["iris_bitstream_vdec_accepts_raw_qc10c_input"])
        self.assertFalse(gate["windows_mft_nv12_conversion_owner_proven"])
        self.assertFalse(gate["current_turnip_10bit_multiplanar_modifier_available"])
        self.assertFalse(gate["physical_front_nv12_app_frames_proven"])
        self.assertFalse(gate["safe_sp11_linear_isp_register_state_transition_proven"])
        self.assertTrue(gate["require_independent_decoded_image_oracle"])

if __name__=="__main__":unittest.main(verbosity=2)
