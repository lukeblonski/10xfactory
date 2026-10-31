# Zmiany w skillach 10x — etap 1: porządki

- **Zakres:** `d063e05..04c9950`, od oryginalnych skilli kursu (tag `upstream-10x`) do zamknięcia etapu 1.
- **Lista skilli:** `git diff --name-only d063e05 04c9950 -- 'skills/10x-*'`.
- **Cel etapu:** każde odwołanie w skillach prowadzi do czegoś, co istnieje. Opisy tego samego formatu są spójne. Każdy skill z łańcucha podaje poprawny następny krok.

**Wspólne zależności:**
- `scripts/check_refs.py` i `scripts/test_check_refs.py` z repo fabryka. Skrypt sprawdza odwołania `/10x-*`, `references/…` i `scripts/…` w skillach oraz to, czy kopie `references/progress-format.md` są identyczne z wersją w `10x-plan`.
- Nie jest potrzebny do działania skilli, tylko do sprawdzenia zmian.

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-archive

- **Co zmienić:** w części o obsłudze błędów przy przenoszeniu folderu usuń wzmiankę o skillu `/10x-status`. Powiedz, że niezgodność statusu z miejscem folderu wykryje planowane sprawdzenie spójności, którego dziś żaden skill nie uruchamia.
- **Dlaczego:** skill `/10x-status` nie istnieje. Agent, który go szuka albo każe go uruchomić, zatrzymuje się.
- **Zależności:** brak.
- **Jak sprawdzić:** `grep -n "10x-status" skills/10x-archive/SKILL.md` nic nie zwraca, a `python3 scripts/check_refs.py` kończy się kodem 0.

## 10x-bootstrapper

- **Co zmienić:** w `SKILL.md` (opis roli skilla i zasada o rejestrze startów), w `references/bootstrapper-config.yaml` i w `references/scaffold-merge.md` usuń twierdzenie, że zgodność `starter_id` z rejestrem pilnuje walidator CI `scripts/validate-starter-registry-sync.mjs`. Napisz, że zgodność utrzymuje się ręcznie, a w czasie działania skill odrzuca nieznany `starter_id` zgodnie z `references/refusal-protocol.md` (przypadek b). W nagłówku `bootstrapper-config.yaml` ścieżkę do rejestru zapisz względnie: `../../10x-tech-stack-selector/references/starter-registry.yaml`.
- **Dlaczego:** walidator nie istnieje, więc tekst obiecywał zabezpieczenie, którego nie ma. Ścieżka bez `../../` wskazywała plik we własnym folderze skilla, gdzie go nie ma.
- **Zależności:** brak.
- **Jak sprawdzić:** `grep -rn "validate-starter-registry-sync" skills/10x-bootstrapper` nic nie zwraca, a `python3 scripts/check_refs.py` kończy się kodem 0.

## 10x-e2e

- **Co zmienić:** dodaj podsekcję o niezgodności planu z rzeczywistością, obok zasad pisania testów (przed częścią o umieszczaniu plików). Gdy ryzyka nie da się przetestować tak, jak opisuje plan, skill zatrzymuje się i pokazuje problem w czterech polach: miejsce w planie, czego plan oczekuje, co jest naprawdę i dlaczego to ważne. Potem pyta o wybór: dostosować i kontynuować, pominąć tę część albo zatrzymać się i poprawić plan. Brak całej funkcji obsługuje już wcześniejsza bramka sprawdzająca, czy funkcja istnieje.
- **Dlaczego:** `10x-tdd` i `10x-implement` mają taką procedurę, a `10x-e2e` nie. Ta sama niezgodność była obsługiwana różnie w zależności od skilla.
- **Zależności:** brak.
- **Jak sprawdzić:** w `skills/10x-e2e/SKILL.md` jest podsekcja o niezgodności planu z rzeczywistością z tym samym zestawem pól i opcji co w `10x-tdd`.

## 10x-goal-implement

