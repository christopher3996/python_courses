#!/usr/bin/env python3
"""Compile the reference sources into Python-Kurzreferenz.pdf at repository root."""
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'quellen' / 'kurzreferenz'
CACHE = ROOT / '.build' / 'kurzreferenz'


def main():
    compiler = shutil.which('pdflatex')
    if not compiler:
        raise SystemExit('pdflatex fehlt. Bitte TeX Live oder MacTeX installieren.')
    CACHE.mkdir(parents=True, exist_ok=True)
    command = [compiler, '-interaction=nonstopmode', '-halt-on-error',
               '-jobname=kurzreferenz', '-output-directory=' + str(CACHE),
               'kurzreferenz.tex']
    for _ in range(2):
        result = subprocess.run(command, cwd=SOURCE, capture_output=True)
        (CACHE / 'build.log').write_bytes(result.stdout + result.stderr)
        if result.returncode:
            raise SystemExit('LaTeX-Fehler: ' + str(CACHE / 'build.log'))
    log = (CACHE / 'kurzreferenz.log').read_text(errors='replace')
    pages = re.search(r'Output written on .*?\((\d+) pages?', log, re.S)
    if not pages or int(pages.group(1)) != 2:
        raise SystemExit('Die Kurzreferenz hat nicht genau zwei Seiten. Layout prüfen.')
    if re.search(r'Overfull \\[hv]box', log):
        raise SystemExit('Überlaufender Inhalt in der Kurzreferenz. Layout prüfen.')
    target = ROOT / 'Python-Kurzreferenz.pdf'
    shutil.copy2(CACHE / 'kurzreferenz.pdf', target)
    print('Erstellt: ' + str(target) + ' (2 Seiten)')


if __name__ == '__main__':
    main()
