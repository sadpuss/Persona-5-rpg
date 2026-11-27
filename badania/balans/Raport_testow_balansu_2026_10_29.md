# Testy balansu Persona 5 RPG — 29 października 2026

> **Uwaga (porządki repozytorium):** raport dotyczy starych wersji podręczników (GM 0.7, Gracza 0.4, Bestiariusz 0.4) i może nie odpowiadać aktualnym zasadom. Skrypty i wyniki leżą w `badania/balans/`. Wymagane stare Wordy i pliki `skill_*_0_7.json` są w historii Git pod tagiem `archiwum-przed-porzadkami`.

## Wynik dla prowadzącej

Rdzeń systemu nadaje się do dalszego rozwijania, ale obecne podręczniki mają kilka konkretnych luk. Najpilniejsze są: Despair pomijający całe HP bossa, nieproporcjonalne koszty części skilli oraz odnawianie zasobów przez ucieczkę. Początkowe wyprawy wymagają ostrożniejszego doboru liczby przeciwników; pojedynczy KO przed dostępem do wskrzeszania dodatkowo je zaostrza.

Poniżej są propozycje po testach, a nie już wprowadzone zasady. **Nie zmieniłam trzech podręczników.** Testy komputerowe sprawdzają matematykę i przykładowe strategie. Nie zastępują sesji z ludźmi i nie dowodzą, że każda możliwa drużyna jest równie silna.

## 1. Despair przeciw bossom — poprawić przed grą

Ominous Words jest dostępne od poziomu 10, kosztuje 1 SP i nakłada Despair przy nieudanym teście DC 15: 70% szans bez odporności. Obecny Despair powoduje KO w trzeciej turze ofiary, niezależnie od jej HP. Sama etykieta „miniboss” nie daje odporności.

Sprawdziłam pełną walkę: dwójka bohaterów używa jednego Ominous Words, potem korzysta z Guard. Bossowie mają 140, 300 albo 600 HP. Przy 1800 powtórzeniach na wariant obecna zasada dawała **68% zwycięstw dla każdego z tych trzech HP**. To omijanie walki, a nie zwykła skuteczna taktyka.

**Proponowana reguła:** na przeciwnikach oznaczonych jako boss lub miniboss Despair nadal odbiera SP, lecz zamiast KO przy trzecim rozliczeniu zadaje **20 obrażeń Almighty**, po czym się kończy. Zwykłe Shadows zachowują dotychczasowy efekt. Guard i inne właściwości działają według zwykłych zasad obrażeń.

W tym samym teście poprawka dawała 0% zwycięstw od samego statusu i średnio 13,6 obrażenia na próbę rzucenia. To oczekiwany wynik: status pomaga, lecz nie zabija dowolnego bossa. Test nie oznacza, że boss ma być odporny na pozostałe statusy. Ewentualne odporności należy jawnie umieścić na jego karcie.

## 2. Koszty skilli — potrzebna korekta tabel

### Fizyczne i Gun

Obecnie Cleave kosztuje 3 HP i zadaje takie same 1d6+4 jak darmowy atak podstawowy. Stomach Blow kosztuje 0 HP, a zadaje średnio 18,5 obrażenia i może powodować Hunger. God’s Hand, Brave Blade oraz Myriad Slashes mają po uproszczeniu takie same obrażenia, lecz różne koszty. To nie są znaczące wybory taktyczne: część opcji jest zwyczajnie gorsza albo bezpodstawnie lepsza.

**Proponowana wspólna tabela dla aktywnych skilli Physical/Gun:**

| Siła | Koszt HP jednego celu | Obrażenia |
|---|---:|---|
| Light | 2 | 1d6+6 |
| Medium | 4 | 2d6+6 |
| Heavy | 6 | 3d6+8 |
| Severe | 8 | 3d6+14 |
| Colossal | 10 | 3d6+20 |

