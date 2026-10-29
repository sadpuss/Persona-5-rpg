"""Buduje lokalny katalog wyłącznie z aktualnych reguł i tabel Word."""
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def tables(name):
    with zipfile.ZipFile(ROOT / name) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    return [[[' '.join(t.text or '' for t in cell.findall('.//w:t', NS)) for cell in row.findall('w:tc', NS)] for row in table.findall('w:tr', NS)] for table in root.findall('.//w:tbl', NS)]

gates = json.loads((ROOT / 'skill_level_gates_0_8.json').read_text('utf-8'))
rules = {r['skill']: r for r in json.loads((ROOT / 'skill_rules_0_8.json').read_text('utf-8'))}
player = tables('Persona_5_RPG_Podrecznik_Gracza_0_5.docx')
gm = tables('Persona_5_RPG_Podrecznik_GM_0_8.docx')
effects = {}
arcana = []
starters = []
for table in player + gm:
    if not table:
        continue
    header = ' | '.join(table[0])
    if table[0] == ['Skill', 'Min. lvl', 'Koszt', 'Gotowe działanie RPG']:
        for row in table[1:]:
            if len(row) >= 4:
                effects[row[0]] = {'effect': row[3], 'cost': row[2]}
    if table[0] == ['Umiejętność', 'Cel i efekt', 'Koszt']:
        for row in table[1:]:
            if len(row) >= 3:
                effects[row[0]] = {'effect': row[1], 'cost': row[2]}
    if 'Koszt RPG' in table[0] and 'Min. lvl / dostęp' in table[0]:
        for row in table[1:]:
            if len(row) >= 7:
                effects.setdefault(row[0], {})['cost'] = row[3]
    if 'Skill' in header and 'Działanie RPG' in header and 'Koszt' in header:
        for row in table[1:]:
            if len(row) >= 3:
                effects[row[0]] = {'effect': row[1], 'cost': row[2]}
for table in player:
    if table and 'Osobisty trait na start' in ' '.join(table[0]):
        arcana = [{'name': r[0], 'effect': r[1]} for r in table[1:] if len(r) >= 2]
    if table and 'Działanie RPG' in ' '.join(table[0]) and 'Koszt' in ' '.join(table[0]):
        starters = [r[0] for r in table[1:] if len(r) >= 3]
skills = []
for g in gates:
    r = dict(g)
    r.update(effects.get(g['skill'], {}))
    r.update(rules.get(g['skill'], {}))
    r['starter'] = r['skill'] in starters
    skills.append(r)
data = {'version': 'GM 0.8 / Gracz 0.5', 'skills': skills, 'arcana': arcana}
(ROOT / 'aplikacja' / 'prototyp-html' / 'data.js').write_text('window.RULES = ' + json.dumps(data, ensure_ascii=False) + ';\n', encoding='utf-8')
(ROOT / 'aplikacja' / 'src' / 'rules.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Katalog: {len(skills)} skilli, {len(arcana)} Arkan, {len(starters)} skilli startowych; opisanych: {sum(bool(s.get("effect")) for s in skills)}')
