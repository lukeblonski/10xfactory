# Sesja główna: rozmowa z człowiekiem i autopilot

Ten plik mówi sesji Claude Code w repo fabryki (`<fabryka>`) albo w repo aplikacji (sekcja „Start w repo aplikacji”), jak prowadzić zmianę z rozmowy z człowiekiem. Autopilot (`scripts/autopilot.py`) jest silnikiem: jedno wywołanie prowadzi łańcuch do najbliższej granicy kroku, zapisuje plik stanu `.autopilot-local/<id>/stan.json` i kończy się kodem. Sesja uruchamia wywołania w tle, czyta plik stanu i rozmawia z człowiekiem. Kolejność kroków, pola pliku stanu i kody wyjścia opisuje docstring `scripts/autopilot.py`.

## Kiedy ten plik obowiązuje

- Tylko w rozmowie z człowiekiem: gdy człowiek mówi „zrób zmianę X”, w repo aplikacji „zrób <ID kawałka>” albo „zrób kolejny kawałek” (sekcja „Kawałek roadmapy”), „kontynuuj <change-id>” albo „co się dzieje?” i gdy przychodzi powiadomienie o końcu wywołania autopilota w tle.
- Krok `claude -p` autopilota go nie wykonuje i nie uruchamia autopilota. Autopilot ustawia w środowisku każdego swojego kroku `claude -p` zmienną `AUTOPILOT_KROK=<id>` i odmawia startu (kod 2), gdy ta zmienna jest ustawiona.
- Sesje autora i recenzenta kroku PR (`scripts/retro_pr.py`) też go nie wykonują. To sesje `claude -p` bez człowieka, z poleceniem kroku PR; zmiennej `AUTOPILOT_KROK` nie dostają.

## Start: „zrób zmianę X”

1. Sesja ustala z człowiekiem nazwę zmiany `<id>` i tworzy gałąź: `git switch -c <id> master`. Potem, przed `/intent`, ocenia frame. Ta ocena jest tylko w tej drodze („zrób zmianę”); kawałek roadmapy jej nie ma (D-352).
   - Sesja zakłada folder zmiany: `/10x-new <id> <prośba człowieka jednym zdaniem>`.
   - Ocenia prośbę według sekcji „When to use, when to skip” w `skills/10x-frame/SKILL.md` (akapity „Use when” i „Skip when”). Frame pasuje do trzech kształtów prośby: objaw z gotową diagnozą albo poprawką, pytanie o zakres, wybór projektu.
   - Przy pasującym kształcie sesja mówi to człowiekowi i prowadzi z nim w tej rozmowie `/10x-frame <id> <prośba człowieka>`. Brief trafia do `context/changes/<id>/frame.md`. Przekazanie do `/10x-plan` z kroku 7 frame sesja pomija i idzie do punktu 2.
   - Inaczej sesja pisze człowiekowi jedno zdanie, dlaczego pomija frame, i idzie do punktu 2.
2. Intencję ustala w tej rozmowie: `/intent <id> <opis człowieka>`. `/intent` działa w folderze z punktu 1 i czyta `frame.md`, gdy jest. Człowiek odpowiada na pytania `/intent` tutaj. Potem sesja commituje `context/changes/<id>/` na gałęzi `<id>`, razem z `frame.md`, gdy jest.
3. Sesja uruchamia autopilota narzędziem Bash z parametrami `command: python3 scripts/autopilot.py <id>`, `run_in_background: true` i `timeout: 7200000` (2 h, najwyższy limit polecenia w tle; najdłuższy krok trwał dotąd 56 min).
4. W tej samej odpowiedzi sesja raz uruchamia na pierwszym planie `python3 scripts/autopilot.py <id> --krok`. Polecenie tylko czyta plik stanu: czeka najwyżej 30 s na krok, który trwa, i wypisuje jego linię `autopilot: krok <nazwa>: początek, log <ścieżka>`. Krótki krok `start` pomija, więc zaraz po starcie pokazuje research. Przy ryzyku Niskie pierwsze wywołanie kończy się zaraz po pominiętym researchu, więc `--krok` zwykle kończy się kodem innym niż 0, a granica pokaże research jako pominięty. Przy kodzie 0 sesja wypisuje człowiekowi tę linię. Przy kodzie innym niż 0 nic nie dopisuje. Ta reguła dotyczy każdego uruchomienia autopilota w tle w tym pliku: startu, granicy kroków, kontynuacji, wznowienia po zatrzymaniu i ponowienia po samonaprawie. Poza tym jednym `--krok` sesja nie odpytuje: bez `sleep`, bez Monitora i bez czytania wyjścia w pętli. Kończy odpowiedź i czeka na powiadomienie o końcu polecenia. Powiadomienie podaje kod wyjścia, a wyjście jest w pliku wyjścia zadania w tle. W kroku implement autopilot sam wypisuje na to wyjście linię fazy `autopilot: krok implement: faza <n> z <liczba faz>: <nagłówek>` przy każdej zmianie fazy planu. Człowiek widzi ją poleceniem `/tasks`, w karcie zadania w tle z ostatnim wyjściem. Linia fazy nie łamie reguły bez odpytywania, bo sesja jej nie czyta ani nie odpytuje; na „co się dzieje?” sesja podaje tę samą treść z pola `faza` w `stan.json`.

Krok `start` autopilota sprawdza, że `check_intent.py` przechodzi, bieżąca gałąź to `<id>`, gałąź główna istnieje (z `origin/HEAD`, a bez niego jedyna z `master` i `main`), git ignoruje `.autopilot-local/`, a `research.md` jeszcze nie ma.

### Start w repo aplikacji

Nowy projekt w pustym folderze zaczyna się według `<fabryka>/docs/start-projektu.md`, a nie według tego pliku. Tryb startu autopilota (`python3 <fabryka>/scripts/autopilot.py --start`) ma plik stanu `.autopilot-local/start-projektu/stan.json`, więc „co się dzieje?”, granica kroków i „Kontynuuj” działają jak w zmianie, z `--start` zamiast `<id>`. Wznowienie po zatrzymaniu idzie tylko przez `--start` (albo `--start --odpowiedz`, gdy autopilot podpowiada je dla zatrzymanego kroku `claude -p`), bez `--przyjmij`, które w trybie startu kończy się kodem 2, poza zatrzymaniem na dostępie kroków (`rodzaj: zgoda`, opis w sekcji „Domena spoza domyślnych” w `docs/start-projektu.md`). Zatrzymanie z `rodzaj: zgoda` i powodem „ustawienia repo kroku mają wyjątek piaskownicy” albo „ustawienia repo kroku mają zmienione polecenia poza piaskownicą” sesja prowadzi według akapitów o tych zatrzymaniach niżej, także w trybie startu (wtedy na końcu `--start` zamiast `<id>`). Zatrzymania `rodzaj: akceptacja` i `rodzaj: domena` prowadzi `docs/start-projektu.md`. Linie zatrzymań, pytań i kosztów trybu startu są w `context/foundation/start.md` aplikacji, a nie w `change.md`.

Skrypty, skille i reguły zostają w repo fabryki (`<fabryka>`). `<fabryka>` to folder fabryki, którego pełną ścieżkę podaje hook startu sesji; w poleceniach i liniach do wklejenia sesja wpisuje tę pełną ścieżkę zamiast `<fabryka>`. `context/`, `.autopilot-local/`, gałąź zmiany i ślady przebiegu powstają w repo aplikacji. Kroki startu są takie same jak wyżej, z tymi różnicami:

- Polecenia autopilota mają pełną ścieżkę repo fabryki: `python3 <fabryka>/scripts/autopilot.py <id>` w tle i `python3 <fabryka>/scripts/autopilot.py <id> --krok` na pierwszym planie. Tak samo wszystkie inne polecenia autopilota z tego pliku (`--odpowiedz`, `--przyjmij`); autopilot w repo aplikacji sam podpowiada je z pełną ścieżką.
- Gałąź zmiany powstaje od gałęzi głównej aplikacji: `git switch -c <id> <gałąź główna>`, np. `main`.
- Warunki startu: repo git z `origin` (krok `push` wypycha do niego gałąź główną; start tego nie sprawdza, więc bez `origin` przebieg idzie przez wszystkie kroki, scala zmianę lokalnie i staje dopiero na `push`); gałąź główna z `origin/HEAD`, a bez niego jedyna z `master` i `main` (przy obu albo żadnej start kończy się kodem 1 z poleceniem naprawy, np. `git remote set-head origin <gałąź>`); `/.autopilot-local/` w `.gitignore`, zacommitowane; folder `context/` (np. z `/10x-init`).
- Sesja w repo aplikacji bierze instrukcje z tego pliku przez odesłanie w `CLAUDE.md` aplikacji, a nie przez `~/.claude`. Linia do wklejenia do `CLAUDE.md` aplikacji:

  ```
  Gdy człowiek w rozmowie mówi „zrób zmianę”, „zrób <ID kawałka>”, „zrób kolejny kawałek”, „kontynuuj <change-id>” albo „co się dzieje?”, albo gdy kończy się wywołanie autopilota uruchomione w tle, sesja czyta <fabryka>/docs/sesja-glowna.md i działa według niego. Krok claude -p autopilota (ma w środowisku zmienną AUTOPILOT_KROK) tego nie robi i nie uruchamia autopilota.
  ```

  Reguły „Jak pisać do człowieka” i „Kiedy pytać człowieka”, do których odsyła ten plik, są w `<fabryka>/CLAUDE.md`, a lista bramek w `<fabryka>/docs/zgoda-czlowieka.md`.
