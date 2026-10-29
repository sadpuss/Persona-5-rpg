from pathlib import Path
from docx import Document
R=Path(__file__).parent
for name in ['Persona_5_RPG_Podrecznik_GM_0_5.docx','Persona_5_RPG_Podrecznik_Gracza_0_2.docx']:
    path=R/name;d=Document(path)
    for p in d.paragraphs:
        if p.text.startswith('W daily life zmiany banku i kart są trwałą częścią ekwipunku.'):
            p.text=('Zmiany banku i kart w daily life zapisujemy jako aktualny stan postaci. Na początku nowej wyprawy GM aktualizuje punkt zapisu do bieżącego stanu pałacu, EXP, poziomów, punktów nauki i ekwipunku po daily life. Miejscem powrotu pozostaje ostatni odkryty safe room, a przed odkryciem pierwszego wejście do pałacu. Nie odradza to pokonanych wcześniej Shadows. Zapobiega to cofnięciu codziennych zmian do zapisu z poprzedniej wyprawy. W trakcie wyprawy kolejne wejścia do safe roomów nadpisują ten stan jak dotąd. Zmiany wykonane w Velvet Roomie po zapisie obejmie dopiero następny zapis; sama wizyta go nie tworzy. Po porażce materiały zużyte po zapisie wracają, a nowe produkty przepadają. Nie zachowujemy jednocześnie składników i produktu.')
        elif p.text.startswith('W Velvet Roomie wybierz kartę i osobistą Personę właściciela.'):
            p.text+=' Już znany skill nie może zostać nauczony drugi raz dla kumulacji; nie zużywamy wtedy karty.'
        elif 'Ich rozwój ustalimy razem z awansem.' in p.text:
            p.text=p.text.replace('Ich rozwój ustalimy razem z awansem.','Dalszy rozwój premii ataku i Obrony pozostaje osobnym ustaleniem; nie wynika automatycznie z tabeli EXP.')
    for t in d.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    if 'GM 0.4' in p.text:p.text=p.text.replace('GM 0.4','GM 0.5')
    d.save(path)
print('Clarified new-expedition saves and updated remaining player references.')
