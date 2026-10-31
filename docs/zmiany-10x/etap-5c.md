# Zmiany w skillach 10x — etap 5c: retrospektywa i jawny model

- **Zakres:** gałąź `etap-5c-retrospektywa` od `425c725` (`master` przed etapem) do zamknięcia zmiany.
- **Lista skilli:** `git diff --name-only 425c725 etap-5c-retrospektywa -- 'skills/10x-*'`. Wynik: `10x-implement`, `10x-goal-implement`, `10x-tdd`, `10x-e2e`, `10x-impl-review`, `10x-archive`.
- **Własny skill:** `skills/retro/` (retrospektywa jednej zmiany). Jego kod jest publikowany wprost, więc nie ma tu sekcji.
- **Cel etapu:** fabryka wyciąga wnioski z każdej zamkniętej zmiany. Archiwizacja zostawia w folderze zmiany plik `retro.md` z propozycjami dla człowieka. Każdy raport z przebiegu i raport weryfikatora mówi, jaki model wykonał krok, a polecenie headless kroku fabryki podaje model jawnie.

**Wspólne zależności:**
- `run-report-format.md` z repo fabryka: oryginał w `10x-implement`, kopie w `10x-goal-implement`, `10x-tdd`, `10x-e2e`, `10x-impl-review` i `10x-archive`. Ten etap dopisuje do niego pole `Model`.
- `scripts/check_refs.py` z repo fabryka pilnuje, żeby pięć kopii było bajt w bajt równych oryginałowi.
- `.claude/settings.json` projektu z kluczem `"model": "opus"` (opcjonalnie; polecenia headless podają model same).

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-implement

- **Co zmienić:**
  - W `references/run-report-format.md` (oryginał) dodaj pole `Model` w nagłówku raportu z przebiegu (po `Skill`) i w nagłówku raportu weryfikatora (po `Agent`), także w obu przykładach.
  - Dopisz zasadę: wartość to pełny identyfikator modelu sesji podany w prompcie systemowym, a nie alias; stare raporty bez tego pola zostają ważne. Przy raporcie weryfikatora dopisz, że agent bez własnego modelu dziedziczy model sesji.
  - W kroku zakładania pliku raportu dopisz, że nagłówek dostaje `Model` z pełnym identyfikatorem.
- **Dlaczego:** alias wskazuje różne modele w kolejnych wersjach Claude Code, a raz krok bez człowieka wykonał domyślny model konta zamiast Opusa. Bez zapisu nie da się później ustalić, który model zrobił krok.
- **Zależności:** pięć kopii formatu i `check_refs.py`.
- **Jak sprawdzić:** `grep -n 'Model' skills/10x-implement/references/run-report-format.md` pokazuje pole w obu nagłówkach i w obu przykładach; `python3 scripts/check_refs.py` kończy się kodem 0.

## 10x-goal-implement

- **Co zmienić:**
  - Do polecenia uruchomienia bez człowieka (tryb headless z `--permission-mode acceptEdits`) dodaj `--model opus`.
  - W kroku zakładania pliku raportu i w opisie pliku raportu dopisz pole `Model` z pełnym identyfikatorem modelu sesji.
  - Skopiuj nowy `run-report-format.md` z `10x-implement`.
- **Dlaczego:** polecenie headless nie może zależeć od ustawień konta ani projektu użytkownika; raport ma mówić, który model wykonał plan.
- **Zależności:** oryginał formatu w `10x-implement`.
- **Jak sprawdzić:** `grep -n 'claude -p' skills/10x-goal-implement/SKILL.md` pokazuje polecenie z `--model opus`. Przebieg `claude -p "/goal <warunek> /10x-goal-implement <change-id>" --model opus` zostawia w `runs/` raport z linią `- **Model**: claude-…`.

## 10x-tdd

- **Co zmienić:**
  - W obu miejscach zakładania raportu, w trybie planu i w trybie naprawy błędu, dopisz pole `Model` z pełnym identyfikatorem modelu sesji.
  - Skopiuj nowy `run-report-format.md` z `10x-implement`.
