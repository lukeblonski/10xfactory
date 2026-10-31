# Zmiany w skillach 10x — retro-upgrade-b: poprawka z rundy przeglądu wymienia i sprawdza, co jeszcze zmienia

- **Źródło:** propozycja P2 retrospektywy retro-upgrade (`context/archive/2026-10-23-retro-upgrade/retro.md`), przyjęta w D-161; D-165 kieruje ją do kroku stosowania poprawek, a nie do polityki triage'u.

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-impl-review

- **Co zmienić:** w kroku stosowania poprawek automatycznych (punkt, w którym agent nanosi poprawki AUTO-FIX) dopisać podpunkt: gdy miejsce wskazane przez uwagę jest już poprawione, agent wymienia pozostałe miejsca, których dotyka ta sama poprawka (testy zmienianej funkcji, wywołania i kroki oparte na tej samej funkcji lub pliku, dokumentacja, przykłady). Listę bierze z wyszukiwania `grep` nazwy, wartości albo reguły, którą zmienia, a nie z pamięci. Każde z tych miejsc otwiera i poprawia w tej samej rundzie, a weryfikacja i commit poprawek obejmują je razem z miejscem uwagi. W sekcji o zapisie decyzji, w opisie linii uwagi w `## Decyzje triage`, dopisać przyrostek ` · zmienia też: <miejsca>` (same ścieżki albo nagłówki w backtickach, rozdzielone przecinkami) albo ` · zmienia też: nic poza miejscem uwagi`; przyrostek stoi przed ` · commit <sha>`. Gdy weryfikacja po poprawkach je cofa, w ścieżce cofnięcia przyrostek ` · zmienia też: …` tej rundy usuwa się z linii uwag razem z poprawkami. Sekcja o podagencie triage'u i plik polityki triage'u zostają bez zmian.
- **Dlaczego:** w dziesięciu zmianach z rzędu poprawka z rundy 1 przeglądu wywoływała nowe uwagi w rundzie 2, bo poprawiała jedno miejsce, a pomijała inne, które od niego zależą (retrospektywa retro-upgrade, P2). Lista zapisana przy linii uwagi pozwala retrospektywie później policzyć, czy takich uwag w rundzie 2 jest mniej.
- **Zależności:** opis linii w sekcji o zapisie decyzji jest wspólny dla `10x-impl-review` i `10x-plan-review`; obie kopie muszą mieć ten sam tekst (w fabryce pilnuje tego `scripts/check_refs.py`). Odwołanie do lekcji o listach z wyszukiwania dotyczy pliku `context/foundation/lessons.md`, gdy istnieje.
- **Jak sprawdzić:** `grep -c 'zmienia też' skills/10x-impl-review/SKILL.md` wypisuje co najmniej `2` (krok poprawek i opis linii), a sekcja promptu podagenta triage'u jest taka sama jak przed zmianą.

## 10x-plan-review

- **Co zmienić:** w kroku poprawek planu (punkt, w którym agent nanosi poprawki AUTO-FIX do planu) dopisać ten sam podpunkt w wersji dla planu: pozostałe miejsca to inne sekcje planu, fazy i kroki oparte na tej samej funkcji lub pliku, przykłady w kontraktach, kryteria Automated i `plan-brief.md`. Wyszukiwanie obejmuje plan i `plan-brief.md`, a repozytorium wtedy, gdy poprawka zmienia plik albo regułę poza planem. Miejsca w planie i `plan-brief.md` poprawia się przed ponownym przeglądem; trafienie poza tymi dwoma plikami trafia tylko na listę, bo cofnięcie i commit poprawek planu obejmują tylko te dwa pliki. Gdy sprawdzenie po poprawkach je cofa, przyrostek ` · zmienia też: …` tej rundy znika z linii uwag razem z poprawkami. Opis linii w `## Decyzje triage` dostaje ten sam przyrostek co w `10x-impl-review`, słowo w słowo.
- **Dlaczego:** ten sam wzorzec dotyczy przeglądu planu: poprawka jednej sekcji zostawiała sprzeczność w innej fazie albo w kryterium, a następna runda zgłaszała ją jako nową uwagę.
- **Zależności:** wspólny tekst z `10x-impl-review` (sekcja o zapisie decyzji); bez innych plików.
- **Jak sprawdzić:** `grep -c 'zmienia też' skills/10x-plan-review/SKILL.md` wypisuje co najmniej `2`, a `python3 scripts/check_refs.py` przechodzi (wspólny blok jest identyczny w obu skillach).
