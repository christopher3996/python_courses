#!/usr/bin/env python3
"""Generate clean student notebooks and optionally solution PDFs. Never execute code."""
import argparse
import copy
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://colab.research.google.com/github/christopher3996/python_courses/blob/main/pilot/'


def student_version(nb, filename):
    result = copy.deepcopy(nb)
    cells = []
    for cell in result['cells']:
        meta = cell.get('metadata', {})
        if 'instructor' in meta.get('tags', []):
            continue
        if cell['cell_type'] == 'code':
            if 'solution' not in meta.get('tags', []) or 'student_source' not in meta:
                raise ValueError('Every code cell must have a solution tag and student_source')
            cell['source'] = meta['student_source'].splitlines(True)
            cell['outputs'] = []
            cell['execution_count'] = None
        cell['metadata'] = {k: v for k, v in meta.items() if k == 'task_id'}
        if not cells and cell['cell_type'] == 'markdown':
            cell['source'] = ''.join(cell['source']).replace(' · Lösungen\n', '\n', 1).splitlines(True)
        cells.append(cell)
    cells.insert(0, {'id': 'colab-link', 'cell_type': 'markdown', 'metadata': {},
                    'source': [f'[![In Colab öffnen](https://colab.research.google.com/assets/colab-badge.svg)]({REPO}{filename})\n']})
    result['cells'] = cells
    # Whitelist metadata: no solution text can be copied through notebook metadata.
    result['metadata'] = {k: copy.deepcopy(nb['metadata'][k])
                          for k in ('kernelspec', 'language_info')}
    return result


