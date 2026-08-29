#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
EXP=$REPO/experiments/E003-front-imx681-cphy/e003h-bounded-vfe1-pix-runtime-candidate
BOOT=/boot/sp11-7.1.5-camera-e003h-pix-one-shot
ENTRY=/etc/grub.d/99l_sp11_camera_e003h_pix_one_shot
sudo -n mkdir -p "$BOOT"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e003h-pix-one-shot"
sudo -n cp "$EXP/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb" "$BOOT/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb"
ROOTUUID=$(findmnt -no UUID /)
cat >/tmp/99l_sp11_camera_e003h_pix_one_shot <<EOF
#!/bin/sh
exec tail -n +3 \$0
menuentry 'SP11 Camera E003h — bounded VFE1 PIX one-shot' --id 'sp11-camera-e003h-pix-one-shot' --class ubuntu --class gnu-linux --class gnu --class os {
 load_video
 set gfxpayload=keep
 insmod gzio
 insmod part_gpt
 insmod ext2
 insmod fdt
 search --no-floppy --fs-uuid --set=root $ROOTUUID
 devicetree $BOOT/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb
 linux $BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+ root=UUID=$ROOTUUID ro cma=128M efi=noruntime quiet splash console=tty0 modprobe.blacklist=qcom_camss,imx681,ov13858 firmware_class.path=$EXP/firmware sp11_entry=7.1.5-sp11-camera-e003h-pix-one-shot sp11_camera_e003h_pix_one_shot=1
 initrd $BOOT/initrd.img-7.1.5-sp11-camera-e003h-pix-one-shot
}
EOF
sudo -n install -m 0755 /tmp/99l_sp11_camera_e003h_pix_one_shot "$ENTRY"
sudo -n update-grub >/dev/null
# Do not grub-reboot here.
grub-editenv list
sha256sum "$EXP/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb"
echo 'PASS: disposable PIX boot entry installed; next_entry intentionally not armed'