- Kroki `claude -p` widzą tylko serwery MCP z `.mcp.json` w katalogu głównym repo aplikacji, bez pytania. Bez tego pliku nie mają żadnego serwera. Serwerów z `~/.claude.json` i konektorów claude.ai nie widzą.
- Przebieg pomija `testy-fabryki`, `wynik-testow`, `synchronizacja-skilli`, `krok-pr` i `synchronizacja-po-pr`, z linią powodu `pominięty, repo aplikacji: …` w logu kroku. Każda propozycja retrospektywy ma na liście końca przebiegu stan „czeka na człowieka”: człowiek przenosi ją do zmiany w repo fabryki.
- Kroki `przygotowanie-wdrozenia` (po `impl-review`) i `wynik-wdrozenia` (po `push`) niczego nie robią bez `## Zgody` w `change.md` zmiany, plików w `context/changes/<id>/chronione/` i `## Wdrożenie` w `CLAUDE.md` aplikacji. Pierwszy zapisuje wtedy w logu `nic do wpisania`, a drugi `pominięty: repo nie ma ## Wdrożenie w CLAUDE.md`. Bez pliku CI z linią `# autopilot: ci-galezi` pierwszy zapisuje też `brak CI gałęzi` i niczego nie wysyła. Tak samo przechodzą w repo fabryki. Co robią, gdy te sekcje są, opisuje sekcja „Kawałek roadmapy”, punkty 3 i 6.
- Reguła uprawnień dla filtra trybu automatycznego (sekcja „Filtr trybu automatycznego”) ma pełną ścieżkę: `Bash(python3 <fabryka>/scripts/autopilot.py:*)`. Zamień w niej `<fabryka>` na pełną ścieżkę, którą podał hook startu sesji.

## Kawałek roadmapy: „zrób <ID kawałka>” i „zrób kolejny kawałek”

Ta sekcja działa w repo aplikacji po starcie, gdy jest `context/foundation/roadmap.md`. Kawałek to zmiana w repo aplikacji, która idzie łańcuchem autopilota jak w „Start w repo aplikacji”, przy ryzyku Niskie bez researchu. Różnice wobec „zrób zmianę X”: sesja nie ustala nazwy zmiany z człowiekiem i nie pyta go o treść intencji. Przed łańcuchem zadaje najwyżej jedno pytanie: o dostępy, konta i zgody, których nie zebrało posiedzenie dostępów po starcie. Sesja robi kolejno:

1. **Przygotowanie przed pierwszym kawałkiem.** Gdy aplikacja nie ma `context/foundation/test-plan.md`, sesja robi na gałęzi głównej, przed wyborem kawałka:
   - (a) Plan testów. Sesja uruchamia w tej rozmowie narzędziem Skill `10x-test-plan` z argumentem `context/foundation/prd.md` i prośbą `TEST_PLAN_REQUEST` z `<fabryka>/scripts/autopilot.py`. Pytania skilla rozstrzyga sesja według „Kiedy pytać człowieka” w `<fabryka>/CLAUDE.md`; to jest tu „reguła z końca tej prośby”, o której mówi `TEST_PLAN_REQUEST`. Każde rozstrzygnięcie zostawia linię w `## Pytania do człowieka` w `context/foundation/start.md`, z `krok: plan-testow`. Pytanie z bramki idzie do człowieka.
   - (b) CI. Gdy w `.github/workflows/` nie ma workflow uruchamianego przy wysłaniu (`push`) na gałąź główną, sesja zatrzymuje się z dowodami: lista plików w `.github/workflows/` albo jej brak. Mówi człowiekowi, że kawałek nie rusza bez CI, a agent tej ścieżki nie zapisze, bo chronią ją zabezpieczenia aplikacji. Dalej idzie dopiero, gdy workflow jest w repo.
   - (c) Pola „Potrzebuje”. Każda pozycja roadmapy z `- **Change ID:**` bez linii `- **Potrzebuje:**` dostaje ją z dostępami, które wynikają z PRD i `context/foundation/tech-stack.md` (konta, klucze, płatne usługi), albo `- **Potrzebuje:** nic`. Pole nazywa dostęp, nigdy nie podaje wartości sekretu (jak krok `roadmapa` w `<fabryka>/docs/start-projektu.md`).
   - (d) Sprawy odłożone. Sesja czyta `context/foundation/limitations.md`, `context/changes/bootstrap-verification/verification.md` i otwarte pytania roadmapy. Każdą sprawę, którą trzeba zrobić przed użyciem albo wdrożeniem aplikacji (np. luki HIGH w zależnościach), wpisuje zwykłym językiem w `Prerequisites` pozycji, którą ta sprawa blokuje. Nie robi z niej nowego kawałka.

   Potem jeden commit poleceniem z listą ścieżek, np. `git add context/foundation/test-plan.md && git commit -m "docs(roadmap): przygotowanie przed pierwszym kawałkiem" -- context/foundation/test-plan.md context/foundation/roadmap.md context/foundation/start.md`. Sesja go nie wysyła, bo w piaskownicy repo aplikacji nie ma logowania do GitHuba. Wyśle go krok `push` kawałka.
2. **Wybór.** Kawałki idą po kolei (D-223): gdy `pid` albo `pid_kroku` w pliku stanu innej zmiany (`.autopilot-local/*/stan.json`) należy do żywego procesu (`kill -0 <pid>` kończy się kodem 0), sesja mówi to człowiekowi i niczego nie zaczyna. Inaczej bierze z `context/foundation/roadmap.md`:
   - na „zrób <ID>”: pozycję o tym ID;
   - na „zrób kolejny kawałek”: pierwszą w kolejności roadmapy pozycję ze statusem `ready`, której każde wymaganie wstępne ma status `done`; wyjątki są w akapicie „Warunek wstępny” niżej.

   Change-id kawałka to wartość z kolumny `Change ID` tej pozycji. Bez takiej pozycji albo przy pozycji ze statusem `done` sesja mówi to człowiekowi i niczego nie zaczyna.

   Warunek wstępny (W11). Dwie rzeczy nie blokują wyboru:
   - wymaganie wstępne z `Prerequisites`, które nie jest ID innej pozycji roadmapy i nie jest spełnione (np. aktualizacja zależności z lukami HIGH);
   - status `blocked`, gdy blokują go tylko otwarte pytania z `Unknowns` z `Block: yes`, które rozstrzyga pytanie z punktu 3 (np. kiedy człowiek zakłada konta i czy zgadza się na publiczny adres).

   Kawałek zaczyna wtedy od warunku wstępnego, w tej samej zmianie, jako pierwszej fazy (reguła w punkcie 4). Sesja mówi to człowiekowi jednym zdaniem, np. „<ID> zaczyna od warunku wstępnego: <warunek>; zrobię go w pierwszej fazie kawałka.”, i nie pyta o to. Wymaganie wstępne, które jest ID pozycji bez statusu `done`, blokuje wybór jak dotąd.
