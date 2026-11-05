# Zmiany w skillach 10x — martwe-pliki-i-kontrole: archiwum bez weryfikatora, kryteria ocenia przegląd kodu

- **Źródło:** zmiana `martwe-pliki-i-kontrole` (decyzje człowieka 2026-11-05, D-500 w `context/foundation/decisions.md`).
- **Cel zmiany:** kontrole, które przy każdej zmianie kosztują, a nie łapią błędów, wychodzą z łańcucha. Archiwum nie uruchamia już agenta weryfikatora i nie wymaga jego raportu. Każde kryterium akceptacji, także z rodzajem „weryfikator”, ocenia świeży agent przeglądu kodu: pełny przegląd na przeglądanym commicie, a przy poprawkach sprawdzenie zamknięcia na commicie poprawek.

**Wspólne zależności:**
- `validate_change.py` w `10x-impl-review` ma reguły 1, 2, 3, 4, 6 i 7; reguły 5 (raport weryfikatora) już nie ma, a `--rules 5` kończy się kodem 2.
- `references/run-report-format.md` jest identyczny w sześciu skillach (oryginał w `10x-implement`, kopie w `10x-archive`, `10x-e2e`, `10x-goal-implement`, `10x-impl-review` i `10x-tdd`; `scripts/check_refs.py` pilnuje, żeby były identyczne). Opisuje już tylko raport przebiegu, bez raportu weryfikatora i bez zasad jego aktualności.
- Agent weryfikatora zostaje w `/guardrails` (szablon i instalacja w `.claude/agents/verifier.md`), ale żaden skill 10x go nie uruchamia.

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-archive

- **Co zmienić:** archiwum nie uruchamia agenta weryfikatora. Znika cała sekcja tego kroku (czyste drzewo kodu, sprawdzenie agenta, wywołanie, zapis raportu w `runs/` i jego osobny commit). Akapit o bramce mówi, że skill uruchamia `validate_change.py` z regułami 1, 2, 3, 4, 6 i 7. Z części o tym, co skill czyta, znika raport agenta, a `references/run-report-format.md` zostaje tylko do pola `Skill` raportów przebiegu. Odmowa z `validate_change.py` traci dwie linie reguły 5 i zdanie, że ponowne archiwum uruchomi agenta od nowa. Z listy tego, czego skill nie robi, znikają dwa punkty o agencie. Z `allowed-tools` znikają `Agent` i `Write`, których używało tylko to wywołanie, więc skill wraca do kształtu bliższego oryginałowi kursu.
- **Dlaczego:** w 61 przebiegach weryfikator dał 13 wyników negatywnych, z czego jeden był prawdziwym błędem (linia dokumentu); pozostałe wynikały z brzmienia kryterium, braku dowodu, piaskownicy i własnych plików. Kryteria z rodzajem „weryfikator” ocenia teraz przegląd kodu.
- **Zależności:** `validate_change.py` bez reguły 5 (`10x-impl-review`). Zmiana w toku, która ma jeszcze stary `runs/*-verifier.md`, musi go usunąć przed archiwum (opis w `10x-impl-review`).
- **Jak sprawdzić:** `grep -ni verifier skills/10x-archive/SKILL.md` nic nie znajduje; `grep -nE '^  - (Agent|Write)$' skills/10x-archive/SKILL.md` nic nie znajduje.

## 10x-impl-review

