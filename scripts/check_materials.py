#!/usr/bin/env python3
"""Execute trusted local teaching solutions with simulated input and check boundary cases."""
import ast
import contextlib
import io
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
solutions = {}


def run(source, inputs=(), scope=None):
    values = iter(inputs)
    def read(prompt=''):
        try:
            return next(values)
        except StopIteration:
            raise AssertionError('Missing simulated input: '+prompt) from None
    namespace = {} if scope is None else scope
    namespace['input'] = read
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exec(compile(source, '<teaching solution>', 'exec'), namespace)
    assert next(values, None) is None, 'Unused simulated input'
    return output.getvalue(), namespace


def override(source, **values):
    """Replace top-level example assignments, retaining the actual algorithm."""
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in values:
                node.value = ast.Constant(values[target.id])
    return ast.unparse(ast.fix_missing_locations(tree))


def check():
    for p in sorted((ROOT/'loesungen'/'notebooks').glob('*.ipynb')):
        nb = json.loads(p.read_text())
        student = json.loads((ROOT/'pilot'/p.name).read_text())
        assert nb['nbformat'] == student['nbformat'] == 4
        for document in (nb, student):
            ids = [c['id'] for c in document['cells']]
            assert len(set(ids)) == len(ids)
            for i, c in enumerate(document['cells']):
                if c['cell_type'] == 'markdown' and c['metadata'].get('task_id'):
                    assert document['cells'][i+1]['cell_type'] == 'code'
                if c['cell_type'] == 'code':
                    ast.parse(''.join(c['source']))
                    assert c['outputs'] == [] and c['execution_count'] is None
        for c in student['cells']:
            assert set(c['metadata']) <= {'task_id'}
        scope = {}
        for c in nb['cells']:
            if c['cell_type'] == 'code':
                source = ''.join(c['source'])
                meta = c['metadata']
                run(source, meta['example_inputs'], scope)
                solutions[meta['task_id']] = source
        print('Executed all cells in order:', p.name)
    assert len(solutions) == 54, len(solutions)
    # Maximum: all positions, ties and exclusively negative values.
    for key in ['V04', 'V10']:
        for a,b,c in itertools.product([-5,-1,0,2,5], repeat=3):
            output,_ = run(override(solutions[key], a=a,b=b,c=c))
            assert output.strip() == str(max(a,b,c)), (key,a,b,c,output)
    for a,b in itertools.product([-5,0,5], repeat=2):
        assert run(override(solutions['V01'],a=a,b=b))[0].strip() == str(max(a,b))
    for num in [-4,0,7]:
        assert run(override(solutions['V03'],num=num))[0].strip() == ('negativ' if num<0 else 'positiv' if num>0 else 'null')
    for x in ['9','10','0','-6']:
        assert ('nicht' not in run(solutions['V02'],[x])[0]) == (int(x)%3==0)
    for x,expected in [('2024','Schaltjahr!'),('2023','Kein Schaltjahr!'),('1900','Kein Schaltjahr!'),('2000','Schaltjahr!'),('0040','Schaltjahr!'),('１２','Schaltjahr!')]:
        assert run(solutions['V08'],[x])[0].strip() == expected
    for x in ['0','0000','-4','+4','20.5','abc','²','10000','',' 2000','2000 ','9'*5000]:
        assert run(solutions['V08'],[x])[0].strip() == 'Ungültige Eingabe'
    for x,expected in [('Alice123','Keine Sonderzeichen vorhanden'),('Müller','Keine Sonderzeichen vorhanden'),(' ','Sonderzeichen vorhanden'),('','Keine Eingabe'),('Hallo!','Sonderzeichen vorhanden')]:
        assert run(solutions['V07'],[x])[0].strip() == expected
    for x,expected in [('Otto','Palindrom'),('Lagerregal','Palindrom'),('Python','Kein Palindrom'),('O, t t o!','Palindrom'),('?!','Kein prüfbarer Text'),('','Kein prüfbarer Text')]:
        assert run(solutions['V09'],[x])[0].strip() == expected
    for price in ['100000','200000','0']:
        _,ns=run(solutions['B17'],[price])
        assert ns['nebenkosten'] == float(price)*.13
        assert abs(ns['gesamtkosten']-float(price)*1.13)<1e-8
    assert '19 Jahre' in run(solutions['B05'],['18'])[0]
    assert run(solutions['S10'],[''])[0] == 'Anzahl: 0\nSumme: 0.0\nKein Mittelwert vorhanden\n'
    assert 'Mittelwert: 6.0' in run(solutions['S10'],['5','7',''])[0]
    assert 'Mittelwert: 0.0' in run(solutions['S10'],['-2','2',''])[0]
    assert run(solutions['S09'],['Python'])[0].strip()=='Zutritt gewährt!'
    assert run(solutions['S01'])[0].splitlines()==list(map(str,range(1,11)))
    assert run(solutions['S02'])[0].splitlines()==list(map(str,range(10,0,-1)))
    assert run(solutions['S05'])[0]==run(solutions['S08'])[0]
    _,ns=run(solutions['F08'])
    assert ns['kapital_liste'](1000,.1,0)==[1000]
    assert abs(ns['kapital_liste'](1000,.1,2)[-1]-1210)<1e-9
    print('All structure, execution, and boundary checks passed (54 tasks).')


if __name__ == '__main__':
    check()
