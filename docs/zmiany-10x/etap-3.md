# Zmiany w skillach 10x — etap 3: dowody

- **Zakres:** gałąź `etap-3-dowody` od `819f802` (`master` przed etapem) do zamknięcia zmiany.
- **Lista skilli:** `git diff --name-only 819f802 etap-3-dowody -- 'skills/10x-*'`. Wynik: `10x-new`, `10x-plan`, `10x-plan-review`, `10x-implement`, `10x-goal-implement`, `10x-tdd`, `10x-e2e`, `10x-impl-review`, `10x-archive`.
- **Własny skrypt:** `skills/10x-impl-review/scripts/validate_change.py` (biblioteka standardowa Pythona, testy w `scripts/test_validate_change.py`). Leży w skillu `10x-impl-review`, bo w projekcie użytkownika nie ma katalogu `scripts/` fabryki. Pozostałe skille wołają go przez `${CLAUDE_SKILL_DIR}/../10x-impl-review/scripts/validate_change.py`, więc wymagają zainstalowanego `10x-impl-review` obok siebie. Kod skryptu jest publikowany wprost.
- **Cel etapu:** o tym, czy zmiana jest skończona, decyduje skrypt, a nie deklaracja modelu. Każdy przebieg implementacji zostawia plik z dowodami. Każde kryterium akceptacji ma fazę i aktualny dowód od agenta weryfikującego. Odejście od planu jest zapisane w planie w tym samym commicie. Archiwizacja blokuje, gdy czegoś brakuje.

**Wspólne zależności:**
- Trzy pliki formatów z repo fabryka, w `references/`:
  - opis bloku kryteriów w `10x-new/references/change-md.md`;
  - `progress-format.md`: oryginał w `10x-plan`, kopie w `10x-implement`, `10x-goal-implement`, `10x-tdd`, `10x-e2e` (nowa kopia), `10x-impl-review`, `10x-plan-review`;
  - `run-report-format.md` (nowy): oryginał w `10x-implement`, kopie w `10x-goal-implement`, `10x-tdd`, `10x-e2e`, `10x-impl-review`, `10x-archive` (nowy folder `references/`).
- `scripts/check_refs.py` z repo fabryka pilnuje, żeby kopie `run-report-format.md` były identyczne z oryginałem, i sprawdza odwołania `${CLAUDE_SKILL_DIR}/../<skill>/scripts/…`.
- Agent weryfikujący `.claude/agents/verifier.md`, instalowany przez własny skill `/guardrails` (etap 2). Bez niego `10x-archive` nie zarchiwizuje zmiany.

**Siedem reguł skryptu** (numery używane niżej): 1 — odhaczony wiersz Progress ma SHA commita z historii HEAD; 2 — odhaczony wiersz ma wpis Observed z kodem 0 w raporcie z przebiegu; 3 — status `implemented` albo `impl_reviewed` i wszystkie wiersze Automated odhaczone; 4 — każda faza ma linię kryteriów z istniejącymi numerami, a każde kryterium ma fazę; 5 — najnowszy raport weryfikatora jest zacommitowany, po nim nie zmienił się kod, a każde kryterium ma `MET` z dowodem; 6 — każdy plik zmieniony przez commity zmiany (temat z zakresem `(<change-id>)`), poza `context/`, jest w liniach plików planu albo w `## Plan Changes`; 7 — brak nieodhaczonych wierszy Manual. Kody wyjścia: 0 brak problemów, 1 problemy, 2 nie ma czego sprawdzić.

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-new

- **Co zmienić:**
  - Dodaj punkt „Co czytam”: argument, lista folderów zmian do sprawdzenia unikalności, plik kontraktu `change.md`.
  - Przy zapisie intencji do Notes dopisz, że kryteria akceptacji zostają dosłownie, bez zmiany numerów i kształtu.
  - W `references/change-md.md` dodaj sekcję o kryteriach: blok zaczyna się od linii z pogrubionym nagłówkiem kryteriów (angielskim albo polskim), kończy się przed następną linią od kolumny 0 z `**` albo `#`, kryterium to punkt z pogrubionym numerem z kropką (wielkie litery i cyfry), ciąg dalszy jest wcięty, numery są unikalne, inny pogrubiony punkt w bloku to błąd formatu, plik ma najwyżej jeden blok. Wymień, kto czyta blok, i powiedz, że dowodem kryterium jest werdykt `MET` w najnowszym raporcie weryfikatora.
  - Zastąp zapowiedź przyszłego sprawdzenia spójności statusu odesłaniem do skryptu (reguła 3).
