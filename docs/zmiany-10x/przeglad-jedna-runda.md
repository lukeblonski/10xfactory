# Zmiany w skillach 10x — przeglad-jedna-runda: jeden przegląd i jedno sprawdzenie zamknięcia

- **Źródło:** zmiana `przeglad-jedna-runda` (decyzje człowieka 2026-11-04, D-488 i D-489 w `context/foundation/decisions.md`).
- **Cel zmiany:** przegląd planu i przegląd kodu kończą się po jednym pełnym przeglądzie i jednym sprawdzeniu poprawek, bez kolejnych rund szukających nowych problemów. Naprawiane jest tylko to, co trafi człowieka przy normalnej pracy albo jest atakiem z modelu zagrożenia intencji, a znany rodzaj błędu ma wskazane źródło sposobu naprawy.

**Wspólne zależności:**
- `CLAUDE.md` z sekcją „Kiedy pytać człowieka” (lista bramek), jak w poprzedniej wersji polityki.
- Plik polityki `references/triage-policy.md`, ten sam w obu skillach przeglądu (oryginał w `10x-impl-review`, kopia w `10x-plan-review`; `scripts/check_refs.py` pilnuje, żeby były identyczne, i porównuje też wspólną część obu skilli, z nową podsekcją o sprawdzeniu zamknięcia).
- Intencja w `change.md` ze scenariuszem człowieka, kryteriami akceptacji i modelem zagrożenia („Chroni przed / Nie chroni przed”), bo z nich triage bierze odpowiedzi na swoje dwa pytania.
- `scripts/autopilot.py` w tej samej wersji: rozpoznaje raport zamknięcia po przyrostku `-zamkniecie.md`, ocenia jego werdykt i przy powtórzeniu kroku po zatrzymaniu nie zaczyna drugiego przeglądu tej samej serii.

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-impl-review

- **Co zmienić:**
  - Polityka triage'u traci regułę zapętlenia, reguły wagi zależne od numeru rundy i sekcję o ponownym przeglądzie. Bramka zostaje bez zmian. Zamiast reguł wagi agent triage'u przy każdej uwadze odpowiada na dwa pytania: czy to wydarzy się przy zwykłym używaniu (dowód ze scenariusza, kryterium albo zwykłej ścieżki w intencji) i czy to atak wymieniony w „Chroni przed”. Wynik jest jeden z trzech: naprawa (reguła `normalne używanie` albo `Chroni przed`), wpis w rejestrze ograniczeń z warunkiem powrotu bez poprawki (reguła `przypadek szczególny`, także dla przypadku wymyślonego) albo pominięcie jedną linią (reguła `styl`). Waga z raportu recenzenta nie przesądza wyniku; jej trzy definicje zostają słowo w słowo.
  - Nowa sekcja polityki o znanym rodzaju błędu: taka uwaga podaje nazwę i identyfikator źródła (strona OWASP Cheat Sheet Series, wpis CWE albo rozdział dokumentacji narzędzia) i jednym zdaniem sposób naprawy, a poprawka idzie tym sposobem. Format uwagi w skillu dostaje opcjonalne pole `Source`; przykład uwagi o wstrzyknięciu SQL ma je wypełnione. Recenzent nie pobiera stron, tylko je nazywa.
  - Po commicie poprawek świeży sub-agent robi jedno sprawdzenie zamknięcia. Dostaje tylko listę naprawianych uwag, uruchamia polecenia weryfikacji automatycznej przeglądanych faz i polecenia ich kryteriów akceptacji, przy każdej uwadze pisze „załatwione” albo „niezałatwione” z dowodem, przy uwadze ze źródłem sprawdza, czy poprawka go użyła, i nie zgłasza nic spoza listy. Sprawa niezałatwiona dostaje jedną próbę naprawy, po której drugi świeży sub-agent sprawdza tylko ją; gdy dalej jest niezałatwiona, trafia do człowieka z dowodami (reguła `niezałatwione`).
  - Wynik sprawdzenia leży obok raportu przeglądu jako `<nazwa raportu bez .md>-zamkniecie.md`, ze znacznikiem `<!-- REVIEW-CLOSURE -->`, linią werdyktu po poprawkach i sekcjami uwag, poleceń, kryteriów i próby. Krok poprawek zapisuje ten plik na każdej swojej ścieżce, także gdy nie było nic do naprawy albo gdy zatrzymał się przed poprawkami.
  - Znikają: odmowa czwartej rundy, linia numeru rundy w raporcie, numer rundy w nagłówku zapisu decyzji, blok zapętlenia w odpowiedzi agenta triage'u, punkt pętli w kroku poprawek i licznik rund w komunikacie końcowym, który zamiast niego pokazuje ścieżkę raportu i raportu zamknięcia z werdyktem.
- **Dlaczego:** od wprowadzenia automatycznego triage'u 70 z 79 przeglądów miało dwie albo więcej rund, a 80% zgłoszeń z rund drugiej i trzeciej dotyczyło tekstu dopisanego poprzednią poprawką. Z 868 zgłoszeń naprawiono 658, a około 60% z nich to drobiazgi albo przypadki tylko wymyślone. Przykład z jednej zmiany: trzy rundy przeglądu planu kosztowały 8,85 USD, trzy rundy przeglądu kodu 11,66 USD, a kolejne łatki poprawiały własne testy.
- **Zależności:** `CLAUDE.md` z sekcją „Kiedy pytać człowieka”; `references/triage-policy.md`; intencja z modelem zagrożenia.
- **Jak sprawdzić:** `grep -n 'Round 4' skills/10x-impl-review/SKILL.md` nic nie znajduje; `python3 scripts/check_refs.py` kończy się kodem 0, więc polityka i wspólna część są identyczne w obu skillach; `python3 -m unittest discover -s scripts -p 'test_evallib.py'` przechodzi, więc prompt recenzenta daje się wyciąć z nowego pliku.

## 10x-plan-review

- **Co zmienić:** to samo co w `10x-impl-review`: ta sama polityka, ta sama wspólna część z triage'em, sprawdzeniem zamknięcia i zapisem decyzji, pole `Source` w formacie uwagi. Sprawdzenie zamknięcia planu nie ma czego testować, więc uruchamia skan zgodności Progress z fazami i pokrycie kryteriów (`validate_change.py --rules 4`) z pierwszego kroku przeglądu. Raport zamknięcia ma nazwę `plan-review-zamkniecie.md` albo `plan-review-<n>-zamkniecie.md`, a komunikat końcowy podaje werdykt po poprawkach z tego pliku. Werdykt wymagający przemyślenia planu od nowa przechodzi przez triage jak wcześniej.
- **Dlaczego:** jak wyżej; przegląd planu ma tę samą politykę co przegląd kodu.
- **Zależności:** jak w `10x-impl-review`.
- **Jak sprawdzić:** `cmp skills/10x-impl-review/references/triage-policy.md skills/10x-plan-review/references/triage-policy.md` kończy się kodem 0; `grep -nE 'Round 4|Rounds:' skills/10x-plan-review/SKILL.md` nic nie znajduje.
