# Zmiany w skillach 10x — etap 8d: krok PR retrospektywy, przegląd planu w łańcuchu, kryteria unieważniane przez późniejszą fazę

Krok PR retrospektywy usunięto w etapie 2a naprawy (2026-11-02, `docs/zmiany-10x/etap-2a-koniec-kroku-pr.md`). Opis niżej zostaje jako historia.

- **Zakres:** gałąź `etap-8d-retro-pr` od `c4e98b8` (`master` przed zmianą) do zamknięcia zmiany.
- **Lista skilli:** `git diff --name-only master...HEAD -- 'skills/10x-*'`. Sekcje dostają skille `10x-*` z tej listy.
- **Własne skille:** `skills/retro/` (opis mówi, że propozycje z celem w `skills/` idą krokiem PR po scaleniu zmiany, a nowy plik `references/pr.md` opisuje ten krok i zawiera polecenia dla sesji autora i recenzenta poprawki) i `skills/intent/` (format wpisu w dzienniku dla propozycji scalonej przez krok PR). Ich kod jest publikowany wprost, więc nie mają tu sekcji.
- **Poza skillami:** skrypt kroku PR z testami na atrapach `gh` i `claude` w test kroku PR; lista ścieżek wymagających zgody człowieka `docs/zgoda-czlowieka.md`; punkty 4 i 9 w `docs/zasady-budowy.md`; ścieżki w lekcji o piaskownicy w `context/foundation/lessons.md`; wpisy w `context/foundation/decisions.md`, `limitations.md` i `decisions-archive.md` (D-043 i D-062 naprawione).
- **Źródło:** lista zadań człowieka (poza repo), `po-8c.md`, punkt 3, zatwierdzona przez człowieka 2026-10-22; propozycja P1 retrospektywy etap-8c-porzadki (D-099); `docs/spec.md`, etap 8.

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-plan

- **Co zmienić:** w sekcji o kryteriach sukcesu faz dopisać akapit o kryteriach Automated, które późniejsza faza celowo psuje. Plan ma najpierw wybierać kryteria sprawdzające stan, który przetrwa do końca planu. Gdy późniejsza faza z założenia zmienia to, co sprawdza kryterium wcześniejszej fazy (usuwa plik, zmienia nazwę sekcji, zmienia wartość), plan przy tym kryterium podaje fazę, po której przestaje ono obowiązywać, i kryterium zastępcze dla nowego stanu.
- **Dlaczego:** w etapie 8c trzy kryteria Automated sprawdzały stan, który późniejsza faza zgodnie z planem zmieniała. Dopisek o tym dostały dopiero po uwagach z review planu i review kodu, a poprawka jednego dopisku sama wymagała kolejnej poprawki. Retrospektywa 8c zaproponowała regułę (P1), a człowiek ją przyjął.
- **Zależności:** brak własnych plików. Reguła działa w samym tekście skilla.
- **Jak sprawdzić:** `awk '/^## Success Criteria Guidelines/,/^## Common Patterns/' skills/10x-plan/SKILL.md | grep -i 'later phase'` pokazuje nowy akapit.

## 10x-test-plan

- **Co zmienić:**
  - Każdy opis łańcucha wykonania fazy wdrożenia testów (opis skilla, tabela powiązań z innymi skillami, reguła kontynuacji po fazie) ma przegląd planu `/10x-plan-review` między `/10x-plan` a `/10x-implement`.
  - Automat stanów, który z plików zmiany wybiera następny skill, rozpoznaje stan „plan bez przeglądu” po braku pliku `reviews/plan-review.md` i wtedy kieruje do `/10x-plan-review`. Do `/10x-implement` kieruje dopiero plan z tym plikiem i niezakończonym Progress.
  - Przekazanie do implementacji mówi, że bez pliku przeglądu najpierw idzie przegląd planu i jego triage.
- **Dlaczego:** opisy łańcucha pomijały przegląd planu, który w fabryce jest obowiązkowym krokiem przed implementacją. Skill kierował więc prosto z planu do implementacji. Ograniczenie D-043 miało spełniony warunek powrotu.
- **Zależności:** `/10x-plan-review` zapisuje swój wynik w `reviews/plan-review.md` zmiany. Automat opiera się na tej nazwie pliku.
- **Jak sprawdzić:** `grep -n '10x-plan\b' skills/10x-test-plan/SKILL.md` — każda linia z łańcuchem do `/10x-implement` ma `/10x-plan-review`; `grep -n 'reviews/plan-review.md' skills/10x-test-plan/SKILL.md` coś zwraca.

## 10x-opportunity-map

- **Co zmienić:** w pytaniu o dalszy krok na końcu skilla opcja „od razu budować” wymienia łańcuch z przeglądem planu `/10x-plan-review` między `/10x-plan` a `/10x-implement`.
- **Dlaczego:** ten sam brak co w `10x-test-plan` (ograniczenie D-043). Użytkownik, który wybrał tę opcję, nie dowiadywał się o przeglądzie planu.
- **Zależności:** brak.
- **Jak sprawdzić:** `grep -n 'Go straight to building' skills/10x-opportunity-map/SKILL.md | grep -c '10x-plan-review'` daje 1.

## 10x-archive

- **Co zmienić:**
  - Punkt „czego skill nie robi” o propozycjach retrospektywy mówi, że po scaleniu i pushu propozycje z celem w `skills/` idą krokiem PR projektu (skrypt kroku PR, gdy repo go ma), a o pozostałych decyduje człowiek po przeczytaniu `retro.md`.
  - Potwierdzenie na końcu archiwizacji dostaje jedną linię z poleceniem kroku PR do uruchomienia po `git merge --ff-only` i `git push`. Linia pojawia się tylko wtedy, gdy repo ma skrypt kroku PR.
  - Krok retrospektywy w archiwum się nie zmienia: dalej zostawia jedyny nowy plik `retro.md` i commituje go osobno.
- **Dlaczego:** w fabryce poprawki skilli z retrospektywy przestały czekać na człowieka. Zatwierdzają je testy skilli i recenzent w osobnej sesji, a człowiek zatwierdza tylko pliki z `docs/zgoda-czlowieka.md`, usunięcie kroku łańcucha, poprawki poza zakresem i płatne testy. Archiwum to commit na gałęzi zmiany, więc PR założony w kroku retrospektywy nie zawierałby ocenianej zmiany. Krok PR idzie dlatego po scaleniu, a archiwum tylko o nim przypomina.
- **Zależności:** skrypt kroku PR, `docs/zgoda-czlowieka.md`, `skills/retro/references/pr.md`. W repo bez skryptu skill zachowuje się jak dotąd, bez nowej linii.
- **Jak sprawdzić:** `diff <(git show c4e98b8:skills/10x-archive/SKILL.md | awk '/^## Retrospective/,/^## Move and stamp/') <(awk '/^## Retrospective/,/^## Move and stamp/' skills/10x-archive/SKILL.md)` nic nie zwraca; `grep -n 'Retro PR step' skills/10x-archive/SKILL.md` pokazywał (do etapu 2a) linię potwierdzenia i punkt o propozycjach.
