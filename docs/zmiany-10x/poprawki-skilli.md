# Zmiany w skillach 10x — poprawki-skilli: testy celowane i bramki bez doklejonego potoku, pytanie o resztki w przeglądzie, sesja główna wśród autorów raportu przebiegu

- **Źródło:** propozycja P2 retrospektywy porzadki (`context/archive/2026-10-24-porzadki/retro.md`), przyjęta w D-242, oraz intencja zmiany poprawki-skilli (`context/changes/poprawki-skilli/change.md`, kryteria P2, P3, P4 i P6). Zmiana zamyka też ograniczenie D-240.

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-goal-implement

- **Co zmienić:** w `SKILL.md`, w sekcji ze stosem bramek fazy, przed listą bramek dopisać akapit o testach w trakcie pracy: dopóki kod fazy nie jest gotowy, podagent puszcza tylko testy plików, które ta faza zmienia, a przy celowym psuciu jeden test, którego to dotyczy. Pełny zestaw idzie najwyżej raz na fazę, w stosie bramek na jej koniec, więc błąd w pliku spoza fazy wychodzi dopiero wtedy; jedyne dodatkowe pełne przebiegi to te, których wymagają bramka repozytorium i commit, czyli po próbie samonaprawy albo po zmianie pliku spoza `context/`. W bramce kryteriów planu (pierwszy punkt listy) dopisać, że polecenie kryterium idzie dokładnie w brzmieniu z planu, bez dołączonego potoku w rodzaju `| tail` albo `| head`, bo wtedy werdykt bramki to kod wyjścia potoku; skraca się tylko to, co polecenie wypisuje (np. zapis do pliku i osobny odczyt jego końca), nie kod wyjścia. W bramce sprawdzeń całego repozytorium dopisać, że gdy bramka kryteriów puściła już to samo polecenie na tym samym drzewie, przebieg się nie powtarza: linia werdyktu bierze tamten wynik i mówi to wprost. Ponowny przebieg tylko po próbie samonaprawy albo po zmianie pliku spoza `context/` po bramce. Kopia formatu raportu przebiegu w `references/run-report-format.md` zmienia się tak samo jak w `10x-implement`.
- **Dlaczego:** w rdzeniu (przebudowa-autopilota) implementacja trwała 128 min, w tym 14 pełnych przebiegów testów (ok. 36 min, ok. 30% implementacji) i 34 częściowe, a w planach laboratorium bramka kryteriów i bramka repozytorium często puszczały ten sam pełny zestaw dwa razy. W porzadki podagent fazy dokleił `| tail` do polecenia kryterium, więc kod 0 bramki pochodził z `tail`, a nie z testów (retro porzadki P2).
- **Zależności:** `references/run-report-format.md` (kopia z `10x-implement`, pilnowana bajt w bajt przez `scripts/check_refs.py`); reguła bez potoku ma odpowiednik w kroku 3 `10x-impl-review`. Bramki kryteriów w `10x-implement`, `10x-tdd` i `10x-e2e` tej reguły nie dostają (ograniczenie D-244).
- **Jak sprawdzić:** `sed -n '/\*\*(a) Plan criteria\*\*/,/Stage the touched-file set/p' skills/10x-goal-implement/SKILL.md | grep -qF '| tail'` kończy się kodem 0, a akapit przed listą bramek mówi o testach celowanych i o pełnym zestawie najwyżej raz na fazę.

## 10x-impl-review

