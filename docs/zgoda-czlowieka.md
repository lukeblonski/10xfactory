# Zgoda człowieka na poprawki skilli

Ten plik zmienia tylko człowiek. Krok PR retrospektywy (`skills/retro/references/pr.md`) czyta jego wersję z `origin/master`, a nie z gałęzi PR-a, więc PR nie osłabi listy, którą sam jest sprawdzany.

Poprawka skilla z retrospektywy czeka na zgodę człowieka, gdy jej diff dotyka ścieżki z `## Ścieżki`, wychodzi poza `## Zakres poprawki skilla`, usuwa krok łańcucha albo zmienia skill z płatnym testem. Pozostałe poprawki scala krok PR, gdy przejdą testy skilli i recenzent w osobnej sesji (D-100, D-101, D-105).

## Ścieżki

Pozycja to plik albo katalog. Katalog kończy się `/` i obejmuje wszystko pod nim.

### Kryteria przeglądu

- `skills/10x-plan-review/` — kryteria przeglądu planu i sekcja triage'u są w treści `SKILL.md`.
- `skills/10x-impl-review/` — kryteria przeglądu kodu, sekcja triage'u i `validate_change.py`.
- `skills/10x-impl-review-ci/references/impl-review-instructions.md` — kryteria przeglądu kodu w CI.
- `skills/retro/references/pr.md` — polecenia dla autora i recenzenta poprawki, czyli kryteria oceny PR-a.

### Testy skilli

- `scripts/fixtures/` — zamrożone dane i oczekiwane wyniki testów skilli.
- `scripts/run_evals.sh` — rejestr testów i progi.
- `scripts/evallib.py` — ocena wyników testów i stałe progów.
- `scripts/eval_common.sh` — wspólne uruchomienie testów w piaskownicy.
- `scripts/eval_chain.sh` — test całego przebiegu autopilota w klonie piaskownicy.
- `scripts/eval_intent.sh` — test `intent`.
- `scripts/eval_triage.sh` — test triage'u.
- `scripts/eval_triage_archiwa.sh` — test triage'u na archiwach.
- `scripts/eval_reviewer.sh` — test recenzenta na zasianych błędach.
- `scripts/eval_reviewer_models.sh` — porównanie modeli recenzenta.
- `scripts/e2e_guardrails.sh` — test zabezpieczeń na prawdziwym Claude Code.
- `scripts/create_sandbox.sh` — piaskownica, w której działają testy.
- `scripts/retro_pr.py` — krok PR: bramki, które decydują o scaleniu poprawki skilla.
- `scripts/test_retro_pr.py` — testy kroku PR, w tym przypadki, w których scalenie nie może nastąpić.

### Polityka triage'u

- `skills/10x-impl-review/references/triage-policy.md` — polityka triage'u, oryginał.
- `skills/10x-plan-review/references/triage-policy.md` — polityka triage'u, kopia.

### Ta lista

- `docs/zgoda-czlowieka.md` — lista, którą krok PR sprawdza każdą poprawkę.
- `docs/umowa-obserwatora.md` — umowa obserwatora; zmienia się tylko przez PR zatwierdzony przez człowieka.

## Zakres poprawki skilla

PR z poprawką skilla może zmieniać tylko pliki pod tymi ścieżkami:

- `skills/`
- `docs/zmiany-10x/`
- `context/foundation/lessons.md`

Plik spoza nich (np. `scripts/`, `CLAUDE.md`, `.claude/`, `context/foundation/decisions.md`) oznacza, że PR czeka na człowieka. Wpis w `context/foundation/decisions.md` dopisuje sam skrypt kroku PR jako ostatni commit gałęzi, tuż przed scaleniem, więc nie liczy się do zakresu.

## Usunięcie kroku łańcucha

Poprawka usuwa krok łańcucha, gdy w `git diff --name-status` PR-a plik w `skills/` jest usunięty (`D`) albo przeniesiony (`R`). Tak samo, gdy w zmienionym pliku spadła liczba wystąpień `/<nazwa>` dla którejkolwiek nazwy katalogu z `skills/` w `origin/master`. Liczby porównuje się między `origin/master` a gałęzią PR-a. Reguła jest mechaniczna i czasem da człowiekowi poprawkę, która kroku nie usuwa; to świadomy koszt (D-100).

## Płatne testy skilli

Poprawka skilla z tej listy czeka na człowieka z decyzją na jedno słowo, bo jego test zachowania kosztuje. Koszt to średnia z `docs/testy-fabryki.md`.

- `skills/10x-new/` → `chain` (ok. 3 USD)
- `skills/10x-plan/` → `chain` (ok. 3 USD)
- `skills/10x-goal-implement/` → `chain` (ok. 3 USD)
- `skills/10x-archive/` → `chain` (ok. 3 USD)
- `skills/retro/` → `chain` (ok. 3 USD)
- `skills/intent/` → `intent` (ok. 0,6 USD)
- `scripts/autopilot.py` → `chain` (ok. 3 USD)
- `scripts/retro_pr.py` → `chain` (ok. 3 USD)