- **Co zmienić:** dodaj plik `references/progress-format.md` jako dokładną kopię `skills/10x-plan/references/progress-format.md`, w wersji po zmianie opisanej w sekcji `10x-plan` poniżej.
- **Dlaczego:** skill odsyła do tego pliku, a w jego folderze go nie było. Zainstalowany osobno, bez `10x-plan`, nie miał opisu formatu, na którym działa.
- **Zależności:** sekcja `10x-plan` (treść kopii). Opcjonalnie `scripts/check_refs.py`, który pilnuje identyczności kopii.
- **Jak sprawdzić:** `cmp skills/10x-plan/references/progress-format.md skills/10x-goal-implement/references/progress-format.md` nie zgłasza różnic.

## 10x-impl-review

- **Co zmienić:** dwie poprawki w `SKILL.md`.
  - W kroku weryfikacji kryteriów mów o punktach (`- `) w sekcjach Automated Verification, a nie o polach wyboru.
  - W części o zapisie raportu zamień `/10x-status` na planowane sprawdzenie spójności statusu, bez nazwy skilla.

  Dodaj też `references/progress-format.md` jako kopię pliku z `10x-plan`.
- **Dlaczego:** od zmiany formatu planu pola wyboru występują tylko w `## Progress`, więc skill opisywał coś, czego w planie nie ma. Skill `/10x-status` nie istnieje. Bez kopii formatu skill zainstalowany osobno odsyłał do brakującego pliku.
- **Zależności:** sekcja `10x-plan` (treść kopii).
- **Jak sprawdzić:** `grep -n "10x-status" skills/10x-impl-review/SKILL.md` nic nie zwraca. Krok weryfikacji kryteriów mówi o punktach Automated Verification. Pola wyboru pojawiają się w skillu tylko przy sekcji `## Progress`. Kopia jest identyczna z plikiem z `10x-plan` (`cmp`).

## 10x-impl-review-ci

- **Co zmienić:**
  - `SKILL.md` i `references/impl-review-instructions.md`: kryteria w fazach planu to zwykłe punkty `- `. Stan wykonania (`[ ]`/`[x]` i SHA zamykającego commita) czyta się tylko z wierszy `N.M` w `## Progress` na końcu planu. Opisz to w części o wyciąganiu zobowiązań z planu, w dopasowaniu komend testowych i w weryfikacji kryteriów ręcznych.
  - `references/workflow-template.yml`: model w `claude_args` to alias `opus` zamiast nazwy konkretnej wersji.
- **Dlaczego:** recenzja w CI szukała pól wyboru w fazach, których po zmianie formatu tam nie ma, więc mogła źle ocenić kryteria. Sztywna wersja modelu się starzeje, a alias zawsze wskazuje najnowszego Opusa.
- **Zależności:** brak.
- **Jak sprawdzić:** `grep -n "opus" skills/10x-impl-review-ci/references/workflow-template.yml` pokazuje `--model opus`. W instrukcjach recenzji stan kryteriów pochodzi z `## Progress`.

## 10x-implement

- **Co zmienić:** dodaj `references/progress-format.md` jako dokładną kopię pliku z `10x-plan`.
- **Dlaczego:** skill odsyła do tego pliku, a w jego folderze go nie było.
- **Zależności:** sekcja `10x-plan` (treść kopii).
- **Jak sprawdzić:** `cmp skills/10x-plan/references/progress-format.md skills/10x-implement/references/progress-format.md` nie zgłasza różnic.

## 10x-infra-research

- **Co zmienić:** zamiast stałego następnego kroku `/10x-implement` skill wybiera go z miejsca projektu w procesie.
  - Jest `context/foundation/tech-stack.md`, a nie ma `context/changes/bootstrap-verification/` (folder, który zakłada bootstrapper): `/10x-bootstrapper`.
  - W każdym innym przypadku: `/10x-roadmap`.

  Zmień to w trzech miejscach: w opisie we frontmatterze (gdzie skill stoi w łańcuchu), na liście sąsiednich skilli i w zakończeniu (schowek, linia `► Next:` i zakaz automatycznego przejścia dalej).
