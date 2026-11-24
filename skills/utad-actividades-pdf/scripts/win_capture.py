#!/usr/bin/env python3
"""In-guest HiDPI desktop capture for a running VirtualBox Windows VM.

Uses VBoxManage guestcontrol + PowerShell GDI CopyFromScreen (with SetProcessDPIAware).
Useful when you want a native HiDPI capture directly from the guest session; for
normal screenshots, `VBoxManage controlvm <vm> screenshotpng` (default in vm_capture.py)
needs no guest credentials.

Usage:
    python win_capture.py "W-UD2-Sanjurjo" fig/raw_fig2.png --username sanjurjo --password ...
"""
import argparse
import base64
import os
import shutil
import subprocess
import sys

PS_CAPTURE = r"""
$d = Add-Type -MemberDefinition '[DllImport("user32.dll")] public static extern bool SetProcessDPIAware(); [DllImport("user32.dll")] public static extern int GetSystemMetrics(int n);' -Name D -PassThru
$d::SetProcessDPIAware() | Out-Null
$w = $d::GetSystemMetrics(0)
$h = $d::GetSystemMetrics(1)
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap($w, $h)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, [System.Drawing.Size]::new($w, $h))
$ms = New-Object System.IO.MemoryStream
$bmp.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()
[Convert]::ToBase64String($ms.ToArray())
""".strip()


def find_vboxmanage():
    found = shutil.which("VBoxManage") or shutil.which("VBoxManage.exe")
    if found:
        return found
    default = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
    if os.path.isfile(default):
        return default
    sys.exit("win_capture.py: VBoxManage.exe not found")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vm", help="VirtualBox VM name or UUID")
    ap.add_argument("out_path")
    ap.add_argument("--username", default=os.environ.get("VBOX_GUEST_USER"))
    ap.add_argument("--password", default=os.environ.get("VBOX_GUEST_PASS"))
    ap.add_argument("--passwordfile", default=os.environ.get("VBOX_GUEST_PASSFILE"))
    args = ap.parse_args()

    vbox = find_vboxmanage()
    b64_cmd = base64.b64encode(PS_CAPTURE.encode("utf-16le")).decode()
    cmd = [vbox, "guestcontrol", args.vm, "run",
           "--exe", r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"]
    if args.username:
        cmd += ["--username", args.username]
    if args.password:
        cmd += ["--password", args.password]
    elif args.passwordfile:
        cmd += ["--passwordfile", args.passwordfile]
    cmd += ["--", "-NoProfile", "-WindowStyle", "Hidden", "-EncodedCommand", b64_cmd]

    res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if res.returncode != 0:
        sys.stderr.write(res.stderr or res.stdout)
        sys.exit(res.returncode)
    raw = "".join(res.stdout.split())
    png = base64.b64decode(raw)
    if not png.startswith(b"\x89PNG"):
        sys.stderr.write("win_capture.py: unexpected output (not PNG)\n")
        sys.exit(1)
    with open(args.out_path, "wb") as fh:
        fh.write(png)
    print("Captured %s (%d bytes)" % (args.out_path, len(png)))


if __name__ == "__main__":
    main()