- Atak obszarowy: +3 HP.
- Dodatkowy status albo zwiększona celność o +2: +1 HP; jeden taki dodatek także przy obu właściwościach.
- Warunkowe wyjątki sprawdzone w modelu: Cornered Fang −2 HP za warunek zaskoczenia przez przeciwnika; Deadly Fury, Giant Slice i Rising Slash +1 HP za premię po Baton Pass.
- Darmowy atak podstawowy i darmowy strzał pozostają przy 1d6+4. Nie dostają premii płatnego Light.
- Wielokrotne trafienia zachowują uproszczony zapis tabeli RPG; nie mnożymy ponownie obrażeń przez liczbę ciosów z gry komputerowej.

Przykłady: Cleave 3→2 HP i 1d6+4→1d6+6; Stomach Blow 0→7 HP; God’s Hand 13→10 HP; Brave Blade 12→10 HP. To usuwa 11 wykrytych przypadków droższej, porównywalnej lub identycznej opcji. Kryterium porównania obejmowało typ, cel, obrażenia i dodatkowy efekt; nie jest dowodem optymalności wszystkich buildów.

Pierwsza testowana wersja kosztów 3/5/8/11/14 HP była za surowa. Odrzuciłam ją. W powtórzeniu problematycznej walki fizycznego bohatera na poziomie 35 jej skuteczność spadła z 65,14% do 58%; finalna tabela przywróciła 65,14% (350 prób na wariant). W osobnej regresji sprawdziłam 54 600 walk z trzema wersjami kosztów. Finalna wersja nadal zmienia niektóre wyniki o kilka punktów procentowych, ale usuwa wskazaną dużą regresję. Nie obiecuję identycznej skuteczności każdej fizycznej konfiguracji.

### Najmocniejsze zaklęcia żywiołów

Agidyne kosztuje 3 SP i zadaje średnio 18,5 obrażenia; Inferno kosztuje 12 SP i zadaje 24,5. To około 32% więcej obrażeń za czterokrotny koszt. Analogiczny problem dotyczy części pozostałych żywiołów.

**Propozycja:** standardowe zaklęcia żywiołowe Severe kosztują **4 SP pojedynczo / 6 SP obszarowo**. Heavy pozostaje przy 3/5 SP. Ta propozycja nie obejmuje automatycznie leczenia, Almighty ani specjalnych skilli o dodatkowych właściwościach.

W 36 000 izolowanych walk sprawdziłam oba cenniki, oszczędny i agresywny dobór czarów oraz obecność pasywnych obniżek. Przykład poziomu 65 bez zaawansowanych pasywów: skuteczność agresywnej pary magów 90,93→100%, mediana pozostałego SP 16,32→66,32%, mediana długości walki nadal 7 rund. W oszczędnej wersji tej konfiguracji skuteczność obu cenników wynosiła 100% — poprawka usuwa karę za korzystanie z odblokowanego mocnego czaru, nie jest konieczna do każdego zwycięstwa.

Koszty oryginalnego P5R mogą zostać w kolumnie referencyjnej; zmiana dotyczy kolumny RPG.

## 3. Ucieczka resetuje regenerację — zamknąć pętlę

Limit Invigorate do trzech tur działa wewnątrz pojedynczej walki, ale obecnie po ucieczce przeciwnik odzyskuje SP, a kolejna walka odnawia limit regeneracji bohatera. Można więc odzyskiwać SP przez wielokrotne prowokowanie tej samej grupy, bez pokonywania jej.

Konkretny test: bohater poziomu 65, Invigorate 3, Resist Wind, Guard przez trzy tury, potem ucieczka i legalne leczenie. Przeciwnik ma ograniczone SP. Po dziesięciu takich cyklach mediana zdobytego SP wynosiła **86**. Po poprawce wynosiła **4**; po pierwszym cyklu w obu wersjach było to 9. Po 5000 prób na wariant.

**Proponowana reguła:** ucieczka i ponowne zaatakowanie tej samej grupy to nadal jedno spotkanie na potrzeby limitów odnowy zasobów. Przeciwnicy zachowują pozostałe SP, bohaterowie zachowują wykorzystane liczniki regeneracji. HP wrogów może wracać według obecnej reguły. Liczniki odnoszą się do konkretnej grupy, nie do wszystkich Shadows tego gatunku.

