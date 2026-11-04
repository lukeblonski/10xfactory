# Zgoda człowieka na poprawki skilli

Ten plik zmienia tylko człowiek. Zmiana, która dotyka ścieżki z `## Ścieżki` albo usuwa krok łańcucha, wymaga zgody człowieka (bramka 2 w `CLAUDE.md`). Propozycja retrospektywy, która ich dotyka, idzie do intencji najbliższej zmiany w repo fabryki (`docs/zasady-budowy.md`, punkt 9).

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
- `scripts/eval_triage.sh` — test triage'u.
- `scripts/eval_reviewer.sh` — test recenzenta na zasianych błędach.
- `scripts/e2e_guardrails.sh` — test zabezpieczeń na prawdziwym Claude Code.
- `scripts/create_sandbox.sh` — piaskownica, w której działają testy.

### Polityka triage'u

- `skills/10x-impl-review/references/triage-policy.md` — polityka triage'u, oryginał.
- `skills/10x-plan-review/references/triage-policy.md` — polityka triage'u, kopia.

### Zabezpieczenia aplikacji

- `skills/guardrails/` — cały skill zabezpieczeń aplikacji: szablony (CI gałęzi z linią `# autopilot: ci-galezi` w `templates/ci.yml`, na które autopilot czeka przed scaleniem, piaskownica i hooki w `templates/guardrails.json`, agent weryfikujący w `templates/verifier.md`), instalator `scripts/install.py`, który zapisuje piaskownicę i hooki aplikacji, same hooki w `scripts/hooks/` oraz `SKILL.md`.

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

Zmiana pliku z tej listy uruchamia płatny test fabryki (krok `testy-fabryki` autopilota, `docs/zasady-budowy.md`, punkt 8). Plan sumuje średnie koszty testów, które ten krok uruchomi dla zmienianych plików, i pyta człowieka tylko wtedy, gdy suma przekracza budżet z bramki 3 w `CLAUDE.md`. Krok uruchamia każdy test raz, także gdy obejmuje go kilka pozycji, a pozycja z `--quick` zastępuje pozostałe. Koszt to średnia jednego przebiegu z tabeli „Koszt jednego przebiegu” w `docs/testy-fabryki.md`.

- `skills/10x-new/` → `chain` (ok. 2,59 USD), `intent` (ok. 0,57 USD)
- `skills/10x-plan/` → `chain` (ok. 2,59 USD)
- `skills/10x-goal-implement/` → `chain` (ok. 2,59 USD)
- `skills/10x-implement/references/` → `chain` (ok. 2,59 USD)
- `skills/10x-archive/` → `chain` (ok. 2,59 USD)
- `skills/retro/` → `chain` (ok. 2,59 USD)
- `skills/10x-plan-review/` → `chain` (ok. 2,59 USD), `triage` (ok. 2,22 USD)
- `skills/10x-impl-review/` → `chain` (ok. 2,59 USD), `triage` (ok. 2,22 USD)
- `skills/10x-impl-review/scripts/validate_change.py` → `intent` (ok. 0,57 USD)
- `skills/intent/` → `intent` (ok. 0,57 USD)
- `skills/guardrails/` → `guardrails` (ok. 0,04 USD)
- `scripts/e2e_guardrails.sh` → `guardrails` (ok. 0,04 USD)
- `scripts/autopilot.py` → `chain` (ok. 2,59 USD)
- `scripts/run_evals.sh` → `--quick` (ok. 5,80 USD)
- `scripts/eval_*.sh` → `--quick` (ok. 5,80 USD)
- `scripts/evallib.py` → `--quick` (ok. 5,80 USD)
- `scripts/create_sandbox.sh` → `--quick` (ok. 5,80 USD)
- `scripts/fixtures/` → `--quick` (ok. 5,80 USD)
