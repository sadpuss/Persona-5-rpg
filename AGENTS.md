# Persona 5 RPG — zasady pracy

Polskojęzyczny projekt RPG Persona 5 / Royal: podręczniki, bestiariusz, dane, ilustracje, aplikacja i badania balansu.

## Role

- Autorka decyduje o systemie, mechanikach i treści podręczników. Nie zmieniaj zasad gry z własnej inicjatywy: zaproponuj zmianę i wprowadź ją po akceptacji. Wyniki balansu to badania, nie obowiązujące zasady.
- Agent odpowiada za kod, narzędzia, Git i GitHub. Autorka nie zna Gita ani programowania: nie wymagaj od niej poleceń, gałęzi ani PR-ów i nie tłumacz ich bez potrzeby.

## Pliki

- Aktualne podręczniki leżą w katalogu głównym: `Persona_5_RPG_Podrecznik_GM.docx`, `Persona_5_RPG_Podrecznik_Gracza.docx`, `Persona_5_RPG_Bestiariusz.docx`. Aplikacja szuka ich tam. Starsze wersje są tylko w historii Git (tag `archiwum-przed-porzadkami`); nie twórz numerowanych kopii.
- `aplikacja/`: kreator Take Your Heart (Electron); `aplikacja/build_data.py` buduje `src/rules.json` z głównych Wordów i `dane/`.
- `dane/`: aktualne dane gry; `dane/kompendium/`: surowe dane P5R i materiały kompendium.
- `ilustracje/`: `bestiary_images/` oraz skrypty i manifesty pobierania ilustracji.
- `badania/balans/`: archiwalne badania balansu (dotyczą starszych podręczników).
- Wyniki narzędzi zapisuj w ignorowanym `out/`, nie w katalogu głównym.
- Bieżący stan projektu: `STAN_PROJEKTU.md`.

## Każda zmiana

1. Zsynchronizuj się z GitHubem: `git pull --rebase --autostash` na `main`. Pracuj wyłącznie na `main`.
2. Uruchom `sprawdz_podreczniki.ps1` (bez PowerShella: `git status` i wyszukanie innych `Persona_5_RPG_*.docx`). Inne rozmowy mogą zmieniać pliki równolegle; nie polegaj na historii czatu.
3. Wykonaj zadanie i sprawdź wynik.
4. Zapisz commit z polskim opisem, dodając jawnie tylko pliki swojego zadania, i wyślij go: `git push`. Nie cofaj cudzej pracy.
5. W odpowiedzi napisz, czy zmiany są wysłane na GitHuba.

Problemy z synchronizacją (konflikt, odrzucony push, cudze niezapisane zmiany): skill `synchronizacja-github`.

## Skille

- `edycja-podrecznika`: każda zmiana w trzech Wordach, porównywanie kopii, odtwarzanie starych wersji.
- `praca-nad-aplikacja`: kod, testy i dane aplikacji.
- `wydanie-aplikacji`: nowa wersja programu na GitHubie.
- `synchronizacja-github`: nietypowe sytuacje z Gitem i GitHubem.

## Styl

- Pisz po polsku, spójnie używaj terminologii i znaków diakrytycznych. Zachowuj nazwy własne, identyfikatory, polecenia i ścieżki. Wyjaśniaj prosto; uruchamianie najlepiej dwuklikiem.
- Czytaj skrypty przed uruchomieniem lub importem: mogą nadpisywać pliki albo korzystać ze starszych wersji.
- Ten przewodnik ma być zwięzły i trwały; bieżący stan zapisuj w `STAN_PROJEKTU.md`, procedury w skillach.