Analogiczne ograniczenie należy konsekwentnie zastosować do innych odnawiających zasoby zdolności z limitem „na walkę”. Test szczegółowy obejmował Invigorate i Spirit Drain; nie wszystkie możliwe kombinacje takich zdolności. GM potrzebuje jedynie znacznika zużycia przy grupie, od której drużyna uciekła.

## 4. Safe room i celowa porażka — opcjonalne zabezpieczenie

Zapisanie 1 HP i 0 SP, a następnie celowa porażka, obecnie daje połowę maksymalnych zasobów. Przy poziomie 25 to 29 HP i 27 SP. Można powtarzać tę operację po nadpisaniu zapisu. To konsekwencja przyjaznego respawnu, ale daje darmową odnowę bez kończenia dnia.

**Propozycja, jeśli chcemy usunąć tę możliwość:**

```
HP po porażce = max(1, min(HP zapisane, połowa maksymalnego HP w dół))
SP po porażce = min(SP zapisane, połowa maksymalnego SP w dół)
```

Świat, przedmioty i EXP nadal wracają do zapisu. Przegląd 39 826 stanów zasobów na sześciu poziomach wykazał możliwość zwiększenia co najmniej jednego zasobu w 29 371 stanach obecnej reguły; w proponowanej — w żadnym.

**Cena tej poprawki:** zapis w złym stanie pozostaje złym zapisem. Może wymusić wyjście do świata rzeczywistego i powrót kolejnego dnia. Dlatego traktuję to jako świadomy wybór poziomu łagodności gry, mniej pilny niż Despair czy koszty skilli.

## 5. Całe wyprawy: zasoby, wczesny KO i liczba Shadows

Najbardziej miarodajna końcowa seria obejmuje sześć drobnych starć i minibossa, nieznane początkowo właściwości, zapamiętywanie odkryć, ograniczony ekwipunek, leczenie przy 65% HP oraz oszczędne leczenie obszarowe między walkami. Każdy wiersz to 350 wypraw. „Powrót” oznacza wyjście do świata rzeczywistego po trzeciej walce i powrót następnego dnia z pełnym HP/SP oraz uzupełnieniem podstawowych zakupów. Sam safe room nie leczy za darmo.

### Bez proponowanego budzenia po KO

| Poziom i drużyna | Shadows w zwykłej grupie | Obecne, bez powrotu | Obecne, z powrotem | Nowe koszty, bez / z powrotem |
|---|---:|---:|---:|---:|
| 1, dwie postacie | 1 | 91,14% | 94,29% | Bez zmiany w tym zestawie |
| 1, dwie postacie | 2 | 44% | 51,43% | Bez zmiany w tym zestawie |
| 5, dwie postacie | 1 | 98% | 98,57% | Bez zmiany w tym zestawie |
| 5, dwie postacie | 2 | 60,86% | 70,57% | Bez zmiany w tym zestawie |
| 5, dwie postacie | 3 | 2% | 26,86% | Bez zmiany w tym zestawie |
| 25, dwie postacie | 3 | 47,71% | 76,29% | Bez zmiany w tym zestawie |
| 25, cztery postacie | 5 | 100% | 100% | 100% / 100% |
| 65, dwie postacie | 3 | 63,71% | 81,14% | 80,29% / 96% |
| 65, cztery postacie | 5 | 100% | 100% | 100% / 100% |

To nie jest tabelka uniwersalnego poziomu trudności. Grupy testowe mają powtarzających się przeciwników i określone pokrycie słabości. Boss jest testową konstrukcją z odpornością na Physical, Null Fire i bez słabości, nie oficjalną kartą konkretnego bossa P5R. Czteroosobowe drużyny dobrze wykorzystują obszarowe leczenie, akcje i Hold Up. Wynik 100% w 350 próbach nie oznacza niemożliwości porażki; nie świadczy też o dobrze wyważonym bossie dla każdej czteroosobowej grupy.

