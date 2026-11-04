# Zmiany w skillach 10x — poprawka P3 z retrospektywy wdrozenie: źródło zaufania decyzji o dostępie w przeglądzie planu

- **Źródło:** propozycja P3 retrospektywy `context/archive/2026-10-26-wdrozenie/retro.md`, przyjęta przez człowieka w D-348 (`context/foundation/decisions-archive.md`); dowód: trzy zatrzymania przeglądu kodu w zmianie wdrozenie (2026-10-27 00:14, 2026-10-28 10:17, 2026-10-28 12:23) z uwagą o dostępie albo zgodzie opartej na danych, które zmienia ograniczany.

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-plan-review

- **Co zmienić:** w kroku analizy treści planu, w wymiarze o ślepych punktach, przy granicach bezpieczeństwa dopisać jedno zdanie. Recenzent sprawdza, czy decyzja o dostępie albo uprawnieniu opiera się na danych, które może zmienić ten, kogo ta decyzja ogranicza (agent, krok, użytkownik, klient). Zaufanie wolno brać tylko z miejsc, do których ograniczany nie pisze. Sekcja triage'u skilla zostaje bez zmian.
- **Dlaczego:** w zmianie wdrozenie przegląd planu przepuścił plan, w którym zgoda albo granica dostępu kroku opierała się na stanie, który ten krok mógł nadpisać. Błąd wychodził dopiero w przeglądzie kodu i trzy razy zatrzymał autopilota pytaniem do człowieka. Skill wymieniał granice bezpieczeństwa tylko hasłem, bez pytania o to, skąd decyzja bierze zaufanie.
- **Zależności:** brak. Zdanie stoi poza sekcją triage'u, którą `scripts/check_refs.py` porównuje z kopią w `10x-impl-review`, więc kopia nie wymaga zmiany. `10x-impl-review` nie dostaje tego zdania w tej zmianie.
- **Jak sprawdzić:** `grep -n 'cannot write to' skills/10x-plan-review/SKILL.md` pokazuje zdanie w wymiarze o ślepych punktach, a `python3 scripts/check_refs.py` kończy się kodem 0, więc sekcja triage'u jest identyczna w obu skillach. Przegląd planu, który zmienia granice dostępu kroków albo zgodę, dostaje uwagę, gdy decyzja czyta stan zapisywany przez ograniczanego.
