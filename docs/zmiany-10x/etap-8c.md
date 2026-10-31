# Zmiany w skillach 10x — etap 8c: dziennik w trzech plikach, fazy w podagentach, kryteria w ręcznym triage'u

- **Zakres:** gałąź `etap-8c-porzadki` od `36a0195` (`master` przed zmianą) do zamknięcia zmiany.
- **Lista skilli:** `git diff --name-only master...HEAD -- 'skills/10x-*'`. Sekcje dostają skille `10x-*` z tej listy.
- **Własne skille:** `skills/intent/` (opis trzech plików decyzji, jedna numeracja, archiwum, do dziennika tylko decyzje wiążące przyszłe zmiany; rejestr i archiwum poza lekturą) i `skills/retro/` (czyta dziennik i rejestr ograniczeń, archiwum nie). Ich kod jest publikowany wprost, więc nie mają tu sekcji.
- **Poza skillami:** podział `context/foundation/decisions.md` na dziennik, rejestr ograniczeń `context/foundation/limitations.md` i archiwum `context/foundation/decisions-archive.md`; lekcje 5 i 6 w `context/foundation/lessons.md`; podkomendy `phase-agents` i `skill-source` w `scripts/evallib.py` z testami w `scripts/test_evallib.py`; przypadek `chain-subagent` w `scripts/eval_chain.sh`; w `docs/testy-fabryki.md` opis tego przypadku i przepis płatnego przebiegu `retro` na kopii skilla; opis trzech plików w `docs/spec.md` i `context/foundation/README.md`.
- **Źródło:** lista zadań człowieka (poza repo), `po-8b.md`, punkty 2–6, zatwierdzona przez człowieka 2026-10-22; propozycje P1–P3 retrospektywy etap-8b-rejestr-ograniczen (D-091).

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-impl-review

- **Co zmienić:**
  - Zapis decyzji ograniczenia (sekcja wspólna z review planu): wpis trafia na koniec rejestru ograniczeń w osobnym pliku, a brakujący plik powstaje z własnym nagłówkiem. Numer wpisu to największy numer z nagłówków dziennika, rejestru i archiwum plus jeden, bo trzy pliki mają jedną numerację. Ostatni nagłówek jednego pliku nie wystarcza.
  - „Co czytam”: rejestr tylko do dopisania wpisu, a z dziennika i archiwum same nagłówki do numeru.
  - Commit dokumentów triage'u, który bierze plik lekcji, bierze rejestr zamiast dziennika, gdy rejestr się zmienił. To samo w poleceniu commitu przy przekroczonym zakresie planu.
  - Przykład w warunku startu mówi o wpisach dziennika i rejestru. Sama reguła się nie zmienia.
  - Polityka triage'u w jednym miejscu: rejestr ograniczeń leży w nowym pliku. Reszta polityki bez zmian, a obie kopie zostają identyczne.
  - Triage ręczny, nowy punkt przy przyjmowaniu poprawki: gdy decyzja człowieka zmienia zakres zmiany (co zmiana robi, czego nie robi, które pliki zmienia), przed potwierdzeniem skill czyta wszystkie kryteria i decyzje z góry w notatkach zmiany, najpierw te wyłączające i te, które nazywają zmieniany plik. Kryterium, którego decyzja już nie spełnia, dostaje nowe brzmienie. Nowe brzmienie stoi obok poprawki w tym samym pytaniu o zgodę i trafia do tego samego commitu. Gdy żadne kryterium nie wymaga zmiany, pytanie mówi to jednym zdaniem.
- **Dlaczego:** dziennik decyzji miał ok. 70 KB, z czego większość to ograniczenia, których skill intencji nie potrzebuje, a czytał go przy każdej zmianie. Po podziale reguła „ostatni nagłówek pliku plus jeden” dałaby zajęty numer. Dwa razy brzmienie kryterium nie nadążyło za decyzją człowieka wdrożoną w ręcznym triage'u, a weryfikator zatrzymał archiwum (etap-8b E11 przy D-088).
- **Zależności:** format wpisów i reguła numeru w `skills/intent/references/principles-and-decisions.md`. Kontrola `SHARED_SECTIONS` w `scripts/check_refs.py` wymaga, żeby sekcja zapisu decyzji była taka sama w obu skillach review. Test `triage` dostaje politykę triage'u w prompcie, więc nowa ścieżka rejestru zmienia jego wejście. Punktu triage'u ręcznego nie pilnuje żadna kontrola: oba skille trzeba poprawiać razem.
- **Jak sprawdzić:** `! grep -rnE 'end of .context/foundation/decisions\.md|ograniczeń w .context/foundation/decisions\.md' skills` nic nie zwraca; `grep -c 'decisions-archive.md' skills/10x-impl-review/SKILL.md` daje co najmniej 1; `python3 scripts/check_refs.py` kończy się kodem 0; `awk '/^\*\*Handling responses/,/^\*\*Overriding/' skills/10x-impl-review/SKILL.md | grep -i criteri` pokazuje nowy punkt.

## 10x-plan-review

- **Co zmienić:**
  - Zapis decyzji ograniczenia: ta sama zmiana co w review kodu, tym samym tekstem (rejestr w osobnym pliku, numer z trzech plików).
  - „Co czytam”, commit dokumentów triage'u i przykład w warunku startu: jak w review kodu.
  - Polityka triage'u: ta sama zmiana ścieżki rejestru, kopia identyczna z review kodu.
  - Triage ręczny: ten sam nowy punkt o brzmieniu kryteriów przy decyzji, która zmienia zakres zmiany. Dotyczy poprawki planu, poprawki innym sposobem i odpowiedzi własnymi słowami.
