# Python üben

Übungsnotebooks und Kurzreferenz von **Dr. Christopher Gerling**, unter anderem für das Modul „Digitalisierung in Unternehmen“ an der HWR Berlin.

**[Python-Kurzreferenz als PDF](Python-Kurzreferenz.pdf)** · Zwei A4-Seiten zum Nachschlagen.

## Übungsnotebooks

Die **bisherigen Notebooks im Hauptverzeichnis bleiben unverändert**, damit die bestehenden Moodle- und Colab-Links weiter gelten. Die überarbeiteten Fassungen liegen getrennt unter [`pilot/`](pilot/). Die neuen Online-Links funktionieren nach dem Push auf `main`.

| Thema | Bisherige Fassung | Neue Fassung | Neue Fassung in Colab |
| --- | --- | --- | --- |
| Basisoperationen | [Notebook](01_Basisoperationen.ipynb) | [Notebook](pilot/01_Basisoperationen.ipynb) | [Öffnen](https://colab.research.google.com/github/christopher3996/python_courses/blob/main/pilot/01_Basisoperationen.ipynb) |
| Verzweigungen | [Notebook](02_Kontrollstrukturen_I.ipynb) | [Notebook](pilot/02_Verzweigungen.ipynb) | [Öffnen](https://colab.research.google.com/github/christopher3996/python_courses/blob/main/pilot/02_Verzweigungen.ipynb) |
| Listen und Tabellen | [Notebook](03_Listen_und_Tabellen.ipynb) | [Notebook](pilot/03_Listen_und_Tabellen.ipynb) | [Öffnen](https://colab.research.google.com/github/christopher3996/python_courses/blob/main/pilot/03_Listen_und_Tabellen.ipynb) |
| Schleifen | [Notebook](04_Kontrollstrukturen_II.ipynb) | [Notebook](pilot/04_Schleifen.ipynb) | [Öffnen](https://colab.research.google.com/github/christopher3996/python_courses/blob/main/pilot/04_Schleifen.ipynb) |
| Funktionen und Bibliotheken | [Notebook](05_Funktionen_und_Bibliotheken.ipynb) | [Notebook](pilot/05_Funktionen_und_Bibliotheken.ipynb) | [Öffnen](https://colab.research.google.com/github/christopher3996/python_courses/blob/main/pilot/05_Funktionen_und_Bibliotheken.ipynb) |

Noch ältere Materialien liegen unverändert im [`archive/`](archive/). Lösungen werden separat bereitgestellt.

## Aufbau

```text
Python-Kurzreferenz.pdf     fertige Kurzreferenz
01_… bis 05_….ipynb         bisherige Notebooks, unverändert
pilot/                     neue Übungsnotebooks
quellen/kurzreferenz/       LaTeX-Quellen der Kurzreferenz
scripts/                   Build- und Prüfscripte
archive/                   ältere Notebooks
loesungen/                 lokale Lösungen; vom Git-Upload ausgeschlossen
  notebooks/               bearbeitbare Notebooks mit Musterlösungen
  pdf/                     erzeugte, teilbare Lösungs-PDFs
```

## Kurzreferenz kompilieren

Voraussetzung: Python 3 und **pdfLaTeX** (TeX Live / MacTeX). Im Repo-Verzeichnis ausführen:

```bash
python3 scripts/build_kurzreferenz.py
```

Das Skript erzeugt **`Python-Kurzreferenz.pdf` im Hauptverzeichnis**, prüft die zwei Seiten und meldet überlaufenden Inhalt. Zwischenprodukte liegen unter `.build/`. Es verändert keine Notebooks.

Bearbeiten: [Inhalte](quellen/kurzreferenz/kurzreferenz.tex), [Gestaltung](quellen/kurzreferenz/gestaltung.tex), [Funktionen und Bibliotheken](quellen/kurzreferenz/zusatz.tex). Für Overleaf diese drei Dateien hochladen und `kurzreferenz.tex` mit pdfLaTeX kompilieren.

## Notebooks und Lösungen aktualisieren

Die Quellen sind die lokalen Notebooks unter `loesungen/notebooks/`. Sie enthalten Aufgaben und Lösungen; daraus entstehen die lösungsfreien Pilotnotebooks. Die alten Notebooks im Hauptverzeichnis werden niemals vom Build überschrieben.

Nur Pilotnotebooks aktualisieren, ohne zusätzliche Python-Pakete:

```bash
python3 scripts/build_materials.py
```

Für Lösungs-PDFs wird zusätzlich **ReportLab** benötigt. Einmalig installieren:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install 'reportlab>=4.2,<5'
```

Anschließend Pilotnotebooks und alle Lösungs-PDFs mit einem Befehl aktualisieren:

```bash
.venv/bin/python scripts/build_materials.py --pdf
```

Die PDFs liegen unter `loesungen/pdf/` und enthalten die Aufgaben mit Musterlösungen, ohne interne Lehr- oder Überarbeitungskommentare. Der Export benötigt kein LaTeX und führt den Lösungscode nicht aus.

**Quellenpflege:** Änderungen in `loesungen/notebooks/` vornehmen. Jede Aufgaben-Code-Zelle trägt `tags: ["solution"]`, ihre `task_id`, den Studierenden-Startcode als `student_source` und die Testeingaben als `example_inputs`. Der Export ersetzt den Lösungscode durch den Startcode und entfernt Ausgaben und Lösungsmetadaten. Die erzeugten Dateien unter `pilot/` nicht separat bearbeiten.

**Ablage:** `loesungen/` bleibt per `.gitignore` lokal. Den Ordner separat privat sichern; bei einem frischen Clone muss er für den Notebook-Build wieder ergänzt werden. Einzelne PDFs können unabhängig davon über Moodle geteilt werden. Für eine spätere Veröffentlichung der Lösungen im Repo den Git-Ausschluss bewusst aufheben.

Prüfen:

```bash
python3 scripts/build_materials.py --check
python3 scripts/check_materials.py
```

Der zweite Befehl führt die lokalen Musterlösungen mit Testeingaben aus. Nach Layoutänderungen die PDFs zusätzlich ansehen.

## Quellenhinweis zur Kurzreferenz

Gestaltungsanregung: *Python 3 Cheat Sheet*, Laurent Pointal, Mémento v2.0.5, deutsche Übersetzung M. Putzlocher; [Original](https://perso.limsi.fr/pointal/python:memento), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Inhalt und LaTeX-Layout wurden für diesen Kurs neu erstellt; keine Originalgrafiken oder PDF-Ausschnitte wurden übernommen.

Feedback: hello@mission-digital.com
