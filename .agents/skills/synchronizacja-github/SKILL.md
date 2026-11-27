---
name: synchronizacja-github
description: Rozwiązywanie problemów z synchronizacją repozytorium Persona 5 RPG z GitHubem. Użyj, gdy git pull lub git push się nie udaje, wystąpi konflikt (zwłaszcza w plikach .docx), są niezapisane cudze zmiany, lokalna gałąź nie jest main albo brakuje dostępu do GitHuba.
---

# Synchronizacja z GitHubem

Repozytorium: `origin` na GitHubie, jedyna gałąź robocza `main`. Autorka nie zna Gita: rozwiąż problem sam, a ją pytaj wyłącznie o treść („która wersja tego akapitu jest właściwa?”), nigdy o polecenia.

## Zasady

- Nigdy `git push --force`, `git reset --hard` na wspólnej historii, przepisywania historii ani usuwania tagów. Przepisanie historii wymaga osobnej zgody właściciela repozytorium.
- Nie odrzucaj niezapisanych zmian, których nie zrobiłeś. Mogą to być poprawki autorki w Wordzie albo praca innej rozmowy.
- Jeśli lokalnie jesteś na innej gałęzi niż `main`, nie przełączaj jej w ciemno: sprawdź, czy nie ma tam niewysłanych commitów, i dopiero wtedy wróć na `main`.

## Typowe sytuacje

**Niezapisane cudze zmiany.** `git pull --rebase --autostash` je zachowa. Nie dodawaj ich do swojego commita. Zakończone poprawki autorki w trzech głównych Wordach zapisz osobnym commitem (np. „Zapisz poprawki autorki w Podręczniku GM”). Gdy nie wiesz, czy praca jest skończona (np. częściowe zmiany w kodzie), zostaw ją i wspomnij o tym w odpowiedzi.

**Push odrzucony (non-fast-forward).** Ktoś wysłał zmiany w międzyczasie: `git pull --rebase --autostash`, ponów testy, jeśli dotyczyły zmienionych plików, potem `git push`.

**Konflikt w pliku tekstowym (kod, JSON, Markdown).** Połącz obie strony ręcznie, sprawdź wynik (testy, poprawność JSON), `git add`, `git rebase --continue`.

**Konflikt w `.docx`.** Git nie połączy Worda. Przerwij rebase (`git rebase --abort`) albo zachowaj obie wersje jako osobne pliki poza Gitem (`git show origin/main:Plik.docx > out/...`, `git show HEAD:Plik.docx > out/...`), porównaj treść i przenieś zmiany do jednej wersji. Jeśli obie strony zmieniły ten sam fragment, pokaż autorce oba warianty prostymi słowami i zapytaj, który zostaje. Kopie z `out/` usuń po połączeniu.

**Rozjechana historia po porządkach.** Porządki z listopada 2026 (PR #2) przeniosły pliki (`dane/`, `ilustracje/`, `badania/balans/`) i usunęły stare Wordy. Lokalny commit dotykający starych ścieżek przenieś na nowe miejsce zamiast przywracać usunięte pliki.

**Brak dostępu do GitHuba (uwierzytelnianie, sieć).** Zapisz commit lokalnie i napisz wprost, że zmiany nie są jeszcze wysłane na GitHuba. Nie zapisuj tokenów w repozytorium.
