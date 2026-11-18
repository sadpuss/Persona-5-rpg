# Take Your Heart — aplikacja desktopowa

Kreator bohatera i własnej Persony do Persona RPG. Aplikacja działa lokalnie, we własnym oknie, bez serwera i konta.

## Uruchamianie bez terminala

Kliknij dwukrotnie **Uruchom kreator.lnk** w tym folderze. Alternatywnie otwórz `release/win-unpacked/Take Your Heart.exe`. Nie otwieraj głównego `index.html`: to obecnie plik źródłowy projektu React.

Program zapisuje kartę automatycznie na tym komputerze. „Zapisz do pliku” tworzy przenośny zapis JSON. „Otwórz plik” przyjmuje również pliki z wcześniejszego prototypu. W kroku „Gotowe karty” są osobne przyciski „Zapisz PDF” oraz „Podgląd i druk”.

## Wydania i aktualizacje

Po opublikowaniu pierwszego wydania otwórz w repozytorium GitHub sekcję **Releases**. Na Windows uruchom pobrany instalator `.exe`, a na Linuksie uruchom plik `.AppImage` z uprawnieniem do wykonywania. Te wersje sprawdzają dostępność aktualizacji po starcie i co cztery godziny. Pobierają ją w tle i instalują przy zamykaniu programu. Na macOS instalator ma rozszerzenie `.dmg`, a automatyczne aktualizacje wymagają podpisanego wydania.

Wydanie uruchamia się w GitHubie przez **Actions → Wydanie aplikacji → Run workflow** na gałęzi `main`. Zaznaczenie **Opublikuj wydanie po zbudowaniu paczek** publikuje komplet plików po udanej kompilacji i testach na wszystkich systemach. Domyślnie workflow tylko buduje paczki do sprawdzenia. Numer wydania pochodzi z `package.json`. Przed kolejnym wydaniem zwiększ wersję aplikacji poleceniem `npm version <numer> --no-git-tag-version` w folderze `aplikacja` i zapisz oba pliki `package*.json` w Git.

Podpisywanie pakietu macOS można włączyć przez sekrety GitHub Actions `MAC_CSC_LINK` (certyfikat Developer ID Application w formacie P12, jako Base64) i `MAC_CSC_KEY_PASSWORD` (hasło certyfikatu). Bez nich workflow buduje DMG do ręcznej instalacji.

Do przeniesienia programu na inny komputer z Windows trzeba skopiować **cały folder win-unpacked**. Sam plik EXE nie wystarczy. Postać przenosi się oddzielnie przez plik JSON. Wersja Linux x64 jest w `release/Take-Your-Heart-0.5.0-linux-x64.tar.gz`: rozpakuj archiwum na Linuxie i uruchom `take-your-heart` dwuklikiem. Szczegóły i przenoszenie postaci opisuje [LINUX.txt](LINUX.txt). Sprawdzono format ELF, zawartość i prawa wykonywania w archiwum; okna aplikacji na Linuxie jeszcze nie testowano. Paczki Mac nadal nie zweryfikowano.

## Co zachowano

- Sześć kroków, swobodne pomijanie pól i podgląd na żywo.
- Bohater i osobista Persona, Arkany i traity, własna ilustracja, słabość i odporność.
- Zestawy startowe, katalog skilli z filtrami, automatyczne rozliczanie darmowych wyborów i punktów nauki.
- Start na poziomie 1–99, EXP i awanse bez leczenia, zasoby, ekwipunek i notatki.
- Dwie osobne karty do PDF/druku, opcjonalny indeks skilli, stylizowany i uproszczony wygląd.
- Ostrzeżenia nie trafiają na wydruk. Prywatne notatki i uzgodnienia z GM nie są drukowane.

Zasady: GM 0.8 / Gracz 0.5. Wszystkie 346 umiejętności dostępnych przez zwykłą naukę mają opis działania; pozostałe wpisy są oznaczone jako moce unikatowe, nieużywane mechaniki lub źródłowe traity. Premie HP Rydwanu i SP Doradcy są automatyczne; pozostałe pasywy i dodatkowe premie maksimum wpisuje się ręcznie. Skill cards nie mają jeszcze własnego ekwipunku. Brak Velvet Roomu, fuzji, historii/cofania zmian i migracji wersji zasad. To zachowane ograniczenia prototypu, a nie zmiana zasad gry.

