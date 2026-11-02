# Zmiany w skillach 10x — paczka-eksport

- **Źródło:** zmiana `paczka-eksport` (kryteria P6, P7 i P8 w `change.md` zmiany; ograniczenie D-287 w rejestrze ograniczeń repo fabryki).

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-archive

- **Co zmienić:** w części o retrospektywie, w kroku, który uruchamia skill `retro`, brak tego skilla przestaje zatrzymywać archiwum. Skill wypisuje wtedy jedną linię `ℹ skill retro not installed — retrospective skipped.` i przechodzi od razu do przeniesienia folderu i stempla w `change.md`. Sprawdzenie, czy powstał dokładnie jeden nowy plik `retro.md`, i jego osobny commit zostają bez zmian i dotyczą tylko przebiegu, w którym `retro` ruszył. Zdanie we wstępie skilla mówi, że folder w archiwum ma `retro.md` tylko przy zainstalowanym `retro`, a wiersz `Retrospective:` w potwierdzeniu końcowym dopuszcza też wartość `skipped (retro not installed)`.
- **Dlaczego:** paczka 1.0 nie zawiera skilla `retro`, bo pętla uczenia zostaje w repo fabryki. Bez tej zmiany u użytkownika paczki żadna zmiana nie doszłaby do archiwum, bo skill stawał przy braku `retro`. Przy zainstalowanym `retro` archiwum działa jak dotąd.
- **Zależności:** brak nowych plików. Skill `retro` fabryki jest opcjonalny; gdy jest, krok działa jak wcześniej.
- **Jak sprawdzić:** `grep -n 'retro not installed' skills/10x-archive/SKILL.md` pokazuje linię pominięcia w kroku uruchamiania `retro` i wartość wiersza `Retrospective:` w potwierdzeniu. W repo bez skilla `retro` w `~/.claude/skills` i w projekcie `/10x-archive` wypisuje linię pominięcia, nie tworzy commitu `docs(<change-id>): retrospektywa` i kończy commitem `chore(archive): close <change-id>`.

## 10x-infra-research

- **Co zmienić:** z listy `allowed-tools` we frontmatterze skilla znika `Write`. Reszta listy i treść skilla zostają bez zmian.
- **Dlaczego:** pozycja `Write` w `allowed-tools` daje zezwolenie z góry na zapis dowolnego pliku, także wtedy, gdy krok `infrastruktura` autopilota startu projektu pozwala zapisać tylko swoje dwa pliki (D-287). Bez niej skill zapisuje `context/foundation/infrastructure.md` przez uprawnienia kroku albo po zgodzie człowieka w zwykłej sesji.
- **Zależności:** w kroku autopilota uprawnienia kroku `infrastruktura` w `<fabryka>/scripts/autopilot.py` (`INFRA_ALLOWED_TOOLS`: reguły `Edit(./…)` tylko dla dwóch plików kroku, tryb `dontAsk`). W zwykłej sesji Claude Code pyta człowieka o zgodę przy zapisie pliku.
- **Jak sprawdzić:** `awk '/^allowed-tools:/{f=1;next} /^[^ ]/{f=0} f' skills/10x-infra-research/SKILL.md` nie wypisuje linii `  - Write`. W kroku `infrastruktura` autopilota próba zapisu pliku innego niż dwa pliki kroku kończy się odmową uprawnień, a `context/foundation/infrastructure.md` powstaje.