- **Dlaczego:** skrypt musi czytać kryteria deterministycznie, także ze starych zmian. Pogrubione punkty przed blokiem (polityki, decyzje) nie mogą liczyć się jako kryteria.
- **Zależności:** `validate_change.py` (czyta blok), agent weryfikujący (ocenia kryteria).
- **Jak sprawdzić:** `python3 -m unittest scripts/test_validate_change.py` przechodzi, w tym test, który czyta kryteria wszystkich zmian z `context/archive/`.

## 10x-plan

- **Co zmienić:**
  - Dodaj punkt „Co czytam”: `change.md` z blokiem kryteriów, materiały wejściowe, `lessons.md`, `references/progress-format.md`.
  - W kroku czytania plików dopisz blok kryteriów z `change.md`: każdy numer musi trafić do którejś fazy.
  - W szablonie fazy dodaj tuż pod nagłówkiem fazy linię kryteriów z numerami, które faza realizuje. Punkty weryfikacji zostają bez numerów kryteriów.
  - W szablonie planu dodaj pustą sekcję `## Plan Changes` z jednym zdaniem konwencji, między `## References` a `## Progress`.
  - Pod szablonem dodaj zasady: jedna linia kryteriów na fazę, każde kryterium w co najmniej jednej fazie, linie plików obejmują wszystkie pliki fazy, `## Plan Changes` zostaje pusta. Gdy `change.md` nie ma kryteriów, plan pisze fazy bez linii i ostrzega, że archiwizacja nie przejdzie.
  - W `references/progress-format.md`:
    - nowe sekcje o linii kryteriów fazy, o liniach plików w „Changes Required” (ścieżki w backtickach, klamry, katalog z `/`, wzorzec `*`) i o `## Plan Changes` (wpis z fazą, powodem, kryteriami i plikami, tylko dopisywanie, w tym samym commicie co faza);
    - zasada, że notatka w bloku fazy obowiązuje tylko przed implementacją, a potem odejście od planu to wpis w `## Plan Changes`;
    - zasada, że każdy odhaczony wiersz dostaje SHA, także Manual i wiersz fazy bez commita (wtedy bieżący HEAD);
    - lista, kto może dopisywać do `## Plan Changes` i odznaczać wiersze przy naprawie na starcie;
    - odesłanie wykrywania dryfu do reguły 3 skryptu.
- **Dlaczego:** bez linii kryteriów nikt nie sprawdza, czy każde kryterium jest zrobione. Bez `## Plan Changes` plan nie wie o odejściach, a skille wykonawcze mogły zmieniać tylko Progress.
- **Zależności:** `validate_change.py` (reguły 4 i 6 czytają nowe elementy planu).
- **Jak sprawdzić:** `grep -n "Criteria" skills/10x-plan/SKILL.md` pokazuje linię w szablonie fazy, a `grep -n "## Plan Changes" skills/10x-plan/SKILL.md` sekcję w szablonie. Plan napisany nowym skillem przechodzi `validate_change.py <id> --rules 4`.

## 10x-plan-review

- **Co zmienić:**
  - W kroku skanów mechanicznych, obok zgodności Progress z fazami, dodaj skan pokrycia kryteriów: uruchom skrypt z regułą 4. Każda linia problemu reguły 4 to osobna uwaga CRITICAL w wymiarze kompletności planu, z numerem reguły w tytule. Kod 2 z powodu braku kryteriów to jedna uwaga WARNING.
  - Ponowne review w kroku triage'u uruchamia ten skan na całym planie, także poza zmienionymi fragmentami.
  - W „Co czytam” dopisz blok kryteriów i wynik skryptu.
- **Dlaczego:** pokrycie kryteriów fazami sprawdza się mechanicznie przed implementacją, zanim brak wyjdzie przy archiwizacji. Zmianę kryteriów review zatwierdził człowiek (I-1).
- **Zależności:** `validate_change.py` w `10x-impl-review`.
- **Jak sprawdzić:** `grep -n "validate_change.py" skills/10x-plan-review/SKILL.md` pokazuje wywołanie z `--rules 4`. Review planu, w którym kryterium nie ma fazy, ma uwagę z `R4` w tytule.

## 10x-implement