3. **Dostępy i zgody.** Gdy `context/foundation/start.md` nie ma sekcji `## Posiedzenie dostępów` (przerwana rozmowa startu albo aplikacja sprzed paczki 1.1), sesja najpierw prowadzi posiedzenie dostępów całej roadmapy według sekcji „Posiedzenie dostępów” w `<fabryka>/docs/start-projektu.md`, a dopiero potem ten punkt.

   Pytanie nie pada, gdy każdy dostęp z linii `- **Potrzebuje:**` pozycji innego niż „nic” ma linię w sekcji `## Dostępy` w `CLAUDE.md` aplikacji, a każda zgoda potrzebna pozycji (części niżej i `zgoda: sekrety`) ma linię z `kto: człowiek` w `## Zgody` w `start.md` z polem „kawałek” w „czego dotyczy” równym change-id tej pozycji albo `wszystkie`. Sesja kopiuje wtedy te linie do `## Zgody` w `change.md` kawałka (punkt 4) bez zmiany `czas`, `kto` i `odpowiedź`, z dopiskiem `(posiedzenie dostępów, start.md)` w „czego dotyczy”, i o nic nie pyta. Pytanie niżej obejmuje tylko to, czego brakuje (np. pozycja dopisana do roadmapy po posiedzeniu).

   Dla każdego dostępu z linii `- **Potrzebuje:**` pozycji innego niż „nic” sesja szuka linii w sekcji `## Dostępy` w `CLAUDE.md` aplikacji. Brakujące dostępy dają jedno pytanie do człowieka, w jednej wiadomości, zanim ruszy cokolwiek dalej. To bramka płatnego przebiegu (płatna usługa). Pytanie obejmuje wszystkie brakujące dostępy naraz. Dla klucza pyta o ścieżkę bezwzględną do pliku poza repo, w którym jest tylko klucz, i o limit wydatków ustawiony u dostawcy.

   Pozycja, która wdraża aplikację albo potrzebuje kont, logowań albo zgód, dostaje to samo jedno pytanie, rozszerzone. Dotyczy to pozycji, która ma w `Potrzebuje` konto, logowanie albo zgodę, i pozycji, którą `context/foundation/infrastructure.md` aplikacji opisuje jako wdrożenie aplikacji. Sesja wysyła wtedy jedną wiadomość przed gałęzią i autopilotem i nie pyta o nic z niej później, ani sama, ani przez kroki. Platformę, usługi, sekrety, domeny i jednorazowe ustawienia kont bierze z `infrastructure.md` aplikacji, a nie z tego pliku. Nazwy platform w tym pliku są tylko przykładem. Wiadomość ma siedem części:
   1. **Konta.** Konta do założenia, razem z jednorazowymi ustawieniami konta z `infrastructure.md` (np. rejestracja subdomeny platformy albo ustawienie w panelu usługi). Każde konto ma adres strony rejestracji. Do tego każde działanie człowieka w panelu usługi z `infrastructure.md` (np. hasło bazy, ustawienie logowania), z gotowym poleceniem albo ścieżką w panelu.
   2. **Logowania.** Logowanie każdego narzędzia wdrożenia jego poleceniem (np. `<narzędzie> login`), uruchomionym przez człowieka w zwykłym terminalu, a nie w sesji Claude, bo piaskownica blokuje logowanie w przeglądarce. Obok polecenie, które sprawdza logowanie bez wypisywania tokenu (np. `<narzędzie> whoami`).
   3. **Upublicznienie.** Zgoda na publiczny adres aplikacji, z adresem albo jego postacią z `infrastructure.md`.
   4. **Wysyłka danych.** Zgoda na dane w chmurze: jakie dane, u którego dostawcy i w którym regionie.
   5. **Płatne usługi.** Każda płatna usługa z limitem wydatków ustawionym u dostawcy i z tym, kto ma do niej dostęp przez aplikację (np. klucz używany przez konta zakładane przez obce osoby).
   6. **Domeny piaskownicy.** Lista hostów, których narzędzia wdrożenia potrzebują w piaskownicy aplikacji, każdy osobno. Uwaga dla człowieka: wpis `*.x` nie obejmuje samego `x`, więc oba idą na listę, gdy narzędzie łączy się z obydwoma.
   7. **Chronione pliki i `## Wdrożenie`.** Nazwane chronione pliki aplikacji, które wpisze autopilot (np. plik CI z krokiem wdrożenia), i pełna treść sekcji `## Wdrożenie` (format w punkcie 4): polecenia, które autopilot uruchomi poza piaskownicą. Lista obejmuje każdy istniejący plik w `.github/workflows/`, który podaje sekret poza krokiem wdrożenia (np. do budowania albo testów). Krok `przygotowanie-wdrozenia` sprawdza wszystkie pliki CI i zatrzyma przebieg na takim pliku, więc kawałek musi go przepisać.

   Sekrety. Pytanie obejmuje każdy sekret z `infrastructure.md` aplikacji, także ten, którego kawałek użyje dopiero w CI (np. token do migracji bazy). Dla każdego sekretu wiadomość podaje nazwę dostępu i ścieżkę pliku poza repo. Człowiek tworzy ten plik jednym poleceniem według wzoru z punktu 6 sekcji „Posiedzenie dostępów” w `<fabryka>/docs/start-projektu.md` (polecenie prosi o wartość, nie pokazuje jej i wypisuje „Zapisano (N znaków)”), w zwykłym Terminalu, nigdy przez `!`. Wiadomość pyta też o zgodę `zgoda: sekrety`: autopilot przekaże wartości z tych plików do sekretów platformy i CI poleceniami z `## Wdrożenie`. Kawałek bez nowych sekretów nie dostaje tej zgody, bo każde ustawienie sekretu platformy może wdrożyć nową wersję.

   W obu postaciach pytania każde działanie człowieka ma gotowe polecenie do wklejenia i jedno zdanie, dlaczego nie robi go agent. Przykłady powodów: konto zakłada człowiek, bo wymaga jego danych i akceptacji regulaminu; logowanie idzie w zwykłym terminalu, bo piaskownica blokuje przeglądarkę; plik z sekretem tworzy człowiek, bo sesja i kroki nie czytają sekretów. Wiadomość kończy się gotową odpowiedzią do wklejenia w jednym bloku i prośbą, żeby nie wklejać do rozmowy klucza ani tokenu. Pozostałe zasady pisania są w „Jak pisać do człowieka” w `<fabryka>/CLAUDE.md`.

   Po odpowiedzi sesja sprawdza dla każdego pliku z sekretem tylko, że `test -f <ścieżka>` kończy się kodem 0 i że ścieżka nie leży w katalogu repo (`git rev-parse --show-toplevel`). Pliku nie czyta i nie wypisuje jego treści. Gdy sprawdzenie nie przechodzi, sesja mówi, co się nie zgadza, i czeka na poprawioną odpowiedź.
