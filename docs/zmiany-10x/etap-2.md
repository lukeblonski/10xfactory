# Zmiany w skillach 10x — etap 2: zabezpieczenia

- **Zakres:** `04c9950..cc96456`, od zamknięcia etapu 1 do zamknięcia etapu 2.
- **Lista skilli:** `git diff --name-only 04c9950 cc96456 -- 'skills/10x-*' | grep -v guardrails`. Filtr usuwa własny skill fabryki, który w tym zakresie miał jeszcze prefiks kursu.
- **Własny skill:** własny skill etapu 2 to dziś `skills/guardrails/`. Jego kod jest publikowany wprost, więc nie ma tu sekcji. Opisy niżej używają jego obecnej nazwy `/guardrails`.
- **Cel etapu:** twarde zabezpieczenia w projekcie użytkownika: hooki, piaskownica Claude Code dla poleceń powłoki, jedna komenda `verify`, agent weryfikujący i tryb naprawy błędu, który zaczyna się od testu, którego agent nie może zmienić.

**Wspólna zależność:** skill `guardrails` z repo fabryka (`skills/guardrails/`). Instaluje w projekcie:
- hooki `.claude/hooks/guardrails/`;
- ustawienia `.claude/settings.json` z piaskownicą;
- `.claude/guardrails.json`;
- agenta `.claude/agents/verifier.md`.

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-bootstrapper

- **Co zmienić:**
  - W podsumowaniu udanego przebiegu (`SKILL.md`, krok z końcowym raportem) linia `Next:` ma wskazywać `/guardrails` z krótkim opisem (hooki, komenda `verify`, agent weryfikujący), a potem `/10x-agents-md`.
  - Ta sama linia ma się znaleźć w tekście wskazówki w `references/verification-log-schema.md`.
  - Zdanie o przyszłym skillu, który kiedyś zastąpi ten tekst, zamień na zasadę, że obie linie mają być takie same.
- **Dlaczego:** po założeniu projektu następnym krokiem jest instalacja zabezpieczeń, zanim agent zacznie pisać kod. Stary tekst odsyłał do skilla, który nie istniał.
- **Zależności:** skill `guardrails`.
- **Jak sprawdzić:** `grep -n "/guardrails" skills/10x-bootstrapper/SKILL.md skills/10x-bootstrapper/references/verification-log-schema.md` pokazuje oba miejsca z tą samą linią `Next:`.

## 10x-health-check

- **Co zmienić:**
  - W opisie we frontmatterze skill stoi przed `/guardrails` zamiast przed ogólnym „agent onboarding”.
  - W bloku końcowym linia `► Next:` wskazuje `/guardrails` (hooki, `verify`, agent weryfikujący), a potem wdrożenie agenta.
  - W `references/health-check-schema.md` zalecenie „Next step” kończy się poleceniem `/guardrails` przy każdym werdykcie: po poprawkach z raportu albo od razu, gdy projekt jest zdrowy.
- **Dlaczego:** w ścieżce dla istniejącego projektu zabezpieczenia też mają powstać przed pracą agenta. Stary tekst nie podawał żadnej komendy.
- **Zależności:** skill `guardrails`.
- **Jak sprawdzić:** `grep -n "/guardrails" skills/10x-health-check/SKILL.md skills/10x-health-check/references/health-check-schema.md` pokazuje frontmatter, blok końcowy i schemat.

## 10x-tdd

