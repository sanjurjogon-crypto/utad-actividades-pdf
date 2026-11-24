---
name: utad-actividades-pdf
description: Produce UTAD class activities for "Sistemas Operativos" and "Fundamentos de Hardware" as a single black-and-white PDF with Gonzalo Sanjurjo's cover template (ASIR 1º GRUPO A), plain student Spanish, real VirtualBox VM screenshots on Windows, and answers to every question asked. Use whenever the user pastes an "Actividad complementaria" statement, mentions AC/UD numbers, asks for the homework PDF, or wants one of these labs written up (Linux/Windows commands, permissions, memory, networking, DNS, malware protocol, security). Also use when they ask to restyle, shorten or fix an existing one of these PDFs.
---

# UTAD activities — Sistemas Operativos & Fundamentos de HW

This skill encodes how activities are produced end to end on **Windows + VirtualBox**: what the
artefact is, how the text must sound, how the pages are laid out, how the evidence is captured from
VirtualBox VMs, and how to degrade when the environment has no VM or no Python.

Read this file first. Then load only the reference you need:

| Need | File |
| --- | --- |
| Exact cover, margins, fonts, table and caption geometry | `references/layout-and-cover.md` |
| How the prose must sound, banned vocabulary, number style | `references/writing-voice.md` |
| Playbook for each activity archetype | `references/activity-archetypes.md` |
| Capturing evidence on VirtualBox / Windows / Linux / nothing | `references/capture-playbook.md` |
| What to do when tooling is missing | `references/environment-adaptivity.md` |
| Copy-paste reportlab builder | `references/pdf-builder-template.py` |
| A complete real document to copy from | `references/example-full-document.py` |
| Cropping, rendering, QA helpers | `scripts/*.py` |

---

## 1. The artefact

One **A4 PDF**, black text on white, no headers, no footers, no page numbers, no colour except
the dark grey (`#333333`) of the figure captions.

