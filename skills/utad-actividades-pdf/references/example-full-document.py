# Worked example: the whole builder for a real four-block activity (memoria, usuarios y
# grupos, protocolo de malware, director de seguridad + cierre). Copy it, swap the STORY
# for your own content, keep the cover, the helpers and the style constants untouched.
# The figures it references live in figures/ (real VM captures are not shipped here;
# drop your own PNGs in that folder with the same names).
#
# Run:  python example-full-document.py
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import (Image, BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
                                NextPageTemplate, PageBreak, Table, TableStyle)
from reportlab.lib.enums import TA_JUSTIFY
from PIL import Image as PI

W, H = A4
M = 22 * mm
MC = 25.4 * mm
CW = W - 2 * M

ss = ParagraphStyle("ss", fontName="Helvetica", fontSize=10, leading=14,
                    alignment=TA_JUSTIFY, spaceAfter=6)
h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11.5, leading=15,
                    spaceBefore=10, spaceAfter=5, keepWithNext=1)
cap = ParagraphStyle("cap", fontName="Helvetica-Oblique", fontSize=8, leading=10.5,
                     textColor=colors.HexColor("#333333"), spaceBefore=3, spaceAfter=2)
cell = ParagraphStyle("cell", fontName="Helvetica", fontSize=8.5, leading=11)
cellb = ParagraphStyle("cellb", fontName="Helvetica-Bold", fontSize=8.5, leading=11)


def fig(path, w_mm, txt):
    im = PI.open(path); w, h = im.size
    ww = w_mm * mm
    t = Table([[Image(path, ww, ww * h / w)], [Paragraph(txt, cap)]], colWidths=[ww])
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                           ("TOPPADDING", (0, 0), (-1, -1), 0),
                           ("BOTTOMPADDING", (0, 1), (0, 1), 8), ("BOTTOMPADDING", (0, 0), (0, 0), 0),
                           ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    t.hAlign = "CENTER"
    return t


