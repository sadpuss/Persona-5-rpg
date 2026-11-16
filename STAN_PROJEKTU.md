# Persona 5 RPG stan projektu na 29 października 2026

## Aplikacja Linux — 16 listopada 2026

Przygotowano przenośną paczkę `aplikacja/release/Take-Your-Heart-0.5.0-linux-x64.tar.gz` dla Intel/AMD 64-bit. Instrukcja: `aplikacja/LINUX.txt`. Odtwarzanie: `npm run package:linux` w folderze aplikacji (także na Windowsie). Paczka obejmuje Electron dla Linuxa, aplikację i trzy bieżące podręczniki; archiwum przechowuje prawa wykonywania. Kontrola: 22 testy logiki, kompilacja, ELF x64, zawartość archiwum i prawa wykonywania. Uruchomienie pulpitu i PDF na Linuxie pozostają niezweryfikowane — komputer nie ma Linuxa/WSL. Próba AppImage na Windowsie zatrzymała się na uprawnieniach dowiązań; osobne polecenie `package:linux:appimage` pozostaje do użycia na Linuxie. Postacie przenosi się przez eksport/import JSON.

## Aktualne podręczniki

Od wdrożenia Gita edytujemy pliki bez numerów: `Persona_5_RPG_Podrecznik_GM.docx`, `Persona_5_RPG_Podrecznik_Gracza.docx` i `Persona_5_RPG_Bestiariusz.docx`. Poniższe wersje to ich źródła startowe. Procedura kontroli aktualności: `GIT_I_PODRECZNIKI.md`.

- `Persona_5_RPG_Podrecznik_GM_0_8.docx` — główne zasady, walka, eksploracja, daily life, relacje, EXP, katalogi skilli i przedmiotów.
- `Persona_5_RPG_Podrecznik_Gracza_0_5.docx` — tworzenie bohatera i osobistej Persony, akcje, nauka skilli, rozwój, bank i Velvet Room.
- `Persona_5_RPG_Bestiariusz_0_5.docx` — 242 ilustrowane wpisy, dane P5R, robocze profile RPG, polskie nazwy Shadows i przypisane skill cards.

To zestaw do dalszych prac. Starszych wersji nie usuwać; są archiwum i wejściem części wcześniejszych skryptów. Ozdobna karta postaci z osobnymi polami bohatera i Persony pozostaje do stworzenia.

## Ostatnia autoryzowana aktualizacja

Użytkowniczka zaakceptowała wdrożenie propozycji po testach balansu. Reguły wstawiono do właściwych rozdziałów, zamiast dodawać aneks z wyjątkami:

- Despair na bossie/minibossie: trzecie rozliczenie daje 20 Almighty zamiast KO; Guard działa.
- Koszty aktywnych Physical/Gun: 2/4/6/8/10 HP, +3 za obszar, +1 za status lub zwiększoną celność; wyjątki warunkowe są opisane w katalogu. Płatny Light ma 1d6+6, darmowy atak i strzał nadal 1d6+4.
- Standardowe Severe żywiołowe: 4 SP jeden cel, 6 SP obszar. Nie dotyczy automatycznie Almighty ani szczególnych mocy.
- Powrót do tej samej grupy po ucieczce zachowuje SP wrogów i wykorzystane liczniki zdolności na walkę. Liczniki odświeża nowa wyprawa po powrocie do rzeczywistości; zapis/respawn odtwarza je zgodnie z zapisanym stanem.
- Po zwycięstwie/Hold Up nieprzytomni budzą się z 1 HP i niezmienionym SP, po premiach końca walki. Nie działa po ucieczce ani porażce całej drużyny.
- Po porażce HP/SP ogranicza zarówno stan zapisu, jak i połowa maksimum; minimum 1 HP. Zakończenie wyprawy i powrót kolejnego dnia nadal daje pełne zasoby.
- Wskazówki dla początkującej drużyny i jawne oznaczanie negocjacji/Hold Up na karcie bossa są w rozdziałach przygotowania przeciwników.
- Ataki testowe Shadows mają osobny cennik i nie zostały automatycznie przeliczone według cennika nazwanych skilli.

Uwaga redakcyjna: w pierwotnym opisie raportu Stomach Blow błędnie nazwano Medium. Podręcznik i model testowy mają Heavy; właściwy nowy koszt to 7 HP. Raport został skorygowany. Oryginalne koszty P5R w kolumnach referencyjnych pozostają bez zmian.

## Dane i kontrola

Aktualne wersjonowane dane: `skill_rules_0_8.json`, `skill_level_gates_0_8.json`, `persona_skill_cards_0_5.json`. Nazwy kart i progi nauki nie zmieniły się. Nie traktować wcześniejszych niewersjonowanych plików jako nowszych od tego zestawu.

`update_balanced_manuals.py` odtwarza tę aktualizację ze starszych podręczników. `paginate_balance_update.ps1` aktualizuje spisy treści i numery stron w Microsoft Word oraz eksportuje PDF do wewnętrznej kontroli. `render_balanced_manuals.py` tworzy obrazy stron z tych eksportów. Kontrole i podglądy znajdują się w `qa_balance_update/`.

Testy: `Raport_testow_balansu_2026_10_29.md`, skrypty `balance*.py`, wyniki `balance_tests_2026_10_29/`. Są materiałem badawczym, nie dodatkowymi zasadami. Skrypty testowe nadal odwołują się do starszych podręczników i własnych przełączników poprawek — przed nową serią trzeba świadomie dostosować wejścia, nie zmieniać ich w ciemno. Raport omawia ograniczenia modelu; nie symulowano wszystkich możliwych buildów i pełnej kampanii przez 99 poziomów.

## Preferencje użytkowniczki

Proste reguły, mało kości i obliczeń, szybkie walki; brak Technical i krytyków. Jedna własna rozwijana Persona, maksymalnie osiem skilli, trait Arkany oddzielnie. Bank pięciu Person jako materiał do fuzji i kart. Daily life ma dwa bloki dziennie; wyprawy tylko za dnia. Przeszkody fabularne i śledztwo mają zachęcać do powrotów. Użytkowniczka jest początkującą GM i potrzebuje jasnych, konkretnych zasad bez nadmiernego mikrozarządzania.