- **Dlaczego:** tryb naprawy błędu działa też bez człowieka, więc jego raport też ma mówić, jaki model go wykonał.
- **Zależności:** oryginał formatu w `10x-implement`.
- **Jak sprawdzić:** `grep -n 'Model' skills/10x-tdd/SKILL.md` daje dwa trafienia. Przebieg `claude -p "/10x-tdd <change-id> bug" --model opus` zostawia raport z polem `Model`.

## 10x-e2e

- **Co zmienić:**
  - W kroku zakładania raportu dopisz pole `Model` z pełnym identyfikatorem modelu sesji.
  - Skopiuj nowy `run-report-format.md` z `10x-implement`.
- **Dlaczego:** ten sam powód co w pozostałych skillach, które piszą raport z przebiegu.
- **Zależności:** oryginał formatu w `10x-implement`.
- **Jak sprawdzić:** `grep -n 'Model' skills/10x-e2e/SKILL.md` pokazuje wzmiankę przy zakładaniu raportu.

## 10x-impl-review

- **Co zmienić:** skopiuj nowy `run-report-format.md` z `10x-implement`. Skill nie pisze raportów, a jego skrypt nie czyta pól nagłówka, więc nic więcej się nie zmienia.
- **Dlaczego:** kopie formatu muszą być równe oryginałowi.
- **Zależności:** oryginał formatu w `10x-implement`.
- **Jak sprawdzić:** `python3 scripts/check_refs.py` kończy się kodem 0.

## 10x-archive

- **Co zmienić:**
  - Krok uruchomienia weryfikatora notuje, obok `HEAD` i czasu startu, pełny identyfikator modelu sesji, a zapis raportu weryfikatora wpisuje go do nagłówka.
  - Dodaj nowy krok „Retrospective” po ostrzeżeniach, a przed stemplem `change.md` i przeniesieniem folderu:
    - gdy `retro.md` jest już śledzony i czysty (ponowne uruchomienie po zatrzymaniu dalej), krok jest pomijany z jedną linią informacji;
    - przed wywołaniem zapisz wynik `git status --porcelain`, potem wywołaj `/retro <change-id>` narzędziem Skill; brak skilla to zatrzymanie z prośbą o instalację;
    - po wywołaniu jedyną nową linią statusu może być nieśledzony `retro.md` tej zmiany; brud sprzed wywołania nie przeszkadza, a każda inna nowa ścieżka zatrzymuje archiwizację przed przeniesieniem; brak `retro.md` po wywołaniu też ją zatrzymuje, po wypisaniu nowych ścieżek, jeśli są;
    - commit samego `retro.md` po ścieżce, z tematem `docs(<change-id>): retrospektywa`, po sprawdzeniu, że poczekalnia zawiera tylko ten plik.
  - Dodaj `Skill` do dozwolonych narzędzi, `retro.md` (istnienie i stan w git) do „Co czytam”, linię z commitem retrospektywy do potwierdzenia końcowego, krótką wzmiankę w opisie na górze i punkt „nie czyta i nie stosuje propozycji retrospektywy” do listy rzeczy, których skill nie robi.
- **Dlaczego:** wnioski ze zmiany wyciągał dotąd człowiek poza fabryką. Retrospektywa powstaje, póki folder jest jeszcze w `context/changes/`, bo archiwum jest niezmienne. Osobny commit jest potrzebny, bo `git mv` przenosi nieśledzony plik, ale go nie dodaje.
- **Zależności:** własny skill `retro` zainstalowany obok skilli 10x; nowy `run-report-format.md` z `10x-implement`.
- **Jak sprawdzić:** archiwizacja zmiany w projekcie z zainstalowanym `retro` daje w historii commit `docs(<change-id>): retrospektywa` przed `chore(archive): close <change-id>`, a zarchiwizowany folder ma `retro.md`. Bez zainstalowanego `retro` archiwizacja zatrzymuje się przed przeniesieniem folderu.