def tabla(rows, widths):
    data = [[Paragraph(c, cellb if i == 0 else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[x * mm for x in widths], repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t


def _draw_centered_wrapped(c, text, font, size, y, max_w, leading):
    for line in simpleSplit(text, font, size, max_w):
        c.drawCentredString(W / 2, y, line)
        y -= leading
    return y


def portada(c, d):
    c.saveState()
    c.setFillColor(colors.black)
    max_w = W - 2 * MC

    c.setFont("Helvetica", 11)
    c.drawString(MC, H - 16.3 * mm, "17/11/2026")

    c.setFont("Helvetica", 26)
    y = H - 34.0 * mm
    y = _draw_centered_wrapped(c, "Fundamentos de Hardware", "Helvetica", 26, y, max_w, 12.0 * mm)
    y -= 1.2 * mm
    y = _draw_centered_wrapped(c, "ASIR 1º GRUPO A", "Helvetica", 26, y, max_w, 12.0 * mm)
    y -= 6.3 * mm
    _draw_centered_wrapped(c, "Actividad Complementaria 89", "Helvetica", 26, y, max_w, 12.0 * mm)

    c.setFont("Helvetica", 11)
    c.drawRightString(W - MC, 14.1 * mm, "Gonzalo Sanjurjo")
    c.restoreState()


doc = BaseDocTemplate("Sanjurjo_Gonzalo_UD2_AC89.pdf", pagesize=A4,
                      leftMargin=M, rightMargin=M, topMargin=M, bottomMargin=M,
                      title="UD2_AC89 rendimiento y seguridad", author="Sanjurjo, Gonzalo")
doc.addPageTemplates([
    PageTemplate(id="Cover", frames=[Frame(MC, MC, W - 2 * MC, H - 2 * MC, id="c")], onPage=portada),
    PageTemplate(id="Body", frames=[Frame(M, M, CW, H - 2 * M, id="b")])])

story = [NextPageTemplate("Body"), PageBreak()]

story += [Paragraph("1. Observa la memoria", h2),
          Paragraph("Dejo free -s3 corriendo y voy mirando los valores: primero con la máquina en reposo, luego con "
                    "Firefox abierto y por último después de cerrarlo.", ss),
          tabla([
              ["Momento", "used", "free", "available", "swap usado"],
              ["En reposo", "1,79 GiB", "695 MiB", "1,51 GiB", "0"],
              ["Con Firefox", "2,35 GiB", "217 MiB", "975 MiB", "16 MiB"],
              ["Tras cerrarlo", "1,79 GiB", "828 MiB", "1,51 GiB", "12 MiB"]],
              [40, 28, 28, 30, 30])]

story += [Spacer(1, 2*mm), fig("figures/f_before.png", 142, "Figura 1. free -s3 en reposo: 1,79 GiB usados y 1,51 GiB "
                                                          "disponibles."),
          fig("figures/f_ff.png", 138, "Figura 2. Con Firefox abierto sube used, baja free y available, y empieza a "
                                    "usarse swap."),
          fig("figures/f_after.png", 125, "Figura 3. Cerrado Firefox, used y available vuelven a los valores de partida.")]

story += [Paragraph("¿Vuelven los valores iniciales?", h2),
          Paragraph("Sí, en lo que respecta a la RAM: used vuelve a 1,79 GiB y available a 1,51 GiB. Lo que no vuelve "
                    "es el swap, que se queda con unos 12 MiB. El kernel no devuelve una página de swap a la RAM "
                    "hasta que necesita ese hueco, así que ese resto es normal y no indica ningún problema.", ss),
          Paragraph("¿Qué indica available?", h2),
          Paragraph("Es la memoria que un programa nuevo puede usar sin tener que tirar de swap. No es lo mismo que free: "
                    "incluye la memoria libre y también la caché que el sistema puede soltar cuando hace falta. Por eso "
                    "free engaña, porque el equipo iba bien con solo 695 MiB libres. La cifra que se mira para saber si "
                    "queda margen es available.", ss)]

story += [PageBreak()]
story += [Paragraph("2. Usuarios y grupos", h2),
          Paragraph("Todo se hace desde una terminal, comprobando cada paso con id y con /etc/group.", ss),
          fig("figures/g1.png", 133, "Figura 4. Creo el grupo ac8 (gid 1600), le pongo contraseña con chgpasswd y "
                                     "se ve el hash en /etc/gshadow; después la quito con gpasswd -r y vuelve a "
                                     "quedar «!», que significa sin contraseña."),
          fig("figures/g2.png", 133, "Figura 5. Creo el usuario alumno8, lo meto en ac8 y con newgrp ac8 cambio de "
                                      "grupo en la propia sesión: dentro de esa shell el gid pasa a ser 1600(ac8)."),
          fig("figures/g3.png", 133, "Figura 6. Saco a los dos del grupo con gpasswd -d, borro el grupo con "
                                     "groupdel (getent ya no lo encuentra) y elimino el usuario con userdel -r.")]

story += [Spacer(1, 2*mm), tabla([
    ["Paso", "Comando", "Comprobación"],
    ["Crear grupo", "groupadd -g 1600 ac8", "getent group ac8 → ac8:x:1600:"],
    ["Poner contraseña", "chgpasswd (ac8:clave123)", "/etc/gshadow muestra el hash"],
    ["Quitar contraseña", "gpasswd -r ac8", "/etc/gshadow vuelve a ac8:!::"],
    ["Crear usuario", "useradd -m -s /bin/bash alumno8", "id alumno8 → 1017/1601"],
    ["Meter en el grupo", "usermod -aG ac8 alumno8", "id → groups ...1600(ac8)"],
    ["Cambiar de grupo", "newgrp ac8", "id dentro de la shell → gid=1600(ac8)"],
    ["Sacar del grupo", "gpasswd -d alumno8 ac8", "id → sin 1600(ac8)"],
    ["Borrar grupo y usuario", "groupdel ac8 y userdel -r alumno8", "getent sin salida; id: no such user"]],
    [34, 62, 74])]

story += [PageBreak()]
story += [Paragraph("3. Protocolo ante software de origen dudoso", h2),
          Paragraph("Caso: alguien instala un «optimizador» descargado de una web de anuncios.", ss),
          tabla([
              ["Señal", "Qué se ve en este caso"],
              ["Origen", "web de anuncios, sin fabricante conocido ni página oficial"],
              ["Firma digital", "el ejecutable no está firmado o la firma no es de una empresa reconocible"],
              ["Permisos que pide", "administrador para instalarse y servicios al arrancar, cuando la tarea no lo necesita"],
              ["Comportamiento", "se abre solo al iniciar, añade tareas programadas, manda tráfico a dominios raros, "
                                 "sube el uso de CPU o de disco sin motivo"]],
              [38, 132])]

story += [Spacer(1, 2*mm), Paragraph("Actuación, en este orden:", h2),
          tabla([
              ["Paso", "Qué hago", "Herramienta"],
              ["1. Aislar", "saco el equipo de la red (cable o wifi) para que no siga comunicándose ni se propague",
               "firewall, desconexión de red"],
              ["2. Analizar", "miro qué procesos corren, cuáles tiran de CPU y qué se ejecuta al arrancar",
               "Administrador de tareas, antivirus, autoruns"],
              ["3. Eliminar", "desinstalo el programa, borro sus carpetas, tareas y claves de arranque",
               "panel de control, Administrador de tareas, antivirus"],
              ["4. Recuperar", "restauro los datos desde la última copia y cambio las contraseñas que se usaron",
               "copia de seguridad, restaurar el sistema"],
              ["5. Prevenir", "reviso de dónde se instaló y aplico la norma: solo software firmado y de la fuente oficial",
               "política de instalación, formación"]],
              [26, 92, 52])]

story += [Spacer(1, 4 * mm), Paragraph("Primero se corta la salida a la red, luego se mira qué está pasando, después se borra, se recupera lo "
                    "que falte y por último se corrige la causa para que no vuelva a pasar.", ss)]

story += [Paragraph("4. Director de seguridad", h2),
          Paragraph("Antes de nada hay que saber qué puede pasar y qué se perdería. Estos son los riesgos que veo en los "
                    "equipos de la empresa y lo que haría con cada uno.", ss),
          tabla([
              ["Riesgo", "Probabilidad", "Impacto", "Medida"],
              ["Ransomware en un puesto", "media", "alto", "copias de seguridad y antivirus al día"],
              ["Correo con adjunto peligroso", "alta", "alto", "filtro en el correo y bloquear los .exe"],
              ["USB que viene de fuera", "media", "medio", "antivirus y nada de ejecución automática"],
              ["Contraseñas flojas o repetidas", "alta", "alto", "gestor de contraseñas y doble factor"],
              ["Equipo sin actualizar", "alta", "alto", "actualizaciones automáticas"]],
              [52, 26, 22, 70])]

story += [Spacer(1, 4 * mm), Paragraph("Cada persona entra con su cuenta y sin permisos de administrador; la cuenta de administrador se "
                    "pide solo cuando hay que instalar algo. Las contraseñas son largas y distintas en cada servicio, y "
                    "el correo y el acceso remoto llevan doble factor. Solo se instala software de la tienda oficial o "
                    "de la web del fabricante, nunca de una web de anuncios. Las copias se hacen a diario, una a la "
                    "semana se guarda fuera del edificio y una vez al mes se prueba a restaurar una para ver que "
                    "sirve.", ss),
          Paragraph("Para prevenir, los equipos se actualizan solos, el antivirus y el firewall van encendidos, el "
                    "correo se filtra antes de llegar y cada mes se revisa quién tiene permisos de más. Si algo pasa, "
                    "se desconecta el equipo de la red, se mira qué se ha tocado, se restaura la copia más reciente, "
                    "se cambian las contraseñas que se usaron en ese equipo y se apunta lo ocurrido para que no se "
                    "repita.", ss),
          Paragraph("La formación es una charla cada tres meses, de una hora, con casos reales: correos falsos, "
                    "contraseñas, USBs que aparecen por ahí y qué hacer cuando algo huele mal. Se cierra con un test "
                    "corto y una vez al año se manda un correo de prueba para ver quién pica.", ss)]

story += [Paragraph("5. Cierre: factura_urgente.exe", h2),
          Paragraph("Un .exe no es una factura, así que no lo abriría. Antes miro tres cosas.", ss),
          Paragraph("Primero, quién lo manda: la dirección completa, no el nombre que sale en pantalla, y si de verdad "
                    "esperaba una factura de esa persona o empresa.", ss),
          Paragraph("Segundo, qué es el archivo: la extensión real y pasarlo por el antivirus o por un servicio de "
                    "análisis antes de tocarlo.", ss),
          Paragraph("Tercero, si el correo mete prisa o pide datos. Si no puedo confirmarlo por teléfono, lo borro y "
                    "lo aviso.", ss)]

doc.build(story)
print("ok")
