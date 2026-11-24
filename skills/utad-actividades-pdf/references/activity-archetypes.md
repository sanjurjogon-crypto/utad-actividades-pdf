# Activity archetypes — how each kind of statement is turned into the PDF

Four archetypes cover every activity seen in these subjects. Identify the archetype from the
statement, then follow its skeleton. Most statements mix two of them.

---

## A. Lab with evidence

*Memory, processes, priorities, users and groups, permissions, disks, compression, network
configuration, DNS diagnosis, file recovery.*

The capture is the argument. The text only says what to look at and what it means.

**Skeleton**

```
1. <título del bloque del enunciado>
<una frase: qué haces y qué buscas>
Figura 1. <qué se ve y qué demuestra>
[tabla comando → resultado → conclusión]      (si hay varios comandos)
<respuesta directa a cada pregunta del bloque>
```

**Rules**

- One figure per command or per short sequence of commands. If a block has four commands, one
  capture of a single terminal running all four is better than four tiny captures.
- The command must be visible in the capture together with its output. If the terminal shows
  only the output, recapture.
- Real values go into the table, copied from the capture. Never approximate.
- If the block asks questions, they are answered after the evidence, in the same order.

**Table shape (commands)**

| Comando | Resultado | Conclusión |
| --- | --- | --- |
| `ip route` | default via 10.0.2.2 | hay puerta por defecto |
| `ping -c 2 10.0.2.2` | 2 recibidos, 0 % de pérdida | el enlace y la puerta están bien |

**Table shape (ficha, when the statement says “ficha”)**

| Ficha | Linux (Ubuntu VM) |
| --- | --- |
| Comando | `taskset -c 0 yes > /dev/null (x2)` |
| Salida antes | 48,1 % y 47,8 % |
| Acción | `renice -n 19 -p 18673` |
| Salida después | 71,6 % y 24,3 % |
| Interpretación | el de nice 19 no se para, solo espera su turno |

---

## B. Pure calculation

*Subnetting, masks, broadcast, number bases, file sizes, compression ratios.*

No captures. Show the arithmetic in one or two lines, then the result. One paragraph per
question, in the statement's order.

**Example shape**

> **192.168.10.37/24.** La /24 son 24 bits para la red, o sea 255.255.255.0. Los tres primeros
> números son la red: 192.168.10.0, y el broadcast es el último de ese rango, 192.168.10.255.
> Quedan 254 direcciones para equipos, porque la de red y la de broadcast no se pueden usar.

Notes:

- The bold markup above is only for the question heading inside the prose; the body stays
  unbolded. In the PDF these come out as separate paragraphs whose first words are the input
  of the exercise, in normal weight.
- Powers as `2<super>24</super> - 2`.
- If the statement asks for a diagram (addressing plan), draw it with reportlab shapes: boxes
  for router and machines, a bus line, labels with IP and mask. Black lines, no fills except a
  very light grey `#F2F2F2` for the router box.

---

## C. Written deliverable

*Malware protocol, security director, risk analysis, incident response, training plan.*

No captures. At most two tables. Each paragraph answers one bullet of the statement, and
nothing else is added.

**Skeleton (one page)**

```
3. Protocolo ante software de origen dudoso
Caso: <una frase que resume el supuesto>
[tabla: señal de riesgo → qué se ve]
[tabla: paso → qué hago → herramienta]
<un párrafo de cierre con el orden de actuación>
```

Rules:

- The order asked by the statement is the order of the rows: *aislar, analizar, eliminar,
  recuperar, prevenir*. Do not reorder, do not add a sixth step.
- Each row says a concrete action, not a category: *desconecto el cable o la wifi*, not
  *aislamiento del activo*.
- Name the tool for each step (antivirus, Administrador de tareas, firewall, copia de
  seguridad). That is explicitly asked.
- For the “director de seguridad” type: four blocks in the statement's order — risk analysis
  (table), policies (paragraph), prevention and recovery plan (paragraph), training programme
  (paragraph). Five risks are enough; more is padding.
- Never invent a company name, a budget, a regulation number or a CVE. If a number is not
  given, do not invent it.

---

## D. Mixed: calculate, configure, verify

*Addressing plan then static IPs then ping both ways; permissions then test as another user.*

Skeleton follows the statement literally:

```
1. Plan de direccionamiento        (tabla + diagrama)
2. Configuración                   (una figura por sistema)
3. Verificación                    (tabla de comprobaciones + figura por sentido)
4. <lo que pida el enunciado después>
```

The verification block always ends with a checklist table:

| Comprobación | Comando | Resultado |
| --- | --- | --- |
| IP de Windows | `ipconfig` | 192.168.56.101/24, puerta 192.168.56.1: bien |
| Windows ve a Ubuntu | `ping -n 3 192.168.56.102` | 3 de 3, 0 % de pérdida, 1–2 ms |

Every row must be backed by something that appears in a figure of the document.

---

## E. Question-only closing blocks

Many statements end with “Responde: …”. That is a section, not a postscript:

```
5. Cierre: <lo que preguntan>
<la respuesta, en el mismo orden, un párrafo corto por punto>
```

If it asks for three checks: three short paragraphs starting *Primero*, *Segundo*, *Tercero*,
or a numbered list. No preamble beyond one sentence.

---

## F. Blocks that share one machine state

When two blocks depend on the same configuration (e.g. static IP on both VMs before pinging),
do them in one session and capture in this order: before, action, after, verification. Keep the
same window on screen so the reader can see continuity between figures.

---

## G. What to leave out

- No introduction of the subject matter (the teacher wrote the statement).
- No “materiales utilizados”.
- No “dificultades encontradas” unless the statement asks.
- No bibliography, no annexes.
- No conclusion paragraph that repeats the tables.
- No page of theory before the first command.
- No closing `Nota:` or AI disclaimer line.