- **Co zmienić:**
  - Dodaj punkt „Co czytam”: plan, `change.md`, `lessons.md`, oba pliki formatów; stare raporty z `runs/` nie są czytane.
  - Dodaj sekcję o raporcie z przebiegu:
    - na starcie, gdy Progress ma odhaczone wiersze, skrypt z regułami 1, 2 i 6 dla faz z tymi wierszami: wiersz z problemem reguły 1 albo 2 zostaje odznaczony i zrobiony jeszcze raz, plik z problemem reguły 6 dostaje wpis `## Plan Changes`, zniekształcony wiersz zostaje przepisany w formacie wiersza bez odhaczenia, brak commitów zmiany przy odhaczonych wierszach to STOP dla człowieka, kod 2 nie zatrzymuje przebiegu;
    - potem plik raportu w `runs/` z nagłówkiem i trzema sekcjami, dodany do zbioru dotkniętych plików, razem z niezacommitowanym raportem przerwanego przebiegu;
    - wpisy Observed po commicie fazy, z jego SHA, jeden na bramkę.
  - Zasadę „zmieniaj tylko Progress” rozszerz o dopisywanie do `## Plan Changes`. Bloki faz zostają nienaruszone.
  - Przy niezgodności z planem odpowiedź „dostosuj” daje wpis `## Plan Changes`, a „pomiń” wpis Skipped.
  - W rytuale commita po stagingu dodaj sprawdzenie zakresu: skrypt z regułą 6 i opcją `--staged`, każdy zgłoszony plik dostaje wpis `## Plan Changes`, kod 2 to błąd przebiegu. Bramkę trzeba powtórzyć, jeśli kod zmienił się po jej uruchomieniu.
  - Pusty diff daje wierszom SHA bieżącego HEAD. Usuń wszystkie zdania o wierszach bez SHA jako stanie końcowym i o archiwizacji, która tylko ostrzega.
  - Potwierdzenie wiersza Manual przez człowieka to wpis Observed z obserwatorem `user` i jego słowami, a wiersz dostaje SHA. Bez potwierdzenia wiersz zostaje i blokuje archiwizację.
  - Epilog dodaje plik raportu. Podsumowanie wskazuje review i mówi, że kryteria oceni agent weryfikujący w `/10x-archive`.
- **Dlaczego:** wyniki bramek ginęły razem z rozmową, a odhaczony wiersz nie musiał mieć commita ani dowodu. Teraz skrypt może to sprawdzić po zamknięciu sesji.
- **Zależności:** `validate_change.py`, `references/run-report-format.md`, `references/progress-format.md`.
- **Jak sprawdzić:** po przebiegu w `context/changes/<id>/runs/` jest raport z wpisami Observed na commitach faz, a `validate_change.py <id> --rules 1,2,6` kończy się kodem 0.

## 10x-goal-implement

- **Co zmienić:**
  - Dodaj „Co czytam” jak w `10x-implement`.
  - W Setup, przed sprawdzeniem bramek, dodaj krok naprawy na starcie (reguły 1, 2, 6 dla odhaczonych faz, z narracją każdej naprawy) i utworzenie pliku raportu. Brak skryptu kończy przebieg komunikatem `PREFLIGHT`.
  - Każde `ADAPT:` przy drobnej niezgodności dopisuje wpis `## Plan Changes`. Niezgodność strukturalna dalej kończy przebieg.
  - W stosie bramek po stagingu dodaj bramkę zakresu planu (reguła 6 z `--staged`). Błąd naprawia się wpisem `## Plan Changes` w tym samym budżecie dwóch prób, potem STOP.
  - Wynik każdej bramki trafia do pliku raportu po commicie fazy: Observed, kroki niepewne do Reported, bramki pominięte do Skipped. Każdy wiersz Manual dostaje wpis Skipped „needs human”.
  - Pusty diff daje SHA bieżącego HEAD. Usuń zdania o wierszach bez SHA i o archiwizacji, która tylko ostrzega. Zasada mutacji planu jak w `10x-implement`.
  - Epilog dodaje plik raportu. Raport w rozmowie zostaje i podaje ścieżkę pliku.
- **Dlaczego:** raport z przebiegu bez nadzoru istniał tylko w rozmowie. Bramka zakresu sprawdza deterministycznie, że plik spoza planu ma wpis w planie, zamiast hooka (lekcja z etapu 2).
- **Zależności:** jak w `10x-implement`.
- **Jak sprawdzić:** w próbie V9 (`context/archive/2026-10-20-etap-3-dowody/reviews/proba.md` po archiwizacji tej zmiany) przebieg zostawił raport z czterema wpisami Observed na commicie fazy i bramkę `plan-scope` w rozmowie.