- **Co zmienić:** dodaj tryb naprawy błędu.
  - **Wejście:** `/10x-tdd <change-id> bug [opis]`. Opis we frontmatterze o nim wspomina. Krok ustalania planu w Setup kieruje tę formę do nowej sekcji `## Bug-fix mode`, z pominięciem reszty Setup, bramki kwalifikacji (kod produkcyjny już istnieje) i pętli faz. `plan.md` nie jest potrzebny. Tryb nie zadaje pytań, więc działa w `claude -p`.
  - **Warunki wstępne** (każdy niespełniony to STOP z powodem):
    - folder zmiany istnieje i nie jest w archiwum;
    - błąd jest opisany w argumencie albo w `change.md`;
    - zabezpieczenia są zainstalowane: istnieje `.claude/hooks/guardrails/lock_tests.py`, `.claude/settings.json` rejestruje go jako hook i ma `sandbox.enabled: true`, w przeciwnym razie STOP z poleceniem `/guardrails`;
    - nic nie jest w indeksie git;
    - jest narzędzie do testów.

    Na starcie `status: implementing`.
  - **Siedem kroków w stałej kolejności:**
    1. Nowy test odtwarzający błąd, bez zmiany innych testów.
    2. Uruchomienie samego tego testu. Musi nie przechodzić z właściwego powodu, czyli przez asercję pokazującą błąd, a nie przez błąd importu. Przy złym powodzie popraw test i uruchom go ponownie. Gdy przechodzi, test nie odtwarza błędu: przerób go, a STOP dopiero wtedy, gdy nie da się doprowadzić go do porażki.
    3. Commit samego testu: `test(<change-id>): failing repro`, bez `--no-verify`, z zapisanym SHA. Gdy hook pre-commit odrzuci ten commit, STOP z jego komunikatem.
    4. Blokada: ścieżka testu dopisana narzędziem Write/Edit do `.claude/locked-tests`. Potem sonda `touch -c <plik testu>` powtarzana (najwyżej 10 razy, bez innych poleceń w międzyczasie), aż piaskownica ją odrzuci („Operation not permitted”). Bez odmowy STOP. `.claude/locked-tests`, `.claude/locked-tests.sandbox` i `.claude/settings.local.json` nie trafiają do commita.
    5. Poprawka tylko w kodzie produkcyjnym. Gdy test wydaje się zły, STOP bez zdejmowania blokady.
    6. Zielony test, potem pełne `verify` z `AGENTS.md`/`CLAUDE.md` albo pełny zestaw testów.
    7. Zdjęcie blokady: linia testu usunięta z `.claude/locked-tests`, a plik usunięty, gdy zostanie pusty. `git diff --quiet <SHA z kroku 3> -- <plik testu>` musi przejść, w przeciwnym razie STOP. Lista plików zmienionych od commita z kroku 3 (`git diff --name-only <SHA>` i pliki nieśledzone, bez lokalnych plików blokady z kroku 4) nie może zawierać kodu ani konfiguracji testów (inne testy, fixtures, snapshoty, konfiguracja runnera), w przeciwnym razie STOP z listą tych plików. Potem `status: implemented` i commit `fix(<change-id>): <opis>` z plikami produkcyjnymi i `change.md`, bez `--no-verify` i bez `--amend`. Po commicie `git status --porcelain` nie pokazuje nic z tego przebiegu.
  - **Podsumowanie:** dwa SHA, potwierdzenie, że test się nie zmienił, lista zmienionych plików i następny krok (`/10x-archive`, a przy zmianie z planem najpierw `/10x-impl-review`).
  - **Wyjątek:** w zasadzie „commit tylko na zielono” (rytuał końca fazy) dopisz, że jedynym wyjątkiem jest commit z kroku 3 trybu naprawy.
- **Dlaczego:** naprawa błędu bez testu, którego agent nie może zmienić, pozwala dopasować test do błędnego kodu. Zablokowany test wymusza poprawkę w kodzie produkcyjnym, a historia git pokazuje, że test był czerwony przed poprawką i nie zmienił się po niej.
- **Zależności:**
  - skill `guardrails` zainstalowany w projekcie: hook `lock_tests.py` (blokuje edycję testu i przepisuje blokadę do piaskownicy przez `.claude/settings.local.json`, z oknem `lock-pending` i wyjątkiem dla sondy `touch -c`) i piaskownica Claude Code w `.claude/settings.json`;
  - opcjonalnie skrypty fabryki `scripts/create_sandbox.sh` i `scripts/e2e_guardrails.sh` do prób.
- **Jak sprawdzić:** w projekcie z zainstalowanym `guardrails` i znanym błędem uruchom `claude -p "/10x-tdd <change-id> bug" --model opus`. W historii git jest `test(<change-id>): failing repro`, a po nim `fix(<change-id>): …`, i `git diff --quiet <test-sha> <fix-sha> -- <plik testu>` kończy się kodem 0. `scripts/e2e_guardrails.sh` (przypadki blokady testu i sondy) przechodzi.
