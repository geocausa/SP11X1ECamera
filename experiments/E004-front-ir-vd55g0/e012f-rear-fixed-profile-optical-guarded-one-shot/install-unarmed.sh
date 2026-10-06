#!/usr/bin/env bash
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean
H=$R/experiments/E004-front-ir-vd55g0/e012f-rear-fixed-profile-optical-guarded-one-shot
D=/var/lib/sp11-camera-e012f
BOOT=/boot/sp11-7.1.5-camera-e012f-rgb-product
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e012f
ID=sp11-camera-e012f-rear-fixed-profile-optical
KERNEL_SOURCE=/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src
KERNEL_BUILD=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
LOOPROOT=/tmp/sp11-e012c-loopback-build
LOOPDEBSHA=86ec85e00c29dd46b70147e509dd164a382f10931b1adc51ce0ffce6030387c7
LOOPSHA=e53a1474db7e9bea5e68006e5a3163ff487a747bb08e6688e5ad31230180370f
cd "$R"
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
for p in "$D" "$BOOT" "$ENTRY"; do sudo -n test ! -e "$p"; done
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
sudo -n "$R/src/sp11-camera-stack/rgb/product/verify-unactivated.py"
[[ "$(sudo -n sha256sum /var/lib/sp11-camera-stack/installed-camera-stack-manifest.sha256|awk '{print $1}')" == 633b23ebad2b7f8085ed078c412dedcf68274506d336bc658fbc377f67ced36d ]]
# Rebuild exact accepted camera authority without loading or opening it.
rm -rf /tmp/sp11-e012f-hardware-install
KERNEL_SOURCE="$KERNEL_SOURCE" KERNEL_BUILD="$KERNEL_BUILD" \
  "$R/src/sp11-camera-stack/build-hardware-authority.sh" /tmp/sp11-e012f-hardware-install >/tmp/e012f-hardware-install.txt
