<img src="assets/icon.svg" width="64" height="64" alt="">

# utad-actividades-pdf

Antigravity plugin and skill (`utad-actividades-pdf`) for generating UTAD *Sistemas Operativos* and *Fundamentos de Hardware* activity PDFs on **Windows** with **Oracle VirtualBox** (`VBoxManage.exe`) screenshots and **Gonzalo Sanjurjo**'s cover template (`ASIR 1º GRUPO A`).

## Contents

- `plugin.json`: Antigravity plugin manifest.
- `skills/utad-actividades-pdf/`: Skill instructions (`SKILL.md`), references, cover asset (`assets/cover-reference.png`), and capture/QA scripts (`vm_capture.py`, `win_capture.py`, `crop_capture.py`, `check_doc.py`, `check_pdf.py`, `check_numbers.py`, `render_pages.py`, `detect_env.py`).

## Environment

- **Host**: Windows 10/11 with Python 3 (`reportlab`, `Pillow`, `pymupdf`)
- **Hypervisor**: Oracle VirtualBox (`VBoxManage.exe` via `PATH` or `C:\Program Files\Oracle\VirtualBox\VBoxManage.exe`)
- **Author**: Gonzalo Sanjurjo (`ASIR 1º GRUPO A`)

## Install / Validate

```powershell
agy plugin install https://github.com/sanjurjogon-crypto/utad-actividades-pdf
```

Or validate locally:

```powershell
agy plugin validate --strict .
```
