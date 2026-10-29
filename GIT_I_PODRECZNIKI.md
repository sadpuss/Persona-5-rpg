# Podręczniki i historia zmian

Od tej chwili edytujemy trzy pliki w katalogu głównym:

- `Persona_5_RPG_Podrecznik_GM.docx`
- `Persona_5_RPG_Podrecznik_Gracza.docx`
- `Persona_5_RPG_Bestiariusz.docx`

Git przechowuje kolejne zapisy tych samych plików. Nie trzeba tworzyć nazw 0_9, 0_10 itd. Dotychczasowe wersje pozostają na miejscu, ponieważ korzystają z nich starsze skrypty. Kopie startowe pochodzą z GM 0.8, Gracza 0.5 i Bestiariusza 0.5.

Git obsługuje Codex. Użytkowniczka otwiera i edytuje zwykłe dokumenty Word. Historia jest lokalna na tym komputerze; nie jest kopią na innym dysku ani publikacją w internecie.

Przed każdą zmianą Codex czyta AGENTS.md, uruchamia `sprawdz_podreczniki.ps1`, sprawdza `git status` oraz ponownie wyszukuje wszystkie wersje trzech dokumentów. Nowy plik ze starej rozmowy wymaga porównania i przeniesienia zmian do pliku głównego. Nie wolno automatycznie nadpisywać go na podstawie samego numeru wersji lub daty.

Przed zapisem należy ponownie sprawdzić skrót SHA256 pliku wejściowego. Jeśli zmienił się w trakcie pracy, trzeba ponownie odczytać dokument i połączyć zmiany. Nie prowadzić jednocześnie dwóch edycji tego samego dokumentu. Git nie łączy automatycznie treści Worda.

Po zakończeniu spójnej zmiany Codex sprawdza wynik i zapisuje w Git tylko pliki należące do swojej pracy, z polskim opisem. Nie cofa i nie zapisuje cudzych zmian bez sprawdzenia. Nie uruchamia starszych skryptów bez sprawdzenia ich wejść i wyjść. Aktualny dokument nie może zostać odtworzony ze starszego z utratą późniejszych poprawek.

Kontrolę wersji można też uruchomić dwuklikiem: `Sprawdz_podreczniki.cmd`. Nie modyfikuje ona podręczników.