- **Dlaczego:** `/10x-implement` bez change-id nie da się uruchomić. Według `docs/spec.md` po wyborze platformy następuje założenie projektu albo roadmapa, a nie implementacja.
- **Zależności:** brak.
- **Jak sprawdzić:** w `skills/10x-infra-research/SKILL.md` nie ma gołego `/10x-implement` jako następnego kroku. Zakończenie opisuje oba warunki i obie komendy.

## 10x-init

- **Co zmienić:** w zasadzie o plikach, których init nie tworzy, usuń `/10x-contract`. Plik `lessons.md` zakładają `/10x-lesson` i gałąź „Record as lesson” w triage `/10x-impl-review`. `contract-surfaces.md` to opcjonalna konwencja projektu, której dziś nie tworzy żaden skill.
- **Dlaczego:** skill `/10x-contract` nie istnieje.
- **Zależności:** brak.
- **Jak sprawdzić:** `grep -n "10x-contract" skills/10x-init/SKILL.md` nic nie zwraca.

## 10x-new

- **Co zmienić:**
  - W `SKILL.md` odwołanie do schematu `change.md` wskazuje `references/change-md.md` (z „s”).
  - W `references/change-md.md`, w części o aktualizacji pliku, zamień `/10x-status` na planowane sprawdzenie zgodności statusu z plikami zmiany, bez nazwy skilla.
- **Dlaczego:** folder nazywa się `references/`, więc stara ścieżka prowadziła donikąd. Skill `/10x-status` nie istnieje.
- **Zależności:** brak.
- **Jak sprawdzić:** `python3 scripts/check_refs.py` kończy się kodem 0, a `grep -rn "10x-status" skills/10x-new` nic nie zwraca.

## 10x-plan

- **Co zmienić:**
  - W `SKILL.md`, po zapisaniu planu, następny krok to `/10x-plan-review <change-id>` (w schowku i w podsumowaniu). `/10x-implement <change-id> phase 1` jest podany jako krok po review.
  - W wytycznych o kryteriach sukcesu kryteria w fazach to zwykłe punkty `- `, a pola wyboru występują tylko w `## Progress`.
  - W `references/progress-format.md` usuń `/10x-status` z listy skilli czytających Progress i z listy skilli, które go tylko czytają. Wykrywanie rozjazdu statusu opisz jako planowane sprawdzenie, którego dziś nikt nie uruchamia.
- **Dlaczego:** pominięcie review planu było domyślną ścieżką, bo skill od razu podsuwał implementację. Wytyczne o polach wyboru przeczyły szablonowi planu z tego samego skilla. `/10x-status` nie istnieje.
- **Zależności:** ten plik `progress-format.md` jest wzorcem kopii w `10x-goal-implement`, `10x-implement`, `10x-impl-review`, `10x-plan-review` i `10x-tdd`.
- **Jak sprawdzić:** po `/10x-plan` w schowku jest `/10x-plan-review <change-id>`. `grep -n "10x-status" skills/10x-plan/references/progress-format.md` nic nie zwraca.

## 10x-plan-review

- **Co zmienić:**
  - Dodaj na końcu triage podsekcję „Next command”: następna komenda zależy od werdyktu.
    - SOUND: `/10x-implement <change-id> phase 1`.
    - REVISE: ta sama komenda z dopiskiem, że uruchamia się ją po naniesieniu poprawek.
    - RETHINK: `/10x-plan <change-id>`.
    - Gdy triage zmienił werdykt, decyduje werdykt po poprawkach.
    - Komenda trafia do schowka i jest wypisana.
  - Podaj ją w trzech miejscach: po „Save report only”, po podsumowaniu triage i przy wznowieniu, gdy nie zostało nic do rozstrzygnięcia.
  - W sprawdzaniu powierzchni kontraktu usuń `/10x-contract`. `contract-surfaces.md` to opcjonalna konwencja projektu, której nie tworzy żaden skill.
  - Dodaj `references/progress-format.md` jako kopię pliku z `10x-plan`.
- **Dlaczego:** skill kończył pracę bez następnego kroku, więc łańcuch się urywał. `/10x-contract` nie istnieje. Bez kopii formatu skill zainstalowany osobno odsyłał do brakującego pliku.
- **Zależności:** sekcja `10x-plan` (treść kopii).
- **Jak sprawdzić:** po review z werdyktem SOUND skill wypisuje `/10x-implement <change-id> phase 1`. `grep -n "10x-contract" skills/10x-plan-review/SKILL.md` nic nie zwraca.

