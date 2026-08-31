#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-vfe1-sp11-active-start-prefix-0057-candidate
BOOT=/boot/sp11-7.1.5-camera-e003h-vfeactive-0057
ENTRY=/etc/grub.d/99u_sp11_camera_e003h_vfeactive_0057
ID=sp11-camera-e003h-vfeactive-0057-one-shot
"$NEW/preflight.sh" >/dev/null
[ ! -e "$BOOT" ] || { echo "FAIL: candidate boot directory already exists: $BOOT" >&2; exit 1; }
sudo -n test ! -e "$ENTRY" || { echo "FAIL: candidate GRUB entry already exists: $ENTRY" >&2; exit 1; }
sudo -n mkdir -p "$BOOT"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e003h-vfeactive-0057"
sudo -n cp "$NEW/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb" "$BOOT/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb"
ROOTUUID=$(findmnt -no UUID /)
cat >/tmp/99u_sp11_camera_e003h_vfeactive_0057 <<EOF2
#!/bin/sh
exec tail -n +3 \$0
menuentry 'SP11 Camera E003h — active IFE1 DAL prefix 0057 bounded one-shot' --id '$ID' --class ubuntu --class gnu-linux --class gnu --class os {
 load_video
 set gfxpayload=keep
 insmod gzio
 insmod part_gpt
 insmod ext2
 insmod fdt
 search --no-floppy --fs-uuid --set=root $ROOTUUID
 devicetree $BOOT/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb
 linux $BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+ root=UUID=$ROOTUUID ro cma=128M efi=noruntime quiet splash console=tty0 modprobe.blacklist=qcom_camss,imx681,ov13858 firmware_class.path=$NEW/firmware sp11_entry=7.1.5-sp11-camera-e003h-vfeactive-0057 sp11_camera_e003h_vfeactive_0057=1
 initrd $BOOT/initrd.img-7.1.5-sp11-camera-e003h-vfeactive-0057
}
EOF2
sudo -n install -m 0755 /tmp/99u_sp11_camera_e003h_vfeactive_0057 "$ENTRY"
sudo -n update-grub >/dev/null
ENV=$(grub-editenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || { echo 'FAIL: saved_entry changed' >&2; exit 1; }
if grep -q '^next_entry=.' <<<"$ENV"; then echo 'FAIL: installer unexpectedly armed next_entry' >&2; exit 1; fi
sha256sum "$BOOT"/*
echo "PASS: installed fresh candidate $ID; next_entry intentionally empty"