- **Co zmienić:**
  - `validate_change.py` traci regułę 5 razem z czytaniem tabeli raportu weryfikatora i filtrem, który odsuwał pliki `runs/*-verifier.md` od reguły 2. Reguła 2 czyta teraz wszystkie `runs/*.md`. Zmiana w toku, która ma jeszcze stary `runs/*-verifier.md`, musi go usunąć przed archiwum, bo reguła 2 weźmie go za raport przebiegu.
  - Warunek wstępny przeglądu mówi, że przegląd nie uruchamia reguł 3 i 7 (robi to archiwum) i nie pisze do `runs/`, a kryteria akceptacji ocenia krok 3 i sprawdzenie zamknięcia. Linie naprawy reguł 1, 2 i 6 nie wyłączają już raportu weryfikatora.
  - Krok 3 dostaje punkt o kryteriach akceptacji: każde kryterium z `change.md`, które przeglądane fazy dostarczają (przy przeglądzie wszystkich faz każde kryterium), jest oceniane na przeglądanym commicie. Kryterium z `Sprawdzenie: polecenie` przez uruchomienie polecenia dokładnie tak, jak jest zapisane, bez dopisanego potoku; kryterium z `Sprawdzenie: weryfikator` przez ocenę z kodu, diffu i wyników poleceń, z dowodem (`plik:linia` albo wynik polecenia). Wynik to jedna linia na kryterium w nowej sekcji `## Kryteria` raportu, po tabeli werdyktów: `- <numer>: spełnione | niespełnione — <dowód>`. Niespełnione kryterium to uwaga krytyczna w wymiarze kryteriów sukcesu, a ten wymiar dostaje FAIL także przy niespełnionym kryterium.
  - Sprawdzenie zamknięcia ocenia każde kryterium przeglądanych faz na commicie poprawek: z poleceniem przez jego uruchomienie, z rodzajem „weryfikator” przez ocenę z dowodem. Agent zamknięcia może czytać inne pliki także po to, żeby ocenić kryterium. Po jedynej próbie poprawki nowy agent uruchamia całe sprawdzenie zamknięcia znowu na commicie próby, a sekcja `## Próba` raportu zamknięcia dostaje jego linie poleceń i kryteriów w kształcie linii z `## Polecenia` i `## Kryteria`. Ostatni commit przeglądu ma więc zawsze ocenę każdego kryterium.
  - `references/run-report-format.md` bez raportu weryfikatora (wspólne zależności).
- **Dlaczego:** kryteriów z rodzajem „weryfikator” nie oceniało nic poza weryfikatorem w archiwum, a sprawdzenie zamknięcia oceniało tylko kryteria z poleceniem i ruszało tylko przy poprawkach. Po usunięciu weryfikatora ocenę daje świeży agent przeglądu.
- **Zależności:** `scripts/check_refs.py` porównuje wspólną część obu skilli przeglądu, więc zmiana sprawdzenia zamknięcia jest identyczna w `10x-plan-review`.
- **Jak sprawdzić:** `python3 skills/10x-impl-review/scripts/validate_change.py <change-id> --rules 5` kończy się kodem 2 z komunikatem `unknown rule(s): 5`; `grep -ni verifier skills/10x-impl-review/scripts/validate_change.py` nic nie znajduje; `sed -n '/^## Step 3/,/^## Step 4/p' skills/10x-impl-review/SKILL.md | grep -q "Sprawdzenie: weryfikator"` i `sed -n '/^### Closure check/,/^\*\*One attempt/p' skills/10x-impl-review/SKILL.md | grep -q "Sprawdzenie: weryfikator"` kończą się kodem 0; `python3 scripts/check_refs.py` kończy się kodem 0.

## 10x-plan-review

- **Co zmienić:** tylko wspólna część z `10x-impl-review`, tym samym brzmieniem: opis tego, co uruchamia sprawdzenie zamknięcia w każdym skillu, ocena kryteriów w wariancie przeglądu kodu, czytanie innych plików także do oceny kryterium, ponowne sprawdzenie zamknięcia na commicie jedynej próby i linie poleceń i kryteriów w sekcji `## Próba`. W wariancie przeglądu planu sprawdzenie zamknięcia dalej uruchamia skany z kroku 1. Nic poza tą częścią się nie zmienia.
- **Dlaczego:** wspólna część musi być identyczna w obu skillach przeglądu.
- **Zależności:** jak w `10x-impl-review`.
- **Jak sprawdzić:** `python3 scripts/check_refs.py` kończy się kodem 0; `sed -n '/^### Closure check/,/^\*\*One attempt/p' skills/10x-plan-review/SKILL.md | grep -q "Sprawdzenie: weryfikator"` kończy się kodem 0.

