# Start projektu aplikacji

Ten plik prowadzi sesję Claude Code od pustego folderu do repo aplikacji z PRD, zaakceptowaną technologią i infrastrukturą, szkieletem z CI, zabezpieczeniami, roadmapą i planem testów. Czyta go sesja główna, którą skierował tu hook startu sesji, polecenie `/fabryka` albo `CLAUDE.md` aplikacji.

## Raz, przed pierwszym użyciem

Człowiek wkleja dwa wpisy do `~/.claude/settings.json`. Ten plik zmienia tylko człowiek: to ustawienia globalne, więc sesja ich nie zapisuje. `<fabryka>` w tym pliku to folder laboratorium, nie działająca ścieżka.

W paczce oba wpisy i skille zapisuje `python3 scripts/instaluj.py --zapisz` uruchomione przez człowieka w folderze paczki, więc wpisów niżej nie wkleja się ręcznie.

Pierwszy wpis to hook startu sesji. Plik `~/.claude/settings.json` nie ma dziś klucza `"hooks"`, więc człowiek wkleja blok niżej jako wartość nowego klucza `"hooks"`:

```json
{
  "SessionStart": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python3 -I -B <fabryka>/scripts/hook_start_sesji.py"
        }
      ]
    }
  ]
}
```

Przed wklejeniem zamień `<fabryka>` na pełną ścieżkę, którą podał hook startu sesji (przed pierwszą instalacją hooka: folder nad `docs/` tego pliku).

Co robi ten wpis:

- Hook uruchamia się przy starcie każdej sesji. W pustym folderze (najwyżej `.git` i `.DS_Store`) każe sesji zapytać raz „fabryką czy zwyczajnie?” przy pierwszej prośbie o budowę albo zmianę. W folderze ze znacznikiem `.fabryka` odsyła sesję do tego pliku, a po starcie do `<fabryka>/docs/sesja-glowna.md`. W obu przypadkach i w samym laboratorium mówi sesji, że `<fabryka>` to folder laboratorium, z jego pełną ścieżką. W każdym innym folderze z plikami nic nie robi.
- Wpis nie ma `matcher`, więc działa też po skróceniu rozmowy (`compact`): sesja dostaje instrukcję jeszcze raz.
- W krokach autopilota (zmienna `AUTOPILOT_KROK` w środowisku) hook milczy.
- Polecenie `/fabryka` nie wymaga wpisu: instaluje się samo przy synchronizacji skilli do `~/.claude/skills/`.

Drugi wpis wyjmuje z piaskownicy repo aplikacji polecenie autopilota laboratorium. Plik `~/.claude/settings.json` nie ma dziś klucza `"sandbox"`, więc człowiek wkleja blok niżej jako wartość nowego klucza `"sandbox"`:

```json
{
  "excludedCommands": [
    "python3 <fabryka>/scripts/autopilot.py *"
  ]
}
```

Przed wklejeniem zamień `<fabryka>` na pełną ścieżkę, którą podał hook startu sesji, tak samo jak w pierwszym wpisie.

Co robi ten wpis:

- Krok zabezpieczeń włącza w repo aplikacji piaskownicę. Bez tego wpisu kolejne kroki autopilota nie zapiszą `~/.claude` i nie połączą się z modelem.
- Wpis wyjmuje z piaskownicy tylko polecenie autopilota laboratorium. Inne polecenia sesji dalej idą przez piaskownicę. Poza piaskownicą działa sam proces Pythona autopilota (D-278: wpis wklejany razem z hookiem). Każdy krok `claude -p` dostaje własną piaskownicę od autopilota, w laboratorium i w repo aplikacji (zmiana wdrozenie, faza 9; D-279).
- Autopilota uruchamia się samym poleceniem z pełną ścieżką, np. `python3 <fabryka>/scripts/autopilot.py --start`, bez `cd`, zmiennej środowiska ani innego przedrostka. Tylko takie polecenie pasuje do wpisu; polecenie z przedrostkiem idzie przez piaskownicę i pada.

## Kiedy obowiązuje

- Tylko przy prośbie o zbudowanie albo zmianę czegoś. Zwykłe pytanie (np. „co znaczy ten błąd?”) dostaje zwykłą odpowiedź, bez tego pliku, także w folderze ze znacznikiem `.fabryka`.
- Tylko w pustym folderze (najwyżej `.git` i `.DS_Store`) albo w folderze ze znacznikiem `.fabryka`, dopóki `context/foundation/start.md` nie ma sekcji `## Lista końcowa`. Potem sesja działa według `<fabryka>/docs/sesja-glowna.md`.
- W folderze z kodem bez `.fabryka` ten plik nie działa. Przejęcie istniejącego projektu przyjdzie w osobnej zmianie.
- Krok `claude -p` autopilota (zmienna `AUTOPILOT_KROK` w środowisku) tego pliku nie wykonuje i nie uruchamia autopilota.

## Wybór: fabryką czy zwyczajnie

