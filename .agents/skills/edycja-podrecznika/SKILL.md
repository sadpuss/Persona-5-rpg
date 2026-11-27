---
name: edycja-podrecznika
description: Procedura zmiany podręczników Word (GM, Gracza, Bestiariusz) w Persona 5 RPG. Użyj przy każdej edycji, porównaniu lub odtwarzaniu pliku Persona_5_RPG_*.docx, gdy na dysku pojawi się inna kopia podręcznika albo gdy zmiana zasad wymaga aktualizacji danych.
---

# Edycja podręcznika

Edytujemy tylko trzy pliki z katalogu głównego: `Persona_5_RPG_Podrecznik_GM.docx`, `Persona_5_RPG_Podrecznik_Gracza.docx`, `Persona_5_RPG_Bestiariusz.docx`. Git przechowuje ich kolejne zapisy, więc nie twórz nazw `_0_9`, `_przed_*` itp. Treść i mechaniki należą do autorki: wprowadzaj zmiany, które zleciła lub zaakceptowała.

## Przed edycją

1. Zsynchronizuj `main` z GitHubem (patrz `AGENTS.md`).
2. Uruchom `sprawdz_podreczniki.ps1` (dwuklik: `Sprawdz_podreczniki.cmd`). Pokazuje datę, rozmiar i SHA256 trzech Wordów, ostrzega `DO POROWNANIA` przed innymi kopiami i wypisuje `git status`. Bez PowerShella zrób to samo ręcznie: `sha256sum Persona_5_RPG_*.docx` i `git status --short`.
3. Jeśli główny Word ma niezapisane w Git zmiany, to najczęściej poprawki autorki z Worda. Nie nadpisuj ich: zapisz je najpierw osobnym commitem albo, gdy nie wiesz, czy skończyła, zapytaj prosto, czy zakończyła edycję pliku.
4. Każdy inny `Persona_5_RPG_*.docx` (np. z innej rozmowy) porównaj z głównym, przenieś brakujące zmiany do głównego i usuń kopię. Nie wybieraj wersji po numerze ani dacie.
5. Zapamiętaj SHA256 pliku, który edytujesz.

## Edycja

- Upewnij się, że plik nie jest otwarty w Wordzie (plik blokady `~$...docx` obok). Jeśli jest, poproś o zamknięcie dokumentu.
- Nie prowadź równolegle dwóch edycji tego samego dokumentu. Git nie łączy treści Worda.
- Przed zapisem ponownie sprawdź SHA256 wejścia. Jeśli się zmienił, odczytaj dokument ponownie i połącz zmiany; nie nadpisuj cudzej pracy.
- Zachowuj style, tabele i układ dokumentu. Zrzuty `*.docx.txt` są generowane i ignorowane; źródłem jest Word.

## Po edycji

- Obejrzyj wyrenderowany układ zmienionych stron (np. konwersja do PDF przez LibreOffice headless albo Word) i sprawdź spis treści, tabele, podziały stron.
- Sprawdź powiązane dane w `dane/`, jeśli zmiana dotyczy skilli, kosztów, progów poziomów, EXP lub Shadows. Dane zmieniaj tylko zgodnie z decyzją autorki.
- Jeśli zmieniły się tabele skilli, Arkan lub zestawów startowych, odbuduj dane aplikacji: skill `praca-nad-aplikacja`.
- Aplikacja odczytuje Wordy z katalogu głównego przy każdym otwarciu, więc sama zmiana treści nie wymaga przebudowy programu. Wydana wersja ma własne kopie podręczników: aktualizuje je dopiero nowe wydanie.
- Zaktualizuj `STAN_PROJEKTU.md`, jeśli zmienił się stan projektu.
- Commit z polskim opisem zmiany treści, potem `git push`.

## Starsze wersje

Usunięte wersje (GM 0.3–0.8, Gracza 0.1–0.5, Bestiariusz 0.1–0.5, `Persona_5_RPG_Zasady_*`, `*_przed_*`) i jednorazowe skrypty, które je tworzyły, są pod tagiem `archiwum-przed-porzadkami`. Odtworzenie jednego pliku do porównania:

```
git restore --source archiwum-przed-porzadkami -- Persona_5_RPG_Podrecznik_GM_0_7.docx
```

Odtworzony plik służy tylko do odczytu lub porównania. Po użyciu usuń go i nie dodawaj do Git. Starsze wersje głównych plików po porządkach: `git log -- Persona_5_RPG_Podrecznik_GM.docx`. Aktualny dokument nie może zostać odtworzony ze starszego z utratą późniejszych poprawek.