## Dla osoby rozwijającej aplikację

Kod jest w TypeScript i React. Electron obsługuje okno, pliki, automatyczny zapis, kopię zapasową oraz eksport PDF. Renderer nie ma dostępu do Node.js; używa wąskiego interfejsu `contextBridge`, włączonej izolacji kontekstu i sandboxa. Zgodnie z [dokumentacją bezpieczeństwa Electron](https://www.electronjs.org/docs/latest/tutorial/security) ograniczono nawigację, nowe okna, uprawnienia i nadawców IPC.

Struktura:

- `src/App.tsx` — nawigacja, biblioteka postaci i stan interfejsu React.
- `src/Dashboard.tsx` — pulpit sesji, rozwój, nauka, ekwipunek i notatki.
- `src/Manuals.tsx`, `electron/manuals.ts` — otwieranie i pobieranie bieżących podręczników Word.
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
node tests/session.cjs --packaged
```

`npm run dev` kompiluje projekt i uruchamia Electron bez serwera. Po zmianach uruchom ponownie. `npm start` otwiera ostatnią kompilację. `npm run package:linux` buduje przenośną paczkę Linux x64 `.tar.gz` także na Windowsie. Skrypt `scripts/package-linux.cjs` sprawdza ELF, dodaje instrukcję i launcher, ustawia prawa wykonywania w archiwum, kontroluje jego zawartość i zapisuje SHA256. Korzysta z biblioteki `tar` dostarczanej z electron-builder. `npm run package:linux:appimage` służy do budowania AppImage na Linuxie; na tym Windowsie próba zakończyła się błędem uprawnień dowiązań. `npm run package:mac` buduje DMG na macOS.

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


## Prowadzenie postaci i podręczniki 0.5.0

Po zakończeniu kreatora przyciskiem „Rozpocznij grę” otwiera się pulpit. Także wybór aktywnej postaci z biblioteki i ponowne uruchomienie otwierają jej pulpit. Przełączniki „Prowadzenie” i „Kreator” pozwalają wrócić do edycji.

Prowadzenie obejmuje aktualne HP/SP i dodawanie/odejmowanie zasobów, odpoczynek po potwierdzeniu, EXP z podglądem awansu, wspólne poziomy i punkty nauki, naukę nowych skilli z wyborem zastępowanego przy ośmiu miejscach, ekwipunek z ilościami i opisami, prywatne notatki oraz rangi cech społecznych. Awans nie leczy. Zapominanie skilli nie zwraca punktów nauki. Premie pasywów, buffy, statusy i efekty przedmiotów nadal rozlicza gracz według opisu; nie ma automatycznego przebiegu walki.

Pole `items` jest opcjonalnym rozszerzeniem istniejącego formatu zapisu: stare karty otrzymują pustą listę. Dawny opis `inventory` pozostaje nietknięty i jest dostępny w notatkach o ekwipunku. Lista przedmiotów oraz dawny opis są uwzględniane w PDF i eksporcie JSON. Notatki sesji nie są drukowane.

Przycisk „Podręczniki” jest dostępny u góry w obu trybach. „Otwórz Word” uruchamia systemowy program do DOCX, a „Pobierz Word” zapisuje kopię w wybranym miejscu. Aplikacja odszukuje trzy główne, nienumerowane Wordy w folderze projektu i odczytuje je przy każdym otwarciu/pobraniu. Aktualizacja pliku w projekcie jest więc od razu widoczna bez przebudowy aplikacji. Jeśli folder projektu nie jest dostępny (np. na drugim komputerze), aplikacja korzysta z kopii dołączonych do swojej wersji i wyraźnie wskazuje to w oknie podręczników.

`scripts/copy-manuals.cjs` wykonuje przy budowaniu odczyt i kopię trzech głównych dokumentów, sprawdzając niezmienność źródła. Nie edytuje Wordów. Kopie są w ignorowanym `assets/manuals/`, a do paczki trafiają jako zwykłe pliki `resources/podreczniki/`, żeby można było otworzyć je w Wordzie. Spakowany program nie korzysta z serwera ani zewnętrznych linków do dokumentów.