- W pustym folderze sesja przy pierwszej prośbie o budowę albo zmianę pyta raz: „fabryką czy zwyczajnie?”. Gdy człowiek już wybrał w tej rozmowie, nie pyta ponownie.
- „Zwyczajnie”: koniec tego pliku. Sesja pracuje jak zwykły Claude Code, bez laboratorium i bez znacznika `.fabryka`.
- „Fabryką”: sesja przechodzi do sekcji „Przygotowanie folderu”. Pierwsza prośba człowieka (np. „Zbuduj aplikację do nauki z fiszek…”) to początek opisu właściciela; sesja zachowuje ją do sekcji „Kształtowanie w rozmowie”.
- Polecenie `/fabryka` w pustym folderze zaczyna od przygotowania folderu, bez tego pytania.

## Przygotowanie folderu

Sesja robi kolejno, bez pytań:

1. Pusty plik znacznika: `touch .fabryka`.
2. Repo git z gałęzią `main`: bez `.git` polecenie `git init -b main`. Gdy `.git` już jest, a repo nie ma commitów i gałąź nie nazywa się `main`: `git symbolic-ref HEAD refs/heads/main`.
3. `/10x-init`: foldery `context/changes/`, `context/archive/` i `context/foundation/`.
4. `.gitignore` z linią `/.autopilot-local/` (pliki stanu i logi autopilota).
5. `CLAUDE.md` z dwiema liniami: pierwsza kieruje sesję do tego pliku na czas startu, druga to linia z `docs/sesja-glowna.md` (sekcja „Start w repo aplikacji”):

   ```
   Dopóki context/foundation/start.md nie ma sekcji „## Lista końcowa”, przy prośbie o budowę albo zmianę sesja czyta <fabryka>/docs/start-projektu.md i działa według niego.
   Gdy człowiek w rozmowie mówi „zrób zmianę”, „zrób <ID kawałka>”, „zrób kolejny kawałek”, „kontynuuj <change-id>” albo „co się dzieje?”, albo gdy kończy się wywołanie autopilota uruchomione w tle, sesja czyta <fabryka>/docs/sesja-glowna.md i działa według niego. Krok claude -p autopilota (ma w środowisku zmienną AUTOPILOT_KROK) tego nie robi i nie uruchamia autopilota.
   ```

6. `context/foundation/start.md`, plik śladu startu w git. Nagłówek `# Start projektu: <nazwa folderu>` i puste sekcje, w tej kolejności: `## Zgody`, `## Opis właściciela`, `## Pytania do człowieka`, `## Decyzje bez podstawy`, `## Wymagania komputera`, `## Sprawdzalność scenariusza`, `## Do decyzji na posiedzeniu`, `## Akceptacja`, `## Zatrzymania autopilota`, `## Koszty kroków`, `## Pierwszy kawałek`. Sekcje zostają bez linii zastępczych, bo autopilot sprawdza w nich linie człowieka i kroków. Sekcji `## Lista końcowa` jeszcze nie ma: powstaje na końcu startu, a hook i `CLAUDE.md` czytają ją jako znak, że start się skończył.
7. Pierwszy commit: `git add .fabryka .gitignore CLAUDE.md context && git commit -m "chore(start): przygotowanie folderu"`.

## Pytania-bramki

Zaraz po przygotowaniu folderu, przed kształtowaniem, sesja wysyła jedną wiadomość z obiema bramkami startu i gotową odpowiedzią do wklejenia. W trakcie startu tych pytań już nie ma. Wyjątki to domena spoza domyślnych (sekcja „Domena spoza domyślnych”) i decyzja kroku w tle, która trafia na bramkę (sekcja „Inne zatrzymania startu”). O konta, klucze i płatne usługi aplikacji (np. klucz do modelu AI) start nie pyta: zbierze je kawałek roadmapy, który ich potrzebuje (D-280).

Treść wiadomości:

- **GitHub:** na końcu startu sesja zakłada na koncie człowieka prywatne repo o nazwie folderu (`gh repo create <nazwa folderu> --private`) i wysyła do niego kod. Repo widzi tylko człowiek.
- **Domyślne zabezpieczenia projektu:** od pierwszego kroku startu w tle polecenia w projekcie działają w piaskownicy. Ich sieć obejmuje tylko domeny z `<fabryka>/skills/guardrails/templates/guardrails.json` (`allowed_domains`): `registry.npmjs.org`, `github.com`, `*.github.com` i `*.githubusercontent.com`, czyli rejestr npm i GitHub. Poza projektem mogą pisać tylko w folderze podręcznym npm `~/.npm`. Po szkielecie `/guardrails` zapisuje te same domeny i `~/.npm` w `.claude/settings.json`, razem z hookami. Gdy projekt będzie potrzebował innej domeny, start stanie i sesja zapyta osobno.
- Gotowa odpowiedź w jednym bloku, np.:

  ```
  Zgadzam się na prywatne repo na GitHubie i wysłanie kodu na końcu startu. Zgadzam się na domyślne zabezpieczenia projektu z domenami rejestru npm i GitHuba.
  ```

Po odpowiedzi sesja dopisuje do `## Zgody` w `start.md` jedną linię na każdą zgodę, z czasem, tym, kto się zgodził, czego zgoda dotyczy, i cytatem odpowiedzi:

