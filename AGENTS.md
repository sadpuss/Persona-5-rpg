# Workspace guide

This is a Polish-language Persona 5 / Persona 5 Royal tabletop RPG design and publishing workspace. It contains rulebooks, a bestiary, supporting game data, document-generation scripts, illustrations, and balance research.

## Where things are

Most documents, scripts, and data files live in the root directory.

| Files or folders | General role |
| --- | --- |
| `Persona_5_RPG_Podrecznik_GM_*.docx` | GM handbooks. |
| `Persona_5_RPG_Podrecznik_Gracza_*.docx` | Player handbooks. |
| `Persona_5_RPG_Bestiariusz_*.docx` | Bestiary documents. |
| `Persona_5_RPG_Zasady_*.docx` | Earlier combined rules documents. |
| `*_przed_*.docx` | Backups from before particular changes. |
| `*.docx.txt` | Text extracts for convenient reading; consult the Word documents for formatting and tables. |
| `*.py` | Document generation/refinement, data processing, image handling, QA, and balance scripts. Names generally indicate their purpose. |
| `paginate_*.ps1` | Word pagination and PDF-export helpers. |
| `p5*.json`, `skill_*.json`, `persona_skill_cards*`, `exp_*.json` | Game reference data and tabletop adaptation data. |
| `*.ts`, `repo_tree.json` | Reference material from the upstream compendium project. |
| `bestiary_images/`, `bestiary_image*.json` | Illustration assets and supporting image metadata. |
| `qa_*/` | Document QA outputs, such as PDFs, rendered pages, text extracts, and reports. |
| `balance*.py`, `balance_tests_*/` | Balance simulation tools and their results. |
| `*_audit.*` | Reports from document or data processing stages. |

## Working conventions

- Obowiązkowo przed KAŻDĄ zmianą sprawdź wszystkie trzy podręczniki (GM, Gracza, Bestiariusz): przeczytaj `GIT_I_PODRECZNIKI.md`, uruchom `sprawdz_podreczniki.ps1`, sprawdź `git status` i wyszukaj wersje dokumentów na dysku. Inne rozmowy mogą je aktualizować. Nie zakładaj, że wersja znana z historii rozmowy jest aktualna.
- Edytuj główne pliki `Persona_5_RPG_Podrecznik_GM.docx`, `Persona_5_RPG_Podrecznik_Gracza.docx`, `Persona_5_RPG_Bestiariusz.docx`. Nowe lub zmienione pliki numerowane porównaj i uwzględnij przed pracą. Nie wybieraj automatycznie wyłącznie według daty lub numeru.
- Przed zapisem ponownie porównaj SHA256 wejścia z początkiem pracy; zmiana oznacza konieczność ponownego odczytu i połączenia prac. Nie nadpisuj równoległych zmian. Git obsługuj w całości za użytkowniczkę; po sprawdzeniu wyniku zapisuj spójne zmiany z polskim opisem, dodając jawnie tylko pliki własnego zadania. Nie cofaj cudzej pracy. Nie twórz kolejnych numerowanych kopii podręczników; historię przechowuje Git.

- Użytkownik nie jest programistą. Wyjaśniaj działanie aplikacji prostym językiem, podawaj konkretne instrukcje bez zakładania znajomości terminala i, gdy to możliwe, przygotowuj uruchamianie dwuklikiem. Szczegóły techniczne podawaj wtedy, gdy są potrzebne do decyzji lub użytkownik o nie poprosi.
- Zawsze używaj języka polskiego w komunikacji z użytkownikiem, w tym w pytaniach, aktualizacjach postępu, wyjaśnieniach i odpowiedziach końcowych, oraz w tworzonych i redagowanych treściach opisowych. Zachowuj oryginalną postać nazw własnych, identyfikatorów kodu, poleceń i ścieżek plików.
- Keep Polish prose, diacritics, and game terminology consistent.
- Check the relevant files to establish the intended document version; this guide deliberately does not track the latest versions or detailed contents.
- Preserve historical documents and backups, which may still serve as script inputs.
- Read scripts before running or importing them: some overwrite files, perform work on import, or target specific versions and local paths.
- For document changes, check related data and references, then use the appropriate QA tools and inspect the rendered layout.
- Treat balance results as research; proposed mechanics are not automatically part of the written rules.
- Keep this guide broad and stable. Leave changing details in the documents, data, and scripts themselves.
