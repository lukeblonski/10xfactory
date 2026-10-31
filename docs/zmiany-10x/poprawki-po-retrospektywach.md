# Zmiany w skillach 10x — poprawki po retrospektywach: zatwierdzone wnioski z retrospektyw 5a, 5b i 5c

- **Zakres:** gałąź `poprawki-po-retrospektywach` od `dc77f89` (`master` przed zmianą) do zamknięcia zmiany.
- **Lista skilli:** `git diff --name-only dc77f89 poprawki-po-retrospektywach -- 'skills/10x-*'`. Wynik: `10x-archive`, `10x-impl-review`, `10x-lesson`, `10x-plan-review`, `10x-plan`.
- **Własne skille:** `skills/intent/` (pytania zwykłym językiem, gałąź przed pierwszym zapisem, krok mniejszego zamiaru, walidator przepuszcza jednolinijkowe wpisy z review) i `skills/retro/` (pliki czytane narzędziami do plików). Ich kod jest publikowany wprost, więc nie mają tu sekcji.
- **Skrypty fabryki:** `scripts/eval_common.sh` (jedna funkcja sprawdzająca katalog zachowanych przebiegów), `scripts/eval_reviewer_models.sh` i `scripts/eval_triage.sh` (wołają ją). Są publikowane wprost, bez sekcji.
- **Cel zmiany:** nanieść 13 propozycji retrospektyw zatwierdzonych przez człowieka 2026-10-21. Kolejne zmiany nie powtarzają już problemów opisanych w retrospektywach: pytań planu o rzeczy rozstrzygnięte przez research, review planu zablokowanego przez decyzje zapisane poza folderem zmiany, podwójnej gałęzi zatrzymania przy archiwizacji i lekcji, których nie wolno było rozszerzyć.

**Wspólne zależności:**
- `context/foundation/lessons.md` z nagłówkiem, który pozwala poprawić istniejącą lekcję w miejscu. Ten sam nagłówek wpisują `10x-plan-review`, `10x-impl-review` i `10x-lesson`, gdy tworzą brakujący plik.

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-archive

- **Co zmienić:**
  - W kroku retrospektywy, w punkcie sprawdzającym, co zostawił skill `retro`, połącz dwie gałęzie zatrzymania w jedną. Warunek: nowe linie `git status --porcelain` względem zapisanego stanu sprzed retrospektywy to cokolwiek innego niż dokładnie nieśledzony `retro.md` tej zmiany, także brak nowych linii.
  - W tej jednej gałęzi skill wypisuje nowe ścieżki, jeśli są, potem jeden komunikat, że archiwizacja zatrzymała się przed przeniesieniem, z instrukcją: usuń `retro.md`, jeśli istnieje, cofnij inne zmiany i uruchom archiwizację ponownie. Potem STOP.
  - Zdanie o plikach, które były brudne już przed retrospektywą, zostaje. Pozostałe punkty kroku bez zmian.
- **Dlaczego:** dwie gałęzie robiły to samo z innym komunikatem, a stary nieśledzony `retro.md` z wcześniejszego przebiegu nie pasował do żadnej z nich. Jedna gałąź obejmuje każdy przypadek, w którym retrospektywa nie zostawiła dokładnie jednego nowego pliku.
- **Zależności:** skill `retro` z repo fabryka (bez zmian w tej części).
- **Jak sprawdzić:** w punkcie sprawdzającym jest jedna gałąź ze STOP. Archiwizacja z `retro`, który niczego nie zapisał, i z `retro`, który zmienił też inny plik, kończy się tym samym komunikatem.

## 10x-impl-review

- **Co zmienić:**
  - W bloku z nagłówkiem, którym skill tworzy brakujący `context/foundation/lessons.md` (gałąź zapisu reguły jako lekcji), zamień zdanie o rejestrze, do którego tylko się dopisuje, na zasadę: nowe lekcje trafiają na koniec, istniejącą lekcję poprawia się w miejscu, gdy zatwierdzona poprawka ją rozszerza, a poprzednia wersja zostaje w historii git. Lista skilli, które czytają plik na starcie, zostaje.
  - Linia nagłówka ma być identyczna z nagłówkiem `lessons.md` fabryki i z tą samą linią w `10x-plan-review` i `10x-lesson`.
- **Dlaczego:** retrospektywy zaproponowały rozszerzenie trzech istniejących lekcji. Stary nagłówek tego zabraniał, więc rozszerzenie musiałoby powstać jako nowa, powtórzona lekcja. Nowy projekt dostawałby dwie sprzeczne zasady, gdyby skill dalej tworzył plik ze starym nagłówkiem.
- **Zależności:** brak.
- **Jak sprawdzić:** `grep -rn 'Append-only register' skills/` nic nie zwraca, a linia nagłówka w skillu jest równa linii `> ` w `context/foundation/lessons.md`.

## 10x-lesson

- **Co zmienić:**
  - Nagłówek tworzonego pliku jak w `10x-impl-review` (ta sama linia).
  - W kroku dopisywania zdanie, które nazywało plik rejestrem tylko do dopisywania, ma mówić, że to ten skill tylko dopisuje i nie zmienia kolejności ani formy istniejących wpisów.
  - W uwagach etykieta punktu o niezmienianiu istniejących lekcji mówi, że skill tylko dopisuje, a uzasadnienie odnosi się do reguły skilla, a nie do konwencji pliku. Treść punktu zostaje: lekcję poprawia człowiek wprost w pliku.
