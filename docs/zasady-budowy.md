# Zasady budowy fabryki

Stałe zasady dla każdego etapu. Prompt etapu odsyła do tego pliku. Agent czyta go przed `/intent`.

## 1. Nazwy własnych skilli

- Skille, które tworzymy od zera, nie mają prefiksu `10x-`. Przykłady: `guardrails`, `intent`, `autopilot`, `babysit`.
- Prefiks `10x-` mają tylko skille z kursu.
- Przed nadaniem nazwy sprawdź, czy nie koliduje z innym skillem w `~/.claude/skills`, z wbudowaną komendą Claude Code ani ze skillem z zainstalowanej wtyczki. Przy kolizji zaproponuj inną nazwę w Notes.

## 2. Opis zmian w skillach 10x

Skilli z kursu nie publikujemy. Publikujemy tylko własny kod i opis zmian w skillach 10x, napisany własnymi słowami.

- Po każdym etapie, który zmienia skill `10x-*`, powstaje plik `docs/zmiany-10x/etap-N.md`.
- Dla każdego zmienionego skilla `10x-*` jedna sekcja z czterema punktami:
  - **Co zmienić:** opis celu zmiany, a nie dokładnych linii.
  - **Dlaczego:** jaki problem to rozwiązuje.
  - **Zależności:** jakie własne pliki lub skille fabryki są potrzebne.
  - **Jak sprawdzić:** polecenie albo obserwowalne zachowanie po zmianie.
- Opis nie cytuje tekstu skilli z kursu. Nazwy plików, sekcji i komend wolno podawać.
- Opis jest dla ludzi. W paczce zmiany nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`, a nie Claude z opisu (D-372).

## 3. Kryteria a intencja

Gdy kryteria akceptacji nie obejmują czegoś, czego wymaga oczekiwany efekt z intencji, nie trzymaj się samej litery kryteriów. Zapisz lukę w Notes i zaproponuj nowe kryterium.

## 4. Gałęzie

Każdy etap pracuje na własnej gałęzi o nazwie zmiany, np. `etap-3-dowody`. Kolejność: review na gałęzi, archiwum na gałęzi (`/10x-archive`), `git merge --ff-only` do `master`, `git push`, a na końcu liczby zmiany z `scripts/pomiar.py`.

## 5. Kontekst

- Pamięć workflow żyje w plikach, a nie w rozmowie. Każdy krok musi dać się uruchomić w nowej sesji, tylko na podstawie plików zmiany.
- Rzadko używane części skilla trafiają do plików w `references/`, czytanych tylko wtedy, gdy są potrzebne. Główny `SKILL.md` zostaje krótki.
- Każdy nowy albo zmieniany skill ma krótki punkt „Co czytam”: które pliki czyta zawsze, które tylko w określonej sytuacji, a których nie czyta.
- Nie polegaj na automatycznym streszczaniu rozmowy. Gdy krok nie mieści się w jednej sesji, zmianę trzeba podzielić.

## 6. Interwencje człowieka

Każda instrukcja człowieka spoza zwykłego przebiegu skilli trafia do `change.md` w sekcji `## Interwencje`. Dotyczy to triage'u podjętego przez człowieka, zmiany podejścia, ręcznego podziału pracy, poprawki promptu i każdej innej wklejonej instrukcji. Dotyczy to też instrukcji w prompcie startowym, które odbiegają od zwykłego łańcucha skilli, np. pominięcia kroku. Taki wpis powstaje na początku zmiany, razem z `change.md`. Analiza w poprzek zmian (punkt 9) uczy się z tych wpisów.

Format jednego wpisu:

- **I-N (etap, krok):** co zrobił człowiek.
  - **Dlaczego:** powód.
  - **Bez interwencji fabryka:** co zrobiłaby sama.
  - **Możliwa reguła:** jeśli widać, jaka reguła usunęłaby potrzebę interwencji. W przeciwnym razie „do ustalenia w analizie w poprzek zmian”.
  - **Kategoria:** jedno słowo: `kontrole`, `narzędzie`, `koszt`, `ocena` (lista z lekcji „Research odpowiada na pytania o wykonalność, zanim rozpisze zmiany, a pytanie człowieka zapisuje jako interwencję z kategorią” w `context/foundation/lessons.md`) albo `inne`. Podpunkt jest wymagany we wpisie za pytanie, które człowiek dopisał do zakresu researchu; inne wpisy go nie mają.
  - **Cofnięcie:** <rodzaj> — <powód jednym zdaniem>. Opcjonalny podpunkt we wpisie, w którym człowiek cofa decyzję agenta: rodzaj pytania (jeden z sześciu z „Pytań do człowieka” niżej) i powód, który agent zapisuje sam z dopiskiem `(powód: agent, decyzja: człowiek)`, bez pytania człowieka i bez wstrzymania przebiegu; człowiek poprawia go, jeśli trzeba (D-289). Inne wpisy go nie mają.

Jedno działanie człowieka zostawia jeden ślad. Odpowiedź człowieka na pytanie agenta zostawia tylko linię w `## Pytania do człowieka`, bez wpisu `I-N`. Wpis `I-N` jest dla poleceń spoza zwykłego przebiegu, także cofnięć. `scripts/pomiar.py` liczy linię pytania i wpis `I-N` osobno, więc oba ślady jednej odpowiedzi dałyby dwie interwencje.

