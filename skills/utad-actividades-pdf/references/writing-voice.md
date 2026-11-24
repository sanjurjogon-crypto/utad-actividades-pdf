# Writing voice

The document should sound like a normal person explaining what they did: Spanish from Spain, first person singular, plain words, neither stiff/over-technical nor forcedly casual or slangy. Read it as if someone sat down and explained the lab naturally in five minutes.

## The rules that decide everything

1. **One idea per sentence, one to three sentences per paragraph.** This is the rule that decides
   how the document sounds. Measured on the same activity: paragraphs of five long sentences read
   like a technical report however clean the vocabulary is; the same content cut into 15-word
   sentences in two-line paragraphs reads like a student explaining it. Nothing over 30 words in a
   sentence, nothing over 60 in a paragraph. If a paragraph grows a fourth sentence, split it.
2. **If a sentence could appear in a company brochure, delete it.** No “en el mundo actual”,
   no “resulta fundamental”, no “cabe destacar”.
3. **Every sentence carries data, a command, a cause or an answer.** If it carries none, it
   goes.
4. **Say it the way you would say it out loud**, then fix the grammar, not the other way
   round.

The banned-word list below is the cheap half of the job: it removes the tells but leaves the
architecture untouched. Long sentences survive a perfect vocabulary.

## Voice

- First person singular: *he mirado*, *lanzo*, *compruebo*, *me sale*, *no consigo*.
- Plural only when it is really two people, or for impersonal system facts (*los ficheros se
  guardan…*).
- Short sentences. One idea each. Full stops are cheaper than commas.
- Concrete nouns and verbs: *miro*, *cambio*, *quito*, *pego*, *compruebo*, *tarda*, *falla*.
  Not *procedo a*, *realizo la comprobación de*, *efectúo*.
- Use normal, neutral connectors (*así que*, *por eso*, *luego*, *después*). Do not force overly
  colloquial fillers (*total que*, *o sea*, *lo típico*, *ya está*) or stiff textbook connectors
  (*en consecuencia*, *por consiguiente*, *de este modo*). Aim for plain, natural Spanish.
- Admit the mistake when there is one: *una cosa que me comí*, *al principio pensaba que…*.
  It reads honest and it is what the teacher wants to see.

## The register trap: manual Spanish

The failure mode that gets corrected most often is not slang, it is *manual Spanish*: correct,
technical and dead. It happens when the sentence describes the system from above instead of
telling what it did to you. Symptoms, all of them from real corrections:

- **Bureaucratic verbs**: *el sistema lo juzga*, *deniega*, *se queda en la terna*, *procede a*,
  *efectúa*, *aplica la política*. Replace with *mira*, *no te deja*, *no te dice que sí*,
  *le contesta que no*.
- **Nominalisations**: *la realización de la comprobación* → *compruebo*. *El aumento del
  ocupado* → *el usado sube*.
- **The system as the subject of every clause**: *el kernel no devuelve las páginas hasta que
  necesita el hueco* is fine once; five clauses in a row with the kernel as the protagonist is
  a datasheet.
- **Elegant variation for technical nouns**: *terna* for the three permission digits, *emparejar*
  for matching a group. One plain name per thing, used every time.
- **Textbook connectors**: *en consecuencia*, *por consiguiente*, *de este modo*. A normal person
  writes *así que*, *por eso*, *y ya está*.
- **Sentences with no human in them**: if four clauses pass and nobody does anything, rewrite
  from the person: *lo dejo en /tmp*, *lo borro*, *le doy permisos*.

The test before delivering: read a paragraph out loud. If you would not say it to a classmate
across a table, it is written wrong, no matter how correct it is.

## Banned vocabulary (delete on sight)

`fundamental`, `clave`, `crucial`, `robusto`, `óptimo`, `idóneo`, `garantizar`, `permitir`
(as a filler verb), `destacar`, `resaltar`, `cabe mencionar`, `en definitiva`, `en conclusión`,
`en resumen`, `por otro lado`, `asimismo`, `adicionalmente`, `no obstante` (unless it is really
a contrast), `a nivel de`, `de cara a`, `en base a`, `el mismo` (as a pronoun), `se procede a`,
`resulta`, `ciertamente`, `sin duda`, `de forma tal que`, `aprovechar al máximo`,
`optimizar` (unless the activity is literally about an optimiser), `potenciar`, `sinergia`,
`ecosistema`, `solución integral`.

Also banned: opening a paragraph with a label and a colon — `Políticas:`, `Formación:`,
`Conclusión:`, `En una frase:`, `Importante:`. Write the sentence; the reader does not need the
signpost.

Also banned: em dashes, en dashes, and `—` between clauses.

