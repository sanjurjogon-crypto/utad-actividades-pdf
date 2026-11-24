# Environment adaptivity (Windows + VirtualBox)

The artefact never changes: Gonzalo Sanjurjo's cover (`Plantilla Trabajos.docx`), plain Spanish,
real evidence, same layout. What changes is how the evidence is obtained and how the PDF is
produced.

## 1. Detect before you promise anything

Run `python scripts/detect_env.py`, or check by hand in PowerShell:

```powershell
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" --version
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" list vms
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" list runningvms
python -c "
for m in ('reportlab','PIL','pymupdf','docx','win32com'):
    try: __import__(m); print(m, 'ok')
    except Exception: print(m, 'missing')
"
```

## 2. The ladder

| Rung | Evidence | Build | QA |
| --- | --- | --- | --- |
| 5 — Windows + VirtualBox + Python libs | `VBoxManage` / SSH captures, cropped | reportlab, `references/pdf-builder-template.py` | `scripts/render_pages.py` + look at every page |
| 4 — Other hypervisor (VMware/WSL/Hyper-V) + reportlab | same, adapted CLI | same | same |
| 3 — reportlab, no VM | host commands if the statement allows; otherwise user captures | same | same |
| 2 — no reportlab | user captures or host commands | HTML + headless Edge/Chrome / `wkhtmltopdf`; or DOCX + Word COM / `soffice --convert-to pdf` | open the PDF and look |
| 1 — text only | user captures | Markdown/HTML/DOCX handed to the user with instructions to print | none |
| 0 — web chat, no tools | placeholders + exact commands | Markdown or HTML in the answer | none |

Never jump up a rung: if the machine has no VM, do not write “he ejecutado en la VM”.

## 3. Fallbacks in detail

### PDF without reportlab

**HTML → PDF (preferred on Windows).** Write a single `doc.html` with print CSS that reproduces
the layout: A4, `@page { size: A4; margin: 22mm }`, Arial/Helvetica, 10 pt/14, justified, figures
`max-width:100%`, caption 8 pt italic `#333`, tables with `border-collapse:collapse` and 0.4 pt
`#999` borders, cover as a first page reproducing `Plantilla Trabajos.docx`. Then:

```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless --disable-gpu `
  --print-to-pdf=out.pdf --no-pdf-header-footer "file:///C:/abs/path/doc.html"
# or Chrome:
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless --disable-gpu `
  --print-to-pdf=out.pdf --no-pdf-header-footer "file:///C:/abs/path/doc.html"
# or wkhtmltopdf:
wkhtmltopdf --enable-local-file-access doc.html out.pdf
```

**Microsoft Word COM / LibreOffice.** Build a DOCX with `python-docx` starting from
`Plantilla Trabajos.docx` (or from scratch), then convert via Word COM (`win32com.client`
`SaveAs(..., FileFormat=17)`) or `soffice --headless --convert-to pdf doc.docx`.

**LaTeX.** Only if a LaTeX toolchain (`xelatex` / `pdflatex`) exists; keep the same geometry
(`geometry` 22 mm, Helvetica/Arial, `\pagestyle{empty}`).

### Images without Pillow

- Cropping: `magick in.png -crop WxH+X+Y out.png` (ImageMagick) or System.Drawing in PowerShell.
- If nothing can crop, place the raw capture and reduce its width in the layout; legibility
  suffers, the document still ships.

### Rendering for QA without PyMuPDF

- Poppler on Windows: `pdftoppm -png -r 100 doc.pdf page`.
- Ghostscript: `gswin64c -sDEVICE=png16m -r100 -o page-%d.png doc.pdf`.
- If none exist, open the PDF in Edge/Chrome/Acrobat and inspect page by page before delivering;
  do not skip the visual check.

### No VM but the statement demands one

Two acceptable paths:

1. Give the user the exact commands, in order, and a numbered list of captures to send back.
   Build the document with placeholders meanwhile; fill them when the images arrive.
2. If the tools exist on the host (or WSL) and the statement does not forbid it, run it on the
   host and say so in one short line in the document: “Lo he hecho en mi equipo directamente,
   que para el caso es lo mismo.”

Never mix: if half the evidence is real and half is a placeholder, mark clearly which is which.

### No screenshots at all in the environment

Then the deliverable is the text: commands, expected outputs (quoted, and labelled as
expected), and the answers to the questions. The document keeps the same sections and the same
voice. State once, at the end, that the captures have to be pasted by hand and where.

## 4. Windows + VirtualBox gotchas

- **`VBoxManage.exe` not in `PATH`**: VirtualBox on Windows installs to
  `C:\Program Files\Oracle\VirtualBox\VBoxManage.exe` and rarely adds itself to `PATH`. Always
  resolve the full path or use `scripts/vm_capture.py` / `scripts/detect_env.py`.
- **`guestcontrol` credentials and blocking**: `VBoxManage guestcontrol <vm> run` blocks until
  the command finishes and requires `--username` / `--password`. Use `guestcontrol <vm> start`
  for GUI terminals (`gnome-terminal`, `Start-Process powershell`) so it returns immediately.
  `controlvm <vm> screenshotpng` works without any guest credentials.
- **Shared folders**: in VirtualBox Linux guests they appear under `/media/sf_<nombre>` (user
  must belong to `vboxsf`), and in Windows guests as `\\VBOXSVR\<nombre>`. When Guest Additions
  are active, `VBoxManage guestcontrol ... copyto` / `copyfrom` works without configuring shared
  folders.
- **Wayland Linux guests**: launching GUI apps via `guestcontrol` needs
  `--putenv "XDG_RUNTIME_DIR=/run/user/1000"`, `--putenv "WAYLAND_DISPLAY=wayland-0"`, and
  `--putenv "DISPLAY=:0"` together.
- **Windows paths and encodings**: use UTF-8 (`encoding="utf-8"`) in Python file I/O and pass
  `\n` (LF) line endings when generating `.sh` scripts for Linux VMs so `bash` does not choke on
  `\r\n`.
- **Windows without admin**: hosts, static IPs and firewall changes need elevation; run an
  elevated PowerShell or scheduled task (`/RL HIGHEST`) inside the guest.

## 5. Honesty rules

- A placeholder is always better than an invented capture or an invented number.
- If a step could not be completed, say it in one sentence in the document and say what was
  done instead.
