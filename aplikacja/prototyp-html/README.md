# TAKE YOUR HEART — lokalny prototyp kreatora

Otwórz `index.html` w przeglądarce (Edge, Chrome lub Firefox). Nie trzeba instalować pakietów ani uruchamiać serwera. Wszystkie zasoby są lokalne. To prototyp interfejsu przyszłej aplikacji desktopowej, jeszcze bez instalatora.

## Co można sprawdzić

- Sześć swobodnie dostępnych kroków i podgląd na żywo.
- Własny bohater i Persona, 23 Arkany z traitami, ilustracja, słabość i Resist.
- Cztery darmowe umiejętności, trzy gotowe propozycje, katalog z wyszukiwaniem i filtrami, nauka za punkt lub kartę.
- Start na poziomie 1–99; wspólny EXP i poziom; awans bez leczenia, punkty nauki, bieżące zasoby, cechy społeczne, ekwipunek i notatki.
- Automatyczny zapis w bieżącej przeglądarce oraz przenośny plik JSON z ilustracją. Pobierz plik przed zmianą urządzenia lub przeglądarki. Automatyczny zapis pod adresem plikowym zależy od przeglądarki.
- Dwie oddzielne karty i opcjonalny indeks skilli; wydruk stylizowany lub uproszczony. PDF zapisuje się z systemowego okna drukowania. Wyłącz nagłówki/stopki; dla stylizowanego wydruku włącz grafikę tła.
- Wszystkie kroki i wybory można pozostawić niepełne. Ostrzeżenia są tylko w kreatorze. Uzgodnienia z GM pozostają w lokalnych notatkach i pliku, bez wydruku.

## Zasady i granice prototypu

Źródła: podręcznik gracza 0.5, GM 0.8, `skill_level_gates_0_8.json`, `skill_rules_0_8.json`. `build_data.py` czyta DOCX i JSON, a zapisuje wyłącznie `aplikacja/data.js`; nie modyfikuje podręczników. Uruchomienie: `python aplikacja/build_data.py` z katalogu projektu.

Pełny katalog ma 541 pozycji, w tym niedostępne zwykłą nauką. Nie wszystkie opisy zostały jeszcze przeniesione do aplikacji; brak jest wyraźnie oznaczony odsyłaczem do podręcznika. Próg poziomu i dostęp pochodzą z aktualnej bazy. Nie należy traktować tego prototypu jako kompletnego silnika walidacji zasad.

Premie HP Rydwanu i SP Doradcy są automatyczne. Pozostałe premie, w tym pasywy maksimum HP/SP, wpisuje się ręcznie. Efekty pasywów bojowych nie są automatycznie rozliczane. Cechy społeczne mają edycję rangi bez księgowania postępu. Skill card jest ręcznym potwierdzeniem użycia karty; nie ma jeszcze banku kart, Velvet Roomu ani fuzji.

W przygotowaniu można zmieniać naukę i odzyskiwać punkty. Po rozpoczęciu gry zapomnienie skilla nie zwraca punktu. Wyjątki pozostają możliwe i są sygnalizowane. Brak historii/cofania zmian, migracji zasad i wielu lokalnych profili — do przełączania postaci służą pliki JSON. Zapis zawiera wersję zasad, a import obcej wersji jest zatrzymywany do czasu implementacji świadomej migracji.

## Następny etap

Ocena wyglądu i przepływu przez użytkowniczkę, uzupełnienie opisów oraz walidacji, następnie opakowanie w aplikację desktopową i testy instalatorów na docelowych systemach. Pierwsza wersja działa bez sieci, bibliotek z CDN i kont użytkowników.