## 10x-tdd

- **Co zmienić:**
  - Dodaj „Co czytam” jak w `10x-implement`, plus `test-stack.md` w razie potrzeby.
  - W Setup dodaj naprawę na starcie i utworzenie pliku raportu, jak w `10x-implement`.
  - Przebieg RED i GREEN każdego kroku to wpisy Observed. RED z niezerowym kodem jest śladem, a nie dowodem kroku. Pełny zestaw testów to osobny wpis.
  - Ścieżki „zbuduj bez test-first” i „TDD całej fazy mimo to” dają wpis `## Plan Changes`. Ścieżka „już zrobione” daje wpis Reported, ale przed odhaczeniem skill uruchamia testy kroku i zapisuje wynik jako Observed. Pusty diff daje SHA bieżącego HEAD.
  - Rytuał fazy jak w `10x-implement`: sprawdzenie zakresu po stagingu, SHA dla każdego wiersza, wpisy po commicie, dowód Manual, plik raportu w epilogu.
  - W trybie naprawy błędu: raport w `runs/` z wpisem RED na commicie testu i GREEN na commicie poprawki, zacommitowany osobno po commicie poprawki. Bez planu nie ma `## Plan Changes`, a skrypt zwraca kod 2.
- **Dlaczego:** w TDD dowodem kroku jest zielony test na zacommitowanym kodzie. Czerwony przebieg zostaje jako ślad, że test był czerwony.
- **Zależności:** jak w `10x-implement`.
- **Jak sprawdzić:** po przebiegu raport ma dla każdego kroku wpis z kodem 0 na SHA fazy, a `validate_change.py <id> --rules 1,2,6` kończy się kodem 0.

## 10x-e2e

- **Co zmienić:**
  - Dodaj „Co czytam” dla trybu z planem. W trybie samodzielnym nie ma folderu zmiany, więc nie ma raportu.
  - Skill dostaje kopię `references/progress-format.md` i `references/run-report-format.md`, z odwołaniami w sekcji odwołań.
  - W Setup dodaj naprawę na starcie i utworzenie pliku raportu, jak w `10x-implement`.
  - Zielony spec (VERIFY) to wpis Observed, który dowodzi kroku. Celowe psucie to wpis Observed z niezerowym kodem jako śladem.
  - „Już zrobione” i „przechodzący test już istnieje” dają wpis Reported, potem uruchomienie specu i wpis Observed przed odhaczeniem.
  - „E2E mimo to” w obu miejscach daje wpis `## Plan Changes`.
  - Rytuał fazy jak w `10x-implement`.
- **Dlaczego:** E2E też odhaczało wiersze bez śladu uruchomienia. Skill zapisywał Progress bez kopii kontraktu.
- **Zależności:** jak w `10x-implement`.
- **Jak sprawdzić:** `ls skills/10x-e2e/references/` pokazuje oba pliki formatów, a `python3 scripts/check_refs.py` kończy się kodem 0.

## 10x-impl-review

- **Co zmienić:**
  - Dodaj skrypt `scripts/validate_change.py` do skilla.
  - W „Co czytam” dopisz blok kryteriów i wynik warunku wstępnego, a w razie potrzeby nagłówki raportów z `runs/` (pole skilla) i plik formatu raportu.
  - Na końcu kroku ładowania planu dodaj warunek wstępny (tylko runda 1): skrypt z regułami 1, 2, 4 i 6 dla przeglądanych faz (bez ograniczenia faz przy review całości).
    - Kod 1: lista problemów i pod nią jedna linia naprawy na regułę. Reguły 1, 2 i 6 wskazują skill z pola skilla najnowszego raportu z przebiegu (raport weryfikatora się nie liczy), a bez raportu `/10x-implement`. Reguła 4 daje instrukcję dla człowieka. Potem STOP.
    - Kod 2: komunikat skryptu z instrukcją i STOP.
    - Przy STOP review nie zapisuje raportu, nie zmienia statusu i nie uruchamia triage'u. Te problemy nie są uwagami.
  - Review nie uruchamia reguł 3, 5 i 7, nie tworzy tabeli kryteriów i nie pisze do `runs/`.
  - Zdanie, że każda ścieżka zapisuje raport, dostaje wyjątek dla STOP z warunku wstępnego.
  - Przed commitem poprawek z triage'u: skrypt z regułą 6, `--staged` i przeglądanymi fazami. Każdy zgłoszony plik dostaje wpis `## Plan Changes` (faza, której kod dotyczy poprawka, albo ostatnia przeglądana faza przy poprawce przekrojowej) w tym samym commicie. Gdy po 2 próbach skrypt dalej zgłasza pliki, poprawki zostają w drzewie dla człowieka, commit obejmuje tylko dokumenty, podane jawnymi ścieżkami, a sprawa trafia do „Wymaga Twojej decyzji”. Poprawki mogą w planie tylko dopisywać do `## Plan Changes`.
  - Ponowne review w sub-agencie pomija warunek wstępny.
  - Kopie `progress-format.md` i `run-report-format.md` zaktualizowane.
