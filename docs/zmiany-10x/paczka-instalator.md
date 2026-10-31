# Zmiany w skillach 10x — paczka-instalator

- **Źródło:** zmiana `paczka-instalator` (kryterium P5 w `change.md` zmiany: blokada 8 kolejnych słów kursu w dopiskach laboratorium; decyzja D-373 o odwołaniu do pliku kursu tylko dla fragmentów zgodnych bajt w bajt).

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-tdd

- **Co zmienić:** w trybie naprawy błędu pogrubiony początek kroku 2 (uruchomienie nowego testu powtarzającego błąd) dostaje nowe brzmienie: test ma się wywrócić właśnie z powodu opisanego błędu. Reszta kroku, czyli co liczy się jako zła przyczyna porażki i co zrobić, gdy test przechodzi, zostaje bez zmian.
- **Dlaczego:** dotychczasowe brzmienie różniło się od zdania z innego miejsca tego skilla tylko pogrubieniem. Eksport paczki zatrzymuje się na 8 kolejnych słowach kursu w tekście dopisanym przez laboratorium, a odwołanie do pliku kursu bierze tylko fragment zgodny bajt w bajt, więc to zdanie zatrzymywało eksport.
- **Zależności:** brak nowych plików. Blokada żyje w `scripts/eksport_paczki.py` laboratorium.
- **Jak sprawdzić:** eksport laboratorium `python3 scripts/eksport_paczki.py <pusty folder>` kończy się kodem 0 i nie wypisuje linii z `skills/10x-tdd/SKILL.md`. Krok 2 trybu naprawy błędu dalej każe uruchomić sam plik testu i odrzucić porażkę z powodu importu, literówki albo brakującego przygotowania.

## 10x-impl-review

- **Co zmienić:** w części o triage'u, w punkcie o lekcji (L3) dopisywanej do `context/foundation/lessons.md`, zdanie o pliku, którego jeszcze nie ma, dostaje nowe brzmienie bez zmiany sensu: najpierw utwórz plik z podanym nagłówkiem. Nagłówek i reszta punktu zostają bez zmian.
- **Dlaczego:** dotychczasowe zdanie miało 8 kolejnych słów z innego zdania tego skilla w kursie i różniło się od niego wielką literą, więc odwołanie do pliku kursu go nie brało, a eksport paczki stawał.
- **Zależności:** brak nowych plików.
- **Jak sprawdzić:** eksport laboratorium kończy się kodem 0 i nie wypisuje linii z `skills/10x-impl-review/SKILL.md`. `grep -n 'when it is missing' skills/10x-impl-review/SKILL.md` pokazuje nowe zdanie w punkcie L3.

## 10x-plan-review

- **Co zmienić:** ta sama zmiana co w `10x-impl-review`: w punkcie o lekcji (L3) zdanie o brakującym `context/foundation/lessons.md` dostaje nowe brzmienie bez zmiany sensu. Nagłówek pliku i reszta punktu zostają bez zmian.
- **Dlaczego:** ten sam powód: 8 kolejnych słów z kursu różniących się wielką literą zatrzymywało eksport paczki.
- **Zależności:** brak nowych plików.
- **Jak sprawdzić:** eksport laboratorium kończy się kodem 0 i nie wypisuje linii z `skills/10x-plan-review/SKILL.md`. `grep -n 'when it is missing' skills/10x-plan-review/SKILL.md` pokazuje nowe zdanie w punkcie L3.