# Deterministic loopback build from the Ubuntu source package, also camera-free.
rm -rf "$LOOPROOT"; mkdir -p "$LOOPROOT"; cd "$LOOPROOT"
apt-get download v4l2loopback-dkms >/tmp/e012f-loopback-download.txt 2>&1
DEB=$(ls v4l2loopback-dkms_0.15.3-1ubuntu2_all.deb)
[[ "$(sha256sum "$DEB"|awk '{print $1}')" == "$LOOPDEBSHA" ]]
dpkg-deb -x "$DEB" root
make -C root/usr/src/v4l2loopback-0.15.3 KERNEL_DIR="$KERNEL_BUILD" v4l2loopback.ko -j4 >/tmp/e012f-loopback-build.txt
LOOP=$LOOPROOT/root/usr/src/v4l2loopback-0.15.3/v4l2loopback.ko
[[ "$(sha256sum "$LOOP"|awk '{print $1}')" == "$LOOPSHA" ]]
[[ "$(modinfo -F vermagic "$LOOP")" == '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ]]
cd "$R"
# Root-private candidate assets.
sudo -n install -d -m 0700 "$D" "$D/modules" "$D/helpers"
for m in qcom-camss imx681 ov13858 sp11-vd55g0; do sudo -n install -m 0600 "/tmp/sp11-e012f-hardware-install/modules/$m.ko" "$D/modules/$m.ko"; done
sudo -n install -m 0600 "$LOOP" "$D/modules/v4l2loopback.ko"
sudo -n install -m 0600 "$R/experiments/E004-front-ir-vd55g0/e004jr-media-graph-diagnostic/camera-media-graph-diagnostic.py" "$D/helpers/camera-media-graph-diagnostic.py"
sudo -n install -m 0600 "$R/experiments/E004-front-ir-vd55g0/e004ne-screen-rear-stable-window-guarded-one-shot/discover-unified.py" "$D/helpers/discover-unified.py"
for f in live-prep.sh capture-optical.sh return-golden.sh rear-profile.py; do sudo -n install -m 0700 "$H/$f" "$D/$f"; done
printf '%s\n' "$(git rev-parse HEAD)" | sudo -n tee "$D/EXPECTED-HEAD" >/dev/null
sudo -n chmod 0600 "$D/EXPECTED-HEAD"
( cd /tmp/sp11-e012f-hardware-install && sha256sum -c HARDWARE-MANIFEST.sha256 >/dev/null )
# Dedicated boot assets: same Golden kernel/initrd, unified accepted camera DTB.
sudo -n install -d -m 0755 "$BOOT"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-fullio-v19c"
sudo -n install -m 0644 /tmp/sp11-e012f-hardware-install/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb "$BOOT/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb"
cat > /tmp/99zzzzzz_sp11_camera_e012f <<'GRUB'
#!/bin/sh
exec tail -n +3 $0
menuentry 'SP11 Camera E012F — rear fixed-profile optical' --id 'sp11-camera-e012f-rear-fixed-profile-optical' --class ubuntu --class gnu-linux --class gnu --class os {
 load_video
 set gfxpayload=keep
 insmod gzio
 insmod part_gpt
 insmod ext2
 insmod fdt
 search --no-floppy --fs-uuid --set=root 33e842b7-0434-4749-b03a-299bdcdb8b9f
 devicetree /boot/sp11-7.1.5-camera-e012f-rgb-product/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb
 linux /boot/sp11-7.1.5-camera-e012f-rgb-product/vmlinuz-7.1.5-sp11-render-parity-v4+ root=UUID=33e842b7-0434-4749-b03a-299bdcdb8b9f ro clk_ignore_unused pd_ignore_unused cma=128M efi=noruntime quiet splash console=tty0 crashkernel=2G-4G:320M,4G-32G:512M,32G-64G:1024M,64G-128G:2048M,128G-:4096M mshw0485_touch.windows_init_parity=1 mshw0485_touch.parity_linux_power=1 mshw0485_touch.windows_read_cadence=1 mshw0485_touch.parity_display_bitmap=1 mshw0485_touch.parity_stitching_flag=0 mshw0485_touch.parity_hinge_angle=400 mshw0485_touch.parity_fast_host_id=400 mshw0485_touch.parity_report56_identity=0xbc,0xe6,0x4a,0x2e,0x86,0x78 mshw0485_touch.parity_report56_flag=0 mshw0485_touch.parity_cfu_inventory=1 mshw0485_touch.parity_cfu_offer=0x00,0x00,0x12,0x00,0x89,0x14,0x00,0x3f,0xff,0xff,0xff,0xff,0x04,0x04,0x75,0x00 mshw0485_touch.parity_heat_input=1 mshw0485_touch.behavior_v2=1 mshw0485_touch.host_fault_recovery=1 mshw0485_touch.ready_quiesce=1 sp11_cps_parity_v2=1 sp11_cps_v3=1 sp11_volume_transaction=1 sp11_softpause=1 sp11_headroom_link=1 sp11_wsa_clockstop=1 sp11_visense_parity=1 sp11_wsa_windows_init=1 sp11_wsa_macro0db_oracle=1 sp11_wsa_winproducer_nohd2_v3=1 sp11_wsa_csren0_v4=1 sp11_wsa_csren0_v5_idlegated=1 sp11_wsa_windows_3state_v26=1 sp11_wsa_windows_3state_retain_v27=1 sp11_wsa_dp2_offsetctrl2_v28=1 soundwire_qcom.sp11_feedback_active_offset2_zero=1 soundwire_qcom.sp11_cps_pcm_route_105c=1 sp11_entry=7.1.5-sp11-camera-rgb-product modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0 sp11_camera_rgb_product=1
 initrd /boot/sp11-7.1.5-camera-e012f-rgb-product/initrd.img-7.1.5-sp11-fullio-v19c
}
GRUB
chmod 0755 /tmp/99zzzzzz_sp11_camera_e012f
tail -n +3 /tmp/99zzzzzz_sp11_camera_e012f | grub-script-check
sudo -n install -m 0755 /tmp/99zzzzzz_sp11_camera_e012f "$ENTRY"
sudo -n update-grub >/tmp/e012f-update-grub.txt
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
printf 'installed_at=%s\nhead=%s\nloopback_sha256=%s\n' "$(date -Is)" "$(git rev-parse HEAD)" "$LOOPSHA" | sudo -n tee "$D/INSTALL-STATE" >/dev/null
sudo -n chmod 0600 "$D/INSTALL-STATE"
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
echo E012F_INSTALL_UNARMED=PASS CAMERA_STARTED=NO REBOOT_ARMED=NO
