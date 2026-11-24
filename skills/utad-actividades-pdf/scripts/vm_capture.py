#!/usr/bin/env python3
"""Capture and crop a clean terminal screenshot from a VirtualBox VM with retries.

Uses `VBoxManage controlvm <vm> screenshotpng` by default (works for both Linux and
Windows guests without requiring guest credentials), or optionally `win_capture.py`
in-guest GDI capture when `--in-guest` is passed for a Windows VM. Validates and
crops via `crop_capture.py --window`.

Usage:
    python vm_capture.py "U-UD2-Sanjurjo" fig/raw_fig1.png fig/fig1.png
    python vm_capture.py "W-UD2-Sanjurjo" fig/raw_fig2.png fig/fig2.png --attempts 4
"""
import argparse
import os
import shutil
import subprocess
import sys
import time

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def find_vboxmanage():
    found = shutil.which("VBoxManage") or shutil.which("VBoxManage.exe")
    if found:
        return found
    for env_var in ("VBOX_MSI_INSTALL_PATH", "VBOX_INSTALL_PATH"):
        base = os.environ.get(env_var)
        if base:
            p = os.path.join(base, "VBoxManage.exe")
            if os.path.isfile(p):
                return p
    for prog_var in ("ProgramFiles", "ProgramFiles(x86)"):
        base = os.environ.get(prog_var)
        if base:
            p = os.path.join(base, "Oracle", "VirtualBox", "VBoxManage.exe")
            if os.path.isfile(p):
                return p
    default = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
    if os.path.isfile(default):
        return default
    sys.exit("vm_capture.py: VBoxManage.exe not found in PATH or Program Files")


def vm_info(vbox, vm):
    res = subprocess.run([vbox, "showvminfo", vm, "--machinereadable"],
                         capture_output=True, text=True)
    info = {}
    for line in res.stdout.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            info[k.strip()] = v.strip().strip('"')
    return info


def detect_os(info):
    ostype = info.get("ostype", "").lower()
    return "windows" if "win" in ostype else "linux"


def capture_once(vbox, vm, raw_path, os_kind, in_guest=False, user=None, password=None, wake=False):
    if in_guest and os_kind == "windows":
        cmd = [sys.executable, os.path.join(SCRIPTS_DIR, "win_capture.py"), vm, raw_path]
        if user:
            cmd += ["--username", user]
        if password:
            cmd += ["--password", password]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            sys.stderr.write(r.stderr or r.stdout)
            return False
        return True

    if wake:
        # Send Left Shift press (0x2a) + release (0xaa) to wake sleeping guest display.
        subprocess.run(
            [vbox, "controlvm", vm, "keyboardputscancode", "2a", "aa"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        time.sleep(2.0)

    r = subprocess.run([vbox, "controlvm", vm, "screenshotpng", raw_path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr or r.stdout)
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vm", help="VirtualBox VM name or UUID")
    ap.add_argument("raw_out")
    ap.add_argument("crop_out")
    ap.add_argument("--os", choices=("auto", "linux", "windows"), default="auto")
    ap.add_argument("--in-guest", action="store_true",
                    help="use win_capture.py via guestcontrol for Windows VMs")
    ap.add_argument("--username", help="guest username (with --in-guest)")
    ap.add_argument("--password", help="guest password (with --in-guest)")
    ap.add_argument("--attempts", type=int, default=5)
    ap.add_argument("--delay", type=float, default=2.0)
    ap.add_argument("--pad", type=int, default=18)
    args = ap.parse_args()

    vbox = find_vboxmanage()
    info = vm_info(vbox, args.vm)
    state = info.get("VMState", "").lower()
    if state and state != "running":
        sys.stderr.write("vm_capture.py: VM %r is not running (VMState=%s)\n" % (args.vm, state))
        return 1

    os_kind = detect_os(info) if args.os == "auto" else args.os
    os.makedirs(os.path.dirname(os.path.abspath(args.raw_out)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(args.crop_out)), exist_ok=True)
    crop_py = os.path.join(SCRIPTS_DIR, "crop_capture.py")

    for attempt in range(1, args.attempts + 1):
        if capture_once(vbox, args.vm, args.raw_out, os_kind,
                        in_guest=args.in_guest, user=args.username,
                        password=args.password, wake=(attempt > 1)):
            r = subprocess.run(
                [sys.executable, crop_py, args.raw_out, args.crop_out,
                 "--window", "--pad", str(args.pad)],
                capture_output=True, text=True,
            )
            if r.returncode == 0:
                sys.stdout.write(r.stdout)
                return 0
            sys.stderr.write("attempt %d/%d rejected: %s"
                             % (attempt, args.attempts, r.stderr or r.stdout))
        if attempt < args.attempts:
            time.sleep(args.delay)

    sys.stderr.write("vm_capture.py: failed to get a clean %s capture after %d attempts\n"
                     % (os_kind, args.attempts))
    return 1


if __name__ == "__main__":
    sys.exit(main())