**Pytania do człowieka.** Każde pytanie agenta do człowieka i każde pytanie rozstrzygnięte przez agenta według reguły „kiedy pytać człowieka” w `CLAUDE.md` zostawia jedną linię w sekcji `## Pytania do człowieka` w `change.md` zmiany. To osobna sekcja `## …`, bo `/intent` przepisuje tylko `## Notes`. Linię dopisuje agent, który pytał, zaraz po odpowiedzi, i commituje `change.md`. Format linii, pola w tej kolejności, rozdzielone ` · `:

```
- rodzaj: <r> · krok: <k> · pytanie: <p> · rekomendacja: <tekst> · wybór: rekomendacja|inny: <tekst> · rozstrzygnął: człowiek|agent|obserwator
```

- `rodzaj` to jeden z sześciu: `spór recenzenta z autorem`, `eskalacja`, `płatny przebieg`, `zakres`, `kryterium`, `inne`. `spór recenzenta z autorem` to rodzaj tylko wpisów sprzed zmiany polityka-przegladu, w której zniknął agent autora w przeglądzie.
- Pytanie, które wymaga płatnego przebiegu, ma zawsze rodzaj `płatny przebieg`, nawet gdy dotyczy też zakresu albo kryterium.
- `krok` to krok łańcucha, w którym padło pytanie (np. `intent`, `plan`, `plan-review`, `implement`). Pytanie zadane na zatrzymaniu autopilota ma w `krok` tę samą nazwę kroku co linia tego zatrzymania (np. `archiwum`, a nie `archive` ani `manual`), bo `scripts/pomiar.py` liczy pytanie i zatrzymanie z tym samym krokiem jako jedną interwencję.
- `wybór` to `rekomendacja`, gdy rozstrzygnięcie jest zgodne z rekomendacją agenta, albo `inny: <tekst>` z tym, co wybrał człowiek.
- `rozstrzygnął` to `człowiek`, `agent` albo `obserwator`. Przy `agent` i `obserwator` pole `wybór` to zawsze `rekomendacja`.

## 7. Najpierw odjęcie

Gdy pojawia się problem (uwaga z review, nowa potrzeba), najpierw sprawdź, czy rozwiąże go usunięcie, połączenie albo użycie istniejącego komponentu. Nowy mechanizm, regułę albo krok dodaj tylko wtedy, gdy to nie wystarcza, i zapisz w Notes dlaczego. Odejmujemy mechanizmy, a nie cele: uproszczenie nie może usunąć niczego, czego wymaga kryterium akceptacji.

To samo dotyczy nowej pozycji w planie: etapu, kroku albo narzędzia. Zanim ją dopiszesz, sprawdź, który istniejący etap albo komponent już robi część tego, i czy da się to dołączyć tam. Nową pozycję dodaj tylko wtedy, gdy nic istniejącego tego nie obejmuje. Entuzjazm człowieka wobec pomysłu nie zastępuje tego sprawdzenia.

## 8. Testy fabryki

- Zmiana nie uruchamia testów fabryki (`scripts/run_evals.sh`). Uruchamia je człowiek na żądanie, a sesja przed każdym wydaniem fabryki dla użytkowników: dziś przed publikacją paczki (`docs/publikacja-paczki.md`, punkt 1), tak samo przed każdym przyszłym wydaniem. Test `guardrails` sprawdza hooki zainstalowane w repo testowym z `scripts/create_sandbox.sh` (`scripts/e2e_guardrails.sh`), a nie skill z gałęzi, więc zmiana `skills/guardrails/` wymaga przed tym testem ponownego `/guardrails` w piaskownicy.
- Zamknięcie etapu planu wdrożenia uruchamia tryb pełny, `scripts/run_evals.sh --full`.
- Wynik trafia do `reviews/` zmiany (`--change <id>`, a bez tej flagi folder zmiany o nazwie bieżącej gałęzi) albo do folderu z `--out`. Wynik poniżej progu idzie do człowieka.
- Progi, oczekiwane wyniki i zamrożone dane w `scripts/fixtures/` zmienia tylko człowiek. Agent nie zmienia ich po to, żeby test przeszedł.
- Opis testów, progów, kosztów i trybów: `docs/testy.md`.

## 9. Wnioski z analizy w poprzek zmian

- Wnioski i propozycje poprawek fabryki powstają tylko z ręcznej analizy w poprzek zmian. Robi ją obserwator w rozmowie z człowiekiem co kilka zmian albo co tydzień, z liczb `scripts/pomiar.py` i śladów zmian (D-492).
- Ta analiza sprawdza też warunki „Kiedy wrócić” w rejestrze ograniczeń (`context/foundation/limitations.md`).
- Poprawka z analizy wchodzi jako zwykła zmiana, po decyzji człowieka. Nic nie wchodzi samo po scaleniu zmiany.

## 10. Najpierw proste rozwiązanie

Projektujemy najprostsze rozwiązanie, które spełnia cel. Rozbudowę dodajemy dopiero wtedy, gdy zapisany z góry sygnał z danych pokaże, że prosta wersja nie wystarcza. Każda propozycja rozbudowy (w intencji, planie, analizie w poprzek zmian) podaje ten sygnał i dowód, że wystąpił.

Zasada obowiązuje też przy budowie etapu ze spec. Przy każdym elemencie opisu etapu pada pytanie, czy jest potrzebny w pierwszej wersji. Element bez potrzeby w pierwszej wersji czeka na swój sygnał.

Punkt 7 („Najpierw odjęcie”) mówi, co sprawdzić przed dodaniem czegoś nowego. Ten punkt mówi, kiedy prostą wersję wolno rozbudować. Ta sama zasada prowadzi autopilota (D-127).
