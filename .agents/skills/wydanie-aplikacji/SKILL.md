---
name: wydanie-aplikacji
description: Publikacja nowej wersji aplikacji Take Your Heart na GitHubie (instalator Windows, AppImage Linux, opcjonalnie macOS) z automatycznymi aktualizacjami. Użyj, gdy trzeba wydać, opublikować lub zaktualizować program dla graczy.
---

# Wydanie aplikacji

Wydania buduje workflow `.github/workflows/release.yml` („Wydanie aplikacji”), uruchamiany ręcznie wyłącznie z `main`. Zainstalowane wersje same pobierają aktualizację z GitHub Releases po starcie i co cztery godziny, a instalują ją przy zamknięciu programu.

## Kroki

1. Zsynchronizuj `main` z GitHubem. `npm test` i `npm run build` w `aplikacja/` muszą przejść.
2. Podbij wersję (wydanie o istniejącym numerze workflow odrzuci):
   ```sh
   cd aplikacja && npm version <x.y.z> --no-git-tag-version
   ```
   Poprawki: ostatnia cyfra; nowe funkcje: środkowa.
3. Zapisz commit z `aplikacja/package.json` i `aplikacja/package-lock.json` (np. „Wydaj wersję 0.5.2”) i wyślij go: `git push`.
4. Uruchom workflow:
   ```sh
   gh workflow run "Wydanie aplikacji" --ref main -f publish=true
   ```
   Bez `publish=true` workflow tylko buduje paczki do sprawdzenia (artefakty przebiegu). `-f include_macos=true` dodaje macOS; automatyczne aktualizacje na Macu działają tylko z podpisem (sekrety `MAC_CSC_LINK`, `MAC_CSC_KEY_PASSWORD`).
   Bez `gh` lub uprawnień: GitHub → Actions → Wydanie aplikacji → Run workflow na `main`, zaznaczyć „Opublikuj wydanie po zbudowaniu paczek”.
5. Śledź przebieg (`gh run watch`) i sprawdź wydanie `v<x.y.z>` w Releases: `.exe`, `.AppImage`, `latest.yml`, `latest-linux.yml`.

## Uwagi

- Wydanie zawiera kopie trzech podręczników z chwili budowania. Zmiana treści podręczników dociera do graczy z gotową aplikacją dopiero z kolejnym wydaniem.
- Workflow ma uprawnienie zapisu tylko w kroku publikacji. Nie rozszerzaj uprawnień ani nie uruchamiaj wydań z innych gałęzi.
- Uruchomienie opublikowanego AppImage i działanie aktualizatora nie były jeszcze zweryfikowane (issue #1).