**Wniosek dla przygotowania przygody:** na początku nie zakładać automatycznie liczby Shadows równej liczbie bohaterów +1. Dla dwóch postaci na poziomie 1 zacząć od jednego Shadowa, potem sprawdzić dwójkę. Trójka może być trudnym starciem. Dużo zależy od dostępnych słabości; solo wymaga osobnej, łagodniejszej rozpiski. Nie podnosiłabym globalnie HP/SP, żeby naprawić źle dobraną grupę.

### Opcjonalne budzenie towarzysza po wygranej

Przed Recarm na poziomie 15 pojedynczy KO bywa długotrwałym wyłączeniem z wyprawy: zwykłe leczenie nie wskrzesza, a przedmioty do wskrzeszania mają być rzadkie.

**Przetestowana propozycja:** po zwycięstwie lub Hold Up nieprzytomni członkowie drużyny odzyskują przytomność z **1 HP i niezmienionym SP**, po rozliczeniu premii końca walki. Nie dotyczy to ucieczki ani porażki całej drużyny. W walce nadal potrzeba normalnego wskrzeszenia. Dalsze leczenie zużywa zasoby.

Przy dwóch bohaterach poziomu 5 i dwóch Shadows na grupę poprawiało to ukończenie wyprawy z **60,86→78,29%** bez pełnego powrotu i z **70,57→83,43%** z powrotem. Na poziomie 1 przy jednym Shadowie: 91,14→100%. Przy trzech Shadows na poziomie 5 nie ratowało zbyt trudnej trasy: 2→2,29% bez powrotu. Nie zastępuje więc doboru spotkań. Polecam jako łagodną zasadę dla tej kampanii, ale jest to dodatkowe ułatwienie, a nie naprawa matematycznej sprzeczności.

## 6. Co zostawiłabym

- **Stałe trafienie i obrona.** Nie znalazłam powodu, by dodawać wzrost wraz z poziomem. Problemy leżały w kosztach, ekonomii akcji i doborze przeciwników.
- **Guard: redukcja o 60% i ochrona przed Down.** W 10 000 porównanych atakach obszarowych Heavy Fire na dwie postacie mające po 20 HP, z których jedna miała Weak Fire, obie przeżywały w 30,02% prób bez Guard i 100% z Guard. To daje sens reagowaniu na zapowiedziany silny cios.
- **Limit łańcucha One More/Baton Pass.** Pozwala wykorzystać słabości bez nieograniczonego oddawania tej samej dodatkowej akcji. Nie zwiększałabym kosztu SP za Baton Pass.
- **Pełne zasoby po wyjściu i powrocie kolejnego dnia.** Daje rozsądny zawór bezpieczeństwa, zachowując koszt czasu.
- **Limit ośmiu skilli, silniejsza wersja pasywu zamiast sumowania i limit pierwszych trzech tur regeneracji.** Wymagają jedynie doprecyzowania ciągłości spotkania po ucieczce.

Dopisek przy bossach powinien jawnie określać możliwość negocjacji. W testach bossowie byli nienegocjowalni, ale podlegali All-Out Attack; samo nazwanie Shadowa minibossem nie może niejawnie zmieniać reguł. To doprecyzowanie karty, nie przetestowana nowa mechanika.

## 7. Zakres, wiarygodność i odtwarzanie

Źródła: Podręcznik GM 0.7, Podręcznik Gracza 0.4, Bestiariusz 0.4. Hashe plików zapisano w `balance_tests_2026_10_29/input_manifest.json`. Przeanalizowano 541 pozycji katalogu, w tym 346 oznaczonych jako dostępne, oraz 232 drukowane profile bojowe. Pozostałe wpisy bestiariusza to skarby i nawigator. Nie twierdzę, że wszystkie 346 umiejętności przeszły pełną symulację: parser ataków obejmuje 116 skilli; pozostałe sprawdzano w zakresie tabel i wybranych reguł.

