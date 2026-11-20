#!/bin/sh
# HAKO Milestone 1 — read-only Raspberry Pi audit.
# Run ON THE PI:  sh pi-audit-commands.sh
# This script installs nothing, changes no configuration, and prints no secrets.

line() { printf '\n===== %s =====\n' "$1"; }
show() { printf '%-28s ' "$1"; shift; "$@" 2>&1 || printf '(unavailable)\n'; }

line 'IDENTITY / OS / ARCH'
show 'hostname'             hostname
show 'whoami'               whoami
show 'uname -a'             uname -a
show 'uname -m'             uname -m
show 'dpkg --print-arch'    dpkg --print-architecture
show 'os-release'           sh -c 'grep -E "^(ID|VERSION_ID|PRETTY_NAME)=" /etc/os-release'
show 'kernel release'       uname -r
show 'RPi model'            sh -c 'grep -E "^(Model|Hardware|Revision)" /proc/cpuinfo | head -3'

line 'PYTHON / VENV / PIP'
show 'python3 --version'    python3 --version
show 'python3 path'         sh -c 'command -v python3'
show 'venv support'         sh -c 'python3 -c "import venv, ensurepip; print(\"venv+ensurepip OK\")"'
show 'pip --version'        sh -c 'python3 -m pip --version'
show 'vosk import'          sh -c 'python3 -c "import vosk; print(getattr(vosk, \"__version__\", \"imported\"))"'
show 'cffi import'          sh -c 'python3 -c "import cffi; print(cffi.__version__)"'

line 'MEMORY / STORAGE'
show 'free -h'              free -h
show 'df -h /'              df -h /
show 'df -h /home'          df -h /home
show 'swap'                 sh -c 'swapon --show || true'
show 'GPU/ARM mem (Pi)'     sh -c 'vcgencmd get_mem arm 2>/dev/null; vcgencmd get_mem gpu 2>/dev/null; true'

line 'INSTALLABLE PACKAGES (apt metadata only, no install)'
show 'apt policy espeak-ng'     sh -c 'apt-cache policy espeak-ng | head -6'
show 'apt policy alsa-utils'    sh -c 'apt-cache policy alsa-utils | head -6'
show 'apt policy python3-cffi'  sh -c 'apt-cache policy python3-cffi | head -6'
show 'apt policy python3-venv'  sh -c 'apt-cache policy python3-venv | head -6'
show 'installed espeak-ng'      sh -c 'dpkg-query -W -f="${Version}\n" espeak-ng 2>/dev/null || true'
show 'installed vosk (pip)'     sh -c 'python3 -m pip show vosk 2>/dev/null | grep -E "^(Name|Version|Location):" || true'

line 'AUDIO HARDWARE (ALSA)'
show 'aplay -l'             sh -c 'command -v aplay >/dev/null && aplay -l || true'
show 'arecord -l'           sh -c 'command -v arecord >/dev/null && arecord -l || true'
show '/proc/asound/cards'   sh -c 'cat /proc/asound/cards 2>/dev/null || true'
show 'aplay -L (first 40)'  sh -c 'command -v aplay >/dev/null && aplay -L 2>/dev/null | head -40 || true'
show 'USB devices'          sh -c 'command -v lsusb >/dev/null && lsusb || true'
show 'sound modules'        sh -c 'lsmod | grep -E "snd|bcm2835|vc4" || true'
show 'audio config lines'   sh -c 'grep -R -n -E "dtparam=audio|audio_pwm_mode|disable_audio" /boot/firmware/config.txt /boot/config.txt 2>/dev/null || true'

line 'END OF READ-ONLY AUDIT'
printf 'Nothing was installed or changed. Paste the full output to the developer.\n'