4. **Gałąź i intencja.** Sesja tworzy gałąź kawałka: `git switch -c <change-id> <gałąź główna>`. Gdy było pytanie o dostępy, `CLAUDE.md` aplikacji dostaje sekcję `## Dostępy` (gdy jej nie ma) z nagłówkiem i jedną linią na dostęp:

   ```
   ## Dostępy

   Ścieżki do plików z sekretami, poza repo. Kroki i sesja nie czytają tych plików i nie wypisują ich treści. Czyta je tylko polecenie z `## Uruchomienie lokalne` i krok autopilota `przygotowanie-wdrozenia`, który podaje wartość na wejście polecenia z `## Wdrożenie` i jej nie wypisuje. Testy używają atrapy usługi.

   - <nazwa dostępu>: <ścieżka>
   ```

   Gdy było pytanie z siedmioma częściami, `CLAUDE.md` aplikacji dostaje też sekcję `## Wdrożenie` (albo jej nową wersję) z nagłówkiem i polami, które autopilot czyta:

   ```
   ## Wdrożenie

   Pisze sesja główna przed autopilotem, razem ze zgodą człowieka w ## Zgody zmiany. Autopilot czyta te pola i uruchamia ich polecenia poza piaskownicą (kroki przygotowanie-wdrozenia i wynik-wdrozenia). Zmiana tej sekcji wymaga nowej zgody człowieka; krok agenta jej nie zmienia.

   - workflow: <plik w .github/workflows/, który wdraża po wysłaniu na gałąź główną>
   - krok wdrożenia: <nazwa kroku tego workflow, który wdraża aplikację>
   - narzędzia z sekretami: <lista po przecinku: uses: akcji bez @wersji albo początek jednoliniowego run:>
   - sekret: <polecenie, które czyta wartość z wejścia i jej nie wypisuje> < <nazwa dostępu z ## Dostępy>
   - tokeny logowania: <ścieżki po przecinku, w których narzędzia z tej sekcji trzymają logowanie na tym komputerze>|brak
   - cofnięcie: <polecenie bez parametrów, które cofa wersję kodu o jedną>|brak
   - adres: <publiczny adres aplikacji>
   - punkt zdrowia: <adres punktu zdrowia aplikacji>
   ```

   Aplikacja z `## Wdrożenie` ma punkt zdrowia, który odpowiada kodem 503 z samymi nazwami brakujących ustawień, bez wartości, gdy któregoś brakuje. Workflow CI zaraz po kroku wdrożenia odpytuje go poleceniem `curl -fsS --retry 5 <punkt zdrowia>`, więc brak ustawienia kończy przebieg CI porażką.

   Linii `- sekret:` jest tyle, ile sekretów (platformy i CI). Wartości pól pochodzą z `infrastructure.md` aplikacji. `cofnięcie` ma polecenie tylko wtedy, gdy `infrastructure.md` pozwala cofać wersję kodu bez człowieka, a inaczej `brak`. `tokeny logowania` sesja wpisuje po sprawdzeniu w dokumentacji każdego narzędzia z tej sekcji, gdzie na tym komputerze trzyma ono logowanie (zasada „Fakty o usługach zewnętrznych sprawdzaj w źródle” z `CLAUDE.md` fabryki), np. folder konfiguracji narzędzia w katalogu domowym. Żaden krok `claude -p` nie czyta tych miejsc ani ścieżek z `## Dostępy`, także w przebiegach innych aplikacji i w repo fabryki, o ile ta aplikacja przeszła już krok `start` autopilota (zapisał jej sekcje w pliku zaufanym); ścieżki aplikacji bez takiego przebiegu chroni tylko stała lista miejsc z kluczami. Autopilot uruchamia każde polecenie bez powłoki, więc polecenie nie ma `|`, `&&` ani przekierowań poza końcowym `< <nazwa dostępu>`. Krok `start` autopilota zapisuje tę sekcję, `## Dostępy` i `## Zgody` w wersji z commita. Gdy któraś się potem zmieni, kroki wdrożenia zatrzymują przebieg (sekcja „Zatrzymanie i samonaprawa”).

   Potem sesja pisze intencję bez pytania człowieka o jej treść: uruchamia narzędziem Skill `intent` z argumentem:

   ```
   <change-id> bez człowieka. Kawałek roadmapy aplikacji, blok pozycji z context/foundation/roadmap.md dosłownie:
   <blok pozycji>
   Scenariusz ze szkicu, kroki scenariusza pierwszej wersji z PRD, które pozycja dostarcza według PRD refs, dosłownie:
   <kroki scenariusza z context/foundation/prd.md>
   Reguły kawałka: scenariusz człowieka ułóż z Outcome tej pozycji i z tych kroków. Gdy CLAUDE.md nie ma sekcji ## Uruchomienie lokalne, kawałek dodaje do CLAUDE.md i README.md jedno polecenie uruchomienia lokalnego: sprawdzenie wymagań, lokalne usługi, zmienne środowiska, dostępy z plików z ## Dostępy w CLAUDE.md i serwer. Dostęp z pola Potrzebuje aplikacja czyta ze ścieżki z ## Dostępy w CLAUDE.md i nigdy go nie commituje. Testy zastępują płatną usługę atrapą. Test, który wymaga usługi lokalnej (np. kontenera albo bazy), kawałek dopisuje do polecenia z sekcji ## Testy w CI w CLAUDE.md, a nie do polecenia sprawdzającego: kroki w piaskownicy tych usług nie mają, a test biegnie w CI gałęzi przed scaleniem; wiersz Automated planu sprawdza tylko, że taki test istnieje i jest w tym poleceniu. Plan kawałka nie ma wiersza #### Manual do sprawdzenia w przeglądarce ani kroku scenariusza do sprawdzenia przez człowieka: człowiek ogląda aplikację raz, po ostatnim kawałku roadmapy. Wymaganie wstępne z Prerequisites, które nie jest ID pozycji roadmapy, to pierwsza faza kawałka z kryterium sprawdzanym poleceniem (np. liczba luk HIGH z polecenia audytu równa 0); poprawka, która wymaga wymuszenia (np. --force) albo skoku wersji głównej zależności, to bramka. Każda nowa migracja bazy jest wstecznie zgodna i niczego nie usuwa (danych, tabel ani kolumn); migracja, która nie jest wstecznie zgodna albo usuwa dane, to bramka przed scaleniem. Chroniony plik ze zgody w ## Zgody change.md kawałek przygotowuje w context/changes/<change-id>/chronione/<ścieżka w repo>, a wpisze go autopilot po przeglądzie kodu. Plik CI w chronione/ używa dokładnie pól workflow, krok wdrożenia i narzędzia z sekretami z ## Wdrożenie w CLAUDE.md, a sekret podaje tylko w env: albo with: kroku wdrożenia tych narzędzi; gdy plan kawałka potrzebuje innej wartości, sekretu, chronionego pliku albo domeny spoza ## Zgody, to bramka kroku planu (pytanie przed implementacją), a nie zmiana ## Wdrożenie w trakcie. Polecenia na kontach usług i sekretach uruchamia autopilot krokami skryptu, a nie kroki agenta; kroki agenta nie czytają plików z ## Dostępy.
   ```

   Wpisy `/intent` w `## Wymaga Twojej decyzji` zostają w `change.md` kawałka: człowiek może je przeczytać, a sesja pokaże je na końcu przebiegu. Gdy było pytanie o dostępy, sesja dopisuje po `/intent` do `## Pytania do człowieka` w `change.md` kawałka linię z odpowiedzią, bez sekretu, np. `- rodzaj: płatny przebieg · krok: dostępy · pytanie: gdzie leży plik z kluczem <dostęp> i jaki limit wydatków jest ustawiony u dostawcy · rekomendacja: plik poza repo z samym kluczem i limit u dostawcy · wybór: <ścieżka>, limit <kwota> · rozstrzygnął: człowiek`. Pytanie z siedmioma częściami dostaje taką samą jedną linię, z rodzajem `płatny przebieg`, gdy obejmuje płatną usługę, a inaczej `inne`, np. `- rodzaj: płatny przebieg · krok: dostępy · pytanie: konta, logowania i zgody na wdrożenie · rekomendacja: … · wybór: <streszczenie odpowiedzi bez sekretu> · rozstrzygnął: człowiek`.

   Po tym pytaniu sesja dopisuje też na końcu `change.md` kawałka sekcję `## Zgody`, jedną linią na każdą zgodę z odpowiedzi człowieka:

   ```
   ## Zgody

   - czas: <YYYY-MM-DD HH:MM> · kto: człowiek · zgoda: <rodzaj> · czego dotyczy: <po co> · odpowiedź: „<cytat odpowiedzi człowieka, bez sekretu>”
   ```

   Zgody z posiedzenia dostępów sesja kopiuje do tej sekcji według punktu 3, z dopiskiem `(posiedzenie dostępów, start.md)`; nowa odpowiedź człowieka dostaje nowe linie. Rodzaje, które czyta autopilot: `domena <host>` (jeden host w linii), `plik <ścieżka w repo>` (jeden chroniony plik w linii) i `sekrety`. Rodzaje będące śladem: `upublicznienie`, `dane <gdzie i w jakim regionie>` i `płatna usługa <nazwa> <limit>`. Konto i logowanie nie dostają linii, bo to działania człowieka, a nie zgody. Autopilot ufa tylko liniom z `kto: człowiek`, w wersji z commita sprzed startu.

   Potem commit poleceniem z listą ścieżek: `git add context/changes/<change-id> CLAUDE.md && git commit -m "docs(<change-id>): intencja kawałka" -- context/changes/<change-id> CLAUDE.md`.
5. **Autopilot.** Sesja uruchamia autopilota jak w „Start w repo aplikacji”, pełną ścieżką: `python3 <fabryka>/scripts/autopilot.py <change-id>` w tle i raz `python3 <fabryka>/scripts/autopilot.py <change-id> --krok` na pierwszym planie (punkty 3 i 4 „Startu”). Granica kroków, zatrzymania i „co się dzieje?” idą dalej według tego pliku, a koniec przebiegu według sekcji „Koniec kawałka w repo aplikacji”.
6. **Wdrożenie w łańcuchu.** Polecenia na kontach usług i sekretach uruchamia proces Pythona autopilota, krokami skryptu, poza piaskownicą. Sesja i kroki agenta ich nie uruchamiają i nie czytają plików z `## Dostępy`.
   - **`przygotowanie-wdrozenia`**, po przeglądzie kodu. Najpierw same sprawdzenia: `## Zgody`, `## Dostępy` i `## Wdrożenie` są takie jak przy starcie przebiegu, każdy plik w `context/changes/<change-id>/chronione/` ma linię `zgoda: plik <ścieżka>`, każdy plik CI podaje sekret tylko krokowi narzędzia z `narzędzia z sekretami`, a domeny dodane na gałęzi mają linię `zgoda: domena <host>`. Gdy wszystko przechodzi, krok dopisuje domeny ze zgody do ustawień piaskownicy aplikacji, kopiuje pliki z `chronione/` na ich ścieżki i robi jeden commit tylko tych plików. Gdy ten commit obejmuje wszystkie pliki ustawień, które gałąź zmienia, autopilot od razu zapisuje zgodę na scalenie (pole `zgoda_scalenia`), więc archiwum nie zatrzyma się na nich. Różnica tego commita trafia do raportu końcowego. Na końcu, tylko przy `zgoda: sekrety`, krok uruchamia każdą linię `- sekret:` z `## Wdrożenie`. Wartość z pliku z `## Dostępy` idzie na wejście polecenia, bez powłoki. Wyjście polecenia nie trafia nigdzie, bo może zawierać sekret. Log kroku ma tylko polecenie i kod wyjścia.
     Ostatnia część kroku to CI gałęzi, także po `nic do wpisania`. Gdy plik w `.github/workflows/` w HEAD ma linię `# autopilot: ci-galezi` (CI z szablonu zabezpieczeń, krok `szkielet`), krok wysyła gałąź poleceniem `git push -u origin <change-id>` i czeka na przebieg tego workflow dla HEAD gałęzi. Tam biegną testy z `## Testy w CI`, czyli testy z usługami lokalnymi. Sukces: linia `CI gałęzi przeszło`. Porażka zatrzymuje kawałek przed archiwum i scaleniem; powód podaje nieudany job i krok CI oraz ścieżkę ostatnich 200 linii `gh run view --log-failed` w `.autopilot-local/<change-id>/`. Sesja pokazuje to człowiekowi, poprawka idzie commitem na gałąź kawałka, a potem sesja uruchamia autopilota bez opcji. Bez takiej linii krok zapisuje w logu `brak CI gałęzi` i idzie dalej (aplikacje z paczki 1.0). Krok `merge` scala commit, który sprawdziło CI gałęzi, a gdy gałąź kończy się już na innym commicie (np. po commicie archiwum), uruchamia CI gałęzi jeszcze raz na tym commicie i dopiero po sukcesie scala, więc kawałek z CI gałęzi czeka na CI dwa razy.
   - **`wynik-wdrozenia`**, po `push`. Gdy `CLAUDE.md` gałęzi głównej ma `## Wdrożenie`, krok czeka na przebieg CI z `workflow` dla wysłanego commita i patrzy na jego wynik. Sukces: linia `wdrożenie przeszło; adres: <adres>`. Porażka po udanym `krok wdrożenia`: krok uruchamia polecenie `cofnięcie` (gdy nie jest `brak`) i zapisuje linię zatrzymania z `zrobiono: cofnięcie wersji kodu` i `skutek: łańcuch dalej`, a łańcuch idzie do `zapis-przebiegu`. Porażka przed krokiem wdrożenia: krok niczego nie cofa, bo działa wersja sprzed scalenia, i zapisuje taką samą linię z `zrobiono: bez cofnięcia: krok wdrożenia nie przeszedł`. W obu przypadkach powód linii to wiadomość dla człowieka: co nie przeszło (job i krok), która wersja działa (commit gałęzi głównej sprzed scalenia, o ile był wdrożony; przy pierwszym wdrożeniu pod adresem nie działa nic), że migracje bazy zostają, bo są wstecznie zgodne, i że kolejny `push` wdroży gałąź główną od nowa. `cofnięcie: brak`, nieudane cofnięcie, brak przebiegu CI i zmienione pola `## Wdrożenie` zatrzymują przebieg z poleceniem dla człowieka.

