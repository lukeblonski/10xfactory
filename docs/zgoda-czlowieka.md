# Zgoda człowieka na poprawki skilli

Ten plik zmienia tylko człowiek. Zmiana, która dotyka ścieżki z `## Ścieżki` albo usuwa krok łańcucha, wymaga zgody człowieka (bramka 2 w `CLAUDE.md`). Poprawka z analizy w poprzek zmian, która ich dotyka, idzie jako zwykła zmiana ze zgodą człowieka (`docs/zasady-budowy.md`, punkt 9).

## Ścieżki

Pozycja to plik albo katalog. Katalog kończy się `/` i obejmuje wszystko pod nim.

### Kryteria przeglądu

- `skills/10x-plan-review/` — kryteria przeglądu planu i sekcja triage'u są w treści `SKILL.md`.
- `skills/10x-impl-review/` — kryteria przeglądu kodu, sekcja triage'u i `validate_change.py`.
- `skills/10x-impl-review-ci/references/impl-review-instructions.md` — kryteria przeglądu kodu w CI.

### Testy skilli

- `scripts/fixtures/` — zamrożone dane i oczekiwane wyniki testów skilli.
- `scripts/run_evals.sh` — rejestr testów i progi.
- `scripts/evallib.py` — ocena wyników testów i stałe progów.
- `scripts/eval_common.sh` — wspólne uruchomienie testów w piaskownicy.
- `scripts/eval_chain.sh` — test całego przebiegu autopilota w klonie piaskownicy.
- `scripts/eval_intent.sh` — test `intent`.
- `scripts/e2e_guardrails.sh` — test zabezpieczeń na prawdziwym Claude Code.
- `scripts/create_sandbox.sh` — piaskownica, w której działają testy.

### Polityka triage'u

- `skills/10x-impl-review/references/triage-policy.md` — polityka triage'u, oryginał.
- `skills/10x-plan-review/references/triage-policy.md` — polityka triage'u, kopia.

### Zabezpieczenia aplikacji

- `skills/guardrails/` — cały skill zabezpieczeń aplikacji: szablony (CI gałęzi z linią `# autopilot: ci-galezi` w `templates/ci.yml`, na które autopilot czeka przed scaleniem, piaskownica i hooki w `templates/guardrails.json`, agent weryfikujący w `templates/verifier.md`), instalator `scripts/install.py`, który zapisuje piaskownicę i hooki aplikacji, same hooki w `scripts/hooks/` oraz `SKILL.md`.

### Instalator serwera

- `instalator/` — instalator serwera: skrypt instalacji, reguła sudo obserwatora, skrypty startowe, usługi systemu i wzór umowy i granic obserwatora.

### Ta lista

- `docs/zgoda-czlowieka.md` — lista ścieżek, których zmiana wymaga zgody człowieka.
- `docs/obserwator.md` — umowa, granice i polecenie obserwatora; zmienia się tylko przez PR zatwierdzony przez człowieka.
- `scripts/hook_obserwator.py` — hak obserwatora: kiedy obserwator rusza, jego uprawnienia i granice.
- `scripts/obserwator_tydzien.py` — zadanie tygodniowe obserwatora: źródła w sieci i uprawnienia przebiegu.
- `scripts/z_master.py` — program uruchamiający kod obserwatora z gałęzi `master`: który kod hak uruchamia.
- `scripts/zapis_decyzji.py` — hak zapisu decyzji sesji rozmowy obserwatora: kiedy zatrzymuje obserwatora i jakim modelem.
- `scripts/instaluj_obserwatora.py` — polecenie instalacji sesji rozmowy obserwatora: jej piaskownica, zakazy zapisu i odczytu oraz hak zapisu decyzji.

## Usunięcie kroku łańcucha

Zmiana usuwa krok łańcucha, gdy w `git diff --name-status` zmiany plik w `skills/` jest usunięty (`D`) albo przeniesiony (`R`), albo gdy zmiana usuwa krok z `CHAIN` w `scripts/autopilot.py`. Spadek liczby odwołań `/<nazwa skilla>` w zmienionym pliku nie jest usunięciem kroku.

## Płatne testy skilli

Zmiana nie uruchamia płatnych testów fabryki (`scripts/run_evals.sh`). Uruchamia je człowiek na żądanie, a sesja przed każdym wydaniem (`docs/zasady-budowy.md`, punkt 8). Krok, plan albo sesja, która sama uruchamia płatny test, sumuje średnie koszty testów, które uruchomi, i pyta człowieka tylko wtedy, gdy suma przekracza budżet z bramki 3 w `CLAUDE.md`. Koszt to średnia jednego przebiegu z tabeli „Koszt jednego przebiegu” w `docs/testy.md`.