```
- czas: <YYYY-MM-DD HH:MM> · kto: człowiek · zgoda: github · czego dotyczy: prywatne repo <nazwa folderu> na GitHubie i wysłanie kodu na końcu startu · odpowiedź: „<cytat>”
- czas: <YYYY-MM-DD HH:MM> · kto: człowiek · zgoda: zabezpieczenia · czego dotyczy: domyślne zabezpieczenia projektu (.claude/settings.json, domeny rejestru npm i GitHuba) · odpowiedź: „<cytat>”
```

Potem commit: `git commit -m "docs(start): zgody człowieka" -- context/foundation/start.md`. Bez którejś zgody start stoi: sesja mówi, czego brakuje, i nie uruchamia autopilota. Krok `start` autopilota i tak odmówi bez obu linii.

## Kształtowanie w rozmowie

Kształtowanie idzie w tej rozmowie, z człowiekiem, przez skill `/10x-shape`. Sesja nie porównuje opisu z własną listą wymagań PRD; luki i pytania ustala skill.

1. Sesja zapisuje opis właściciela dosłownie w `## Opis właściciela` w `start.md`: każdą jego wiadomość, która opisuje aplikację, jako cytat. Commit: `git commit -m "docs(start): opis właściciela" -- context/foundation/start.md`.
2. Sesja uruchamia narzędziem Skill `10x-shape` z argumentem:

   ```
   context/foundation/start.md
   Notatki to sekcja ## Opis właściciela w context/foundation/start.md. context_type: greenfield. Pytaj tylko o to, czego notatki nie mówią, oraz o to, co warto zakwestionować w zakresie; nie pytaj o rzeczy, które notatki już mówią. Aplikację buduje fabryka (autopilot laboratorium), a nie człowiek: nie pytaj o czas, jaki człowiek da pierwszej wersji, i nie tnij zakresu pod jego czas pracy. Człowieka pytaj tylko o kierunek: dla kogo, jaki problem, co wchodzi do pierwszej wersji, czego nie robimy i co jest miarą sukcesu. Szczegóły (np. limit długości tekstu, język, pola i cechy widoczne z zewnątrz) rozstrzygnij sam swoją rekomendacją i zapisz w shape-notes.md z dopiskiem rozstrzygnął: agent; człowiek zobaczy je na posiedzeniu akceptacji. Każde pytanie o potwierdzenie treści (np. listy wymagań) pokazuje tę treść w tej samej wiadomości, przed pytaniem, np. każde wymaganie jednym zdaniem. Zapisz context/foundation/shape-notes.md.
   ```

3. Na pytania skilla odpowiada człowiek, w rozmowie. Sesja nie odpowiada za niego. Gdy skill mimo prośby pyta o czas pracy człowieka albo o szczegół, sesja odpowiada tylko za tę część: fabryka buduje aplikację, a szczegół rozstrzyga model z zapisem. Gdy skill prosi o potwierdzenie treści, której w pytaniu nie pokazał, sesja pokazuje ją człowiekowi przed jego odpowiedzią (I-11).
4. Pytania i odpowiedzi kształtowania zapisuje skill w `context/foundation/shape-notes.md`; sesja nie powiela ich w `## Pytania do człowieka`.
5. Gdy skill skończy, sesja sprawdza, że `shape-notes.md` ma `context_type: greenfield`, i commituje: `git commit -m "docs(start): notatki kształtowania" -- context/foundation/shape-notes.md`. Krok `start` autopilota odmówi bez zacommitowanych notatek.

## Kroki bez rozmowy

Dalej start prowadzi tryb startu autopilota. Sesja uruchamia go narzędziem Bash z parametrami `command: python3 <fabryka>/scripts/autopilot.py --start`, `run_in_background: true` i `timeout: 7200000`. W tej samej odpowiedzi raz na pierwszym planie uruchamia `python3 <fabryka>/scripts/autopilot.py --start --krok` i wypisuje człowiekowi linię trwającego kroku. Granica kroków, „co się dzieje?” i „kontynuuj” działają jak w `<fabryka>/docs/sesja-glowna.md`, z `--start` zamiast identyfikatora zmiany i plikiem stanu `.autopilot-local/start-projektu/stan.json`. Człowiek widzi linie początku i końca kroków. Czas i koszt każdego kroku `claude -p` autopilot zapisuje sam w `## Koszty kroków` w `start.md`.

Każde polecenie autopilota to samo polecenie z pełną ścieżką, bez `cd`, zmiennej środowiska ani innego przedrostka, bo tylko takie pasuje do wpisu `sandbox.excludedCommands` z sekcji „Raz, przed pierwszym użyciem”. Gdy wywołanie po kroku `zabezpieczenia` pada na błędzie piaskownicy (np. brak zapisu do `~/.claude` albo brak połączenia z modelem), sesja zatrzymuje start i prosi człowieka o wklejenie drugiego wpisu z tej sekcji. Sama ustawień globalnych nie zmienia.

Łańcuch startu, w kolejności:

