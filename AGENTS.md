# Persona 5 RPG — zasady pracy

Polskojęzyczny projekt RPG Persona 5 / Royal: podręczniki, bestiariusz, dane, ilustracje, aplikacja i badania balansu.

## Pliki

- Aktualne podręczniki leżą w katalogu głównym repozytorium (przed edycją zawsze sprawdź aktualność): `Persona_5_RPG_Podrecznik_GM.docx`, `Persona_5_RPG_Podrecznik_Gracza.docx`, `Persona_5_RPG_Bestiariusz.docx`. Aplikacja szuka ich właśnie tam.
- Na dysku są tylko trzy główne Wordy. Starsze wersje (numerowane, `*_przed_*`, `Persona_5_RPG_Zasady_*`) i jednorazowe skrypty, które je tworzyły, są w historii Git pod tagiem `archiwum-przed-porzadkami`. Nie twórz numerowanych kopii. Zrzuty `*.docx.txt` są generowane i ignorowane; źródłem układu i tabel jest Word.
- `aplikacja/`: kreator Take Your Heart (Electron); `aplikacja/build_data.py` buduje `src/rules.json` z głównych Wordów i `dane/`.
- `dane/`: aktualne dane gry (`skill_rules.json`, `skill_level_gates.json`, `persona_skill_cards.json`, tabele EXP, nazwy Shadows); `dane/kompendium/`: surowe dane P5R i materiały źródłowe kompendium.
- `ilustracje/`: `bestiary_images/` oraz skrypty i manifesty pobierania ilustracji.
- `badania/balans/`: archiwalne badania balansu (dotyczą starszych podręczników).
- Wyniki narzędzi zapisuj w ignorowanym `out/`, nie w katalogu głównym.

## Obowiązkowe zasady

- Pisz po polsku, spójnie używaj terminologii i znaków diakrytycznych. Zachowuj nazwy własne, identyfikatory, polecenia i ścieżki. Wyjaśniaj prosto: użytkowniczka nie programuje. Podawaj konkretne kroki, w miarę możliwości uruchamianie dwuklikiem.
- Przed KAŻDĄ zmianą przeczytaj `GIT_I_PODRECZNIKI.md`, uruchom `sprawdz_podreczniki.ps1`, sprawdź `git status` i wersje wszystkich trzech podręczników na dysku. Inne rozmowy mogą je aktualizować; nie polegaj na historii czatu, samym numerze ani dacie pliku.
- Edytuj główne Wordy bez numerów. Każdy inny `Persona_5_RPG_*.docx` na dysku (np. z innej rozmowy) porównaj z głównym, przenieś zmiany i usuń kopię. Przed zapisem ponownie sprawdź SHA256 wejścia; jeśli się zmienił, odczytaj plik ponownie i połącz zmiany. Nie nadpisuj równoległej pracy.
- Obsługuj Git za użytkowniczkę. Po kontroli zapisuj spójne zmiany z polskim opisem, dodając jawnie tylko pliki własnego zadania. Nie cofaj cudzej pracy. Historię trzymaj w Git zamiast tworzyć kolejne numerowane Wordy.
- Czytaj skrypty przed uruchomieniem lub importem: mogą nadpisywać pliki albo korzystać ze starszych wersji. Sprawdzaj wejścia i wyjścia.
- Przy zmianach dokumentów sprawdź powiązane dane i źródła, wykonaj odpowiednie QA i obejrzyj wyrenderowany układ. Wyniki balansu to badania, nie automatycznie obowiązujące zasady.
- Ten przewodnik ma być zwięzły i trwały; bieżący stan zapisuj w dokumentach, danych i `STAN_PROJEKTU.md`.