## 10x-research

- **Co zmienić:**
  - W „Initial Setup”: gdy pytanie badawcze jest w argumentach, skill zaczyna od razu. O pytanie prosi tylko wtedy, gdy dostał sam change-id albo nic.
  - Pierwszy token argumentów, który nazywa istniejący folder `context/changes/<token>/`, to change-id, a reszta to pytanie.
  - Przy ustalaniu folderu zmiany kolejność jest taka: pierwszy token jako istniejący folder, potem jawna ścieżka `context/changes/<change-id>/` w treści pytania (tak przekazuje zmianę `/10x-test-plan`), na końcu nowy folder.
  - Na koniec skill podaje i kopiuje do schowka `/10x-plan <change-id>`.
- **Dlaczego:** skill zawsze pytał o pytanie, które już dostał, co blokuje pracę bez człowieka. Nie podawał też następnego kroku.
- **Zależności:** brak.
- **Jak sprawdzić:** `/10x-research <change-id> <pytanie>` zaczyna badanie bez pytania o temat i kończy się wypisaniem `/10x-plan <change-id>`.

## 10x-roadmap

- **Co zmienić:** usuń z opisu cyklu życia pozycji roadmapy statusy `planning` i `in-progress` oraz zapowiedzi, że kiedyś ustawią je `/10x-plan` i `/10x-implement`. Zostają `proposed`, `ready`, `blocked` (pisze je ten skill) i `done` (pisze `/10x-archive`). Zmień to na liście sąsiednich skilli, w opisie pól i w notatkach końcowych.
- **Dlaczego:** żaden skill tych statusów nie ustawia, więc opis zapowiadał stany, które nigdy nie wystąpią.
- **Zależności:** brak.
- **Jak sprawdzić:** `grep -n "in-progress\|planning" skills/10x-roadmap/SKILL.md` nie pokazuje ich jako statusów roadmapy.

## 10x-stack-assess

- **Co zmienić:** w `references/agent-friendly-criteria.md` odwołania do `decision-flow.md` i `starter-registry.yaml` wskazują pliki skilla `10x-tech-stack-selector`: `../../10x-tech-stack-selector/references/…`.
- **Dlaczego:** te pliki należą do `10x-tech-stack-selector`. Ścieżka względem własnego folderu prowadziła donikąd.
- **Zależności:** skill `10x-tech-stack-selector` zainstalowany obok.
- **Jak sprawdzić:** `python3 scripts/check_refs.py` kończy się kodem 0.

## 10x-tdd

- **Co zmienić:** dodaj `references/progress-format.md` jako dokładną kopię pliku z `10x-plan`.
- **Dlaczego:** skill odsyła do tego pliku, a w jego folderze go nie było.
- **Zależności:** sekcja `10x-plan` (treść kopii).
- **Jak sprawdzić:** `cmp skills/10x-plan/references/progress-format.md skills/10x-tdd/references/progress-format.md` nie zgłasza różnic.

## 10x-tech-stack-selector

- **Co zmienić:** w `SKILL.md`, `references/handoff-schema.md` i nagłówku `references/starter-registry.yaml` usuń twierdzenie o walidatorze CI `scripts/validate-starter-registry-sync.mjs`. Napisz, że zgodność rejestru z bootstrapperem utrzymuje się ręcznie, a bootstrapper odrzuca nieznany `starter_id` (`../10x-bootstrapper/references/refusal-protocol.md` z `SKILL.md`, `../../10x-bootstrapper/…` z `references/`).
- **Dlaczego:** walidator nie istnieje. To ta sama poprawka co w `10x-bootstrapper`, po drugiej stronie tej samej zależności.
- **Zależności:** skill `10x-bootstrapper` zainstalowany obok.
- **Jak sprawdzić:** `grep -rn "validate-starter-registry-sync" skills/10x-tech-stack-selector` nic nie zwraca, a `python3 scripts/check_refs.py` kończy się kodem 0.