## Do / Don't, from real corrections

| Don't | Do |
| --- | --- |
| «Cada situación pide un compromiso distinto entre compatibilidad, tamaño y rapidez» | «Cada caso pide una cosa distinta» |
| «Lo primero es saber qué puede pasar y cuánto dolería» | «Antes de nada hay que saber qué puede pasar y qué se perdería» |
| «En una frase: primero se corta la salida a la red…» | «Primero se corta la salida a la red…» |
| «Por eso free engaña (con 695 MiB libres el equipo iba bien) y available es la cifra que se mira» | «Por eso free engaña, porque el equipo iba bien con solo 695 MiB libres. La cifra que se mira para saber si queda margen es available» |
| «Es un valor normal en documentación: mucho texto plano, nada de imágenes» | «Es lo normal con documentación: mucho texto y ninguna imagen» |
| «Conviene no mezclarlas, porque un ratio de 1,85 no significa un 85 % de ahorro» | «Conviene no liarlos, porque un ratio de 1,85 no es un 85 % menos» |
| «La conclusión práctica es que conviene cifrar antes de guardar» | «Resumiendo: cifra antes de guardar y no te fíes de que borrar deja el dato fuera de alcance» |
| «el sistema lo juzga con la terna de grupo, que en 600 está a cero… se queda en la que ha emparejado y, si ahí no hay permiso, deniega» | «entonces Linux mira los permisos del grupo: en 600 el grupo está a cero. Y ahí se queda… Por eso le contesta que no» |
| «Lo que cambia son los bits de grupo y de otros, que se apagan» | «Se apagan los permisos de grupo y de otros» |
| «queda margen de sobra» | «va holgada» |
| «lo dejo en /tmp/pruebas para que otro usuario pueda llegar hasta él sin tropezar con mi carpeta personal» | «lo dejo en /tmp/pruebas para que otro usuario llegue sin chocar con mi carpeta personal» |
| «Uso df -m porque df -h redondea a GB y ahí 100 MB no mueven la cifra» | «Uso df -m en vez de df -h porque en GB no se nota: 100 MB no mueven la cifra redondeada» |

## Structure of a section

```
2. Usuarios y grupos                      <- heading, matches the enunciado
Una frase diciendo qué se hace.            <- optional, only if it helps
[figura]
Caption: qué se ve y qué demuestra.
[tabla comando/resultado/conclusión]       <- if the block is about commands
[respuesta directa a cada pregunta]        <- only if the block asks something
```

Order inside an answer: **the number first, the explanation second**. Then, if the mechanism is
the point of the question, one everyday sentence saying what the machine does to you
(*por eso le contesta que no*), and only after that the technical name of the mechanism. *Sale 10.0.0.99 y el ping
pierde el 100 %. Eso pasa porque /etc/hosts se consulta antes que el DNS.*

If the block asks a yes/no question, the first word of the answer is *Sí* or *No*, then the
reason: *Sí, en lo que respecta a la RAM…*

## Numbers, units, code

- Decimal comma: `1,79 GiB`, `0,02 s`, `46 %`.
- Space before the unit and before `%`: `3,8 GB`, `0 % de pérdida`.
- Thousands with a dot: `16.777.214`, `65.534`.
- Commands and file names in the body: plain text, exactly as typed (`free -s3`,
  `/etc/netplan/01-netcfg.yaml`, `New-NetIPAddress`). No bold, no monospace, no backticks in
  the PDF.
- Times and lengths with the unit the tool printed; do not convert unless it helps
  (`16.005 bytes` is fine, `16 KB` in a caption when the tool rounded it).
- IPs, masks and gates always written in full: `192.168.56.101/24`, `255.255.255.0`,
  `192.168.56.1`.

## Captions

`Figura 4. En /etc/hosts había una línea metida a mano: 10.0.0.99 google.com. Esa es la que gana.`

- Start with the figure number and a full stop.
- Say what the reader is looking at and what it proves.
- Never “captura de pantalla de la terminal”; that is obvious.
- Two lines maximum. If it needs three, the figure is doing too little.

## Table rows

- First column: the command, the moment, or the step, in the imperative or noun form
  (`Crear grupo`, `ping -c 2 192.168.56.1`, `Con Firefox`).
- Middle columns: what the tool printed, trimmed to the part that matters.
- Last column: the conclusion in one short clause, no full stop if it is a phrase, full stop if
  it is a sentence. Be consistent inside a table.

## Length

Cover + 2 to 4 body pages is the norm. A block with three captures and no questions can fit in
half a page. If the document passes five body pages, something is being explained twice. Do not
add any closing `Nota:` or AI disclaimer at the end.