| Krok | Co robi | Skill | Ślad, który krok zostawia |
|---|---|---|---|
| `start` | sprawdza warunki: gałąź główna, `/.autopilot-local/` w `.gitignore`, `context/`, zacommitowany `start.md` z opisem i obiema zgodami, zacommitowany `shape-notes.md` z `context_type: greenfield`, czyste drzewo | — | — |
| `prd` | PRD | `/10x-prd` | `context/foundation/prd.md` |
| `technologia` | propozycja technologii | `/10x-tech-stack-selector` | `context/foundation/tech-stack.md` |
| `infrastruktura` | propozycja infrastruktury | `/10x-infra-research` | `context/foundation/infrastructure.md` |
| `przeglad` | lista decyzji bez podstawy | — | `## Decyzje bez podstawy` w `start.md` |
| `wymagania` | wymagania technologii na tym komputerze i sprawdzalność scenariusza pierwszej wersji | — | `## Wymagania komputera` i `## Sprawdzalność scenariusza` w `start.md`, każda z co najmniej jedną linią |
| `akceptacja` | bramka człowieka: posiedzenie akceptacji | — | linia w `## Akceptacja` |
| `szkielet` | szkielet aplikacji, CI i jedno polecenie uruchomienia lokalnego | `/10x-bootstrapper` | `package.json`, bez `*.scaffold` i `AGENTS.md`, workflow CI w `.github/workflows/` uruchamiany przy `push`, `## Uruchomienie lokalne` z poleceniem w `CLAUDE.md` |
| `zabezpieczenia` | zabezpieczenia i polecenie sprawdzające | `/guardrails` | `.claude/settings.json`, `## Verify` w `CLAUDE.md` |
| `domeny` | bramka człowieka: domeny spoza domyślnych | — | linie `zgoda: domena <host>` |
| `roadmapa` | roadmapa z polem „Potrzebuje” i polecany pierwszy kawałek | `/10x-roadmap` | `context/foundation/roadmap.md` z `- **Potrzebuje:**` przy każdej pozycji, `## Pierwszy kawałek` |
| `plan-testow` | plan testów aplikacji przed pierwszym kawałkiem | `/10x-test-plan` | `context/foundation/test-plan.md` |
| `github` | prywatne repo i wysłanie kodu | — | `origin` na GitHubie |
| `lista` | czeka na listę końcową sesji i wysyła jej commit (`git push`) | — | `## Lista końcowa` w `start.md` na GitHubie |

Zasady kroków:

- Automatycznie uruchamiają się tylko te skille, w tej kolejności: `/10x-init` (w przygotowaniu folderu), `/10x-shape` (w rozmowie z człowiekiem, sekcja „Kształtowanie w rozmowie”), `/10x-prd`, `/10x-tech-stack-selector`, `/10x-infra-research`, `/10x-bootstrapper`, `/guardrails`, `/10x-roadmap` i `/10x-test-plan`. Sesja nie uruchamia w trakcie startu innych skilli i nie uruchamia tych kroków ręcznie.
- Każdy krok ze skillem kończy się commitem na gałęzi `main`: `/10x-init` commitem przygotowania folderu, a kroki `claude -p` commitem autopilota `feat(start): krok <nazwa>`, w którym jest też wiersz kosztów kroku.
- W krokach `claude -p` nikt nie odpowiada. Każde pytanie skilla (`/10x-prd`, `/10x-tech-stack-selector`, `/10x-infra-research`, `/10x-bootstrapper`, `/guardrails`, `/10x-roadmap`, `/10x-test-plan`) agent kroku rozstrzyga sam decyzją najlepszą dla prawidłowej realizacji intencji właściciela (opis właściciela, `shape-notes.md`), z zachowaniem założeń z PRD i zasad, i zapisuje linią z `rozstrzygnął: agent` w `## Pytania do człowieka`. Człowiek nie odpowiada na te pytania: PRD, technologię, infrastrukturę i decyzje modelu akceptuje w całości na posiedzeniu akceptacji, a decyzje kroków po posiedzeniu widzi na liście końcowej. Wcześniej angażuje się tylko przy bramkach.
- Wyjątek jak w kroku planu: decyzja, która trafia na jedną z siedmiu bramek z „Kiedy pytać człowieka” w `<fabryka>/CLAUDE.md`, nie zapada w tle. Prośby kroków startu i krok planu biorą te siedem bramek z jednej stałej `GATES_TEMPLATE` w `scripts/autopilot.py`. Płatna usługa aplikacji (np. klucz do płatnego modelu AI) to przykład bramki płatnego przebiegu. Krok kończy odpowiedź pytaniem z rekomendacją i linią `PYTANIE_DO_CZLOWIEKA: …`, a autopilot zatrzymuje start (sekcja „Inne zatrzymania startu”). Propozycja technologii albo infrastruktury do posiedzenia nie jest taką decyzją, dopóki krok niczego nie zakłada, nie kupuje i nie wysyła. Zgody z `## Zgody` człowiek już dał.
- Technologia i infrastruktura: tryb lokalny jest mocno preferowany. Szkielet ma się uruchamiać i przechodzić polecenie sprawdzające lokalnie bez żadnych kont (tryb deweloperski, np. lokalny odpowiednik bazy). Gdy najlepszy dostawca nie ma trybu lokalnego, nie odpada. Trafia na posiedzenie akceptacji jako decyzja z wyjaśnieniem i listą kont potrzebnych przed szkieletem, zapisana w `## Do decyzji na posiedzeniu` w `start.md`. Te konta człowiek zakłada na posiedzeniu, a nie w trakcie startu. Poza tym konta są potrzebne dopiero do wdrożenia.
- Sprawy odłożone: sprawę, którą krok odkłada na później (np. luki HIGH z audytu zależności szkieletu), krok zapisuje wpisem z „Kiedy wrócić” w rejestrze ograniczeń aplikacji `context/foundation/limitations.md`, a krok `infrastruktura` w `infrastructure.md`. Sam raport kroku nie wystarcza, bo fabryka go potem nie czyta. Krok `roadmapa` czyta te wpisy, ryzyka infrastruktury i `context/changes/bootstrap-verification/verification.md`. Sprawę, którą trzeba zrobić przed użyciem albo wdrożeniem aplikacji, wpisuje w `Prerequisites` pozycji roadmapy, którą ta sprawa blokuje, jako stan zewnętrzny zwykłym językiem. Nie robi z niej nowego kawałka, bo `/10x-roadmap` nie wymyśla kawałków spoza PRD. Reszta zostaje w rejestrze z „Kiedy wrócić” (I-11).
- Pole „Potrzebuje”: krok `roadmapa` dopisuje każdej pozycji z `- **Change ID:**` linię `- **Potrzebuje:**` z dostępami, które wynikają z PRD i technologii (konta, klucze, płatne usługi), albo `- **Potrzebuje:** nic`. Pole nazywa dostęp, nigdy nie podaje wartości sekretu. Konta do wdrożenia są w polu „Potrzebuje” fundamentu wdrożenia.
- Scenariusz pierwszej wersji: prośba kroku `prd` każe zapisać w Success Criteria podsekcję `### Scenariusz pierwszej wersji`. To numerowane kroki, które właściciel przejdzie w działającej aplikacji, każdy z odpowiedzią tak albo nie. To miara „test zdany” aplikacji. Każdy krok właściciel sprawdza w działającej aplikacji bez programisty. Krok, który wymaga danych niewidocznych w aplikacji, ma zdanie „Sprawdzenie: jedno polecenie <nazwa>, które wypisuje <dane>; powstaje w kawałku, który dostarcza ten krok.”. Kawałek roadmapy, który dostarcza taki krok, ma to polecenie w zakresie.
- Krok `wymagania` idzie po `przeglad`, w osobnej, świeżej sesji, bez skilla. (1) Wypisuje wymagania wybranej technologii do uruchomienia lokalnego na tym komputerze, tak jak wynikają z `tech-stack.md` (programy i wersje, usługi, pamięć, dysk), i sprawdza każde poleceniem tylko do odczytu. Naprawia tylko to, na co pozwala reguła samonaprawy z `<fabryka>/docs/sesja-glowna.md`; instalacji programu, startu usługi ani zmiany ustawień systemu nie robi. Zapisuje `## Wymagania komputera` w `start.md`, a każde niespełnione wymaganie także w `## Do decyzji na posiedzeniu`, prostymi słowami, z instrukcją albo propozycją lżejszej technologii. (2) Ocenia każdy krok scenariusza pierwszej wersji: czy nietechniczny właściciel sprawdzi go w działającej aplikacji. Zapisuje `## Sprawdzalność scenariusza` w `start.md`, a krokowi, który wymaga danych, dopisuje w PRD zdanie „Sprawdzenie: jedno polecenie …”. Innych części PRD, technologii ani infrastruktury nie zmienia. Prośba kroku nie nazywa żadnej technologii: wymagania biorą się z `tech-stack.md` aplikacji (D-296).
- Krok `szkielet` poza szkieletem dodaje workflow CI w `.github/workflows/`, który uruchamia polecenie sprawdzające przy wysłaniu na gałąź główną i przy PR-ach. Robi to w szkielecie, bo po kroku `zabezpieczenia` ta ścieżka jest chroniona. Dodaje też jedno polecenie uruchomienia lokalnego w menedżerze pakietów projektu: sprawdza wymagania z `## Wymagania komputera`, uruchamia lokalne usługi, ustawia zmienne środowiska (z lokalnych usług i z plików z `## Dostępy` w `CLAUDE.md`, gdy są) i uruchamia serwer. Polecenie trafia do sekcji `## Uruchomienie lokalne` w `CLAUDE.md` aplikacji i do `README.md`.
- Krok `plan-testow` idzie po `roadmapa`: `/10x-test-plan` pisze `context/foundation/test-plan.md` i kończy po jego zapisie, bez przekazania do `/10x-new` i bez nowych zmian w `context/changes/`. Punkty kontrolne skilla (zakres skanu, wywiad, akceptacja szkicu) agent kroku rozstrzyga sam z linią `rozstrzygnął: agent`. Testy powstają w kawałkach roadmapy, a nie w osobnych zmianach (D-304).
- Kolejność: CI powstaje w kroku `szkielet`, a plan testów w kroku `plan-testow`, więc oba są gotowe przed łańcuchem pierwszego kawałka każdej nowej aplikacji. Aplikacja, której start skończył się bez planu testów, dostaje go w sesji przed pierwszym kawałkiem (`<fabryka>/docs/sesja-glowna.md`).
- Krok `przeglad` idzie w osobnej, świeżej sesji (własny `--session-id`), bez skilla. Dostaje PRD, propozycję technologii, propozycję infrastruktury, `shape-notes.md` i opis właściciela, a nie rozmowę sesji, która je pisała. Porównuje decyzje z opisem i `shape-notes.md` i zapisuje jedną linię na decyzję bez podstawy albo `- brak`. Jedno przejście, bez drugiego modelu.
- Krok `infrastruktura` szuka w sieci (`WebSearch`, `WebFetch`), ale nie ma `Bash`, a zapisywać może tylko `context/foundation/infrastructure.md` i `context/foundation/start.md` (każdy inny zapis autopilot mu odmawia). Pytania wywiadu `/10x-infra-research` agent kroku rozstrzyga sam, jak w innych krokach: z opisu właściciela w `start.md`, `shape-notes.md`, PRD i technologii, z linią `rozstrzygnął: agent` w `## Pytania do człowieka`. Prośba podaje wskazówkę, a nie regułę: właściciel jest nietechniczny i chce jak najmniej ingerencji. Człowiek nie odpowiada na wywiad, tylko akceptuje wynik na posiedzeniu. Zmiana innego pliku niż `infrastructure.md` i `start.md` zatrzymuje start bez commita kroku; sesja przegląda te pliki z człowiekiem.

