# Zmiany w skillach 10x — etap 2a naprawy: koniec kroku PR retrospektywy

- **Zakres:** gałąź `koniec-kroku-pr` od `master` z 2026-11-02 do jej scalenia.
- **Lista skilli:** `git diff --name-only master...koniec-kroku-pr -- 'skills/10x-*'`.
- **Źródło:** decyzja człowieka 2026-11-02 o etapie 2a (D-441 w `context/foundation/decisions.md`).

Opis nie cytuje skilli. Opis jest dla ludzi: w paczce zmiany w skillach `10x-*` nanosi `scripts/instaluj.py` z przepisu `zmiany-10x.json`.

## 10x-archive

- **Co zmienić:** potwierdzenie na końcu archiwizacji traci linię z poleceniem kroku PR retrospektywy. Punkt „czego skill nie robi” o propozycjach retrospektywy mówi tylko, że skill ich nie czyta i nie nanosi, a zajmuje się nimi praca po scaleniu i wysyłce, poza skillem.
- **Dlaczego:** krok PR retrospektywy usunięto (etap 2a). Propozycje prowadzi sesja główna według `docs/sesja-glowna.md`, sekcja „Propozycje retrospektywy”, więc linia wskazywałaby skrypt, którego nie ma.
- **Zależności:** brak.
- **Jak sprawdzić:** `grep -c 'Retro PR step' skills/10x-archive/SKILL.md` daje 0, a krok „Retrospective” skilla zostaje bez zmian.
