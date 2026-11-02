# Zmiany w skillach 10x — przebudowa-autopilota-b: plan bez zbędnych wierszy ręcznych, przeglądy bez kroku „co jeszcze zmienia poprawka”

- **Źródło:** propozycja P1 retrospektywy retro-upgrade-c (`context/archive/2026-10-24-retro-upgrade-c/retro.md`) oraz propozycje P1 i P2 retrospektywy przebudowa-autopilota (`context/archive/2026-10-24-przebudowa-autopilota/retro.md`), przyjęte w D-209 i D-211.

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-plan

- **Co zmienić:** w sekcji z wytycznymi kryteriów sukcesu, pod opisem weryfikacji ręcznej, dopisać akapit zaczynający się od pogrubionego `Not a Manual row.`. Akapit mówi trzy rzeczy. Po pierwsze, kryterium z `change.md`, które ocenia agent weryfikatora przy `/10x-archive`, nie dostaje wiersza w podsekcji `#### Manual` w `## Progress`, bo ocenia je raport weryfikatora i reguła 5 skryptu `validate_change.py`. Po drugie, sprawdzenie, które da się zrobić dopiero po scaleniu albo w następnej zmianie, też nie dostaje takiego wiersza; trafia jako punkt do intencji następnej zmiany. Po trzecie, wiersz ręczny zostaje dla czynności człowieka możliwych przed archiwum: zgody, oceny, przeglądu diffu, polecenia, które człowiek sam uruchamia i czyta. Plik `references/progress-format.md` zostaje bez zmian.
- **Dlaczego:** plany stawiały wiersze ręczne typu „weryfikator czyta X” i wiersze ze sprawdzeniem po scaleniu. Archiwum odmawiało zamknięcia zmiany z niezaznaczonym wierszem ręcznym, choć żaden człowiek nie miał nic do zrobienia przed archiwum, a sprawdzenia po scaleniu nie dało się zaznaczyć w ogóle.
- **Zależności:** agent weryfikatora (`.claude/agents/verifier.md`, instaluje go skill `guardrails`), raport weryfikatora w `runs/` i reguła 5 skryptu `validate_change.py` ze skilla `10x-impl-review`; bez nich kryterium weryfikatora nie ma innej oceny niż wiersz ręczny.
- **Jak sprawdzić:** `grep -F "**Not a Manual row.**" skills/10x-plan/SKILL.md` znajduje akapit, a nowy plan nie ma w `## Progress` wiersza ręcznego dla kryterium z `Sprawdzenie: weryfikator` ani dla sprawdzenia po scaleniu.

## 10x-plan-review

- **Co zmienić:** cofnąć sekcję `10x-plan-review` z `docs/zmiany-10x/retro-upgrade-b.md`. W kroku poprawek planu usunąć podpunkt, w którym agent po poprawce wymienia pozostałe miejsca planu i `plan-brief.md`, których dotyka ta sama poprawka. W sekcji o zapisie decyzji, w opisie linii uwagi w `## Decyzje triage`, usunąć zdanie o przyrostku ` · zmienia też: …`. W ścieżce cofnięcia poprawek po nieudanym sprawdzeniu usunąć polecenie zdjęcia tego przyrostka z linii uwag. Sekcja o podagencie triage'u i plik polityki triage'u zostają bez zmian.
- **Dlaczego:** retrospektywa przebudowa-autopilota oceniła ten krok werdyktem „szkodzi” (D-161 P2, D-211): w trzech zmianach po jego wprowadzeniu uwag rundy 2 wywołanych poprawką rundy 1 było 5, 4 i 6, czyli więcej niż w punkcie wyjścia (2).
- **Zależności:** cofa sekcję `10x-plan-review` z `docs/zmiany-10x/retro-upgrade-b.md`. Opis linii w sekcji o zapisie decyzji jest wspólny z `10x-impl-review`; obie kopie muszą mieć ten sam tekst (w repo fabryki pilnuje tego `scripts/check_refs.py`).
- **Jak sprawdzić:** `grep -c 'zmienia też' skills/10x-plan-review/SKILL.md` wypisuje `0`, `grep -c 'What else the fix changes' skills/10x-plan-review/SKILL.md` wypisuje `0`, a `python3 scripts/check_refs.py` przechodzi.

## 10x-impl-review

- **Co zmienić:** cofnąć sekcję `10x-impl-review` z `docs/zmiany-10x/retro-upgrade-b.md`. W kroku stosowania poprawek automatycznych usunąć podpunkt, w którym agent wymienia pozostałe miejsca, których dotyka ta sama poprawka, razem ze zdaniem, że te miejsca idą przez weryfikację i commit poprawek. W opisie linii uwagi w `## Decyzje triage` usunąć zdanie o przyrostku ` · zmienia też: …`, słowo w słowo tak samo jak w `10x-plan-review`. W ścieżce cofnięcia poprawek po nieudanej weryfikacji usunąć polecenie zdjęcia tego przyrostka. Sekcja o podagencie triage'u i plik polityki triage'u zostają bez zmian.
- **Dlaczego:** ten sam powód co w `10x-plan-review` (D-211): krok nie zmniejszył liczby uwag rundy 2 wywołanych poprawką rundy 1, a w trzech zmianach z rzędu było ich więcej niż przed nim.
- **Zależności:** cofa sekcję `10x-impl-review` z `docs/zmiany-10x/retro-upgrade-b.md`; wspólny tekst z `10x-plan-review` (sekcja o zapisie decyzji).
- **Jak sprawdzić:** `grep -c 'zmienia też' skills/10x-impl-review/SKILL.md` wypisuje `0`, `grep -c 'What else the fix changes' skills/10x-impl-review/SKILL.md` wypisuje `0`, a `python3 scripts/check_refs.py` przechodzi.