- **Dlaczego:** problemy stanu zmiany (brak SHA, brak dowodu, kryterium bez fazy, plik spoza planu) nie są uwagami, które review umie naprawić. W triage'u zapętlały się, więc review odmawia na starcie z komendą naprawy (I-4). Zmianę kryteriów review zatwierdził człowiek (I-1).
- **Zależności:** pliki formatów, skille wykonawcze (naprawa na starcie).
- **Jak sprawdzić:** na zmianie z wierszem `[x]` bez SHA `/10x-impl-review <id>` kończy się bez raportu, z linią `R1:` i komendą naprawy. `python3 -m unittest scripts/test_validate_change.py` przechodzi.

## 10x-archive

- **Co zmienić:**
  - Opis bramki „lenient warn-only” zastąp bramką opartą na dowodach. Dodaj narzędzia do zapisu pliku i uruchomienia sub-agenta oraz punkt „Co czytam”.
  - Brak repozytorium git blokuje, bo skrypt potrzebuje historii.
  - Po dwóch twardych odmowach dodaj krok weryfikatora:
    - kod poza `context/` musi być zacommitowany;
    - brak agenta daje STOP z komendą `/guardrails`;
    - agent `verifier` dostaje numer zmiany i numery kryteriów;
    - jego wynik trafia dosłownie do `runs/<data>-<czas>-verifier.md` w kształcie z pliku formatu, z HEAD w nagłówku;
    - commit tylko tego pliku przez ścieżkę, po ponownym sprawdzeniu poczekalni, z tematem `docs(<change-id>): raport weryfikatora`;
    - werdykt `FAIL` nie zatrzymuje kroku.
  - Dodaj trzecią twardą odmowę: skrypt ze wszystkimi regułami. Kod różny od 0 to pełne wyjście i STOP, z jedną linią na regułę:
    - reguły 1, 2, 3 i 6 wskazują skill wykonawczy z najnowszego raportu z przebiegu;
    - reguła 7 wskazuje `/10x-implement` do potwierdzenia wierszy Manual;
    - reguła 4 daje instrukcję dla człowieka;
    - reguła 5 bez raportu albo z nieaktualnym raportem wskazuje ponowne `/10x-archive`;
    - reguła 5 przy kryterium bez `MET` nie ma komendy: pokazuje numer, dowód agenta i to, co sprawdzić (kod, sposób zapisania kryterium, polecenie verify), a dalszy krok wybiera człowiek (lekcja z `lessons.md` o zatrzymaniu z dowodami).
  - Usuń miękkie ostrzeżenia, które rozstrzyga skrypt (status, wiersze w toku, brak SHA), razem z zachętą do archiwizacji przy samych wierszach Manual. Ostrzeżenie o braku review implementacji zostaje.
  - Zaktualizuj zdania o ostrzeganiu przy braku SHA, o nieuruchamianiu testów i o planowanym sprawdzeniu spójności statusu.
- **Dlaczego:** archiwizacja tylko ostrzegała, więc zmiana bez dowodów mogła zostać zamknięta. Teraz zamyka ją tylko kod 0 skryptu, a ocenę kryteriów daje istniejący agent tylko do odczytu, a nie deklaracja modelu.
- **Zależności:** `validate_change.py` w `10x-impl-review`, `references/run-report-format.md` (nowy folder `references/`), agent weryfikujący z `/guardrails`.
- **Jak sprawdzić:** w projekcie z `/guardrails` zmiana przechodząca łańcuch nowych skilli archiwizuje się z commitem raportu weryfikatora przed commitem archiwum. Kopia z commitem kodu po raporcie daje w `validate_change.py` linię `R5:` i kod 1 (próba V9).