Pages: a **cover** (always, following Gonzalo Sanjurjo's `Plantilla Trabajos` layout) plus the
body, which is as short as it can be while answering everything — usually 2 to 4 body pages.
Writing more is not a virtue; every sentence has to carry data, a command, or an answer.

The body mirrors the enunciado's own order. If the statement has four blocks ("Observa tu
memoria", "Usuarios y grupos", …), the PDF has four numbered sections in that order, plus a
final section for the closing question if there is one.

Do **not** add any closing AI disclaimer or `Nota:` line at the end of the document.

---

## 2. Non-negotiables

These come from repeated corrections. Violating any of them means the document is wrong even
if the content is right.

1. **Short paragraphs, short sentences.** One to three sentences per paragraph, ~15 words per
   sentence, nothing past 30. A wall of five long sentences is rejected before anyone reads the
   content.
2. **No bold in the body.** Headings and table headers are bold by style; body paragraphs are
   plain regular text.
3. **No headers, no footers, no page numbers, no "Página X de Y"** in body pages. (Only the
   cover places the date top-left and `Gonzalo Sanjurjo` bottom-right as in `Plantilla Trabajos`.)
4. **No em dashes (—) and no en dashes (–)** anywhere. Use a colon, a comma, a full stop or
   parentheses. Hyphens inside commands (`free -s3`, `-aG`) are fine.
5. **No AI-tell vocabulary.** Banned list in `references/writing-voice.md`. If a sentence
   sounds like a consultancy deck, rewrite it.
6. **No "etiqueta:" at the start of every paragraph.** Do not open paragraphs with
   `Políticas:`, `Formación:`, `Conclusión:`, `En una frase:`. Write the sentence.
7. **No filler.** No "en el mundo actual", no "es importante destacar", no restating the
   statement, no closing flourish.
8. **Answer exactly what is asked, in the order it is asked.** If the statement asks two
   questions, there are two answers, each one short and direct, using the numbers measured.
9. **Every figure is real.** A capture must show the command and its output, from the actual
   machine, cropped tight and legible. Never invent a result, never describe a screenshot you
   did not take.
10. **Every figure needs a caption** `Figura N.` in 8 pt italic grey, under the image,
    explaining what it proves — not what it is.
11. **Numbers are copied, never remembered.** Every figure in the text has to be readable in
    the capture or in the table right next to it. If you write «Available no se mueve de 45.872
    en las tres medidas» and the capture shows 45.772 in the middle one, the document is wrong
    and the teacher sees it in ten seconds. Zoom the capture, read the column, then write the
    sentence. Never phrase a claim as «en las tres medidas» without having looked at three
    numbers.
12. **Nothing but what was asked.** No extra sections, no "bibliografía", no "conclusiones
    generales", no closing `Nota:` line unless the statement explicitly asks for them.

---

## 3. Workflow

### Phase 0 — Read the statement properly

Extract, in writing (to yourself, not in the PDF):

- the blocks of the activity and their order;
- every question mark — those are mandatory answers;
- the deliverable format it asks for (captures, table, one-page protocol, document…);
- the file name it demands (`Sanjurjo_Gonzalo_UD[X]_AC[n].pdf`);
- the subject: **Sistemas Operativos** or **Fundamentos de Hardware**;
- the activity title and AC/AE/EV code, if it appears anywhere (statement, folder name, previous file name);
- any sign-off, reviewer name, team partner, list number `n`, or required date left blank in the statement.

Default author and group unless the statement or user specifies otherwise:
- **Author**: `Gonzalo Sanjurjo`
- **Group**: `ASIR 1º GRUPO A`

If the activity name/code, subject, or required sign-off/reviewer field cannot be inferred and the
user is present, ask **once**, with options, and keep working meanwhile. Never guess silently twice.

### Phase 1 — Detect the environment

Run `python scripts/detect_env.py` (or reason it out). It reports: VirtualBox (`VBoxManage.exe`)
and configured/running VMs, screenshot capability, Python + reportlab/Pillow/PyMuPDF/python-docx,
Microsoft Word COM / LibreOffice, pandoc, `pdftoppm`, Chrome/Edge, network access.

Pick the highest rung of the ladder in `references/environment-adaptivity.md` that the machine
supports. Announce nothing to the user about tooling unless something is missing.

### Phase 2 — Do the lab for real

Do the commands yourself on the machine the statement targets (usually a VirtualBox Linux or
Windows VM, or the Windows host when asked). Capture as you go, not afterwards. Details and
VirtualBox recipes in `references/capture-playbook.md`.

Rules while doing it:

- If a tool is missing (`traceroute`, `dig`, …), install it in the guest; the capture must
  show it working.
- Prefer one command per line inside a scripted terminal so command and output are visible in
  the same frame.
- If a capture comes out illegible, redo it with a bigger terminal font / smaller window
  (`--geometry=100x26`) or a smaller capture window. Do not ship a blurry figure.
- Capture and crop in one command with `python scripts/vm_capture.py "<VM>" fig/raw_fig1.png fig/fig1.png`
  (or crop an existing raw image with `python scripts/crop_capture.py raw.png fig.png --window --pad 18`)
  instead of guessing pixel boxes by hand.
- Record the exact numbers you see (PID, %, sizes, timings). Those numbers go into the tables
  and the answers.

### Phase 3 — Write the text

Follow `references/writing-voice.md`. Draft section by section, in the enunciado's order, in a
normal, natural Spanish register (neither overly technical/bureaucratic nor forcedly casual), and
keep each paragraph to one to three sentences, around 15 words each.

For each block the shape is usually:

1. one sentence saying what you did or what you were looking for;
2. the evidence (figure and/or table);
3. the answer, if that block has questions.

Tables of the "comando → resultado → conclusión" kind are the backbone of the lab blocks
(memory, users, DNS, processes). Fill them with the real values.

When the statement asks a question with a question mark, the section that answers it carries
the question as its heading, **with the question mark and with every qualifier the statement
put in it**: `¿Por qué otro usuario no puede leerlo aunque esté en su mismo grupo?`, not
`Por qué otro usuario no puede leerlo`. The qualifier is usually the interesting part.

### Phase 4 — Build the PDF

Use `references/pdf-builder-template.py` as the base. It already carries Gonzalo Sanjurjo's
cover, the margins, the styles, the figure helper and the table helper. Replace the `STORY` section.

Build with `python build.py`, then render every page to PNG (`python scripts/render_pages.py <file>.pdf`)
and **look at all of them**. This is not optional: pagination breaks are invisible in the code.

Run `python scripts/check_doc.py build.py` before building to catch banned prose issues early,
then run `python scripts/check_pdf.py <file>.pdf`: it verifies the cover layout, body margins,
and scans the text for dashes, banned words, label starts, stray bold, and body headers/footers.
For longer multi-capture AE/EV reports pass `--max-pages N` (and `--allow-no-question` if the
statement has no `?`) instead of skipping `check_pdf.py`. Every line must read PASS. Three of
its rules are worth knowing before you write, not after: it wants **one caption per image** (a
capture that serves two sections is cited in the prose, not duplicated), it checks that at least
one question (`?`) appears in the body, and it treats bold text as body bold only between 9,8 and
10,6 pt, so table headers at 8,5 pt and headings at 11,5 pt are safe.

`python scripts/check_numbers.py <file>.pdf` prints every line of the finished PDF that contains
a digit, page by page. Put that next to the captures and read them together: it is the cheapest
way to catch a number that the figure contradicts.

### Phase 5 — Fix the layout until it looks intentional

Checklist, in this order:

- [ ] Cover: matches `assets/cover-reference.png` (`Plantilla Trabajos.docx`): date top-left at
      25,4 mm, centered 26 pt lines (`<Asignatura>`, `ASIR 1º GRUPO A`, `<Actividad>`), and
      `Gonzalo Sanjurjo` bottom-right at 25,4 mm, black on white.
- [ ] No page ends with a heading and nothing under it, and no block leaves its introduction
      alone at the foot while its figure jumps to the next page (`CondPageBreak(75 * mm)` before
      the heading fixes it).
- [ ] No paragraph is split leaving one line alone at the top or bottom of a page.
- [ ] No table is immediately followed by text without a spacer (4 mm minimum).
- [ ] No figure's caption is cut, overlapping the next element, or separated from its image.
- [ ] No half-empty page in the middle. If one appears, shrink the figure above it or move the
      neighbouring block; a short last page is acceptable, a gap in the middle is not.
- [ ] Every figure is legible at 100 % zoom.
- [ ] Every number in the prose is visible in the capture or the table beside it, and no phrase
      asserts something the figure contradicts. This is the one check a script cannot do.
- [ ] Page count is what it should be: cover + enough pages, no more.

### Phase 6 — Deliver

Name the file exactly `Sanjurjo_Gonzalo_UD[X]_AC[n].pdf` (or whatever format the statement asks;
for two authors: `Apellido_A-Apellido_B_…`, both surnames, hyphen between them). Save it next to
the work folder, present it, and in the chat message give: what the PDF contains, the real
numbers, and anything that was left pending (another author, a number you had to guess).

Never paste the whole document into chat. Summarise in a few lines and link the file.

---

## 4. Environment adaptivity (short version)

Full ladder in `references/environment-adaptivity.md`. The principle: **the artefact is the
same; the evidence changes.**

| Environment | Evidence | Output build |
| --- | --- | --- |
| Windows + VirtualBox + Python libs | live captures from VirtualBox VMs, cropped | reportlab PDF, rendered and reviewed |
| Windows/PC + a VM but no scripting libs | live captures | HTML + Edge/Chrome print-to-PDF, or Word/LibreOffice |
| Local Windows shell, no VM | commands run on the host if the statement allows it; otherwise instructions + user’s screenshots | any PDF path available |
| Web chat, no tools | no captures: produce the document with clearly marked placeholders `[[CAPTURA: …]]` plus the exact commands the user must run, and a one-line instruction to paste each screenshot there | Markdown, HTML or DOCX the user can print |

Degrade **downwards only**, and say so in one sentence at the end (“No tenía VM aquí, así que
las capturas van marcadas para que las pegues”). Never pretend a capture exists.

---

## 5. Activity archetypes

Summarised below; the full plays are in `references/activity-archetypes.md`.

- **Lab with evidence** (memory, processes, users/groups, permissions, disks, compression,
  networking, DNS). Table of commands + real captures + short answers. Captures are the
  argument; the text only points at them.
- **Pure calculation** (subnetting, number bases, sizes). No captures, but show the arithmetic
  step by step in a couple of lines, then the result in bold-free plain text.
- **Written deliverable** (malware protocol, security director, incident report). One page of
  prose, at most two tables, no filler; each paragraph answers one of the statement's bullets.
- **Mixed** (calculation + configuration + verification). Sections in the statement's order;
  the verification block always ends with the checklist table.

---

## 6. Style constants (memorise these)

```
A4 210 × 297 mm · body margins 22 mm · body text width 166 mm
body        Helvetica 10 / 14 · justified · spaceAfter 6
heading h2  Helvetica-Bold 11.5 / 15 · spaceBefore 10 · spaceAfter 5 · keepWithNext
caption     8 / 10.5 italic · #333333 · spaceBefore 3 · 8 mm gap under the block
table       8.5 / 11 · header row #EEEEEE · grid 0.4 pt #999999 · cell padding 3–4 pt
cover page  Plantilla Trabajos.docx layout · margins 25.4 mm (1 in) · black on white
            date: Helvetica 11 regular · top-left (x = 25.4 mm, baseline H - 16.3 mm)
            subject: Helvetica 26 regular · centered (baseline H - 34.0 mm)
            group: Helvetica 26 regular · centered ("ASIR 1º GRUPO A", baseline H - 47.2 mm)
            activity: Helvetica 26 regular · centered (baseline H - 65.5 mm)
            author: Helvetica 11 regular · bottom-right ("Gonzalo Sanjurjo", x = W - 25.4 mm, baseline 14.1 mm)
figure      width 130–170 mm depending on legibility; never wider than 166 mm
```

If a figure is unreadable at 130 mm, recapture it, do not stretch it.

---

## 7. Files in this skill

```
SKILL.md
references/
  layout-and-cover.md          exact geometry + code for cover, figures, tables
  writing-voice.md             voice, banned words, number and unit style, Spanish rules
  activity-archetypes.md       per-type plays with section skeletons
  capture-playbook.md          VirtualBox (VBoxManage), Linux, Windows, no-tool fallback
  environment-adaptivity.md    capability ladder and fallbacks on Windows
  pdf-builder-template.py      the builder to copy
  example-full-document.py     a finished activity, end to end, working
scripts/
  detect_env.py                prints what the Windows/VirtualBox environment can do
  render_pages.py              PDF → PNG per page for visual QA
  crop_capture.py              auto-crop a screenshot to its content (exits 2 on black/empty frames)
  vm_capture.py                capture + validate + crop VirtualBox Linux/Windows VMs with auto-retry
  win_capture.py               HiDPI in-guest capture for VirtualBox Windows VMs via guestcontrol
  check_doc.py                 scans a draft for banned words, dashes and label starts
  check_pdf.py                 grades the finished PDF; every line must read PASS
  check_numbers.py             lists every line with digits for cross-checking against captures
assets/
  cover-reference.png          how the cover must look (from Plantilla Trabajos.docx)
```

When in doubt, the answer is: shorter, plainer, with the real numbers and a real capture.