## 10x-implement

- **Co zmienić:** podsumowanie po ostatniej fazie mówi, że kryteria akceptacji ocenia `/10x-impl-review`, a nie weryfikator w archiwum. `references/run-report-format.md` bez raportu weryfikatora (wspólne zależności).
- **Dlaczego:** archiwum nie uruchamia już weryfikatora.
- **Zależności:** ocena kryteriów w `10x-impl-review`.
- **Jak sprawdzić:** `grep -ni verifier skills/10x-implement/SKILL.md skills/10x-implement/references/run-report-format.md` nic nie znajduje.

## 10x-tdd

- **Co zmienić:** to samo co w `10x-implement`: podsumowanie mówi, że kryteria ocenia `/10x-impl-review`; `references/run-report-format.md` bez raportu weryfikatora.
- **Dlaczego:** jak wyżej.
- **Zależności:** jak w `10x-implement`.
- **Jak sprawdzić:** `grep -ni verifier skills/10x-tdd/SKILL.md skills/10x-tdd/references/run-report-format.md` nic nie znajduje.

## 10x-e2e

- **Co zmienić:** to samo co w `10x-implement`: podsumowanie mówi, że kryteria ocenia `/10x-impl-review`; `references/run-report-format.md` bez raportu weryfikatora.
- **Dlaczego:** jak wyżej.
- **Zależności:** jak w `10x-implement`.
- **Jak sprawdzić:** `grep -ni verifier skills/10x-e2e/SKILL.md skills/10x-e2e/references/run-report-format.md` nic nie znajduje.

## 10x-goal-implement

- **Co zmienić:** sugerowany dalszy krok w raporcie końcowym mówi, że kryteria ocenia `/10x-impl-review`, a nie weryfikator w archiwum. `references/run-report-format.md` bez raportu weryfikatora.
- **Dlaczego:** jak wyżej.
- **Zależności:** jak w `10x-implement`.
- **Jak sprawdzić:** `grep -ni verifier skills/10x-goal-implement/SKILL.md skills/10x-goal-implement/references/run-report-format.md` nic nie znajduje.

## 10x-new

- **Co zmienić:** opis bloku kryteriów w `references/change-md.md`: `validate_change.py` czyta blok tylko dla reguły 4, a każde kryterium ocenia `/10x-impl-review` (pełny przegląd na przeglądanym commicie, sprawdzenie zamknięcia na commicie poprawek). Dowód kryterium to `spełnione` z dowodem w sekcji `## Kryteria` najnowszego raportu przeglądu kodu albo jego raportu zamknięcia, a nie wiersz raportu weryfikatora.
- **Dlaczego:** reguły 5 i raportu weryfikatora już nie ma.
- **Zależności:** ocena kryteriów w `10x-impl-review`.
- **Jak sprawdzić:** `grep -niE 'verifier|rules 4 and 5' skills/10x-new/references/change-md.md` nic nie znajduje.

## 10x-plan

- **Co zmienić:** zasada, że kryterium z rodzajem „weryfikator” nie dostaje wiersza `#### Manual`, mówi teraz, że takie kryterium ocenia przegląd kodu (krok 3 i sprawdzenie zamknięcia), a nie weryfikator w archiwum z regułą 5.
- **Dlaczego:** archiwum nie uruchamia już weryfikatora, a wiersz ręczny dalej tylko blokowałby archiwum krokiem, którego człowiek nie musi robić.
- **Zależności:** ocena kryteriów w `10x-impl-review`.
- **Jak sprawdzić:** `grep -niE 'verifier|rule 5' skills/10x-plan/SKILL.md` nic nie znajduje.
