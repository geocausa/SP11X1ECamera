#!/bin/sh
# E004gq: reproducible, non-root installation into temporary cache ONLY.
# No cameras, LEDs, PMIC, kernel modules, boot settings or system pip.
set -eu
if [ "$(id -u)" -eq 0 ]; then
    echo "Refusing root/system-level installation." >&2
    exit 2
fi
umask 077
cache=/tmp/sp11-camera-face-20260919
venv=/tmp/sp11-camera-face-venv-20260919
mkdir -p "$cache"
python3 -m venv --system-site-packages "$venv"
"$venv/bin/python" -m pip install --disable-pip-version-check --no-input --no-deps --only-binary=:all: opencv-python-headless==4.12.0.88

download_pinned() {
    name=$1
    expected=$2
    url=$3
    dest="$cache/$name"
    if [ -f "$dest" ] && [ ! -L "$dest" ] && [ "$(sha256sum "$dest" | cut -d' ' -f1)" = "$expected" ]; then
        return
    fi
    tmp=$(mktemp "$cache/.download.XXXXXXXX")
    if ! curl -fsSL --retry 2 --max-time 140 "$url" -o "$tmp"; then
        rm -f -- "$tmp"
        echo "Source unavailable: $name" >&2
        exit 3
    fi
    if [ "$(sha256sum "$tmp" | cut -d' ' -f1)" != "$expected" ]; then
        rm -f -- "$tmp"
        echo "Refusing changed upstream asset: $name" >&2
        exit 4
    fi
    if [ -L "$dest" ]; then
        rm -f -- "$dest"
    fi
    mv -f -- "$tmp" "$dest"
}
origin=https://github.com/opencv/opencv_zoo/raw/refs/heads/main/models
download_pinned face_detection_yunet_2023mar.onnx \
    8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4 \
    "$origin/face_detection_yunet/face_detection_yunet_2023mar.onnx"
download_pinned face_recognition_sface_2021dec.onnx \
    0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79 \
    "$origin/face_recognition_sface/face_recognition_sface_2021dec.onnx"
download_pinned largest_selfie.jpg \
    ab8413ad9bb4f53068f4fb63c6747e5989991dd02241c923d5595b614ecf2bf6 \
    "$origin/face_detection_yunet/example_outputs/largest_selfie.jpg"
"$venv/bin/python" -c 'import cv2; assert cv2.__version__ == "4.12.0"'
echo "E004GQ_OFFLINE_DEPENDENCIES=READY VENV_AND_MODELS_IN_TMP_ONLY"