- **Dlaczego:** jak w review kodu. Review planu zapisuje ograniczenia tym samym krokiem, a poprawki planu częściej zmieniają zakres niż poprawki kodu.
- **Zależności:** jak w review kodu.
- **Jak sprawdzić:** `grep -c 'decisions-archive.md' skills/10x-plan-review/SKILL.md` daje co najmniej 1; `cmp skills/10x-impl-review/references/triage-policy.md skills/10x-plan-review/references/triage-policy.md` kończy się kodem 0; `awk '/^\*\*Handling responses/,/^\*\*Overriding/' skills/10x-plan-review/SKILL.md | grep -i criteri` pokazuje nowy punkt.

## 10x-goal-implement

- **Co zmienić:**
  - Sesja główna przestaje sama implementować fazy. Dla każdej fazy uruchamia po kolei jednego podagenta ogólnego typu ze świeżym kontekstem (nigdy rozwidlenia, które dziedziczy rozmowę), z aliasem rodziny modelu sesji. Czeka na jego wynik, zanim zrobi cokolwiek dalej. W sesji interaktywnej podagent idzie w tle, więc sesja czeka na powiadomienie o końcu; ponaglenie w tym czasie tylko sprawdza stan podagenta i niczego nie zmienia. Brak narzędzia podagenta, odmowa uruchomienia i podagent, który skończył bez bloku wyniku albo stoi, idą tą samą ścieżką co brak bloku: zatrzymanie z dowodami. Sesja nigdy nie robi fazy sama i nie uruchamia drugiego podagenta tej fazy. Fazę z samymi wierszami Manual sesja zapisuje w raporcie jako pominiętą dla człowieka.
  - Prompt podagenta zawiera pełne ścieżki skilla, skryptu walidacji, planu, notatek zmiany i raportu z przebiegu, numer fazy, flagę pierwszej fazy zmiany, pliki zmienione przez sesję od ostatniego commitu fazy i linię odwołań do zadań. Podagent nie dostaje nic poza promptem.
  - Podagent robi to, co dotąd robiła pętla fazy: sprawdzenie poleceń swojej fazy, klasyfikację rozjazdów z planem, stos bramek, samodzielne poprawki, zbiór dotkniętych plików (zawsze z raportem z przebiegu), commit, SHA w Progress i wpisy Observed w raporcie. Nie uruchamia innych podagentów i nikogo nie pyta. Po commicie oddaje blok wyniku i nie przechodzi do następnej fazy.
  - Podagent kończy jednym blokiem wyniku o stałym kształcie: status, model, linie bramek, commit, odstępstwa, niepewności, pominięte bramki, wiersze Manual, a przy zatrzymaniu blok STOP.
  - Po wyniku sesja przepisuje linie bramek i commitu do swojej odpowiedzi, bo ewaluator celu czyta tylko jej rozmowę. Sprawdza, że commit istnieje i że wiersze Automated fazy mają jego SHA, a do raportu dopisuje wpisy Reported i Skipped z bloku. Rozjazd albo brak bloku kończy przebieg zatrzymaniem z dowodami.
  - „Co czytam” ma osobne części dla sesji głównej (nagłówki faz, Progress, frontmatter notatek, format raportu) i dla podagenta (cały plan, notatki zmiany, lekcje, formaty). Sprawdzenie poleceń przed startem przechodzi do podagenta. Zadania faz sesja tworzy tylko wtedy, gdy ma odpowiednie narzędzie.
  - Sekcje o bramkach, poprawkach, bloku STOP, plikach, commicie i wierszach Manual zostają w treści i kształcie linii bez zmian. Każda dostaje zdanie o tym, kto ją wykonuje. Opis raportu z przebiegu mówi, kto pisze które sekcje.
  - Frontmatter i polecenie bez człowieka dopuszczają narzędzie podagenta pod jego obecną nazwą, z notą o starszej nazwie.
- **Dlaczego:** w etap-8b sesja z pięcioma fazami doszła do 429 tys. tokenów kontekstu i zużyła 28 mln tokenów. Świeży kontekst na fazę obniża koszt każdej następnej zmiany. Ograniczenie D-041 (brak narzędzia podagenta bez człowieka) przestaje obowiązywać, bo skill zaczyna uruchamiać podagenta.
- **Zależności:** skrypt walidacji z `10x-impl-review` (ścieżka rozwinięta w prompcie podagenta). Format raportu z przebiegu bez zmian, we wszystkich kopiach. Test `chain` z przypadkiem `chain-subagent` (`scripts/eval_chain.sh`, D-094) failuje, gdy log kroku tego skilla ma mniej wywołań podagenta ogólnego typu przez sesję główną niż plan ma faz; inne typy podagentów się nie liczą. Pierwszy prawdziwy przebieg nowego zachowania to `--quick` w fazie 7 zmiany 8c.
- **Jak sprawdzić:** `grep -n 'claude -p "/goal' skills/10x-goal-implement/SKILL.md | grep Agent` coś zwraca; `grep -nE '^  - Task$' skills/10x-goal-implement/SKILL.md` nic nie zwraca; `grep -n '^## Phase sub-agent' skills/10x-goal-implement/SKILL.md` coś zwraca; `python3 -m unittest discover -s scripts -p 'test_evallib.py' -k PhaseAgentsTest` kończy się kodem 0.