## Granica kroków

Kod wyjścia wywołania mówi, co się stało: 0 to granica albo koniec przebiegu, 1 to zatrzymanie albo przerwanie sygnałem, 2 to autopilot, który nie wystartował (komunikat jest na standardowym wyjściu błędów).

Po powiadomieniu z kodem 0 sesja czyta pole `nastepny` w `.autopilot-local/<id>/stan.json` i ostatnią linię wyjścia:

- `nastepny` ma nazwę kroku, a ostatnia linia to `autopilot: dalej: krok <następny>; uruchom ponownie: python3 scripts/autopilot.py <id>`. Sesja od razu uruchamia następne wywołanie w tle, z tymi samymi parametrami co przy starcie. W jednej odpowiedzi wypisuje trzy linie:
  - linię „autopilot: krok <nazwa>: koniec (kod <n>), log <ścieżka>” z wyjścia skończonego wywołania;
  - linię „autopilot: krok <nazwa>: agent rozstrzygnął sam: <n>” z wyjścia skończonego wywołania, przepisaną bez zmian: liczba pytań rozstrzygniętych przez agenta w tym kroku, a przy `n > 0` dalej ` — <pytanie 1>; <pytanie 2>…` z krótkim opisem każdego pytania. Autopilot składa ją z linii `## Pytania do człowieka` z `krok: <nazwa>` i `rozstrzygnął: agent` i wypisuje przed linią `autopilot: dalej: …`. Krok polecenia (bez `claude -p`) takiej linii nie ma, więc sesja ją pomija;
  - linię „autopilot: krok <nazwa>: początek, log <ścieżka>” z wyjścia `python3 scripts/autopilot.py <id> --krok`, uruchomionego raz po starcie nowego wywołania (punkt 4 „Startu”). Przy kodzie innym niż 0 tej linii nie ma i sesja wypisuje tylko dwie pierwsze.

  Sesja nie czeka na odpowiedź człowieka: linia decyzji agenta daje mu szansę zareagować przed scaleniem, a pełna lista pytań rozstrzygniętych przez agenta zostaje na końcu przebiegu.
- `nastepny` jest `null`, a ostatnia linia to `autopilot: przebieg zakończony`: sesja przechodzi do sekcji „Koniec przebiegu”.

Poza linią z `--krok` po starcie w tle, granicą, zatrzymaniem i końcem przebiegu sesja milczy: nie komentuje wyjścia i nie streszcza kroków.

## „Co się dzieje?”

Sesja czyta `.autopilot-local/<id>/stan.json` zmiany z tej rozmowy i odpowiada z jego pól:

- `krok`: krok, który trwa albo trwał ostatni;
- `faza`: bieżąca faza planu w postaci `faza <n> z <liczba faz>: <nagłówek>` (faza z pierwszym `- [ ]` poza `#### Manual` w `## Progress` w `plan.md`, ostatnia, gdy wszystkie są zaznaczone), bez planu z `## Progress` `null`; to ta sama treść, którą autopilot wypisuje w kroku implement jako linię fazy, widoczną dla człowieka w `/tasks`;
- `ostatnia_czynnosc`: nazwa i cel ostatniego wywołania narzędzia w logu kroku albo polecenie, które trwa;
- `czas`: czas ostatniego zapisu; w trakcie kroku `claude -p` autopilot odświeża plik co 30 s.

Gdy `pid` i `pid_kroku` są puste albo należą do martwych procesów, przebieg nie trwa. Sesja mówi to i podaje, co dalej (sekcja „Kontynuuj”). Bez pliku stanu zmiana nie ma jeszcze przebiegu autopilota. Na to pytanie sesja niczego nie uruchamia.

## „Kontynuuj <change-id>”

Zadanie w tle ginie razem z rozmową. Plik stanu zostaje, więc sesja wznawia od niego:

- Brak pliku stanu: zmiana nie ma jeszcze przebiegu. Sesja uruchamia autopilota jak w kroku 3 startu; zaczyna on od kroku `start`.
- `pid` albo `pid_kroku` należy do żywego procesu (`kill -0 <pid>` kończy się kodem 0): przebieg trwa, np. z innej rozmowy. Sesja mówi to człowiekowi i niczego nie uruchamia. Drugi przebieg i tak skończyłby się kodem 2.
- Pole `zatrzymanie` jest ustawione: sesja postępuje jak w sekcji „Zatrzymanie i samonaprawa”.
- `nastepny` jest `null`: przebieg się skończył. Jego wynik jest w `context/przebiegi/<id>.md`.
- W każdym innym przypadku, także z polem `przerwanie` (rozmowa zamknięta albo sygnał w trakcie kroku): sesja uruchamia `python3 scripts/autopilot.py <id>` w tle, jak przy starcie. Autopilot zaczyna od pierwszego kroku spoza listy `zrobione` i nie powtarza kroków z tej listy. Krok przerwany w połowie idzie od nowa. Implement wznawia od niezaznaczonych wierszy `## Progress`, więc zacommitowane fazy zostają.

## Zatrzymanie i samonaprawa

Kod 1 z polem `zatrzymanie` w pliku stanu to zatrzymanie. Pole ma krok i pełny powód (`krok`, `powod`). Wyjście ma linię `autopilot: krok <nazwa>: zatrzymanie. <powód>` i polecenia, którymi można iść dalej. Autopilot zapisał już linię zatrzymania (sekcja „Linia zatrzymania”). Kod 1 z polem `przerwanie` bez pola `zatrzymanie` nie jest zatrzymaniem: sesja uruchamia autopilota ponownie jak w sekcji „Kontynuuj”.

Pliki zmienia jeden proces naraz. Sesja edytuje pliki zmiany i plik stanu tylko wtedy, gdy `pid` i `pid_kroku` w pliku stanu są puste albo należą do martwych procesów.

Reguła samonaprawy. Sesja najpierw naprawia sama, gdy naprawa spełnia wszystkie cztery warunki:

1. **Darmowa.** Nie uruchamia płatnego przebiegu. „Płatny przebieg” w tej regule to płatne testy fabryki: `scripts/run_evals.sh` i `python3 scripts/retro_pr.py <id> --paid-tests P<n>`. Zwykłe kroki agentów (ponowny krok `claude -p` autopilota) i ponowny przegląd recenzenta są dozwolone.
2. **Odwracalna.** Da się ją cofnąć zwykłym commitem. Nie usuwa danych, nie przepisuje historii gita (bez `rebase`, `reset --hard`, `commit --amend` i `push --force`) i nie scala PR-a, który czeka na człowieka.
3. **Poza bramkami.** Nie trafia na żadną z siedmiu bramek z reguły „Kiedy pytać człowieka” w sekcji „Jak pisać do człowieka” w `CLAUDE.md`: intencja i kryteria akceptacji, ścieżka z `docs/zgoda-czlowieka.md` albo usunięcie kroku łańcucha, płatny przebieg i wysyłka danych, upublicznienie, ustawienia globalne (`~/.claude`), operacja trudna do cofnięcia i rozstrzygnięcie, które polityka triage'u zostawia człowiekowi. Dodatkowo nie zmienia zasad budowy (`docs/zasady-budowy.md`). Nie rozstrzyga też wpisu w `## Wymaga Twojej decyzji`.
4. **Sprawdzalna.** Polecenie pokazuje, że naprawa działa, np. polecenie, które padło, kończy się kodem 0 albo polecenie verify z `CLAUDE.md` przechodzi.

Granice reguły:

- Najwyżej 2 próby na jedno zatrzymanie. Po drugiej nieudanej próbie sesja pyta człowieka (sekcja „Pytanie do człowieka”).
- Padający darmowy test sesja naprawia w kodzie, nigdy w teście: nie osłabia asercji, nie usuwa testu i go nie pomija.
- Zatrzymanie, które trafia na bramkę albo płatny test, idzie od razu do człowieka, bez prób. Przykłady: nowy wpis w `## Wymaga Twojej decyzji`, werdykt `RETHINK` albo `REJECTED` przeglądu, wynik testów fabryki poniżej progu, PR czekający na płatny test.
- Pytanie zatrzymania spoza bramek z reguły „Kiedy pytać człowieka” w `CLAUDE.md` sesja rozstrzyga sama według swojej rekomendacji. Dopisuje linię z `rozstrzygnął: agent` do `## Pytania do człowieka` w `change.md` (sekcja „Pytanie do człowieka”), commituje `change.md` poleceniem z listą ścieżek i wznawia krok odpowiedzią `--odpowiedz`.

Po naprawie sesja commituje ją na gałęzi zmiany poleceniem z listą ścieżek, uzupełnia linię zatrzymania (sekcja „Linia zatrzymania”) i uruchamia w tle `python3 scripts/autopilot.py <id>`. Autopilot uruchamia zatrzymany krok od nowa, a krok `claude -p` ocenia względem migawki z jego pierwszego startu.

## Pytanie do człowieka

Sesja pyta człowieka, gdy 2 próby samonaprawy się nie udały albo gdy zatrzymanie trafia na bramkę, płatny test albo decyzję człowieka. Pyta w tej rozmowie, według sekcji „Jak pisać do człowieka” w `CLAUDE.md`:

- najpierw sama sprawdza plik stanu, log kroku, pliki zmiany i `git status`;
- wniosek w pierwszym zdaniu, potem wyjaśnienie zatrzymania zwykłym językiem;
- rekomendacja porównana z celem zmiany (`**Problem.**` i `**Oczekiwany efekt.**` w `change.md`);
- wada polecanej opcji i zawężenie według reguły „Zawęź, zanim zapytasz” w sekcji „Jak pisać do człowieka” w `CLAUDE.md`;
- gotowa odpowiedź do wklejenia w jednym bloku;
- jedno pytanie na końcu.

Każde pytanie sesji zostawia jedną linię w `## Pytania do człowieka` w `change.md`, z rodzajem i rekomendacją (format: `docs/zasady-budowy.md`, punkt 6), w obu przypadkach:

- pytanie do człowieka: po jego odpowiedzi linia z wyborem człowieka i `rozstrzygnął: człowiek`;
- pytanie spoza bramek, które sesja rozstrzyga sama (sekcja „Zatrzymanie i samonaprawa”): linia z `wybór: rekomendacja` i `rozstrzygnął: agent`, zapisana przed wznowieniem kroku.

Sesja commituje `change.md` z tą linią poleceniem z listą ścieżek. Po archiwum `change.md` leży w niezmiennym `context/archive/`: decyzję człowieka sesja zapisuje wtedy tylko w polu `zrobiono` linii zatrzymania w pliku stanu.

Gdy człowiek w rozmowie potwierdzi wiersze `#### Manual` w `## Progress` planu, sesja zapisuje to w jednym commicie, zanim uruchomi krok archiwum: zaznacza te wiersze (`- [x]` z SHA sprawdzonego kodu) i dopisuje raport przebiegu `context/changes/<id>/runs/<YYYY-MM-DD>-<HHMMSS>-sesja-glowna.md` z wpisem `Observed` dla każdego wiersza (`Step: <numer wiersza, np. 2.3>`, `Criteria: <kryteria z linii **Criteria** fazy>`, `Observer: user`, `Command: manual: <co sprawdzono>`, `Exit: 0`, cytat potwierdzenia człowieka w `Output`, `Commit: <SHA z wiersza>`) według `skills/10x-implement/references/run-report-format.md`. Commituje `plan.md` i raport poleceniem z listą ścieżek i dopiero potem uruchamia krok archiwum.

Przed krokiem archiwum autopilot sam sprawdza dwie rzeczy, bez sesji `claude -p`. Każde z tych zatrzymań ma linię zatrzymania w `## Zatrzymania autopilota` w `change.md` z czasem i powodem:

- **Wiersze `#### Manual`** (pole `zatrzymanie` z `rodzaj: manual`). Plan ma niepotwierdzony wiersz `#### Manual`, więc `validate_change.py --rules 7` kończy się kodem innym niż 0. Powód podaje te wiersze. Sesja pyta człowieka o każdy wiersz, a po jego potwierdzeniu zapisuje je jak w akapicie wyżej (wiersze z SHA i raport `sesja-glowna.md` w jednym commicie). Wyjątek: gdy kryterium w zaakceptowanej intencji (`change.md`) mówi, że krok wiersza uruchamia sesja główna, sesja nie pyta, tylko wykonuje wiersz sama, bo akceptacja tego kryterium przez człowieka jest już zgodą na ten przebieg (D-391) i zapisuje go tak samo, z `Observer: agent` i uruchomionym poleceniem w raporcie. Potem uruchamia w tle `python3 scripts/autopilot.py <id>` bez opcji. `--przyjmij` po tym zatrzymaniu kończy się kodem 2. Autopilot nie podpowiada też `--odpowiedz`, bo zatrzymany krok nie miał sesji.
- **Pliki, które poszerzają kroki** (pole `zatrzymanie` z `rodzaj: scalenie`). Gałąź zmienia `.mcp.json` albo `.claude/settings*.json`, więc nie scali się bez zgody człowieka. Powód podaje listę tych plików. Zgoda to bramka człowieka (D-254): sesja pyta człowieka, czy zgadza się na scalenie tych plików. Po zgodzie, przed `--przyjmij`, sesja wpisuje w linii tego zatrzymania w `change.md` `zrobiono: zgoda na scalenie: człowiek, <pliki>` i `skutek:` jak przy przyjęciu kroku (`krok przyjęty, łańcuch dalej`), commituje `change.md` poleceniem z listą ścieżek i uruchamia w tle `python3 scripts/autopilot.py <id> --przyjmij`. Bez tego wpisu w zacommitowanym `change.md` `--przyjmij` kończy się kodem 2. Autopilot zapisuje zgodę w polu `zgoda_scalenia` pliku zaufanego poza folderem projektu (`~/.local/state/fabryka/`; pliki i ich wersje na gałęzi), nie wpisuje archiwum do `zrobione` i uruchamia krok archiwum. Zgoda obowiązuje, dopóki pliki się nie zmienią: nowa wersja któregoś z nich znowu zatrzymuje autopilota przed archiwum. Sprawdzenie plików idzie też przy wznowieniu kroku archiwum przez `--odpowiedz`, a zwykłe `--przyjmij` kroku archiwum po innym zatrzymaniu kończy się kodem 2, dopóki gałąź ma takie pliki bez zgody.

Najpierw idzie sprawdzenie wierszy `#### Manual`, potem plików. Zmiana, która ma oba, staje więc dwa razy.

Każdy krok `claude -p` w repo aplikacji bierze dostęp (wpisy `allowWrite` i `sandbox.network.allowedDomains` z `.claude/settings.json` oraz linie `zgoda: domena` z `start.md`) tylko z zapisu `dostep_krokow` w pliku zaufanym poza folderem projektu, a nie z HEAD (D-336). Zapis powstaje w kroku `start` (przebieg bez niego bierze go raz z gałęzi głównej), a odświeżają go tylko `przygotowanie-wdrozenia` po swoim commicie i `--przyjmij` po zgodzie człowieka. `.claude/settings.local.json` się nie liczy. Gdy HEAD różni się od zapisu, krok staje przed startem procesu z `rodzaj: zgoda`, a powód zaczyna się od „dostęp kroków claude -p różni się od zapisu” i wymienia dodane albo usunięte wpisy. Tę zmianę mógł zrobić sam krok agenta, także poleceniami gita z pominięciem chronionego pliku w drzewie. Sesja pokazuje człowiekowi różnicę (`git log -p -- .claude/settings.json context/foundation/start.md`) i pyta według akapitu niżej; zgoda idzie tą samą drogą co zgoda na sekcje (`zrobiono: zgoda: człowiek, dostęp kroków`, commit `change.md`, `--przyjmij`). Bez zgody sesja przywraca te pliki z gałęzi głównej, commituje je i uruchamia autopilota bez opcji.