- **Co zmienić:** w `SKILL.md`, w instrukcjach pierwszego podagenta (wykrywanie odejść od planu), podać mu też diff zakresu przeglądu i dopisać punkt o resztkach bieżącej zmiany: kodzie, dokumentacji albo wpisach (dziennik decyzji, rejestr ograniczeń, lekcje), których po zmianie nic już nie używa. Podagent bierze z diffu nazwy tego, co zmiana usuwa albo zastępuje (funkcje, opcje, tryby, pliki, numery wpisów), wyszukuje je w `skills/`, `scripts/`, `docs/` i `context/foundation/` i zgłasza każde trafienie bez użytku. Liczą się tylko resztki tej zmiany, nie dawne. Lista werdyktów podagenta dostaje wartość `LEFTOVER`, a jedno zdanie mówi, że taka pozycja idzie do raportu i przez zwykły krok triage'u. Werdykt wymiaru dyscypliny zakresu ostrzega także przy resztkach i je wymienia. W kroku 3 (sprawdzenie kryteriów sukcesu), przy zapisie wyniku polecenia, dopisać, że polecenie idzie w brzmieniu z planu, a skraca się tylko zapisany wynik, nigdy przez doklejony potok, który podmienia kod wyjścia. Sekcja podagenta triage'u i plik polityki triage'u zostają bez zmian, tak samo tokeny czytane przez płatny test `reviewer` (nazwy poziomów uwag, pola `Severity` i `Location`, wymiar `Plan Adherence`). Kopia formatu raportu przebiegu w `references/run-report-format.md` zmienia się tak samo jak w `10x-implement`.
- **Dlaczego:** przegląd nie pytał, czy zmiana zostawiła rzeczy, których nic już nie używa; stary tryb terminalowy zniknął w rdzeniu tylko dlatego, że plan kazał go zastąpić. Reguła bez potoku w kroku 3 domyka to samo miejsce co w `10x-goal-implement`.
- **Zależności:** sekcja podagenta triage'u jest wspólna z `10x-plan-review` (pilnuje tego `scripts/check_refs.py`), więc pytanie o resztki nie zmienia triage'u; uwagi idą przez tę samą politykę. Płatny test `reviewer` czyta tekst od kroku 2 do formatu raportu, więc nowe zdania nie mogą dodać drugiej linii kotwicy wycinka.
- **Jak sprawdzić:** `grep -c 'LEFTOVER' skills/10x-impl-review/SKILL.md` wypisuje liczbę większą od 0, `git diff --quiet master -- skills/10x-plan-review/ skills/10x-impl-review/references/triage-policy.md` kończy się kodem 0, a `python3 scripts/check_refs.py` przechodzi.

## 10x-implement

- **Co zmienić:** w `references/run-report-format.md`, w polu „Writers” raportu przebiegu, obok czterech skilli implementacji wymienić sesję główną laboratorium (`docs/sesja-glowna.md`) jako autora raportu `runs/<YYYY-MM-DD>-<HHMMSS>-sesja-glowna.md` za wiersze `#### Manual`, które człowiek potwierdził w rozmowie. To oryginał formatu; pięć kopii w innych skillach dostaje ten sam tekst.
- **Dlaczego:** od zmiany porzadki raport za potwierdzone wiersze ręczne pisze też sesja główna, a format wymieniał tylko skille implementacji (D-240). `validate_change.py` nie sprawdza autora raportu, więc rozjazd był tylko w opisie.
- **Zależności:** kopie w `10x-goal-implement`, `10x-archive`, `10x-e2e`, `10x-impl-review` i `10x-tdd` muszą być identyczne z oryginałem (w laboratorium pilnuje tego `scripts/check_refs.py`). W paczce bez laboratorium sesja główna z `docs/sesja-glowna.md` może nie istnieć; wtedy nowa część zdania niczego nie zmienia.
- **Jak sprawdzić:** `grep -n '^- \*\*Writers\*\*' skills/10x-implement/references/run-report-format.md | grep -q 'sesja-glowna'` kończy się kodem 0, a `python3 scripts/check_refs.py` przechodzi.

## 10x-archive

- **Co zmienić:** kopia formatu raportu przebiegu w `references/run-report-format.md` zmienia się tak samo jak w `10x-implement` (pole „Writers” wymienia sesję główną). `SKILL.md` bez zmian, także filtr autorów raportu.
- **Dlaczego:** ten sam powód co w `10x-implement`; kopia ma być identyczna z oryginałem.
- **Zależności:** oryginał w `10x-implement`; `scripts/check_refs.py` porównuje kopie.
- **Jak sprawdzić:** `cmp skills/10x-implement/references/run-report-format.md skills/10x-archive/references/run-report-format.md` kończy się kodem 0.

## 10x-e2e

- **Co zmienić:** kopia formatu raportu przebiegu w `references/run-report-format.md` zmienia się tak samo jak w `10x-implement` (pole „Writers” wymienia sesję główną). `SKILL.md` bez zmian.
- **Dlaczego:** ten sam powód co w `10x-implement`; kopia ma być identyczna z oryginałem.
- **Zależności:** oryginał w `10x-implement`; `scripts/check_refs.py` porównuje kopie.
- **Jak sprawdzić:** `cmp skills/10x-implement/references/run-report-format.md skills/10x-e2e/references/run-report-format.md` kończy się kodem 0.

## 10x-tdd

- **Co zmienić:** kopia formatu raportu przebiegu w `references/run-report-format.md` zmienia się tak samo jak w `10x-implement` (pole „Writers” wymienia sesję główną). `SKILL.md` bez zmian.
- **Dlaczego:** ten sam powód co w `10x-implement`; kopia ma być identyczna z oryginałem.
- **Zależności:** oryginał w `10x-implement`; `scripts/check_refs.py` porównuje kopie.
- **Jak sprawdzić:** `cmp skills/10x-implement/references/run-report-format.md skills/10x-tdd/references/run-report-format.md` kończy się kodem 0.