- **Dlaczego:** zasada pliku zmieniła się (lekcję wolno poprawić w miejscu), a ograniczenie skilla zostaje (skill sam niczego nie poprawia). Bez tej zmiany skill opisywałby plik regułą, której plik już nie ma.
- **Zależności:** brak.
- **Jak sprawdzić:** `grep -rn 'the file is append-only' skills/` nic nie zwraca; nagłówek jak w `10x-impl-review`.

## 10x-plan-review

- **Co zmienić:**
  - Warunek startu przed zapisem raportu pierwszej rundy: commit „stan przed review” obejmuje folder zmiany oraz każdy brudny plik w `context/foundation/`, który zawiera wpisy tej zmiany. Pliki dodaje się po nazwie, bez dodawania wszystkiego naraz i bez pomijania hooków. Polecenie commita też wymienia te ścieżki (`git commit -m … -- <folder zmiany> <wybrane pliki>`), więc plik, który ktoś wcześniej dodał do indeksu, nie wchodzi do tego commita.
  - Plik należy do tej zmiany, gdy jego dodane i usunięte linie w `git diff -U0 HEAD` (także zmiany już dodane do indeksu; dla nieśledzonego pliku cała treść) mają linię `Zmiana: <change-id>` i nie mają linii `Zmiana:` z inną wartością. Linie kontekstu diffu się nie liczą, bo dopisek nowego wpisu do `decisions.md` zawsze pokazuje w kontekście ostatnią linię poprzedniego wpisu.
  - Pozostałe brudne pliki dalej zamieniają poprawki w eskalację w kroku poprawek planu, bez zmian.
  - Nagłówek tworzonego `lessons.md` jak w `10x-impl-review`.
  - Nagłówków sekcji agenta triage'u nie zmieniaj, bo test fabryki wycina po nich prompt.
- **Dlaczego:** decyzje zmiany zapisane przy intencji i planie (np. w `decisions.md`) leżą poza folderem zmiany. Brudny `decisions.md` tej samej zmiany zamieniał każdą automatyczną poprawkę w eskalację, choć nic obcego nie było w drzewie.
- **Zależności:** pole `Zmiana: <change-id>` we wpisach `context/foundation/decisions.md` (format dziennika decyzji skilla `intent`).
- **Jak sprawdzić:** zmiana z niezacommitowanym wpisem w `decisions.md`, który kończy się `- Zmiana: <change-id>`, dostaje commit „stan przed review” z tym plikiem, a poprawki AUTO są nanoszone. Brudny plik z wpisem innej zmiany dalej daje eskalację. Plik spoza zmiany dodany wcześniej do indeksu nie trafia do commita „stan przed review”.

## 10x-plan

- **Co zmienić:**
  - Przy tabeli liczby pytań w kroku rozpoznania materiałów wejściowych dopisz zasadę: pytanie o kod, na które research albo sam kod daje rekomendację, nie jest zadawane ani liczone. Agent je rozstrzyga i zapisuje w planie, w sekcji `## Decyzje planu`, z jednym zdaniem uzasadnienia. Liczby w tabeli i w skali złożoności dotyczą tylko pytań o koszt, zakres i zasady.
  - Każde miejsce, które dziś wymusza liczbę pytań albo nazywa kategorie rozwiązania obowiązkowymi do zapytania, odsyła do tej zasady albo powtarza ją jednym zdaniem: komunikat startowy, potwierdzenie liczby pytań i jego opcje, skala złożoności, krok zadawania pytań, przykład z kategorią rozwiązania, zdanie o kategoriach rozwiązania i lista kategorii, lista tego, o co nie pytać, reguła krytyczna, opis sekcji szczegółów implementacji i wytyczna o obowiązkowych pytaniach. W kroku przedstawiania wyników researchu, gdy jedno podejście jest wyraźnie najlepsze i skill nie pyta o wybór, zapisuje to podejście w `## Decyzje planu` z jednym zdaniem uzasadnienia.
  - W szablonie planu dodaj sekcję `## Decyzje planu` po kluczowych odkryciach, a przed listą tego, czego nie robimy: tabela `Decyzja | Wybór | Uzasadnienie` i zdanie, że to decyzje agenta na podstawie researchu i kodu; bez takich decyzji sekcję się pomija.
  - W szablonie usuń luźną listę ręcznych kroków testowych z sekcji strategii testów. Ręczne sprawdzenia to tylko punkty „Manual Verification” fazy i ich wiersze Manual w `## Progress`.
  - W briefie planu tabela kluczowych decyzji obejmuje też wiersze z `## Decyzje planu` (źródło: research).
- **Dlaczego:** skill wymagał minimalnej liczby pytań, więc pytał człowieka o rzeczy, które research już rozstrzygnął, a człowiek wybierał rekomendację. Druga lista ręcznych kroków dublowała wiersze Manual i nie trafiała do `## Progress`, więc nikt jej nie odhaczał.
- **Zależności:** brak.
- **Jak sprawdzić:** `grep -n "^## Decyzje planu" skills/10x-plan/SKILL.md` znajduje sekcję w szablonie, a `grep -n "Manual Testing Steps" skills/10x-plan/SKILL.md` nic nie zwraca. Plan zmiany z researchem pokazuje decyzje o kodzie w `## Decyzje planu`, a pytania tylko o koszt, zakres i zasady.