Zatrzymanie z `rodzaj: zgoda`, którego powód zaczyna się od „ustawienia repo kroku mają wyjątek piaskownicy”, nie jest pytaniem o zgodę: `.claude/settings.json` albo `.claude/settings.local.json` repo kroku (w HEAD albo w drzewie roboczym) ma `sandbox.excludedCommands`, a krok ładuje ustawienia projektu i lokalne, więc polecenie z tej listy biegłoby poza piaskownicą. `--przyjmij` tego nie naprawia i autopilot go nie podpowiada. Sesja pokazuje człowiekowi plik i klucz z powodu i daje mu do zwykłego Terminala albo edytora usunięcie tego klucza, bo pliki ustawień zmienia tylko człowiek. Gdy klucz był w commicie, poprawiony plik commituje sesja poleceniem z listą ścieżek (tak samo mówi powód zatrzymania), a potem uruchamia autopilota bez opcji.

Zatrzymanie z `rodzaj: zgoda`, którego powód zaczyna się od „ustawienia repo kroku mają zmienione polecenia poza piaskownicą”, to inna sprawa niż wyjątek piaskownicy: `hooks`, `apiKeyHelper` albo `awsCredentialExport` w `.claude/settings.json` albo `.claude/settings.local.json` repo kroku (w HEAD albo w drzewie roboczym) różnią się od gałęzi głównej, a te klucze uruchamiają polecenia poza piaskownicą. Sesja nie każe niczego usuwać na ślepo: pokazuje człowiekowi różnicę (`git diff <gałąź główna> -- .claude/settings.json .claude/settings.local.json` i to samo dla drzewa roboczego, `git diff -- .claude/settings.json .claude/settings.local.json`) i pyta, czy zmiana jest jego. Gdy nie, sesja przywraca te klucze z gałęzi głównej (`git checkout <gałąź główna> -- <plik>`, plik ustawień zmienia człowiek, gdy piaskownica sesji go chroni) i commituje poprawiony plik poleceniem z listą ścieżek. Gdy tak, zmiana idzie najpierw na gałąź główną. Potem sesja uruchamia autopilota bez opcji. `--przyjmij` tego nie naprawia i autopilot go nie podpowiada. W trybie startu krok `zabezpieczenia`, który zatrzymał się przed swoim commitem, tego zatrzymania nie dostaje za haki, które zapisuje instalator zabezpieczeń fabryki; dostaje je za każde inne haki.

Zatrzymanie kroku `przygotowanie-wdrozenia` z `rodzaj: zgoda` albo `rodzaj: domena` to nowe pytanie do człowieka (bramka 2: chronione pliki aplikacji). Powód mówi, co się nie zgadza: sekcja `## Zgody`, `## Dostępy` albo `## Wdrożenie` zmieniła się po starcie przebiegu, plik w `chronione/` nie ma zgody albo gałąź dodaje domenę piaskownicy spoza zgody. Sesja pyta według akapitów wyżej:
- pokazuje różnicę sekcji (`git log -p -- <plik>`) albo listę plików i hostów z powodu;
- daje gotową linię zgody do `## Zgody` z powodu zatrzymania, np. `- czas: <YYYY-MM-DD HH:MM> · kto: człowiek · zgoda: domena <host> · czego dotyczy: <po co> · odpowiedź: „<cytat>”`;
- mówi jednym zdaniem, czemu zgody nie daje agent: ta ścieżka poszerza to, co autopilot robi poza piaskownicą.

Po zgodzie sesja dopisuje linię do `## Zgody` w `change.md` (gdy zgoda dotyczy nowego pliku albo hosta). Wpisuje w linii tego zatrzymania `zrobiono: zgoda: człowiek, <czego dotyczy>` i `skutek: krok idzie od nowa`. Commituje `change.md` poleceniem z listą ścieżek i uruchamia w tle `python3 scripts/autopilot.py <id> --przyjmij`. Autopilot odświeża zapis sekcji z HEAD, wypisuje linię `zmiany zapisu sekcji: …`, w repo aplikacji odświeża też z HEAD zapis dostępu kroków `claude -p` (`dostep_krokow`, D-336) i uruchamia krok od nowa. Sesja pokazuje tę linię człowiekowi: zgoda obejmuje tylko to, co pokazał powód zatrzymania. Bez wpisu w polu `zrobiono` w zacommitowanym `change.md` `--przyjmij` kończy się kodem 2. Kodem 2 kończy się też poza gałęzią zmiany (sesja przełącza `git switch <id>`) i wtedy, gdy od zatrzymania zmieniły się `## Dostępy` albo `## Wdrożenie`, a powód zatrzymania ich nie wymienia: sesja uruchamia wtedy `python3 scripts/autopilot.py <id>` bez opcji, krok zatrzymuje się na tej zmianie, a sesja pokazuje ją człowiekowi. Gdy człowiek się nie zgadza, sesja usuwa z gałęzi plik albo domenę spoza zgody, commituje to i uruchamia `python3 scripts/autopilot.py <id>` bez opcji. Zatrzymanie `wynik-wdrozenia` na zmienionych polach `## Wdrożenie` nie ma rodzaju i idzie od razu do człowieka: po archiwum nic nie odświeża zapisu sekcji (ograniczenie D-317 w `context/foundation/limitations.md` repo fabryki).

Potem wznawia w tle, z tymi samymi parametrami co przy starcie:

- `python3 scripts/autopilot.py <id> --odpowiedz '<odpowiedź>'` dla zatrzymanego kroku `claude -p` (research, plan, plan-review, implement, impl-review, archiwum). Odpowiedź idzie w apostrofach, a apostrof w niej sesja zapisuje jako `'\''`: w repo aplikacji polecenie autopilota działa poza piaskownicą (D-278), a powłoka w cudzysłowie rozwinęłaby `$(…)` i odwrócone apostrofy. Autopilot wznawia sesję kroku (`claude -p --resume <sesja>`) z tą odpowiedzią i ocenia krok jak zwykły przebieg. Odpowiedź trafia do agenta kroku jako jego następna wiadomość. Sesja pisze ją pełnym zdaniem dla tego agenta: wybór człowieka i to, co z niego wynika. Odpowiedź nie zaczyna się od `-`.
- `python3 scripts/autopilot.py <id> --przyjmij`, gdy człowiek przyjmuje zatrzymany krok bez ponownego przebiegu, np. wynik testów fabryki przyjęty jako ryzyko albo krok zrobiony ręcznie. Krok trafia do `zrobione` i `przyjete` w pliku stanu, a łańcuch idzie dalej. Po zatrzymaniu `rodzaj: zgoda` albo `rodzaj: domena` kroku `przygotowanie-wdrozenia` `--przyjmij` odświeża zapis sekcji i uruchamia ten krok od nowa, a poza gałęzią zmiany albo przy zmianie sekcji spoza powodu zatrzymania odmawia (opis wyżej). Wyjątki dotyczą też kroku archiwum (wyżej): po `rodzaj: scalenie` `--przyjmij` zapisuje zgodę i uruchamia krok archiwum (gdy zacommitowana linia zatrzymania mówi, kto się zgodził), po `rodzaj: manual` jest odrzucane, a po innym zatrzymaniu archiwum jest odrzucane, dopóki gałąź zmienia `.mcp.json` albo `.claude/settings*.json` bez zgody.
- `python3 scripts/autopilot.py <id>` po naprawie kroku polecenia (start, przygotowanie-wdrozenia, testy-fabryki, wynik-testow, synchronizacja-skilli, checkout-master, merge, push, wynik-wdrozenia, krok-pr, synchronizacja-po-pr, zapis-przebiegu) albo gdy człowiek chce, żeby krok poszedł od nowa. Krok polecenia nie ma sesji, więc `--odpowiedz` daje dla niego kod 2.

Obie opcje działają tylko przy polu `zatrzymanie` w pliku stanu. W innym przypadku autopilot kończy się kodem 2 i podaje polecenie do uruchomienia.

## Linia zatrzymania

Format linii, jeden wiersz na zatrzymanie, pola rozdzielone ` · `:

```
- czas: <YYYY-MM-DD HH:MM> · krok: <nazwa> · powód: <tekst w jednej linii> · zrobiono: <…> · skutek: <…>
```

Gdzie jest linia:

