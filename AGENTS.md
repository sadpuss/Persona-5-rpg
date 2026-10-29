# Persona 5 RPG — zasady pracy

Polskojęzyczny projekt RPG Persona 5 / Royal: podręczniki, bestiariusz, dane, ilustracje, aplikacja i badania balansu. Większość plików znajduje się w katalogu głównym.

## Pliki

- Główne dokumenty: `Persona_5_RPG_Podrecznik_GM.docx`, `Persona_5_RPG_Podrecznik_Gracza.docx`, `Persona_5_RPG_Bestiariusz.docx`.
- Numerowane Wordy, `*_przed_*` i `Persona_5_RPG_Zasady_*` to archiwum i wejścia starszych skryptów; zachowuj je. `*.docx.txt` służą do czytania, Word jest źródłem układu i tabel.
- `*.py`, `paginate_*.ps1`: przetwarzanie dokumentów, paginacja i eksport PDF; `p5*.json`, `skill_*.json`, `persona_skill_cards*`, `exp_*.json`: dane gry.
- `bestiary_images/`, `bestiary_image*.json`: ilustracje; `qa_*/`, `*_audit.*`: kontrole; `balance*.py`, `balance_tests_*/`: badania balansu; `*.ts`, `repo_tree.json`: materiały źródłowe kompendium.

## Obowiązkowe zasady

- Pisz po polsku, spójnie używaj terminologii i znaków diakrytycznych. Zachowuj nazwy własne, identyfikatory, polecenia i ścieżki. Wyjaśniaj prosto: użytkowniczka nie programuje. Podawaj konkretne kroki, w miarę możliwości uruchamianie dwuklikiem.
- Przed KAŻDĄ zmianą przeczytaj `GIT_I_PODRECZNIKI.md`, uruchom `sprawdz_podreczniki.ps1`, sprawdź `git status` i wersje wszystkich trzech podręczników na dysku. Inne rozmowy mogą je aktualizować; nie polegaj na historii czatu, samym numerze ani dacie pliku.
- Edytuj główne Wordy bez numerów. Nowe lub zmienione wersje archiwalne porównaj i uwzględnij przed pracą. Przed zapisem ponownie sprawdź SHA256 wejścia; jeśli się zmienił, odczytaj plik ponownie i połącz zmiany. Nie nadpisuj równoległej pracy.
- Obsługuj Git za użytkowniczkę. Po kontroli zapisuj spójne zmiany z polskim opisem, dodając jawnie tylko pliki własnego zadania. Nie cofaj cudzej pracy. Historię trzymaj w Git zamiast tworzyć kolejne numerowane Wordy.
- Czytaj skrypty przed uruchomieniem lub importem: mogą nadpisywać pliki albo korzystać ze starszych wersji. Sprawdzaj wejścia i wyjścia.
- Przy zmianach dokumentów sprawdź powiązane dane i źródła, wykonaj odpowiednie QA i obejrzyj wyrenderowany układ. Wyniki balansu to badania, nie automatycznie obowiązujące zasady.
- Ten przewodnik ma być zwięzły i trwały; bieżący stan zapisuj w dokumentach, danych i `STAN_PROJEKTU.md`.
