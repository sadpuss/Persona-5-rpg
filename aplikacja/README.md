# Take Your Heart — aplikacja desktopowa

Kreator bohatera i własnej Persony do Persona RPG. Aplikacja działa lokalnie, we własnym oknie, bez serwera i konta.

## Uruchamianie bez terminala

Kliknij dwukrotnie **Uruchom kreator.lnk** w tym folderze. Alternatywnie otwórz `release/win-unpacked/Take Your Heart.exe`. Nie otwieraj głównego `index.html`: to obecnie plik źródłowy projektu React.

Program zapisuje kartę automatycznie na tym komputerze. „Zapisz do pliku” tworzy przenośny zapis JSON. „Otwórz plik” przyjmuje również pliki z wcześniejszego prototypu. W kroku „Gotowe karty” są osobne przyciski „Zapisz PDF” oraz „Podgląd i druk”.

Do przeniesienia programu na inny komputer z Windows trzeba skopiować **cały folder win-unpacked**. Sam plik EXE nie wystarczy. Postać przenosi się oddzielnie przez plik JSON. Mac i Linux mają konfigurację budowania, ale ich paczek nie zweryfikowano na tym komputerze.

## Co zachowano

- Sześć kroków, swobodne pomijanie pól i podgląd na żywo.
- Bohater i osobista Persona, Arkany i traity, własna ilustracja, słabość i Resist.
- Zestawy startowe, katalog skilli z filtrami, nauka za punkty lub skill card.
- Start na poziomie 1–99, EXP i awanse bez leczenia, zasoby, ekwipunek i notatki.
- Dwie osobne karty do PDF/druku, opcjonalny indeks skilli, stylizowany i uproszczony wygląd.
- Ostrzeżenia tylko w kreatorze. Prywatne notatki i uzgodnienia z GM nie są drukowane.

Zasady: GM 0.8 / Gracz 0.5. Część opisów z pełnego katalogu nadal odsyła do podręcznika. Premie HP Rydwanu i SP Doradcy są automatyczne; pozostałe pasywy i dodatkowe premie maksimum wpisuje się ręcznie. Skill cards nie mają jeszcze własnego ekwipunku. Brak Velvet Roomu, fuzji, historii/cofania zmian i migracji wersji zasad. To zachowane ograniczenia prototypu, a nie zmiana zasad gry.

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

Automatyczny zapis: `app.getPath('userData')/postac.json`, na Windows zwykle `%APPDATA%/Take Your Heart/`. Poprzedni prawidłowy zapis jest w `postac.json.bak`. Zapisy są kolejkowane i zastępowane przez plik tymczasowy. Przy uszkodzeniu pliku aplikacja próbuje odczytać kopię. Jeśli odczyt lub wersja zasad są nieprawidłowe, zapis jest wstrzymany do świadomego otwarcia innej karty lub rozpoczęcia nowej. Nowy system zapisu nie odczytuje automatycznie danych localStorage przeglądarki; ze starego prototypu trzeba pobrać JSON.

Test desktopowy używa osobnego profilu w `qa-desktop/`, nie dotyka rzeczywistych kart. Systemowe okna wyboru pliku są w teście zastępowane wskazaniem pliku testowego; sam zapis i PDF wykonuje Electron.


## Poprawki interfejsu 0.2.1

Menu kroków pozostaje widoczne przy przewijaniu, także przy niższym oknie. Kolejność: bohater → poziom i rozwój → Arkana → Persona → umiejętności → gotowe karty. Zasoby do prowadzenia sesji (aktualne HP/SP i dodatkowe premie) są dostępne po rozpoczęciu gry z ostatniego kroku. Oba style kart różnią się również w podglądzie ekranowym. „Podgląd i druk” otwiera rzeczywisty PDF w osobnym oknie z wbudowanym przyciskiem drukowania.

Na życzenie użytkowniczki lista słabości i odporności dopuszcza także Physical i Gun, a nazwy są po polsku. To ustawienie aplikacji; ta zmiana nie edytuje podręczników ani historycznego zestawu reguł zapisanego na karcie.
