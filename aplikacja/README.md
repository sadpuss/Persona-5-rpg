# Take Your Heart — aplikacja desktopowa

Kreator bohatera i własnej Persony do Persona RPG. Aplikacja działa lokalnie, we własnym oknie, bez serwera i konta.

## Uruchamianie bez terminala

Kliknij dwukrotnie **Uruchom kreator.lnk** w tym folderze. Alternatywnie otwórz `release/win-unpacked/Take Your Heart.exe`. Nie otwieraj głównego `index.html`: to obecnie plik źródłowy projektu React.

Program zapisuje kartę automatycznie na tym komputerze. „Zapisz do pliku” tworzy przenośny zapis JSON. „Otwórz plik” przyjmuje również pliki z wcześniejszego prototypu. W kroku „Gotowe karty” są osobne przyciski „Zapisz PDF” oraz „Podgląd i druk”.

Do przeniesienia programu na inny komputer z Windows trzeba skopiować **cały folder win-unpacked**. Sam plik EXE nie wystarczy. Postać przenosi się oddzielnie przez plik JSON. Mac i Linux mają konfigurację budowania, ale ich paczek nie zweryfikowano na tym komputerze.

## Co zachowano

- Sześć kroków, swobodne pomijanie pól i podgląd na żywo.
- Bohater i osobista Persona, Arkany i traity, własna ilustracja, słabość i Resist.
- Zestawy startowe, katalog skilli z filtrami, automatyczne rozliczanie darmowych wyborów i punktów nauki.
- Start na poziomie 1–99, EXP i awanse bez leczenia, zasoby, ekwipunek i notatki.
- Dwie osobne karty do PDF/druku, opcjonalny indeks skilli, stylizowany i uproszczony wygląd.
- Ostrzeżenia tylko w kreatorze. Prywatne notatki i uzgodnienia z GM nie są drukowane.

Zasady: GM 0.8 / Gracz 0.5. Wszystkie 346 umiejętności dostępnych przez zwykłą naukę ma opis działania; pozostałe wpisy są oznaczone jako moce unikatowe, nieużywane mechaniki lub źródłowe traity. Premie HP Rydwanu i SP Doradcy są automatyczne; pozostałe pasywy i dodatkowe premie maksimum wpisuje się ręcznie. Skill cards nie mają jeszcze własnego ekwipunku. Brak Velvet Roomu, fuzji, historii/cofania zmian i migracji wersji zasad. To zachowane ograniczenia prototypu, a nie zmiana zasad gry.

## Dla osoby rozwijającej aplikację