def write_pdf(nb, target):
    try:
        import reportlab
    except ImportError:
        raise SystemExit('PDF-Export benötigt ReportLab: python3 -m pip install reportlab') from None
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                   TableStyle, Preformatted, CondPageBreak, KeepTogether)
    fonts = Path(reportlab.__file__).parent / 'fonts'
    for name, file in [('Vera', 'Vera.ttf'), ('VeraBold', 'VeraBd.ttf'),
                       ('VeraItalic', 'VeraIt.ttf')]:
        pdfmetrics.registerFont(TTFont(name, str(fonts / file)))
    pdfmetrics.registerFontFamily('Vera', normal='Vera', bold='VeraBold', italic='VeraItalic', boldItalic='VeraBold')
    navy = colors.HexColor('#19364B')
    red = colors.HexColor('#AB3047')
    styles = {
        'body': ParagraphStyle('body', fontName='Vera', fontSize=9.5, leading=14, spaceAfter=7),
        'h1': ParagraphStyle('h1', fontName='VeraBold', fontSize=23, leading=29, textColor=navy, spaceAfter=16, keepWithNext=True),
        'h2': ParagraphStyle('h2', fontName='VeraBold', fontSize=15, leading=20, textColor=navy, spaceBefore=18, spaceAfter=9, keepWithNext=True),
        'h3': ParagraphStyle('h3', fontName='VeraBold', fontSize=11, leading=16, textColor=red, spaceBefore=12, spaceAfter=7, keepWithNext=True),
        'code': ParagraphStyle('code', fontName='Courier', fontSize=7.4, leading=10.5, backColor=colors.HexColor('#F1F4F6'), borderPadding=7, spaceBefore=5, spaceAfter=12),
        'small': ParagraphStyle('small', fontName='Vera', fontSize=8, leading=11, spaceAfter=5),
        'label': ParagraphStyle('label', fontName='VeraBold', fontSize=8, leading=11, textColor=navy, keepWithNext=True, spaceBefore=6),
    }
    def inline(s):
        s = escape(s)
        s = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)
        return s
    story = [Paragraph('AUFGABEN UND MUSTERLÖSUNGEN', styles['label'])]
    def markdown(src, instructor=False):
        lines = src.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            if line.startswith('```'):
                block = []
                i += 1
                while i < len(lines) and not lines[i].startswith('```'):
                    block.append(lines[i]); i += 1
                story.append(Preformatted('\n'.join(block), styles['code']))
                i += 1
                continue
            if line.startswith('|'):
                rows = []
                while i < len(lines) and lines[i].startswith('|'):
                    values = [v.strip() for v in lines[i].strip().strip('|').split('|')]
                    if not all(re.fullmatch(r':?-+:?', v) for v in values):
                        rows.append([Paragraph(inline(v), styles['small']) for v in values])
                    i += 1
                t = Table(rows, colWidths=[480 / len(rows[0])] * len(rows[0]), repeatRows=1, hAlign='LEFT')
                t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E3EBEF')),
                                       ('VALIGN', (0,0), (-1,-1), 'TOP'),
                                       ('LINEBELOW', (0,0), (-1,0), .5, navy),
                                       ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                                       ('TOPPADDING', (0,0), (-1,-1), 6)]))
                story.extend([t, Spacer(1,8)])
                continue
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                if level == 2:
                    story.append(CondPageBreak(100))
                story.append(Paragraph(inline(line.lstrip('#').strip()), styles['h'+str(min(level,3))]))
                i += 1
                continue
            paragraph = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(('#','```','|')):
                paragraph.append(lines[i]); i += 1
            # Preserve numbered steps on separate lines without relying on HTML/CSS.
            text = '<br/>'.join(inline(x) for x in paragraph)
            story.append(Paragraph(text, styles['small' if instructor else 'body']))
    index = 0
    pending_section = None
    while index < len(nb['cells']):
        cell = nb['cells'][index]
        group_start = len(story)
        if cell['cell_type'] == 'markdown' and ''.join(cell['source']).startswith('## '):
            pending_section = group_start
        is_task = cell['cell_type'] == 'markdown' and cell['metadata'].get('task_id')
        selected = [cell]
        index += 1
        if is_task:
            while index < len(nb['cells']):
                next_cell = nb['cells'][index]
                if next_cell['cell_type'] == 'code' or 'instructor' in next_cell['metadata'].get('tags', []):
                    selected.append(next_cell)
                    index += 1
                else:
                    break
        for selected_cell in selected:
            src = ''.join(selected_cell['source'])
            if selected_cell['cell_type'] == 'markdown':
                markdown(src, 'instructor' in selected_cell['metadata'].get('tags', []))
            else:
                story.append(Paragraph('MUSTERLÖSUNG', styles['label']))
                story.append(Preformatted(src, styles['code'], maxLineLength=95, splitChars=' ', newLineChars='    '))
        if is_task:
            if pending_section is not None:
                group_start = pending_section
                pending_section = None
            group = story[group_start:]
            del story[group_start:]
            story.append(KeepTogether(group))
    title = ''.join(nb['cells'][0]['source']).splitlines()[0].lstrip('# ')
    def page(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(navy)
        canvas.line(57, 804, 537, 804)
        canvas.setFont('Vera', 7)
        canvas.setFillColor(navy)
        canvas.drawString(57, 813, title)
        canvas.drawString(57, 28, 'Dr. Christopher Gerling · Lösungen')
        canvas.drawRightString(537, 28, str(doc.page))
        canvas.restoreState()
    target.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(target), pagesize=A4, leftMargin=57, rightMargin=57,
                            topMargin=57, bottomMargin=49, title=title, author='Dr. Christopher Gerling')
    doc.build(story, onFirstPage=page, onLaterPages=page)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', action='store_true', help='also generate solution PDFs (requires reportlab)')
    parser.add_argument('--check', action='store_true', help='check student files without writing')
    args = parser.parse_args()
    sources = sorted((ROOT / 'loesungen' / 'notebooks').glob('*.ipynb'))
    if not sources:
        parser.error('Keine Lösungsquellen in loesungen/notebooks/. Siehe README.')
    if args.check and args.pdf:
        parser.error('--check and --pdf are mutually exclusive')
    for source in sources:
        nb = json.loads(source.read_text())
        result = json.dumps(student_version(nb, source.name), ensure_ascii=False, indent=1)+'\n'
        destination = ROOT / 'pilot' / source.name
        if args.check:
            if not destination.exists() or destination.read_text() != result:
                raise SystemExit('Out of date: '+str(destination))
        else:
            destination.parent.mkdir(exist_ok=True)
            destination.write_text(result)
        if args.pdf:
            write_pdf(nb, ROOT / 'loesungen' / 'pdf' / (source.stem+'_Loesungen.pdf'))
        print(('Checked ' if args.check else 'Built ')+source.name)


if __name__ == '__main__':
    main()