- Kroki do archiwum włącznie: sekcja `## Zatrzymania autopilota` na końcu `context/changes/<id>/change.md`. Autopilot ją dopisuje i commituje.
- Kroki po archiwum (checkout-master, merge, push, wynik-wdrozenia, krok-pr, synchronizacja-po-pr, zapis-przebiegu) i krok archiwum po przeniesieniu folderu: lista w polu `zatrzymania_po_archiwum` w `.autopilot-local/<id>/stan.json`. Krok `zapis-przebiegu` przepisuje te linie do `## Zatrzymania po archiwum` w `context/przebiegi/<id>.md` na `master`. Nic nie trafia do `context/archive/`.
- `## Interwencje` zapisują tylko działania człowieka. Autopilot i ta sekcja tam nie piszą.

Autopilot zapisuje linię z `zrobiono: —` i `skutek: —`. Wyjątek to krok przyjęty po samej odmowie uprawnień przy kompletnym śladzie: linia ma od razu `zrobiono: przyjęcie` i `skutek: krok przyjęty, łańcuch dalej`, a sesja jej nie zmienia.

Po samonaprawie, przyjęciu kroku albo decyzji człowieka sesja zastępuje oba `—` w linii tego zatrzymania, zanim uruchomi autopilota ponownie:

- `zrobiono:` to, co zrobiono, np. `samonaprawa: <co sesja poprawiła>`, `przyjęcie: człowiek, --przyjmij` albo `decyzja człowieka: <wybór>`;
- `skutek:` skutek dla łańcucha, np. `krok idzie od nowa`, `wznowienie kroku z odpowiedzią` albo `krok przyjęty, łańcuch dalej`.

Sesja edytuje linię tylko przy martwych albo pustych `pid` i `pid_kroku`:

- W `change.md` zmienia tylko tę linię i od razu commituje plik poleceniem z listą ścieżek, np. `git commit -m "docs(<id>): uzupełnienie linii zatrzymania w kroku <nazwa>" -- context/changes/<id>/change.md`.
- Zatrzymanie po archiwum uzupełnia w polu `zatrzymania_po_archiwum` w `.autopilot-local/<id>/stan.json` i nie zmienia innych pól. Nie edytuje `context/przebiegi/<id>.md` i nie commituje na `master`, bo drzewo na `master` musi być czyste dla `git pull --ff-only` kroku PR. Linię przepisuje do pliku przebiegu następny `zapis-przebiegu`.

## Koniec przebiegu

Ostatnie wywołanie kończy się kodem 0, polem `nastepny: null` i linią `autopilot: przebieg zakończony`. Sesja pokazuje wtedy człowiekowi listę końca przebiegu z wyjścia tego wywołania:

- propozycje retrospektywy ze stanem (scalona, PR czeka na człowieka, czeka na decyzję człowieka albo treść błędu);
- pytania rozstrzygnięte przez agenta;
- zatrzymania i samonaprawy, po jednej linii `<krok> — <powód> — <zrobiono> — <skutek>`, albo „brak”;
- wykonane polecenia synchronizacji skilli przed archiwum i po scaleniach, albo „brak”;
- pliki chronione wpisane przez autopilota: commit, pliki i różnica, albo „brak”.

Pełne wyjście kroku PR, z linią `master: …` o wyrównaniu lokalnego `master`, jest w logu kroku `krok-pr` (ścieżka z jego linii końca). Linia `autopilot: krok PR: …` mówi o płatnych sesjach autora, recenzenta i poprawki po testach oraz o płatnych testach skilli tego kroku.

Ślad przebiegu zostaje w repozytorium: `context/przebiegi/<id>.md` (`## Koszty kroków`, `## Wynik kroku PR`, `## Zatrzymania po archiwum`, `## Pliki chronione`) i `koszty-krokow.md` w folderze zmiany w archiwum. `python3 scripts/pomiar.py` pokazuje czas i koszt kroków. Krok PR nie uruchamia sam płatnych testów i niczego nie scala (D-432), więc PR z poprawką skilla z płatnym testem czeka na człowieka: sesja uruchamia `python3 scripts/retro_pr.py <id> --paid-tests P<n>` tylko po wyraźnej zgodzie człowieka. Uruchamia je przed commitem czegokolwiek innego na `master`: commit zapisu przebiegu (tylko `context/przebiegi/`) nie blokuje testu, ale każdy inny commit na `master` po założeniu PR-a daje odmowę „baza ze znacznika” (D-102). Wpis w `context/foundation/decisions.md`, który podaje wynik testu albo sprawdzenia, sesja pisze dopiero po tym wyniku i go cytuje. Sesja nie wypycha poprawek do PR-ów retrospektywy: PR z niezaliczonymi testami skilli poprawia raz sam krok PR (D-427), a PR, który czeka na człowieka, scala albo zamyka człowiek.

### Koniec kawałka w repo aplikacji

Po przebiegu kawałka roadmapy (sekcja „Kawałek roadmapy”) krok archiwum ustawił już kawałkowi status `done` w roadmapie, a w aplikacji z `## Wdrożenie` robi to dopiero `wynik-wdrozenia` po udanym wdrożeniu. Sesja dopisuje do listy końca przebiegu, w tej samej wiadomości:

- jedno polecenie uruchomienia lokalnego z sekcji `## Uruchomienie lokalne` w `CLAUDE.md` aplikacji, zamiast listy kroków;
- wpisy `## Wymaga Twojej decyzji` z intencji kawałka (`change.md` kawałka w `context/archive/`) albo „brak”.

Sesja nie pyta człowieka o kroki scenariusza po kawałku. Człowiek ogląda aplikację raz, po ostatnim kawałku roadmapy (ostatni akapit tej sekcji).

Gdy `CLAUDE.md` aplikacji ma `## Wdrożenie`, sesja patrzy na wynik kroku `wynik-wdrozenia`:
- Wdrożenie przeszło (linia `wdrożenie przeszło; adres: <adres>` w logu kroku): sesja podaje adres z pola `adres` w `## Wdrożenie`. Polecenie uruchomienia lokalnego zostaje dla pracy lokalnej.
- Wdrożenie nie przeszło (linia zatrzymania `wynik-wdrozenia` w `## Zatrzymania po archiwum` w `context/przebiegi/<change-id>.md`): sesja zamiast adresu przekazuje człowiekowi wiadomość z powodu tej linii: co nie przeszło, która wersja działa, czy wersję cofnięto i że migracje bazy zostają. Przyczynę sesja czyta z pliku logu CI, którego ścieżkę podaje powód, a nie prosi człowieka o `gh run view`. Pisze ją zwykłym językiem, według „Jak pisać do człowieka”, i nie prosi o sprawdzenie scenariusza pod adresem.

Potem, na gałęzi głównej, pozycje roadmapy ze statusem `proposed`, których każde wymaganie wstępne to ID pozycji ze statusem `done`, dostają status `ready` w tabeli i w bloku pozycji. Sesja zapisuje to w jednym commicie: `git commit -m "docs(roadmap): pozycje gotowe po <ID kawałka>" -- context/foundation/roadmap.md`. Nie wysyła go: w piaskownicy repo aplikacji nie ma logowania do GitHuba, a commit wyśle krok `push` następnego kawałka. Gdy żadna pozycja się nie zmienia, commitu nie ma.

Jedno oglądanie aplikacji po ostatnim kawałku: gdy po tym kroku żadna pozycja `context/foundation/roadmap.md` nie ma statusu innego niż `done`, sesja wysyła człowiekowi jedną wiadomość oglądania. Wiadomość ma adres z pola `adres` w `## Wdrożenie` w `CLAUDE.md` aplikacji (gdy ta sekcja jest), a inaczej polecenie z `## Uruchomienie lokalne`, oraz kroki scenariusza pierwszej wersji z PRD (podsekcja `### Scenariusz pierwszej wersji` w `context/foundation/prd.md`), wszystkie, po kolei, jako to, co człowiek przechodzi w działającej aplikacji. To jedyne oglądanie aplikacji przez człowieka w roadmapie; kawałki wcześniej go nie dają.

## Publikacja paczki

Gdy człowiek prosi o publikację paczki w repo fabryki, sesja działa według `docs/publikacja-paczki.md` (ten plik i polecenie publikacji są tylko w repo fabryki, paczka ich nie ma): najpierw daje listę zgód zmiany paczki prostym językiem, potem pyta o publikację jednym słowem, a publikacja idzie poleceniem z adresem noreply GitHuba.

## Filtr trybu automatycznego

Gdy filtr trybu automatycznego zablokuje polecenie autopilota, sesja go nie obchodzi: nie zmienia postaci polecenia, nie uruchamia kroków ręcznie i nie zmienia ustawień. Prosi człowieka o zatwierdzenie przez `/permissions` → „Recently denied” → `r`. Wąską regułę zezwolenia `Bash(python3 scripts/autopilot.py:*)` może dopisać tylko człowiek, bo ustawienia Claude Code zmienia człowiek (D-137). Po zatwierdzeniu sesja uruchamia polecenie jeszcze raz.