Kod jest w TypeScript i React. Electron obsługuje okno, pliki, automatyczny zapis, kopię zapasową oraz eksport PDF. Renderer nie ma dostępu do Node.js; używa wąskiego interfejsu `contextBridge`, włączonej izolacji kontekstu i sandboxa. Zgodnie z [dokumentacją bezpieczeństwa Electron](https://www.electronjs.org/docs/latest/tutorial/security) ograniczono nawigację, nowe okna, uprawnienia i nadawców IPC.

Struktura:

- `src/App.tsx` — kreator i stan interfejsu React.
- `src/model.ts` — typy, obliczenia, import i ostrzeżenia.
- `src/Sheets.tsx`, `src/Preview.tsx` — karty oraz podgląd.
- `src/bridge.ts` — typy interfejsu między Reactem i Electronem.
- `electron/main.ts`, `electron/preload.ts` — część desktopowa.
- `src/rules.json` — lokalne dane, bez pobierania z internetu.
- `build_data.py` — odczyt DOCX/JSON i odbudowa danych, bez edycji podręczników.
- `prototyp-html/` — zachowany poprzedni prototyp, z własnym `index.html`.
- `tests/` — testy reguł i działania aplikacji; wyniki i zrzuty w `qa-desktop/`.

Wymagany jest Node.js zgodny z wymaganiami zainstalowanych wersji narzędzi; użyto Node 26. Zależności i ich wersje są w `package-lock.json`.

```sh
npm ci
npm run dev
npm test
npm run test:desktop
npm run package:win
node tests/desktop.cjs --packaged
```

`npm run dev` kompiluje projekt i uruchamia Electron bez serwera. Po zmianach uruchom ponownie. `npm start` otwiera ostatnią kompilację. Paczki macOS i Linux buduje się na odpowiednich systemach przez `npm run package:mac` i `npm run package:linux`.

Lokalna biblioteka: `app.getPath('userData')/biblioteka.json` (spis i ostatnio otwarta postać) oraz `postacie/<id>.json` (każda karta osobno). Na Windows katalog jest zwykle w `%APPDATA%/Take Your Heart/`. Pliki mają kopie `.bak`; zapisy są kolejkowane, a zapis konkretnej karty zawiera jej identyfikator, żeby opóźniona operacja nie zmieniła innej postaci. Przełączanie najpierw zapisuje bieżącą kartę i jest zatrzymywane w razie błędu zapisu. Przy uszkodzeniu pliku aplikacja próbuje odczytać kopię. Dawny `postac.json` jest automatycznie przenoszony do biblioteki podczas pierwszego uruchomienia, a plik źródłowy pozostaje nietknięty. Zapisów z localStorage przeglądarki nadal nie odczytuje się automatycznie — trzeba pobrać JSON ze starego prototypu.

Test desktopowy używa osobnego profilu w `qa-desktop/`, nie dotyka rzeczywistych kart. Systemowe okna wyboru pliku są w teście zastępowane wskazaniem pliku testowego; sam zapis i PDF wykonuje Electron.


## Poprawki interfejsu 0.2.1

Menu kroków pozostaje widoczne przy przewijaniu, także przy niższym oknie. Kolejność: bohater → poziom i rozwój → Arkana → Persona → umiejętności → gotowe karty. Zasoby do prowadzenia sesji (aktualne HP/SP i dodatkowe premie) są dostępne po rozpoczęciu gry z ostatniego kroku. Oba style kart różnią się również w podglądzie ekranowym. „Podgląd i druk” otwiera rzeczywisty PDF w osobnym oknie z wbudowanym przyciskiem drukowania.

Na życzenie użytkowniczki lista słabości i odporności dopuszcza także Physical i Gun, a nazwy są po polsku. To ustawienie aplikacji; ta zmiana nie edytuje podręczników ani historycznego zestawu reguł zapisanego na karcie.


## Biblioteka postaci 0.3.0

Na górze okna jest przycisk „Nowa postać” i lista „Lokalne postacie”. Każda karta jest zapisywana oddzielnie, również jako niedokończony szkic. Przełączanie nie wymaga eksportu plików; po ponownym uruchomieniu otwiera się ostatnio używana karta. „Otwórz plik” dodaje kolejną postać, a nie zastępuje bieżącej. Własny eksport JSON nadal służy do przekazania postaci GM albo przeniesienia na drugi komputer.


## Czytelniejszy kreator 0.4.0

- „Usuń postać” usuwa wybraną kartę po potwierdzeniu; eksporty JSON/PDF pozostają nietknięte. Usunięcie ostatniej karty otwiera nową pustą postać.
- Opisy Arkan są bezpośrednio na przyciskach. Nad tytułami nie ma powtarzanego oznaczenia kroku; numer jest w bocznym menu.
- Przy umiejętnościach widoczny jest licznik czterech darmowych wyborów oraz limitu dwóch różnych żywiołów. Kolejne wybory są rozliczane automatycznie, bez wybierania sposobu pozyskania. Importowane zapisy nadal zachowują dotychczasowe źródła nauki, w tym skill cards.
- Każda wybrana umiejętność ma osobny przycisk „Usuń” z koszem. Opisy używają pełnych nazw typów obrażeń, również w PDF.
- `build_data.py` czyta główne podręczniki i wersjonowane dane. Uzupełnia podstawowe opisy według tabel celu/statusu, wspólnej skali obrażeń i zasad odporności; sprawdza skróty wejścia przed zapisem. Zapisuje wyłącznie `src/rules.json`, bez edycji Wordów i archiwalnego prototypu.
- Ikona programu i okna to czerwona gwiazda. `assets/generate-icon.cjs` odtwarza SVG, PNG i wielorozmiarowe ICO z tej samej figury. Windows ma włączone osadzanie ikony i metadanych EXE, bez podpisywania programu.