Zakończone serie obejmują **911 310 pełnych symulowanych walk**, w tym walki wewnątrz **70 200 prób wypraw**. Dodatkowo wykonano 60 000 prób pętli ucieczki, 20 000 prób ataku z/bez Guard oraz kontrole stanów i pojedynczych efektów. Liczba prób sama w sobie nie dowodzi poprawności modelu.

Główna macierz: poziomy 1, 5, 10, 15, 25, 35, 50, 65, 80 i 99; drużyny 1/2/4; różna inicjatywa, znajomość słabości i dobór skilli. Osobny sweep obejmuje wszystkie 232 profile. Legalność przykładowych buildów sprawdzono na poziomach 1–99: progi nauki, liczba punktów i osiem slotów. Porównania używają tych samych scenariuszy i ziaren losowania; odmienne decyzje mogą zmienić kolejność zużywania rzutów. JSON-y zawierają przedziały ufności 95%; małe różnice kilku punktów procentowych nie są automatycznie istotne.

Ograniczenia:

- Shadows korzystają z uproszczonych ataków wydrukowanych na kartach, a nie z automatycznie dołączonego pełnego repertuaru P5R. Przeciwnicy dostają One More, ale nie przekazują Baton Pass. Bossowie są fixture'ami testowymi z określoną liczbą akcji.
- Strategia bohaterów jest automatyczna. Porównano oszczędną i agresywną; żadna nie jest dowodem najlepszego możliwego zagrania. Początkowo nieznane właściwości są odkrywane i zapamiętywane. Model zna bieżące HP przeciwnika, co ułatwia decyzje.
- Nie wszystkie statusy, interakcje pasywów, relacje, ekonomia fuzji i nagrody fabularne mają pełny model dynamiczny. Nie przeprowadzono kompletnego testu całych 99 poziomów kampanii ani wszystkich buildów.
- Wyprawy utrzymują stały poziom; nie przyznają nowych skilli w połowie trasy. Zaczynają z czterema przedmiotami po 10 HP i jednym po 6 SP; brak gwarantowanych skrzyń i darmowych wskrzeszeń. Zakupy są przyjętym scenariuszem, bo ostatnia propozycja zakupów nie była jeszcze wpisana do podręcznika.
- Testy wypraw uwzględniają mocne cechy społeczne Courage/Dexterity, więc nie są reprezentatywne dla każdej świeżo stworzonej postaci.
- Wstępne serie miały zbyt zachowawczo uproszczone leczenie poza walką; znalazłam też możliwość użycia w nich leczenia przez nieprzytomnego bohatera. Dlatego powyższa końcowa tabela pochodzi wyłącznie z poprawionej serii `healing_and_encounter_sensitivity.json`: leczą tylko przytomni, wybierane jest wydajne leczenie obszarowe, a próg leczenia w walce wynosi 65%. Starsze serie pozostają materiałem eksploracyjnym i nie służą jako rozstrzygający dowód trudności wypraw.

### Pliki do odtworzenia

Skrypty w katalogu projektu:

```
python balance_lab.py all
python balance_focus.py
python balance_all_cards.py
python balance_revisions.py
python balance_early_palace.py
python balance_sensitivity.py
```

Wymagają lokalnych danych JSON i podręczników z projektu. Pełne wyniki są w `balance_tests_2026_10_29/`. Najważniejsze: `despair_full_combat.json`, `retreat_resource_farming.json`, `physical_revision_regression.json`, `final_dominance.json`, `isolated_magic_prices.json`, `healing_and_encounter_sensitivity.json`, `mechanics_checks.json`. Pliki `*_run.json` podają liczebność poszczególnych serii.

## Proponowany zakres następnej aktualizacji

W pierwszej kolejności: wyjątek Despair dla bossów, poprawione koszty i płatny Light, ciągłość zasobów po ucieczce oraz jawne zasady negocjacji na kartach bossów. Dodatkowo polecam budzenie z 1 HP po zwycięstwie i ostrożne początkowe grupy. Ograniczenie respawnu zasobami zapisu pozostawiam jako opcję, bo zmienia łagodność porażki. Nie proponuję przebudowy rdzenia ani globalnego podnoszenia HP/SP.
