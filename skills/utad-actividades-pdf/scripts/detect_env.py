#!/usr/bin/env python3
"""Print what this Windows + VirtualBox environment can do for a UTAD activity PDF.

Usage: python detect_env.py
Exit code is always 0; read the report.
"""
import json
import os
import shutil
import subprocess
import sys


def find_vboxmanage():
    """Locate VBoxManage executable on PATH or standard Windows install paths."""
    found = shutil.which("VBoxManage") or shutil.which("VBoxManage.exe")
    if found:
        return found
    candidates = []
    for env_var in ("VBOX_MSI_INSTALL_PATH", "VBOX_INSTALL_PATH"):
        base = os.environ.get(env_var)
        if base:
            candidates.append(os.path.join(base, "VBoxManage.exe"))
    for prog_var in ("ProgramFiles", "ProgramFiles(x86)"):
        base = os.environ.get(prog_var)
        if base:
            candidates.append(os.path.join(base, "Oracle", "VirtualBox", "VBoxManage.exe"))
    candidates.append(r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe")
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def find_first(*names_or_paths):
    """Return existing executables/paths from command names or absolute Windows paths."""
    hits = []
    for item in names_or_paths:
        if os.path.sep in item or "/" in item:
            if os.path.exists(item):
                hits.append(item)
        else:
            p = shutil.which(item)
            if p:
                hits.append(p)
    return hits


def py_mods():
    out = {}
    for m in ("reportlab", "PIL", "pymupdf", "docx", "win32com", "yaml"):
        try:
            __import__(m)
            out[m] = True
        except Exception:
            out[m] = False
    return out


def vms():
    report = {}
    vbox = find_vboxmanage()
    if vbox:
        report["VBoxManage_path"] = vbox
        for key, args in (("vbox_vms", ["list", "vms"]),
                          ("vbox_running", ["list", "runningvms"])):
            try:
                r = subprocess.run([vbox] + args, capture_output=True, text=True, timeout=20)
                report[key] = [l.strip() for l in (r.stdout or "").splitlines() if l.strip()]
            except Exception as e:
                report[key] = "error: %r" % e

    for cli, args in (("vmrun", ["list"]), ("multipass", ["list"]), ("wsl", ["-l", "-q"])):
        if shutil.which(cli):
            try:
                r = subprocess.run([cli] + args, capture_output=True, timeout=20)
                raw = r.stdout or r.stderr or b""
                txt = raw.decode("utf-16-le", errors="replace") if cli == "wsl" and b"\x00" in raw else raw.decode("utf-8", errors="replace")
                report[cli] = [l.strip() for l in txt.splitlines() if l.strip()][:8]
            except Exception as e:
                report[cli] = "error: %r" % e
    return report


def main():
    print("== python ==")
    print(sys.version.split()[0], sys.executable)
    mods = py_mods()
    print(json.dumps(mods, indent=2))

    print("== build and QA tools ==")
    print("pandoc:", find_first("pandoc"))
    print("libreoffice:", find_first("libreoffice", "soffice",
                                     r"C:\Program Files\LibreOffice\program\soffice.exe"))
    print("browsers:", find_first(
        "chrome", "msedge",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ))
    print("wkhtmltopdf/weasyprint:", find_first("wkhtmltopdf", "weasyprint"))
    print("pdf->png:", find_first("pdftoppm", "gswin64c", "gs"))
    print("image tooling:", find_first("magick"))

    print("== virtual machines ==")
    v = vms()
    print(json.dumps(v, indent=2, ensure_ascii=False) if v else "no hypervisor CLI found")

    print("== verdict ==")
    if mods.get("reportlab") and mods.get("PIL"):
        print("build: reportlab (preferred)")
    elif find_first("wkhtmltopdf",
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"):
        print("build: HTML -> PDF")
    elif mods.get("win32com") or find_first("libreoffice", "soffice",
                                            r"C:\Program Files\LibreOffice\program\soffice.exe"):
        print("build: DOCX -> Word/LibreOffice")
    else:
        print("build: hand-rolled PDF or Markdown to the user")

    if v.get("vbox_vms"):
        running = len(v.get("vbox_running") or [])
        print("evidence: VirtualBox available (%d VM(s), %d running)" % (len(v["vbox_vms"]), running))
    elif v:
        print("evidence: other hypervisor/WSL present, adapt the commands")
    else:
        print("evidence: none here, use user captures or placeholders")

    if mods.get("pymupdf") or find_first("pdftoppm", "gswin64c", "gs"):
        print("QA: can render pages to PNG")
    else:
        print("QA: open the PDF manually before delivering")


if __name__ == "__main__":
    main()