## Posiedzenie akceptacji

Po krokach `przeglad` i `wymagania` autopilot staje w kroku `akceptacja` z `rodzaj: akceptacja`. To jedyne obowiązkowe posiedzenie z człowiekiem w trakcie startu. Szkielet nie rusza przed zapisaną akceptacją.

1. Sesja pokazuje człowiekowi w jednej wiadomości:
   - PRD (`context/foundation/prd.md`): dla kogo, problem, pierwsza wersja, czego nie robimy i scenariusz pierwszej wersji;
   - proponowaną technologię (`context/foundation/tech-stack.md`) zwykłym językiem;
   - proponowaną infrastrukturę (`context/foundation/infrastructure.md`): platformę i dlaczego;
   - listę decyzji bez podstawy z `## Decyzje bez podstawy`, dosłownie;
   - decyzje modelu: linie z `rozstrzygnął: agent` z `## Pytania do człowieka`, jedną linią każda (pytanie i wybór);
   - `## Do decyzji na posiedzeniu`, gdy nie jest pusta: dostawcę bez trybu lokalnego z wyjaśnieniem i listą kont potrzebnych przed szkieletem. Te konta człowiek zakłada teraz, na posiedzeniu, a sesja podaje polecenia logowania;
   - niespełnione wymagania z `## Wymagania komputera`, prostymi słowami, każde z instrukcją, co właściciel ma zrobić, albo z propozycją lżejszej technologii;
   - `## Sprawdzalność scenariusza`: przy każdym kroku scenariusza, czy właściciel sprawdzi go sam w działającej aplikacji, a przy kroku, który wymaga danych, zdanie „Sprawdzenie: jedno polecenie …” z PRD.
2. Człowiek akceptuje jednym słowem albo poprawia. Wiadomość ma gotową odpowiedź `akceptuję`.
3. Po poprawce sesja zmienia `prd.md`, `tech-stack.md` albo `infrastructure.md`, commituje je poleceniem z listą ścieżek i pokazuje całość jeszcze raz.
4. Po akceptacji sesja dopisuje do `## Akceptacja` w `start.md` linię z czasem, tym, kto zaakceptował, co i cytatem: `- czas: <YYYY-MM-DD HH:MM> · kto: człowiek · akceptacja: PRD, technologia, infrastruktura i decyzje modelu · odpowiedź: „<cytat>”`. Potem commituje: `git commit -m "docs(start): akceptacja PRD, technologii i infrastruktury" -- context/foundation/start.md`.
5. Sesja uruchamia w tle `python3 <fabryka>/scripts/autopilot.py --start`. `--przyjmij` w trybie startu kończy się kodem 2, poza zatrzymaniem na dostępie kroków (`rodzaj: zgoda`, sekcja „Domena spoza domyślnych”).

Agent nie wybiera technologii ani infrastruktury ostatecznie sam. Start nie zakłada kont do wdrożenia i nie pyta o nie w trakcie.

## Inne zatrzymania startu

Linia każdego zatrzymania jest w `## Zatrzymania autopilota` w `start.md`, a nie w `change.md`. Wznowienie idzie przez `python3 <fabryka>/scripts/autopilot.py --start`; `--start --przyjmij` kończy się kodem 2, poza zatrzymaniem na dostępie kroków (`rodzaj: zgoda`, opis w „Domena spoza domyślnych”). Jedyny inny wyjątek to zatrzymany krok `claude -p` z sesją, przy którym autopilot sam podpowiada `python3 <fabryka>/scripts/autopilot.py --start --odpowiedz '<odpowiedź>'`: wtedy sesja może wznowić go odpowiedzią, jak w `docs/sesja-glowna.md`. Odpowiedź idzie zawsze w apostrofach, a apostrof w niej sesja zapisuje jako `'\''`, bo polecenie autopilota działa poza piaskownicą, a powłoka w cudzysłowie rozwinęłaby `$(…)` i odwrócone apostrofy. Jedna reguła na rodzaj zatrzymania:

- **Pytanie kroku z bramki** (`krok pyta człowieka, bo decyzja trafia na bramkę`): sesja pokazuje człowiekowi pytanie i rekomendację z powodu zatrzymania. Po odpowiedzi dopisuje linię z `krok: <krok>` i `rozstrzygnął: człowiek` do `## Pytania do człowieka` w `start.md`, commituje ją i wznawia krok `--start --odpowiedz '<odpowiedź>'`. Samo `--start` uruchamia krok od nowa, bez commita bez przebiegu, bo krok mógł zostawić pliki w połowie.
- **Zatrzymanie kroku `start`** (np. brak zgody): sesja uzupełnia brak (zgody w sekcji „Pytania-bramki”), commituje `start.md` i uruchamia `--start`. Krok sprawdza warunki od nowa.
- **Brak śladu kroku `claude -p`** (np. `brak pliku context/foundation/prd.md`): sesja uzupełnia pliki kroku bez commitowania ich i uruchamia `--start`. Autopilot widzi, że ślad przechodzi, i robi commit kroku bez ponownego przebiegu. Dzięki temu `szkielet` nigdy nie rusza drugi raz na zapełnionym folderze.
- **Plik z sekretem do dodania** (`.env`, `.env.*`, `.env-*`, `.env_*`, `.dev.vars` i `.dev.vars.*`, w dowolnej wielkości liter, poza `*.example`): sesja dopisuje plik do `.gitignore` (albo go usuwa), commituje tylko `.gitignore` (`git commit -m "chore(start): .env w .gitignore" -- .gitignore`) i uruchamia `--start`. Sekret nie trafia do commita kroku.
- **Krok `infrastruktura` zmienił inne pliki**: sesja przegląda z człowiekiem listę z powodu zatrzymania. Potem cofa zmiany tych plików (`git checkout -- <plik>`, a nowy plik usuwa) i uruchamia `--start`. Autopilot robi commit kroku z samym `infrastructure.md` i `start.md`. Zmianę, którą człowiek chce zachować, sesja robi po starcie zwykłą zmianą.
- **Krok sam zrobił commity** (`sam zrobił commity`) albo **zmienił sekcję człowieka w `start.md` lub `context/foundation/shape-notes.md`**: sesja pokazuje człowiekowi commity albo zmiany z powodu zatrzymania i czeka na jego decyzję. Zatrzymanie wraca przy każdym uruchomieniu, dopóki commity kroku są w historii gałęzi albo zmiana zostaje w drzewie. Po decyzji człowieka sesja wyjmuje commity z gałęzi z plikami w drzewie albo przywraca zmieniony plik lub sekcję z HEAD i uruchamia `--start`; pliki kroku przechodzą wtedy sprawdzenia commita kroku.
- **Lista końcowa** (`lista końcowa czeka na sesję`, `rodzaj: lista`): zatrzymanie po kroku `github`, w każdym starcie, i ponownie, gdy lista nie ma linii „Żeby cała roadmapa poszła bez ciebie, przygotuj:”. Sesja robi to, co mówi sekcja „Lista końcowa”.
- **Inne zatrzymania** (np. `.autopilot-local/` nie jest ignorowane, nazwa folderu nie nadaje się na nazwę repo w kroku `github`): sesja robi to, co mówi powód zatrzymania, i uruchamia `--start`.
- Żeby powtórzyć krok od zera, sesja usuwa jego pliki i uruchamia `--start`.

Poza tym obowiązuje reguła samonaprawy z `<fabryka>/docs/sesja-glowna.md` (sekcja „Zatrzymanie i samonaprawa”), z liniami zatrzymań i pytań w `start.md`.

## Domena spoza domyślnych

Po kroku `zabezpieczenia` krok `domeny` porównuje `allowed_domains` z `.claude/guardrails.json` aplikacji i domeny piaskownicy (`sandbox.network.allowedDomains`) z `.claude/settings.json` i `.claude/settings.local.json` z domenami domyślnymi i z liniami `zgoda: domena <host>` w `## Zgody`. Gdy zabezpieczenia potrzebują domeny spoza rejestru npm i GitHuba (np. `pypi.org` dla innego menedżera pakietów), autopilot zatrzymuje start z `rodzaj: domena` i listą hostów.

