---
name: praca-nad-aplikacja
description: Praca nad kodem aplikacji Take Your Heart (Electron, React, TypeScript) w folderze aplikacja/ projektu Persona 5 RPG. Użyj przy zmianach kodu, testach, budowaniu, uruchamianiu programu i odbudowie danych src/rules.json z podręczników i dane/.
---

# Praca nad aplikacją

Kod należy do agenta; zasady gry do autorki. Aplikacja ma odzwierciedlać podręczniki, a nie wprowadzać własnych mechanik. Opis architektury i struktury plików: `aplikacja/README.md`.

## Polecenia (w folderze `aplikacja/`)

```sh
npm ci                  # zależności według package-lock.json
npm test                # testy logiki (tsx --test)
npm run build           # kopiuje podręczniki, sprawdza typy, buduje Electron i Vite
npm run dev             # build + uruchomienie okna
npm run test:desktop    # testy okna: tests/desktop.cjs i tests/session.cjs
npm run package:win     # release/win-unpacked (na nim działa skrót „Uruchom kreator.lnk”)
```

- Na Linuksie bez ekranu testy okna uruchamiaj przez `xvfb-run`. `tests/desktop.cjs` ma znany problem z kliknięciem w ukrytym oknie (opisany w issue #1); nie uznawaj tego błędu za skutek swojej zmiany bez sprawdzenia.
- `aplikacja/prototyp-html/qa.cjs` ma na sztywno ścieżki Playwrighta i Edge z Windowsa.
- Wyniki testów i zrzuty trafiają do ignorowanych `qa-desktop/` i `qa-prototyp/`.

## Dane z podręczników

`python aplikacja/build_data.py` czyta tabele z głównych Wordów (Gracza i GM) oraz `dane/skill_level_gates.json` i `dane/skill_rules.json`, a zapisuje wyłącznie `aplikacja/src/rules.json`. Nie edytuje Wordów. Uruchom go po zmianie tabel skilli, Arkan, zestawów startowych lub danych w `dane/`, potem `npm test` i przejrzyj `git diff aplikacja/src/rules.json`. Nieoczekiwane zmiany w `rules.json` mogą oznaczać zmienioną strukturę tabeli w Wordzie.

## Przed zapisem

- `npm test` i `npm run build` muszą przejść. Przy zmianach okna, zapisu postaci lub PDF uruchom też testy okna.
- Zachowaj izolację kontekstu, sandbox i wąski mostek `preload` Electrona.
- Zmiana formatu zapisu postaci musi czytać stare pliki JSON (biblioteka w `userData`, eksporty).
- Po zmianach widocznych dla użytkowniczki zaktualizuj `aplikacja/README.md` i `aplikacja/URUCHOMIENIE.txt`, jeśli opisują zmienione działanie.
- Nowe wydanie programu: skill `wydanie-aplikacji`.