- Sesja pyta człowieka o każdy host i to, po co jest, z rekomendacją i gotową odpowiedzią.
- Zgoda: jedna linia na host w `## Zgody`: `- czas: <YYYY-MM-DD HH:MM> · kto: człowiek · zgoda: domena <host> · czego dotyczy: <po co> · odpowiedź: „<cytat>”`. Potem commit `start.md` i ponowne uruchomienie `--start`.
- Potem następny krok `claude -p` (zwykle `roadmapa`) staje przed startem z `rodzaj: zgoda`: kroki biorą dostęp tylko z zapisu `dostep_krokow` w pliku zaufanym poza projektem (D-336), a krok `zabezpieczenia` odświeża go sam tylko wtedy, gdy domeny i `allowWrite` mieszczą się w domyślnych. Sesja pokazuje człowiekowi różnicę z powodu zatrzymania. Po jego zgodzie wpisuje w linii tego zatrzymania w `start.md` `zrobiono: zgoda: człowiek, dostęp kroków`, commituje `start.md` i uruchamia `python3 <fabryka>/scripts/autopilot.py --start --przyjmij`: autopilot odświeża zapis z HEAD i uruchamia krok od nowa.
- Odmowa: start stoi. Sesja proponuje zmianę technologii, która nie potrzebuje tej domeny.

## Lista końcowa

Po kroku `github` autopilot staje w kroku `lista` z `rodzaj: lista`. Sesja uruchamia polecenie sprawdzające z sekcji Verify w `CLAUDE.md` aplikacji i pokazuje człowiekowi w jednej wiadomości:

1. technologię jednym zdaniem;
2. jedno polecenie uruchomienia lokalnego z sekcji `## Uruchomienie lokalne` w `CLAUDE.md` aplikacji (zamiast listy kroków) i wynik polecenia sprawdzającego;
3. roadmapę z polecanym pierwszym kawałkiem: z `## Pierwszy kawałek` w `start.md`, a przy linii `- brak w odpowiedzi kroku roadmapa` według reguły polecanego następnego ruchu (sekcja „Selection rule for the recommended next move”) ze skilla kursu `/10x-roadmap`, zastosowanej do `context/foundation/roadmap.md`;
4. scenariusz pierwszej wersji z PRD;
5. pytania rozstrzygnięte przez agenta (linie z `rozstrzygnął: agent` w `## Pytania do człowieka`);
6. czas i koszt kroków z `## Koszty kroków`;
7. adres repo na GitHubie (`gh repo view --json url`).

Do tego:

- sekcja z linią „Żeby cała roadmapa poszła bez ciebie, przygotuj:” i pozycjami z pól „Potrzebuje” w `context/foundation/roadmap.md` innymi niż „nic”, każda z ID pozycji roadmapy (np. „klucz do modelu AI (S-01)”). Konta do wdrożenia są tu przez pole „Potrzebuje” fundamentu wdrożenia. Lista tylko informuje: start nie pyta o sekrety, nie zbiera ich i nie podaje ich wartości; o brakujący dostęp zapyta raz kawałek, który go potrzebuje, przed swoim łańcuchem. Bez tej linii krok `lista` stoi z `rodzaj: lista`;
- gotowa wiadomość do wklejenia `zrób <ID pierwszego kawałka>`, np. `zrób S-01`, z ID polecanego pierwszego kawałka. Ona idzie sekcją „Kawałek roadmapy” w `<fabryka>/docs/sesja-glowna.md`: przygotowanie przed pierwszym kawałkiem, jedno pytanie o dostępy, konta i zgody, intencja bez pytania i łańcuch zmiany (przy ryzyku Niskie bez researchu).

Na koniec sesja zapisuje tę listę w nowej sekcji `## Lista końcowa` na końcu `start.md` i commituje plik (`git commit -m "docs(start): lista końcowa" -- context/foundation/start.md`). Sama go nie wysyła, bo w piaskownicy repo aplikacji nie ma logowania do GitHuba. Uruchamia na pierwszym planie `python3 <fabryka>/scripts/autopilot.py --start`: krok `lista` wysyła commit (`git push -u origin main`) poza piaskownicą i przebieg się kończy (`autopilot: przebieg zakończony`). Od tej chwili hook i `CLAUDE.md` kierują sesję do `docs/sesja-glowna.md`.

## Rozmowa z człowiekiem

- Każda wiadomość do człowieka idzie według zasad „Jak pisać do człowieka” w `<fabryka>/CLAUDE.md`.
- Pytanie o potwierdzenie treści (np. listy wymagań albo scenariusza) pokazuje tę treść w tej samej wiadomości, przed pytaniem. Człowiek nie potwierdza czegoś, czego nie widział.
- Sesja pyta człowieka tylko na bramkach z reguły „Kiedy pytać człowieka” w tym samym pliku (lista ścieżek w `<fabryka>/docs/zgoda-czlowieka.md`) i w miejscach z tego pliku: pytania-bramki, kształtowanie `/10x-shape` w rozmowie, posiedzenie akceptacji, domena spoza domyślnych, pytanie kroku z bramki.
- Każde pytanie do człowieka i każde rozstrzygnięcie sesji, poza pytaniami kształtowania (zapisuje je `/10x-shape` w `shape-notes.md`), zostawia jedną linię w `## Pytania do człowieka` w `start.md`, a nie w `change.md`: z `krok:` etapu rozmowy (`bramki`, `akceptacja`, `domeny`, a przy pytaniu kroku z bramki nazwa kroku) i z tym, kto rozstrzygnął. Sesja commituje ją od razu poleceniem z listą ścieżek.
